#include "safety_monitor.h"
#include "config.h"
#include "servo_controller.h"

bool emergencyStop = false;
unsigned long emergencyTriggeredMs = 0;

void initSafety() {
  emergencyStop = false;
  Serial.printf("[Safety] Monitor initialized. Stall: %.1fA, Max: %.1fA\n", CURRENT_STALL_A, MAX_SAFE_CURRENT_A);
}

void checkSafety(float currentA) {
  if (emergencyStop) return;
  
  // Stall detection
  if (currentA > CURRENT_STALL_A) {
    Serial.printf("[SAFETY] STALL DETECTED: %.2fA > %.2fA\n", currentA, CURRENT_STALL_A);
    triggerEmergencyStop();
    return;
  }
  
  // Absolute overcurrent
  if (currentA > MAX_SAFE_CURRENT_A) {
    Serial.printf("[SAFETY] OVERCURRENT: %.2fA > %.2fA\n", currentA, MAX_SAFE_CURRENT_A);
    triggerEmergencyStop();
  }
}

bool isEmergencyStopped() { return emergencyStop; }

void triggerEmergencyStop() {
  emergencyStop = true;
  emergencyTriggeredMs = millis();
  stopAllServos();
  Serial.println("[SAFETY] *** EMERGENCY STOP *** All servos stopped!");
}

void clearEmergencyStop() {
  emergencyStop = false;
  Serial.println("[SAFETY] Emergency stop CLEARED.");
}

const char* getSafetyStatus() {
  return emergencyStop ? "error" : "ok";
}
