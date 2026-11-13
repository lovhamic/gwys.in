# Webcam Object Coordinate Tracker

A Python/OpenCV tool that turns an overhead webcam (including a phone camera streamed
over Wi-Fi via an IP-camera app) into a simple 2D coordinate-measuring system.
It detects an object placed on a table and reports its real-world position
(in centimeters) relative to a fixed virtual origin at the center of the camera's view.

---

## How it works

The camera is assumed to be mounted **directly above the table, looking straight down**,
at a known height `CAMERA_HEIGHT_CM`. Under that assumption, converting a pixel position
to a real-world position on the table is a standard pinhole-camera projection:

```
X_cm = (u - cx) * H / f
Y_cm = (v - cy) * H / f
```

| Symbol | Meaning |
|---|---|
| `(u, v)` | Pixel coordinates of the detected object |
| `(cx, cy)` | Pixel coordinates of the frame center (the virtual origin, world coordinate `(0, 0)`) |
| `H` | Camera height above the table, in cm (`CAMERA_HEIGHT_CM`) |
| `f` | Camera's focal length, in **pixels** (an intrinsic property of the camera/lens) |

The only real unknown is `f`. The script gets a starting value for it automatically
(from the Redmi Note 7 Pro's published spec), and can be calibrated precisely against
a ruler placed on the table for a verified, exact value.

---

## Requirements

```bash
pip install opencv-python numpy
```

Python 3.8+ recommended.

---

## Camera setup (phone camera over Wi-Fi)

1. Install an IP-camera streaming app on your phone (any app that exposes an
   MJPEG/HTTP video stream works).
2. Connect your phone and computer to the **same Wi-Fi network**.
3. Open the app on the phone — it will display an IP address and port.
4. Set `CAMERA_SOURCE` near the top of the script to that stream URL:
   ```python
   CAMERA_SOURCE = "http://<phone-ip>:4747/video"
   ```
5. Mount the phone on a tripod directly above the table, lens facing straight down.
6. Measure the height from the table surface to the camera lens and set:
   ```python
   CAMERA_HEIGHT_CM = <your measured height>
   ```

You can also use a regular USB/built-in webcam by setting `CAMERA_SOURCE = 0`
(or `1`, `2`... if you have multiple cameras).

---

## Running it

```bash
python webcam_coordinate_tracker.py
```

A window titled **"feed"** opens showing the live camera view with:
- A red crosshair marking the fixed **virtual origin** `(0, 0)`.
- A green outline around whatever object is currently detected on the table.
- Live `X`, `Y`, and `Resultant` (straight-line distance from origin) readings in cm.

---

## Focal length: automatic estimate vs. calibration

On first run, the script estimates the focal length from the Redmi Note 7 Pro's
published camera spec (26mm, 35mm-equivalent) — good enough to use immediately,
but not verified against your actual camera stream (a phone's camera-streaming app can
crop or resize the feed, which may shift it slightly).

For a **verified, exact** value, calibrate once using a ruler:

1. Place a ruler flat on the table, in view of the camera.
2. Press **`k`**.
3. Click two tick marks on the ruler in the video window (a wider gap, e.g. 0–15cm,
   gives a more accurate result). A magnified zoom inset appears near your cursor
   to help you click precisely.
4. Switch to the **terminal** — it will prompt you for the real-world distance
   (in cm) between the two points you clicked. Type it and press Enter.
5. The calibrated focal length is saved to `camera_calibration.json`, next to the
   script, and will be **loaded automatically on every future run** at the same
   resolution — you only need to do this once.

If you ever switch cameras, change the video resolution, or get inconsistent
readings, just press `k` again to recalibrate.

> **Note:** the focal length does not depend on `CAMERA_HEIGHT_CM` — it's a fixed
> property of the lens. If you change the tripod height, just update
> `CAMERA_HEIGHT_CM` in the script; no recalibration needed.

---

## Taking a clean measurement

Live readings can jitter slightly frame-to-frame due to pixel noise. For a
stable, accurate one-time reading:

1. Place the object on the table and let it sit still.
2. Press **`s`**.
3. The program averages the object's position over 25 frames and reports a
   final, "frozen" measurement — `X`, `Y`, `Resultant`, and the angle (in
   degrees) — both printed to the console and pinned on-screen.
4. Press **`r`** to clear the frozen result and take a new one.

---

## Controls

| Key | Action |
|---|---|
| `k` | Start ruler calibration (click 2 points, then type the real length in the terminal) |
| `s` | Take an averaged, jitter-free "frozen" measurement of the current object |
| `r` | Clear the current frozen measurement |
| `m` | Toggle a debug window showing the raw object-detection mask |
| `Esc` | Quit |

---

## Assumptions & limitations

- **Camera must look straight down** at the table. If it's mounted at an angle,
  the projection formula above does not hold as-is — it would need an additional
  tilt-angle correction term.
- **Single object tracking**: the script tracks the single largest moving/placed
  object detected via background subtraction. It's not designed to track multiple
  objects simultaneously.
- **Flat table surface**: the math assumes everything being measured lies on the
  same plane as the calibration ruler (i.e., the tabletop). Tall objects will
  measure slightly inaccurately at their base-contact point vs. their visible top.
- **Resolution-dependent calibration**: `focal_px` is tied to the specific frame
  resolution it was calibrated at. Changing resolution requires recalibration.

---

## Files

| File | Purpose |
|---|---|
| `webcam_coordinate_tracker.py` | Main program |
| `camera_calibration.json` | Auto-generated after calibration; stores the verified focal length so you don't need to recalibrate on every run |
