#ifndef CONFIG_H
#define CONFIG_H

// =============================================================================
// AI ROBOTIC ARM — CONFIGURATION
// ESP32-WROOM-32 | 3-DOF + Stepper Base + Gripper | Remote AI Backend
// =============================================================================

// WiFi Settings
static const char* WIFI_SSID     = "Dhilbar";
static const char* WIFI_PASSWORD = "freefree";  // <-- CHANGE THIS TO YOUR REAL PASSWORD

// Backend Server
static const char* SERVER_HOST   = "10.222.194.223";
static const int   SERVER_PORT   = 8000;
static const char* SERVER_PATH   = "/ws/esp32";

// =============================================================================
// STEPPER MOTOR — Base rotation (NEMA 17 + A4988)
// =============================================================================

#define PIN_STEPPER_STEP   26   // A4988 STEP
#define PIN_STEPPER_DIR    27   // A4988 DIR
#define PIN_STEPPER_EN     12   // A4988 ENABLE (active low)

#define STEPPER_STEPS_PER_REV  200    // NEMA 17 full steps per revolution
#define STEPPER_MICROSTEPS     8      // A4988 microstepping (MS1/MS2/MS3 pins)
#define STEPPER_MIN_ANGLE      0.0f   // degrees
#define STEPPER_MAX_ANGLE      360.0f // degrees
#define STEPPER_DEFAULT_ANGLE  0.0f   // home position
#define STEPPER_STEP_DELAY_US  800    // microseconds between step pulses (adjust for speed)

// =============================================================================
// SERVO CONFIGURATION — Shoulder (standard), Elbow (standard), Wrist (continuous), Gripper (continuous)
// =============================================================================

#define NUM_SERVOS 4

// GPIO pins for each servo (base removed — now stepper)
#define PIN_SERVO_SHOULDER 13   // Servo 1 — Shoulder (STANDARD 0-180°)
#define PIN_SERVO_ELBOW    14   // Servo 2 — Elbow (STANDARD 0-180°)
#define PIN_SERVO_WRIST    15   // Servo 3 — Wrist (CONTINUOUS 360°)
#define PIN_SERVO_GRIPPER  16   // Servo 4 — Gripper (CONTINUOUS 9g)

// Servo types
#define SERVO_TYPE_STANDARD    0
#define SERVO_TYPE_CONTINUOUS  1

// [shoulder, elbow, wrist, gripper]
static const int SERVO_TYPES[NUM_SERVOS] = {
  SERVO_TYPE_STANDARD,    // Shoulder
  SERVO_TYPE_STANDARD,    // Elbow
  SERVO_TYPE_CONTINUOUS,  // Wrist
  SERVO_TYPE_CONTINUOUS   // Gripper
};

static const int SERVO_CHANNELS[NUM_SERVOS] = {0, 1, 2, 3};
static const int SERVO_PINS[NUM_SERVOS] = {PIN_SERVO_SHOULDER, PIN_SERVO_ELBOW, PIN_SERVO_WRIST, PIN_SERVO_GRIPPER};

// Continuous servo control: 90 = stop, 0 = full speed one direction, 180 = full speed other
static const int CONTINUOUS_STOP = 90;
static const int CONTINUOUS_MIN_SPEED = 0;    // Full speed CW (or CCW, depends on servo)
static const int CONTINUOUS_MAX_SPEED = 180;  // Full speed CCW (or CW)

// Standard servo joint limits (degrees) — [shoulder, elbow]
static const int JOINT_MIN[2] = {  0,   0};
static const int JOINT_MAX[2] = {135, 135};
static const int JOINT_DEFAULT[2] = {90, 90};

// Stepper base joint limits
static const float BASE_MIN_ANGLE = 0.0f;
static const float BASE_MAX_ANGLE = 360.0f;
static const float BASE_DEFAULT_ANGLE = 0.0f;

// Gripper (continuous) — 0.5 = stop, 0 = close fast, 1 = open fast
static const float GRIPPER_MIN = 0.0f;
static const float GRIPPER_MAX = 1.0f;
static const float GRIPPER_DEFAULT = 0.5f;
static const float GRIPPER_STOP = 0.5f;

// =============================================================================
// PWM SETTINGS
// =============================================================================
static const int   SERVO_PWM_FREQ        = 50;      // Hz (standard servo)
static const int   SERVO_PWM_RESOLUTION  = 16;      // bits
static const int   MOTION_SMOOTHING_STEPS = 30;     // interpolation steps per command
static const int   MOTION_MIN_STEP_MS    = 15;      // minimum ms between servo updates

// =============================================================================
// SENSOR PINS & SETTINGS
// =============================================================================
#define PIN_ULTRASONIC_TRIG 17
#define PIN_ULTRASONIC_ECHO  5
#define PIN_CURRENT_SENSOR  34

static const unsigned long SENSOR_READ_INTERVAL_MS = 100;
static const unsigned long STATE_SEND_INTERVAL_MS  = 200;

// Current sensor calibration (ACS712-5A with 10k+10k divider)
static const float CURRENT_ADC_TO_VOLTS = 3.3f / 4095.0f;
static const float CURRENT_DIVIDER_RATIO  = 2.0f;
static const float CURRENT_ZERO_OFFSET    = 2.5f;
static const float CURRENT_SENSITIVITY    = 0.185f;
static const float CURRENT_STALL_A        = 2.0f;
static const float MAX_SAFE_CURRENT_A     = 4.0f;

// Ultrasonic calibration
static const float ULTRASONIC_CM_PER_US   = 0.0343f / 2.0f;
static const int   ULTRASONIC_MAX_RANGE_CM = 200;

// =============================================================================
// LED & PERSONALITY
// =============================================================================
#define PIN_LED              4
#define NUM_LEDS             16
#define PIN_ONBOARD_LED      2

#define COLOR_OFF       0x000000
#define COLOR_CURIOUS   0x00FFFF
#define COLOR_HAPPY     0x00FF00
#define COLOR_CONFUSED  0xFFFF00
#define COLOR_SAD       0x0000FF
#define COLOR_BUSY      0xFFFFFF
#define COLOR_SLEEPING  0xFF00FF
#define COLOR_WARNING   0xFF4500

// =============================================================================
// SAFETY & TIMING
// =============================================================================
static const unsigned long WATCHDOG_TIMEOUT_MS = 5000;
static const unsigned long LED_BLINK_INTERVAL_MS = 500;
static const unsigned long MOOD_TIMEOUT_MS = 300000;  // 5 min to sleeping

// =============================================================================
// TEACHING MODE
// =============================================================================
static const unsigned long TEACHING_RECORD_INTERVAL_MS = 50;  // Record every 50ms
static const int MAX_TRAJECTORY_POINTS = 1000;  // ~50 seconds at 50ms

// =============================================================================
// DEBUG
// =============================================================================
#define DEBUG_SERIAL_BAUD 115200
#define DEBUG_ENABLED true

#define DEBUG_PRINT(x)   if(DEBUG_ENABLED) { Serial.print(x); }
#define DEBUG_PRINTLN(x) if(DEBUG_ENABLED) { Serial.println(x); }
#define DEBUG_PRINTF(...) if(DEBUG_ENABLED) { Serial.printf(__VA_ARGS__); }

#endif
