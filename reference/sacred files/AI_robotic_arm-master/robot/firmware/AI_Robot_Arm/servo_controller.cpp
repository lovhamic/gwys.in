#include "servo_controller.h"

// Servo indices: 0=shoulder, 1=elbow, 2=wrist, 3=gripper
// (Base is stepper motor, not a servo)

float currentValues[NUM_SERVOS];
float targetValues[NUM_SERVOS];
bool servoMoving[NUM_SERVOS];

// For continuous servos: track estimated position via dead reckoning
float estimatedPositions[NUM_SERVOS];
unsigned long lastUpdateMs = 0;

// For continuous servos: track how long to spin
unsigned long continuousEndTime[NUM_SERVOS];
bool continuousActive[NUM_SERVOS];

static float mapf(float x, float in_min, float in_max, float out_min, float out_max);

void initServos() {
  Serial.println("[Servo] Initializing 4 servos...");
  const char* names[] = {"shoulder", "elbow", "wrist", "gripper"};
  
  for (int i = 0; i < NUM_SERVOS; i++) {
    Serial.printf("[Servo]   [%d] %s — pin=%d, type=%s\n", 
                  i, names[i], SERVO_PINS[i],
                  SERVO_TYPES[i] == SERVO_TYPE_STANDARD ? "STANDARD" : "CONTINUOUS");
    
    ledcAttach(SERVO_PINS[i], SERVO_PWM_FREQ, SERVO_PWM_RESOLUTION);
    
    if (SERVO_TYPES[i] == SERVO_TYPE_CONTINUOUS) {
      currentValues[i] = CONTINUOUS_STOP;
      targetValues[i] = CONTINUOUS_STOP;
      estimatedPositions[i] = 0;
      continuousActive[i] = false;
    } else {
      currentValues[i] = JOINT_DEFAULT[i];
      targetValues[i] = JOINT_DEFAULT[i];
      estimatedPositions[i] = JOINT_DEFAULT[i];
    }
    servoMoving[i] = false;
    continuousEndTime[i] = 0;
    
    writeServo(i, currentValues[i]);
    Serial.printf("[Servo]   [%d] Initialized to %.1f\n", i, currentValues[i]);
  }
  lastUpdateMs = millis();
  Serial.println("[Servo] All 4 servos initialized OK.");
}

void writeServo(int servoIndex, float value) {
  if (servoIndex < 0 || servoIndex >= NUM_SERVOS) {
    Serial.printf("[Servo] ERROR: writeServo(%d, %.1f) — index out of range!\n", servoIndex, value);
    return;
  }
  
  float pulseUs;
  
  if (SERVO_TYPES[servoIndex] == SERVO_TYPE_CONTINUOUS) {
    value = constrain(value, CONTINUOUS_MIN_SPEED, CONTINUOUS_MAX_SPEED);
    pulseUs = mapf(value, 0, 180, 544.0f, 2400.0f);
  } else {
    value = constrain(value, 0, 180);
    pulseUs = mapf(value, 0, 180, 544.0f, 2400.0f);
  }
  
  uint32_t duty = (uint32_t)((pulseUs / 20000.0f) * 65535.0f);
  ledcWrite(SERVO_PINS[servoIndex], duty);
}

void writeAllServos() {
  Serial.println("[Servo] writeAllServos:");
  for (int i = 0; i < NUM_SERVOS; i++) {
    Serial.printf("[Servo]   [%d] = %.1f\n", i, currentValues[i]);
    writeServo(i, currentValues[i]);
  }
}

void setServoTargets(float angles[2], float wristSpeed, float gripper) {
  Serial.printf("[Servo] setTargets: shoulder=%.1f elbow=%.1f wrist=%.1f gripper=%.2f\n",
                angles[0], angles[1], wristSpeed, gripper);
  // angles[0] = shoulder, angles[1] = elbow
  for (int i = 0; i < 2; i++) {
    if (SERVO_TYPES[i] == SERVO_TYPE_STANDARD) {
      targetValues[i] = constrain(angles[i], JOINT_MIN[i], JOINT_MAX[i]);
      servoMoving[i] = true;
    }
  }
  // Wrist (continuous): wristSpeed = rotation speed
  targetValues[2] = constrain(wristSpeed, CONTINUOUS_MIN_SPEED, CONTINUOUS_MAX_SPEED);
  servoMoving[2] = true;
  // Gripper (continuous): gripper = speed value
  targetValues[3] = constrain(gripper, GRIPPER_MIN, GRIPPER_MAX);
  servoMoving[3] = true;
}

