#include "teaching_mode.h"
#include "config.h"
#include "servo_controller.h"
#include "stepper_controller.h"
#include <ArduinoJson.h>

bool teachingActive = false;
unsigned long lastRecordMs = 0;
StaticJsonDocument<8192> trajectoryDoc;
JsonArray trajectoryArray;
int recordCount = 0;

void initTeachingMode() {
  teachingActive = false;
  recordCount = 0;
  trajectoryArray = trajectoryDoc.createNestedArray("trajectory");
  Serial.println("[Teaching] Mode ready. Max points: ");
  Serial.printf("[Teaching]   %d frames (~%d seconds at %dms intervals)\n",
                MAX_TRAJECTORY_POINTS,
                (MAX_TRAJECTORY_POINTS * TEACHING_RECORD_INTERVAL_MS) / 1000,
                TEACHING_RECORD_INTERVAL_MS);
}

void startTeaching() {
  teachingActive = true;
  recordCount = 0;
  trajectoryDoc.clear();
  trajectoryArray = trajectoryDoc.createNestedArray("trajectory");
  
  stopAllServos();
  
  Serial.println("[Teaching] *** STARTED *** Move the arm freely. Recording every 50ms.");
}

void stopTeaching() {
  teachingActive = false;
  Serial.printf("[Teaching] *** STOPPED *** Recorded %d frames.\n", recordCount);
}

bool isTeaching() { return teachingActive; }

void recordFrame() {
  if (!teachingActive) return;
  if (recordCount >= MAX_TRAJECTORY_POINTS) {
    Serial.println("[Teaching] Max trajectory points reached!");
    return;
  }
  
  unsigned long now = millis();
  if (now - lastRecordMs < TEACHING_RECORD_INTERVAL_MS) return;
  lastRecordMs = now;
  
  JsonObject frame = trajectoryArray.createNestedObject();
  frame["t"] = now / 1000.0f;
  
  // Record stepper base position
  float baseAngle = getStepperCurrentAngle();
  frame["base"] = (int)round(baseAngle);
  
  // Record servo positions
  float shoulder = getCurrentAngle(0);
  float elbow = getCurrentAngle(1);
  float wrist = getCurrentAngle(2);
  float gripper = getCurrentAngle(3);
  
  frame["shoulder"] = (int)round(shoulder);
  frame["elbow"] = (int)round(elbow);
  frame["wrist"] = (int)round(wrist);
  frame["gripper"] = gripper;
  
  recordCount++;
  
  if (recordCount % 20 == 0) {
    Serial.printf("[Teaching] Frame %d: base=%d sh=%d el=%d wr=%d gr=%.2f\n",
                  recordCount, (int)round(baseAngle), (int)round(shoulder),
                  (int)round(elbow), (int)round(wrist), gripper);
  }
}

char* getRecordedTrajectory() {
  static char buffer[8192];
  trajectoryDoc["name"] = "recorded_skill";
  trajectoryDoc["frame_count"] = recordCount;
  serializeJson(trajectoryDoc, buffer, sizeof(buffer));
  Serial.printf("[Teaching] Trajectory serialized: %d bytes, %d frames\n", strlen(buffer), recordCount);
  return buffer;
}

void clearRecording() {
  trajectoryDoc.clear();
  trajectoryArray = trajectoryDoc.createNestedArray("trajectory");
  recordCount = 0;
  Serial.println("[Teaching] Recording cleared.");
}
