import cv2
import numpy as np
import math
import threading
import queue
import json
import os

# =================== Setup ===================
# IP camera stream URL from your phone's camera-streaming app (adjust IP/port as needed)
CAMERA_SOURCE = "http://10.107.8.188:4747/video"

CAMERA_HEIGHT_CM = 79.0  # height from the table surface to the camera (tripod head)
CALIBRATION_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "camera_calibration.json")

cap = cv2.VideoCapture(CAMERA_SOURCE)
if not cap.isOpened():
    raise IOError("Cannot open camera feed")

ret, probe = cap.read()
if not ret:
    raise IOError("Camera opened but returned no frames.")
FRAME_H, FRAME_W = probe.shape[:2]

# Virtual origin = center of the frame -> world coordinate (0, 0) on the table,
# assuming the camera looks straight down and its optical axis passes through this point.
ORIGIN_PX = (FRAME_W // 2, FRAME_H // 2)

# --- Focal length in pixels (key unknown in the projection formula) ---
# This is an intrinsic property of the camera/lens -- it does NOT change with table height,
# so once calibrated it's saved to disk and auto-loaded on every future run at this resolution.
#
# Redmi Note 7 Pro rear camera (48MP primary) is spec'd at 26mm, 35mm-equivalent focal length.
# We convert that to pixels using the standard full-frame sensor width (36mm) as the reference:
#   HFOV = 2 * atan(36mm / (2 * 26mm))
#   focal_px = (frame_width_px / 2) / tan(HFOV / 2)
# This is a much better starting estimate than a generic FOV guess, but it's still derived from
# a spec sheet, not measured on your actual stream -- a phone's camera-streaming app can
# crop or resize the feed, which may shift it slightly.
# Treat it as "good enough to use immediately," and still run one ruler calibration (press 'k')
# if you want the verified, exact value.
PHONE_FOCAL_LENGTH_35MM_EQUIV = 26.0  # mm, Redmi Note 7 Pro main camera spec
FULL_FRAME_SENSOR_WIDTH_MM = 36.0
_hfov_rad = 2 * math.atan(FULL_FRAME_SENSOR_WIDTH_MM / (2 * PHONE_FOCAL_LENGTH_35MM_EQUIV))
FOCAL_PX_FROM_SPEC = (FRAME_W / 2) / math.tan(_hfov_rad / 2)

focal_px = FOCAL_PX_FROM_SPEC
focal_calibrated = False
focal_source = "phone spec (26mm equiv, unverified)"


def load_saved_calibration():
    global focal_px, focal_calibrated, focal_source
    if not os.path.exists(CALIBRATION_FILE):
        return
    try:
        with open(CALIBRATION_FILE, "r") as f:
            data = json.load(f)
        if data.get("frame_w") == FRAME_W and data.get("frame_h") == FRAME_H:
            focal_px = float(data["focal_px"])
            focal_calibrated = True
            focal_source = "ruler-verified (saved)"
            print(f"Loaded saved calibration: focal_px={focal_px:.2f} "
                  f"(from {CALIBRATION_FILE}, matches current {FRAME_W}x{FRAME_H} resolution)")
        else:
            print(f"Found a saved calibration but it was for a different resolution "
                  f"({data.get('frame_w')}x{data.get('frame_h')} vs current {FRAME_W}x{FRAME_H}) "
                  f"-- ignoring it. Using the phone-spec estimate for now; press 'k' to verify with a ruler.")
    except (json.JSONDecodeError, KeyError, ValueError, OSError):
        print("Saved calibration file was unreadable -- ignoring it. Press 'k' to calibrate.")


def save_calibration():
    try:
        with open(CALIBRATION_FILE, "w") as f:
            json.dump({"focal_px": focal_px, "frame_w": FRAME_W, "frame_h": FRAME_H,
                       "camera_height_cm_when_calibrated": CAMERA_HEIGHT_CM}, f, indent=2)
        print(f"Calibration saved to {CALIBRATION_FILE} -- future runs will load it automatically.")
    except OSError as e:
        print(f"Could not save calibration to disk: {e}")


load_saved_calibration()

bg_subtractor = cv2.createBackgroundSubtractorMOG2(history=300, varThreshold=40, detectShadows=True)
MIN_OBJ_AREA = 900

# --- Calibration state ---
calibrating = False
calib_clicks = []          # up to 2 points defining a reference of known real-world length
mouse_pos = (0, 0)
ZOOM_SIZE = 60              # half-size (px) of the region magnified around the cursor
ZOOM_SCALE = 6              # magnification factor

# Typing the reference length happens in the TERMINAL, but via a background thread --
# this is what prevents the console prompt from freezing the video window. The video
# loop keeps running and rendering every frame while it waits for the thread to finish;
# it just checks the queue once per frame to see if you've submitted an answer yet.
awaiting_length = False
pending_pixel_len = 0.0
length_result_queue = queue.Queue()


def ask_for_length_in_background(pixel_len):
    """Runs on a separate thread so input() can block THAT thread without freezing the video."""
    try:
        text = input(f"\n>>> Pixel length measured: {pixel_len:.2f}px. "
                      f"Enter the REAL length between those ruler marks, in cm, then press Enter: ")
        length_result_queue.put(text)
    except EOFError:
        length_result_queue.put("")


def on_mouse(event, x, y, flags, param):
    global calib_clicks, mouse_pos
    mouse_pos = (x, y)
    if event == cv2.EVENT_LBUTTONDOWN and calibrating and len(calib_clicks) < 2:
        calib_clicks.append((x, y))


cv2.namedWindow("feed")
cv2.setMouseCallback("feed", on_mouse)


def largest_contour_centroid(contour):
    M = cv2.moments(contour)
    if M["m00"] == 0:
        return None
    return (int(M["m10"] / M["m00"]), int(M["m01"] / M["m00"]))


def pixel_to_world_cm(px, py):
    """Pinhole projection: pixel position -> real-world (X, Y) cm relative to the origin."""
    u_rel = px - ORIGIN_PX[0]
    v_rel = py - ORIGIN_PX[1]
    x_cm = (u_rel * CAMERA_HEIGHT_CM) / focal_px
    y_cm = (v_rel * CAMERA_HEIGHT_CM) / focal_px
    return x_cm, y_cm


def draw_zoom_inset(frame, source_frame, center):
    """Shows a magnified view around the cursor so calibration clicks can be placed
    precisely on a ruler tick mark instead of guessing at native resolution."""
    cx, cy = center
    x0, x1 = max(0, cx - ZOOM_SIZE), min(FRAME_W, cx + ZOOM_SIZE)
    y0, y1 = max(0, cy - ZOOM_SIZE), min(FRAME_H, cy + ZOOM_SIZE)
    patch = source_frame[y0:y1, x0:x1]
    if patch.size == 0:
        return
    zoomed = cv2.resize(patch, None, fx=ZOOM_SCALE, fy=ZOOM_SCALE, interpolation=cv2.INTER_LINEAR)
    zh, zw = zoomed.shape[:2]
    cv2.line(zoomed, (zw // 2, 0), (zw // 2, zh), (0, 255, 255), 1)
    cv2.line(zoomed, (0, zh // 2), (zw, zh // 2), (0, 255, 255), 1)
    cv2.rectangle(zoomed, (0, 0), (zw - 1, zh - 1), (0, 165, 255), 2)

    ih, iw = zoomed.shape[:2]
    ox, oy = FRAME_W - iw - 10, 10
    if oy + ih <= FRAME_H and ox >= 0:
        frame[oy:oy + ih, ox:ox + iw] = zoomed


# --- One-time "frozen" measurement (averages several frames to cancel out pixel jitter) ---
sampling = False
sample_buffer = []
SAMPLE_FRAMES = 25
frozen_result = None  # (x_cm, y_cm, resultant_cm, angle_deg) once a sample completes

print("== Coordinate tracking ==")
print(f"Frame size: {FRAME_W}x{FRAME_H}. Virtual origin fixed at center: {ORIGIN_PX}")
print(f"Camera height: {CAMERA_HEIGHT_CM} cm.")
print("Press 'k' to calibrate using your ruler: click two tick marks in the VIDEO window,")
print("then switch to THIS terminal and type the real length in cm when prompted.")
print("Press 's' to take an averaged, jitter-free measurement of the current object.")
print("Press 'm' to toggle the detection mask, 'r' to clear a frozen sample, ESC to stop.")

show_mask = False
obj_center = None
obj_contour = None
lost_frames = 0
max_lost_frames = 8

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break
    raw_frame = frame.copy()  # untouched copy for the zoom inset (no overlays baked in)

    # ---- Calibration workflow: click two points in the video window ----
    if calibrating:
        cv2.putText(frame, "CALIBRATING: click 2 tick marks on the ruler (use zoom inset for precision)",
                    (10, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.55, (0, 165, 255), 2)
        for pt in calib_clicks:
            cv2.circle(frame, pt, 5, (0, 165, 255), -1)
        if len(calib_clicks) == 1:
            cv2.line(frame, calib_clicks[0], mouse_pos, (0, 165, 255), 1)
        draw_zoom_inset(frame, raw_frame, mouse_pos)

        if len(calib_clicks) == 2:
            cv2.line(frame, calib_clicks[0], calib_clicks[1], (0, 165, 255), 2)
            pending_pixel_len = float(np.hypot(calib_clicks[1][0] - calib_clicks[0][0],
                                                calib_clicks[1][1] - calib_clicks[0][1]))
            calibrating = False
            calib_clicks = []
            awaiting_length = True
            # Start the console prompt on its own thread -- the video loop below keeps
            # running normally the whole time this is waiting for you to type and hit Enter.
            threading.Thread(target=ask_for_length_in_background, args=(pending_pixel_len,),
                              daemon=True).start()

    # ---- Check if the background thread has received your typed answer yet ----
    if awaiting_length:
        cv2.rectangle(frame, (0, FRAME_H // 2 - 30), (FRAME_W, FRAME_H // 2 + 30), (0, 0, 0), -1)
        cv2.putText(frame, "Switch to the TERMINAL now and type the real length in cm, then press Enter",
                    (20, FRAME_H // 2 + 8), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2)
        try:
            text = length_result_queue.get_nowait()
            try:
                real_len_cm = float(text)
                if real_len_cm > 0:
                    focal_px = (pending_pixel_len * CAMERA_HEIGHT_CM) / real_len_cm
                    focal_calibrated = True
                    focal_source = "ruler-verified (saved)"
                    print(f"Calibrated focal length: {focal_px:.2f}px "
                          f"(valid at camera height {CAMERA_HEIGHT_CM}cm). "
                          f"Scale: {CAMERA_HEIGHT_CM / focal_px:.4f} cm/px")
                    save_calibration()
                else:
                    print("Length must be positive -- calibration cancelled.")
            except ValueError:
                print("Invalid number -- calibration cancelled.")
            awaiting_length = False
        except queue.Empty:
            pass  # still waiting on you to type in the terminal -- keep looping, feed stays live

    # ---- Detect the placed/moving object on the table ----
    fg_mask = bg_subtractor.apply(frame)
    _, fg_mask = cv2.threshold(fg_mask, 200, 255, cv2.THRESH_BINARY)
    fg_mask = cv2.morphologyEx(fg_mask, cv2.MORPH_OPEN, None, iterations=2)
    fg_mask = cv2.dilate(fg_mask, None, iterations=3)

    contours, _ = cv2.findContours(fg_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    largest = max(contours, key=cv2.contourArea, default=None)

    if largest is not None and cv2.contourArea(largest) >= MIN_OBJ_AREA:
        centroid = largest_contour_centroid(largest)
        if centroid is not None:
            obj_center = centroid
            obj_contour = largest
            lost_frames = 0
    else:
        lost_frames += 1
        if lost_frames > max_lost_frames:
            obj_center = None
            obj_contour = None

    # ---- Handle an in-progress averaged sample ----
    if sampling:
        if obj_center is not None:
            sample_buffer.append(obj_center)
        if len(sample_buffer) >= SAMPLE_FRAMES:
            avg_x = sum(p[0] for p in sample_buffer) / len(sample_buffer)
            avg_y = sum(p[1] for p in sample_buffer) / len(sample_buffer)
            x_cm, y_cm = pixel_to_world_cm(avg_x, avg_y)
            resultant_cm = math.hypot(x_cm, y_cm)
            angle_deg = math.degrees(math.atan2(-y_cm, x_cm))  # standard math angle, y-up
            frozen_result = (x_cm, y_cm, resultant_cm, angle_deg)
            print(f"FROZEN MEASUREMENT -- X={x_cm:+.2f}cm  Y={y_cm:+.2f}cm  "
                  f"Resultant={resultant_cm:.2f}cm  Angle={angle_deg:+.1f} deg "
                  f"(averaged over {len(sample_buffer)} frames)")
            sampling = False
            sample_buffer = []

    # ---- Draw the virtual origin ----
    cv2.drawMarker(frame, ORIGIN_PX, (0, 0, 255), markerType=cv2.MARKER_CROSS, markerSize=24, thickness=2)
    cv2.putText(frame, "Origin (0,0)", (ORIGIN_PX[0] + 12, ORIGIN_PX[1] - 12),
                cv2.FONT_HERSHEY_SIMPLEX, 0.55, (0, 0, 255), 2)

    # ---- Draw detected object + live coordinates ----
    if obj_contour is not None and obj_center is not None:
        cv2.drawContours(frame, [obj_contour], -1, (0, 255, 0), 2)
        cv2.circle(frame, obj_center, 4, (0, 255, 0), -1)
        cv2.line(frame, ORIGIN_PX, obj_center, (255, 255, 0), 2)

        x_cm, y_cm = pixel_to_world_cm(*obj_center)
        resultant_cm = math.hypot(x_cm, y_cm)
        cv2.putText(frame, f"X={x_cm:+.1f}cm Y={y_cm:+.1f}cm", (obj_center[0] + 10, obj_center[1] - 28),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.55, (255, 255, 0), 2)
        cv2.putText(frame, f"Resultant={resultant_cm:.1f}cm", (obj_center[0] + 10, obj_center[1] - 8),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.55, (255, 255, 0), 2)

    if sampling:
        cv2.putText(frame, f"Sampling... {len(sample_buffer)}/{SAMPLE_FRAMES} (hold object still)",
                    (10, FRAME_H - 45), cv2.FONT_HERSHEY_SIMPLEX, 0.55, (0, 255, 255), 2)

    if frozen_result is not None:
        fx, fy, fr, fa = frozen_result
        cv2.putText(frame,
                    f"LAST FROZEN: X={fx:+.2f}cm Y={fy:+.2f}cm Resultant={fr:.2f}cm @ {fa:+.1f}deg",
                    (10, FRAME_H - 65), cv2.FONT_HERSHEY_SIMPLEX, 0.55, (0, 255, 0), 2)

    status = "CALIBRATED" if focal_calibrated else f"ESTIMATED from {focal_source} (press 'k' to verify with ruler)"
    cv2.putText(frame, f"Focal length: {status}", (10, FRAME_H - 15),
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (200, 200, 200), 1)

    cv2.imshow("feed", frame)

    if show_mask:
        cv2.imshow("detection mask (debug)", fg_mask)
    else:
        try:
            if cv2.getWindowProperty("detection mask (debug)", 0) >= 0:
                cv2.destroyWindow("detection mask (debug)")
        except cv2.error:
            pass

    key = cv2.waitKey(40) & 0xFF
    if key == 27:
        print("Stopped by user.")
        break
    elif key == ord('k') and not calibrating and not awaiting_length:
        calibrating = True
        calib_clicks = []
        print("Calibration started: click two tick marks on the ruler in the VIDEO window "
              "(a wider gap, e.g. 0-15cm, is more accurate).")
    elif key == ord('m'):
        show_mask = not show_mask
    elif key == ord('s'):
        sampling = True
        sample_buffer = []
        print("Sampling started -- keep the object still...")
    elif key == ord('r'):
        frozen_result = None

cv2.destroyAllWindows()
cap.release()
