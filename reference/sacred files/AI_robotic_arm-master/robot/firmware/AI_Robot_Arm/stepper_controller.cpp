#include "stepper_controller.h"

// Position tracking via step counting
long stepPosition = 0;
long targetStepPosition = 0;
bool stepperMoving = false;
bool stepperEnabled = false;

// Timing for step pulse generation
unsigned long lastStepUs = 0;
bool stepState = false;

// Convert degrees to steps (NEMA 17 = 200 steps/rev, 1/8 microstepping)
// Steps per degree = (200 * 8) / 360 = 4.44 steps/degree
float stepsPerDegree = (float)(STEPPER_STEPS_PER_REV * STEPPER_MICROSTEPS) / 360.0f;

void initStepper() {
  Serial.println("[Stepper] Initializing NEMA 17 + A4988...");
  Serial.printf("[Stepper]   STEP=GPIO%d DIR=GPIO%d EN=GPIO%d\n", PIN_STEPPER_STEP, PIN_STEPPER_DIR, PIN_STEPPER_EN);
  Serial.printf("[Stepper]   Steps/rev=%d, Microsteps=%d, Steps/deg=%.2f\n", 
                STEPPER_STEPS_PER_REV, STEPPER_MICROSTEPS, stepsPerDegree);
  Serial.printf("[Stepper]   Step delay=%dus, Max speed=%.1f deg/s\n", 
                STEPPER_STEP_DELAY_US, 1000000.0f / (STEPPER_STEP_DELAY_US * 2 * stepsPerDegree));
  
  pinMode(PIN_STEPPER_STEP, OUTPUT);
  pinMode(PIN_STEPPER_DIR, OUTPUT);
  pinMode(PIN_STEPPER_EN, OUTPUT);

  digitalWrite(PIN_STEPPER_STEP, LOW);
  digitalWrite(PIN_STEPPER_DIR, LOW);
  digitalWrite(PIN_STEPPER_EN, HIGH);  // HIGH = disabled (active low)

  stepPosition = 0;
  targetStepPosition = 0;
  stepperMoving = false;
  stepperEnabled = false;

  Serial.println("[Stepper] Init OK. Motor DISABLED (will enable on first move).");
}

void enableStepper() {
  digitalWrite(PIN_STEPPER_EN, LOW);  // Active low
  stepperEnabled = true;
  Serial.println("[Stepper] ENABLED");
}

void disableStepper() {
  digitalWrite(PIN_STEPPER_EN, HIGH);
  stepperEnabled = false;
  Serial.println("[Stepper] DISABLED");
}

void setStepperTargetAngle(float angleDeg) {
  angleDeg = constrain(angleDeg, STEPPER_MIN_ANGLE, STEPPER_MAX_ANGLE);
  long newTarget = (long)(angleDeg * stepsPerDegree);
  
  if (newTarget != targetStepPosition) {
    Serial.printf("[Stepper] Target: %.1f° (was %.1f°, steps=%ld -> %ld)\n", 
                  angleDeg, getStepperCurrentAngle(), stepPosition, newTarget);
  }
  
  targetStepPosition = newTarget;
  stepperMoving = (stepPosition != targetStepPosition);

  if (stepperMoving) {
    enableStepper();
    bool dir = (targetStepPosition > stepPosition);
    digitalWrite(PIN_STEPPER_DIR, dir ? HIGH : LOW);
    Serial.printf("[Stepper] Moving %s — %ld steps to go\n", dir ? "CW" : "CCW", 
                  abs(targetStepPosition - stepPosition));
  }
}

float getStepperTargetAngle() {
  return (float)targetStepPosition / stepsPerDegree;
}

float getStepperCurrentAngle() {
  return (float)stepPosition / stepsPerDegree;
}

bool isStepperMoving() {
  return stepperMoving;
}

void updateStepper() {
  if (!stepperMoving || !stepperEnabled) return;

  unsigned long nowUs = micros();

  if (nowUs - lastStepUs < STEPPER_STEP_DELAY_US) return;
  lastStepUs = nowUs;

  if (stepPosition == targetStepPosition) {
    stepperMoving = false;
    Serial.printf("[Stepper] Reached target: %.1f° (steps=%ld)\n", getStepperCurrentAngle(), stepPosition);
    return;
  }

  // Generate step pulse
  if (!stepState) {
    digitalWrite(PIN_STEPPER_STEP, HIGH);
    stepState = true;

    if (targetStepPosition > stepPosition) {
      stepPosition++;
    } else {
      stepPosition--;
    }
  } else {
    digitalWrite(PIN_STEPPER_STEP, LOW);
    stepState = false;
  }
}

void stopStepper() {
  long prev = stepPosition;
  digitalWrite(PIN_STEPPER_STEP, LOW);
  targetStepPosition = stepPosition;
  stepperMoving = false;
  stepState = false;
  Serial.printf("[Stepper] STOPPED at %.1f°\n", getStepperCurrentAngle());
}

void stepperStep(bool direction, unsigned int stepDelayUs) {
  enableStepper();
  digitalWrite(PIN_STEPPER_DIR, direction ? HIGH : LOW);

  digitalWrite(PIN_STEPPER_STEP, HIGH);
  delayMicroseconds(stepDelayUs);
  digitalWrite(PIN_STEPPER_STEP, LOW);
  delayMicroseconds(stepDelayUs);

  if (direction) {
    stepPosition++;
  } else {
    stepPosition--;
  }
}

long getStepperPosition() {
  return stepPosition;
}

void resetStepperPosition() {
  Serial.printf("[Stepper] Position reset: %ld -> 0\n", stepPosition);
  stepPosition = 0;
  targetStepPosition = 0;
}