void setServoSpeeds(float wristSpeed, float gripperSpeed, unsigned long durationMs) {
  Serial.printf("[Servo] setSpeeds: wrist=%.1f gripper=%.1f duration=%lums\n", wristSpeed, gripperSpeed, durationMs);
  unsigned long now = millis();
  unsigned long endTime = now + durationMs;
  
  // Wrist (continuous)
  targetValues[2] = constrain(wristSpeed, CONTINUOUS_MIN_SPEED, CONTINUOUS_MAX_SPEED);
  continuousEndTime[2] = endTime;
  continuousActive[2] = true;
  servoMoving[2] = true;
  
  // Gripper (continuous)
  targetValues[3] = constrain(gripperSpeed, GRIPPER_MIN, GRIPPER_MAX);
  continuousEndTime[3] = endTime;
  continuousActive[3] = true;
  servoMoving[3] = true;
}

void updateServos() {
  unsigned long now = millis();
  float dt = (now - lastUpdateMs) / 1000.0f;
  lastUpdateMs = now;
  
  for (int i = 0; i < NUM_SERVOS; i++) {
    if (SERVO_TYPES[i] == SERVO_TYPE_STANDARD) {
      // Standard servo: smooth interpolation
      float diff = targetValues[i] - currentValues[i];
      if (abs(diff) > 0.5f) {
        float step = 180.0f / MOTION_SMOOTHING_STEPS;
        if (diff > 0) {
          currentValues[i] += min(diff, step);
        } else {
          currentValues[i] += max(diff, -step);
        }
        writeServo(i, currentValues[i]);
        estimatedPositions[i] = currentValues[i];
      } else {
        servoMoving[i] = false;
      }
    } else {
      // Continuous servo: check duration
      if (continuousActive[i]) {
        if (now >= continuousEndTime[i]) {
          Serial.printf("[Servo] [%d] Continuous servo timer expired — stopping\n", i);
          currentValues[i] = CONTINUOUS_STOP;
          continuousActive[i] = false;
          servoMoving[i] = false;
        } else {
          currentValues[i] = targetValues[i];
          float speed = (currentValues[i] - CONTINUOUS_STOP);
          float scale = 30.0f;
          estimatedPositions[i] += (speed / 90.0f) * scale * dt;
        }
        writeServo(i, currentValues[i]);
      } else {
        servoMoving[i] = false;
      }
    }
  }
}

void stopAllServos() {
  Serial.println("[Servo] STOP ALL SERVOS");
  for (int i = 0; i < NUM_SERVOS; i++) {
    if (SERVO_TYPES[i] == SERVO_TYPE_CONTINUOUS) {
      currentValues[i] = CONTINUOUS_STOP;
      targetValues[i] = CONTINUOUS_STOP;
      continuousActive[i] = false;
    }
    servoMoving[i] = false;
    writeServo(i, currentValues[i]);
  }
}

float getCurrentAngle(int servoIndex) {
  if (servoIndex < 0 || servoIndex >= NUM_SERVOS) return 0;
  if (SERVO_TYPES[servoIndex] == SERVO_TYPE_CONTINUOUS) {
    return estimatedPositions[servoIndex];
  }
  return currentValues[servoIndex];
}

float getTargetAngle(int servoIndex) {
  if (servoIndex < 0 || servoIndex >= NUM_SERVOS) return 0;
  return targetValues[servoIndex];
}

bool isServoMoving(int servoIndex) {
  if (servoIndex < 0 || servoIndex >= NUM_SERVOS) return false;
  return servoMoving[servoIndex];
}

static float mapf(float x, float in_min, float in_max, float out_min, float out_max) {
  return (x - in_min) * (out_max - out_min) / (in_max - in_min) + out_min;
}
