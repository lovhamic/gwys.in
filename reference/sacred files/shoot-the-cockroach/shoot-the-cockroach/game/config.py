"""
Configuration for Shoot the Cockroach game
Modify these values to tune the game behavior
"""

# ==================== SERIAL CONFIGURATION ====================
# Windows: usually COM3, COM4, etc. (check Device Manager)
# Linux/Mac: usually /dev/ttyUSB0, /dev/ttyACM0, etc.
SERIAL_PORT = "COM3"          # Change this to your ESP32 port
BAUD_RATE = 115200            # Must match ESP32 code
SERIAL_TIMEOUT = 1.0          # Serial read timeout (seconds)

# ==================== GAME WINDOW ====================
SCREEN_WIDTH = 1024
SCREEN_HEIGHT = 768
FPS = 60
WINDOW_TITLE = "Shoot the Cockroach"

# ==================== COLORS ====================
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
CYAN = (0, 255, 255)
MAGENTA = (255, 0, 255)
DARK_GRAY = (40, 40, 40)
LIGHT_GRAY = (180, 180, 180)
BROWN = (139, 69, 19)
DARK_BROWN = (101, 67, 33)

# ==================== MPU6050 AIMING CONFIGURATION ====================
SENSITIVITY_X = 0.008         # Gyroscope X sensitivity (horizontal aim)
SENSITIVITY_Y = 0.008         # Gyroscope Y sensitivity (vertical aim)
SMOOTHING_FACTOR = 0.15       # Crosshair smoothing (0.0-1.0, lower = smoother)
DEADZONE = 50                 # Gyroscope deadzone to prevent drift
INVERT_X = False              # Invert horizontal axis
INVERT_Y = True               # Invert vertical axis

# Calibration
CALIBRATION_SAMPLES = 200     # Number of samples for calibration
CALIBRATION_DURATION = 3.0    # Calibration time (seconds)
CALIBRATION_MAX_GYRO_RANGE = 3000  # Max raw gyro min/max spread allowed during
                                    # calibration (~23 deg/s peak-to-peak) before
                                    # it's considered "moved, not held still" and
                                    # gets retried automatically. Generous on
                                    # purpose - natural hand tremor on a handheld
                                    # gun easily swings a few deg/s, and a value
                                    # much tighter than this (e.g. 400, ~3 deg/s)
                                    # rejects almost every real attempt, making
                                    # calibration take forever / never settle.
CALIBRATION_MAX_RETRIES = 3        # Give up and accept after this many retries
                                    # (bounds worst case to a few seconds, not
                                    # an indefinite loop)

# ==================== CROSSHAIR ====================
CROSSHAIR_SIZE = 24
CROSSHAIR_COLOR = GREEN
CROSSHAIR_THICKNESS = 3

# ==================== COCKROACH ====================
COCKROACH_BASE_SPEED = 80     # Pixels per second (Level 1)
COCKROACH_MAX_SPEED = 250     # Max speed at highest level
COCKROACH_SIZE = 40           # Cockroach width/height
COCKROACH_HIT_RADIUS = 35     # Hit detection radius
COCKROACH_SPAWN_MARGIN = 80   # Margin from screen edges

# Cockroach behavior
DIRECTION_CHANGE_INTERVAL = (1.5, 4.0)  # Min/max seconds between direction changes
COCKROACH_ACCELERATION = 30   # Speed change rate

# ==================== LEVELS ====================
LEVEL_CONFIGS = [
    {   # Level 1
        "name": "Level 1 - Infestation",
        "cockroach_count": 1,
        "speed_multiplier": 1.0,
        "hitbox_multiplier": 1.5,
        "time_per_cockroach": 8.0,
        "direction_change_rate": 1.0,
        "score_per_hit": 10,
        "fast_hit_bonus": 10,
        "fast_hit_threshold": 2.0,
    },
    {   # Level 2
        "name": "Level 2 - Swarm",
        "cockroach_count": 1,
        "speed_multiplier": 1.5,
        "hitbox_multiplier": 1.2,
        "time_per_cockroach": 6.0,
        "direction_change_rate": 1.3,
        "score_per_hit": 15,
        "fast_hit_bonus": 15,
        "fast_hit_threshold": 1.5,
    },
    {   # Level 3
        "name": "Level 3 - Invasion",
        "cockroach_count": 1,
        "speed_multiplier": 2.0,
        "hitbox_multiplier": 1.0,
        "time_per_cockroach": 4.5,
        "direction_change_rate": 1.6,
        "score_per_hit": 20,
        "fast_hit_bonus": 20,
        "fast_hit_threshold": 1.0,
    },
]

# ==================== SCORING & LIVES ====================
STARTING_LIVES = 3
LIFE_LOST_ON_ESCAPE = 1
POINTS_PER_HIT = 10

# ==================== SHOOTING ====================
SHOOT_EFFECT_DURATION = 0.15   # Seconds
MUZZLE_FLASH_RADIUS = 30
HIT_EFFECT_DURATION = 0.5
MISS_EFFECT_DURATION = 0.3

# ==================== DEBUG ====================
DEBUG_MODE = True              # Enable debug overlay
SHOW_FPS = True                # Show FPS counter
SHOW_RAW_SENSOR_DATA = True    # Show raw MPU6050 values

# ==================== AUDIO (optional) ====================
ENABLE_SOUND = True
SHOOT_SOUND_FILE = "assets/shoot.wav"
HIT_SOUND_FILE = "assets/hit.wav"

# ==================== ASSETS ====================
COCKROACH_IMAGE_FILE = "assets/cockroach.png"
BACKGROUND_IMAGE_FILE = "assets/background.png"