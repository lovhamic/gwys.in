"""
MPU6050 data processing for crosshair aiming
Converts raw gyroscope/accelerometer data to smooth crosshair movement
"""

import time
import math
from typing import Optional, Tuple
from config import *


class MPU6050Controller:
    def __init__(self):
        # Calibration offsets
        self.ax_offset = 0
        self.ay_offset = 0
        self.az_offset = 0
        self.gx_offset = 0
        self.gy_offset = 0
        self.gz_offset = 0

        # Calibration state
        self.calibrating = False
        self.calibration_samples = 0
        self.calibration_start_time = 0
        self.calibration_sum = [0, 0, 0, 0, 0, 0]
        self.calibration_min = [None] * 6
        self.calibration_max = [None] * 6
        self.calibration_retries = 0
        self.calibration_unstable = False

        # Crosshair position (normalized 0.0 to 1.0)
        self.crosshair_x = 0.5
        self.crosshair_y = 0.5

        # Smoothed crosshair position
        self.smooth_x = 0.5
        self.smooth_y = 0.5

        # Velocity for smoothing
        self.vel_x = 0.0
        self.vel_y = 0.0

        # Last update time
        self.last_update = time.time()

        # Raw sensor values (for debug)
        self.raw_ax = 0
        self.raw_ay = 0
        self.raw_az = 0
        self.raw_gx = 0
        self.raw_gy = 0
        self.raw_gz = 0

        # Calibrated sensor values
        self.cal_ax = 0
        self.cal_ay = 0
        self.cal_az = 0
        self.cal_gx = 0
        self.cal_gy = 0
        self.cal_gz = 0

    def start_calibration(self):
        """Begin calibration process (fresh attempt, resets retry count)."""
        self.calibration_retries = 0
        self.calibration_unstable = False
        self._begin_calibration_window()

    def _begin_calibration_window(self):
        """(Re)start the sample-collection window for one calibration attempt."""
        self.calibrating = True
        self.calibration_samples = 0
        self.calibration_start_time = time.time()
        self.calibration_sum = [0, 0, 0, 0, 0, 0]
        self.calibration_min = [None] * 6
        self.calibration_max = [None] * 6

    def is_calibrating(self) -> bool:
        return self.calibrating

    def get_calibration_progress(self) -> float:
        """Return calibration progress 0.0 to 1.0"""
        if not self.calibrating:
            return 1.0
        elapsed = time.time() - self.calibration_start_time
        return min(elapsed / CALIBRATION_DURATION, 1.0)

    def update(self, sensor_data: Tuple[int, int, int, int, int, int]) -> Tuple[float, float]:
        """
        Process sensor data and return crosshair position (0.0-1.0, 0.0-1.0)
        """
        ax, ay, az, gx, gy, gz = sensor_data

        # Store raw values
        self.raw_ax, self.raw_ay, self.raw_az = ax, ay, az
        self.raw_gx, self.raw_gy, self.raw_gz = gx, gy, gz

        # Handle calibration
        if self.calibrating:
            self._process_calibration(sensor_data)
            return self.smooth_x, self.smooth_y

        # Apply calibration offsets
        self.cal_gx = gx - self.gx_offset
        self.cal_gy = gy - self.gy_offset
        self.cal_gz = gz - self.gz_offset

        # Current time for delta calculation
        current_time = time.time()
        dt = current_time - self.last_update
        self.last_update = current_time

        # Clamp dt to reasonable range
        dt = max(0.001, min(dt, 0.1))

        # Apply deadzone to gyroscope
        gx_filtered = self._apply_deadzone(self.cal_gx, DEADZONE)
        gy_filtered = self._apply_deadzone(self.cal_gy, DEADZONE)

        # Convert gyroscope to angular velocity (deg/s)
        # MPU6050 at ±250 deg/s: 131 LSB/deg/s
        GYRO_SCALE = 131.0
        ang_vel_x = gx_filtered / GYRO_SCALE  # Roll rate
        ang_vel_y = gy_filtered / GYRO_SCALE  # Pitch rate

        # Update crosshair position based on angular velocity
        # Gyro Y (pitch) -> horizontal movement
        # Gyro X (roll)  -> vertical movement
        # (matches README.md's documented mapping - the gun's physical
        # mounting means pitch reads as horizontal aim on this rig)
        dx = ang_vel_y * SENSITIVITY_X * dt
        dy = ang_vel_x * SENSITIVITY_Y * dt

        # Apply inversion
        if INVERT_X:
            dx = -dx
        if INVERT_Y:
            dy = -dy

        # Update target position
        self.crosshair_x += dx
        self.crosshair_y += dy

        # Clamp to screen bounds (with margin)
        margin = 0.02
        self.crosshair_x = max(margin, min(1.0 - margin, self.crosshair_x))
        self.crosshair_y = max(margin, min(1.0 - margin, self.crosshair_y))

        # Smooth the crosshair movement
        self._smooth_crosshair(dt)

        return self.smooth_x, self.smooth_y

    def _process_calibration(self, sensor_data: Tuple[int, int, int, int, int, int]):
        """Accumulate samples for calibration"""
        for i, value in enumerate(sensor_data):
            self.calibration_sum[i] += value
            if self.calibration_min[i] is None or value < self.calibration_min[i]:
                self.calibration_min[i] = value
            if self.calibration_max[i] is None or value > self.calibration_max[i]:
                self.calibration_max[i] = value
        self.calibration_samples += 1

        # Check if calibration complete
        elapsed = time.time() - self.calibration_start_time
        if elapsed >= CALIBRATION_DURATION or self.calibration_samples >= CALIBRATION_SAMPLES:
            self._finish_calibration()

    def _finish_calibration(self):
        """Calculate and apply calibration offsets - but only if the gun was
        actually held still. Averaging in real rotation (a bump, a shaky
        hand) produces a skewed offset that never zeroes out, which is what
        makes the crosshair drift and feel impossible to control afterward
        even though calibration "succeeded". Detect that and retry instead
        of accepting bad numbers.
        """
        if self.calibration_samples > 0:
            # Gyro axes are indices 3,4,5 in the sample tuple (ax,ay,az,gx,gy,gz).
            gyro_ranges = [
                self.calibration_max[i] - self.calibration_min[i]
                for i in (3, 4, 5)
            ]
            moved_too_much = max(gyro_ranges) > CALIBRATION_MAX_GYRO_RANGE

            if moved_too_much and self.calibration_retries < CALIBRATION_MAX_RETRIES:
                self.calibration_retries += 1
                self.calibration_unstable = True
                self._begin_calibration_window()
                return

            self.ax_offset = self.calibration_sum[0] / self.calibration_samples
            self.ay_offset = self.calibration_sum[1] / self.calibration_samples
            self.az_offset = self.calibration_sum[2] / self.calibration_samples
            self.gx_offset = self.calibration_sum[3] / self.calibration_samples
            self.gy_offset = self.calibration_sum[4] / self.calibration_samples
            self.gz_offset = self.calibration_sum[5] / self.calibration_samples

            # Reset crosshair to center after calibration
            self.crosshair_x = 0.5
            self.crosshair_y = 0.5
            self.smooth_x = 0.5
            self.smooth_y = 0.5
            self.vel_x = 0.0
            self.vel_y = 0.0

        self.calibrating = False
        self.calibration_unstable = False

    def is_calibration_unstable(self) -> bool:
        """True right after a calibration attempt got restarted because the
        gun moved too much to get a clean reading - the caller can show a
        'hold still' message."""
        return self.calibration_unstable

    def get_calibration_attempt(self) -> tuple:
        """Return (current_attempt, max_attempts), 1-indexed, for on-screen
        feedback so a retry is visibly progressing rather than looking
        like a stuck/frozen screen."""
        return (self.calibration_retries + 1, CALIBRATION_MAX_RETRIES + 1)

    def _apply_deadzone(self, value: float, deadzone: int) -> float:
        """Apply deadzone to reduce noise"""
        if abs(value) < deadzone:
            return 0.0
        # Scale the value to remove deadzone discontinuity
        sign = 1 if value > 0 else -1
        return sign * (abs(value) - deadzone)

    def _smooth_crosshair(self, dt: float):
        """Apply smoothing to crosshair movement"""
        # Exponential smoothing
        alpha = SMOOTHING_FACTOR
        self.smooth_x += (self.crosshair_x - self.smooth_x) * alpha
        self.smooth_y += (self.crosshair_y - self.smooth_y) * alpha

    def get_crosshair_pixel_pos(self, screen_width: int, screen_height: int) -> Tuple[int, int]:
        """Get crosshair position in screen pixels"""
        x = int(self.smooth_x * screen_width)
        y = int(self.smooth_y * screen_height)
        return x, y

    def reset_to_center(self):
        """Reset crosshair to center"""
        self.crosshair_x = 0.5
        self.crosshair_y = 0.5
        self.smooth_x = 0.5
        self.smooth_y = 0.5
        self.vel_x = 0.0
        self.vel_y = 0.0

    def get_debug_info(self) -> dict:
        """Return debug information"""
        return {
            'raw': (self.raw_ax, self.raw_ay, self.raw_az, self.raw_gx, self.raw_gy, self.raw_gz),
            'calibrated': (self.cal_ax, self.cal_ay, self.cal_az, self.cal_gx, self.cal_gy, self.cal_gz),
            'offsets': (self.gx_offset, self.gy_offset, self.gz_offset),
            'crosshair_raw': (self.crosshair_x, self.crosshair_y),
            'crosshair_smooth': (self.smooth_x, self.smooth_y),
            'calibrating': self.calibrating,
            'cal_progress': self.get_calibration_progress(),
        }