#include "motion_planner.h"
#include "servo_controller.h"
#include "stepper_controller.h"

struct TrajectorySegment {
  float startBase, endBase;
  float startShoulder, endShoulder;
  float startElbow, endElbow;
  float startWrist, endWrist;
  float startGripper, endGripper;
  unsigned long startTimeMs;
  unsigned long durationMs;
  bool active;
};

TrajectorySegment currentSegment;
bool motionActive = false;

void initMotionPlanner() {
  motionActive = false;
  currentSegment.active = false;
  Serial.println("[Motion] Planner initialized (stepper base + servo joints).");
}

void planTrajectory(float baseAngle, float shoulderAngle, float elbowAngle,
                    float wristSpeed, float gripper, unsigned long durationMs) {
  Serial.printf("[Motion] Plan: base=%.1f shoulder=%.1f elbow=%.1f wrist=%.1f gripper=%.2f dur=%lums\n",
                baseAngle, shoulderAngle, elbowAngle, wristSpeed, gripper, durationMs);
  
  currentSegment.startBase = getStepperCurrentAngle();
  currentSegment.endBase = baseAngle;
  currentSegment.startShoulder = getCurrentAngle(0);
  currentSegment.endShoulder = shoulderAngle;
  currentSegment.startElbow = getCurrentAngle(1);
  currentSegment.endElbow = elbowAngle;
  currentSegment.startWrist = getCurrentAngle(2);
  currentSegment.endWrist = wristSpeed;
  currentSegment.startGripper = getCurrentAngle(3);
  currentSegment.endGripper = gripper;
  currentSegment.startTimeMs = millis();
  currentSegment.durationMs = durationMs;
  currentSegment.active = true;
  motionActive = true;
  
  Serial.printf("[Motion] From: base=%.1f sh=%.1f el=%.1f wr=%.1f gr=%.2f\n",
                currentSegment.startBase, currentSegment.startShoulder,
                currentSegment.startElbow, currentSegment.startWrist, currentSegment.startGripper);
}

void planSkillFrame(float baseAngle, float shoulderAngle, float elbowAngle,
                    float wristSpeed, float gripper) {
  planTrajectory(baseAngle, shoulderAngle, elbowAngle, wristSpeed, gripper, 100);
}

void updateMotion() {
  if (!motionActive || !currentSegment.active) return;

  unsigned long now = millis();
  float elapsed = (float)(now - currentSegment.startTimeMs);
  float progress = constrain(elapsed / (float)currentSegment.durationMs, 0.0f, 1.0f);

  // Interpolate all joints
  float interpBase = currentSegment.startBase +
                     (currentSegment.endBase - currentSegment.startBase) * progress;
  float interpShoulder = currentSegment.startShoulder +
                         (currentSegment.endShoulder - currentSegment.startShoulder) * progress;
  float interpElbow = currentSegment.startElbow +
                      (currentSegment.endElbow - currentSegment.startElbow) * progress;
  float interpWrist = currentSegment.startWrist +
                      (currentSegment.endWrist - currentSegment.startWrist) * progress;
  float interpGripper = currentSegment.startGripper +
                        (currentSegment.endGripper - currentSegment.startGripper) * progress;

  // Set targets
  setStepperTargetAngle(interpBase);
  float servoAngles[2] = {interpShoulder, interpElbow};
  setServoTargets(servoAngles, interpWrist, interpGripper);

  if (progress >= 1.0f) {
    currentSegment.active = false;
    motionActive = false;
    setStepperTargetAngle(currentSegment.endBase);
    Serial.printf("[Motion] Trajectory COMPLETE at base=%.1f\n", currentSegment.endBase);
  }
}

bool isMotionComplete() {
  return !motionActive;
}

void cancelMotion() {
  motionActive = false;
  currentSegment.active = false;
  stopAllServos();
  stopStepper();
  Serial.println("[Motion] Motion CANCELLED.");
}
