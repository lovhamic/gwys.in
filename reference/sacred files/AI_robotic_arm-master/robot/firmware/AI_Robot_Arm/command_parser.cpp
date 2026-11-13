#include "command_parser.h"
#include "config.h"
#include "servo_controller.h"
#include "stepper_controller.h"
#include "safety_monitor.h"
#include "rgb_led.h"
#include "comms_websocket.h"
#include "teaching_mode.h"
#include "local_memory.h"
#include <ArduinoJson.h>

extern char armStatus[16];
extern char armMood[16];
extern char activeCommand[32];
extern bool thinkingLedActive;

void parseCommand(const char* jsonCmd) {
  Serial.printf("[CMD] Raw JSON (%d bytes): %s\n", strlen(jsonCmd), jsonCmd);
  
  StaticJsonDocument<512> doc;
  DeserializationError error = deserializeJson(doc, jsonCmd);
  
  if (error) {
    Serial.printf("[CMD] JSON PARSE ERROR: %s\n", error.c_str());
    return;
  }
  
  const char* msgType = doc["type"] | "unknown";
  const char* cmdId = doc["command_id"] | "unknown";
  
  Serial.printf("[CMD] Type='%s' ID='%s'\n", msgType, cmdId);
  
  if (strcmp(msgType, "motion_command") == 0) {
    if (isEmergencyStopped()) {
      Serial.println("[CMD] Motion REJECTED — emergency stop active!");
      sendCommandAck(cmdId, "rejected_emergency");
      return;
    }
    
    // Parse joint angles: [base, shoulder, elbow, wrist]
    float baseAngle = BASE_DEFAULT_ANGLE;
    float shoulderAngle = JOINT_DEFAULT[0];
    float elbowAngle = JOINT_DEFAULT[1];
    float wristSpeed = CONTINUOUS_STOP;
    float gripper = GRIPPER_DEFAULT;
    
    if (doc.containsKey("joint_angles")) {
      JsonArray ja = doc["joint_angles"];
      if (ja.size() > 0) baseAngle = ja[0].as<float>();
      if (ja.size() > 1) shoulderAngle = ja[1].as<float>();
      if (ja.size() > 2) elbowAngle = ja[2].as<float>();
      if (ja.size() > 3) wristSpeed = ja[3].as<float>();
    }
    
    gripper = doc["gripper"] | GRIPPER_DEFAULT;
    unsigned long durationMs = doc["duration_ms"] | 1000;
    
    Serial.printf("[CMD] Motion: base=%.1f sh=%.1f el=%.1f wr=%.1f gr=%.2f dur=%lums\n",
                  baseAngle, shoulderAngle, elbowAngle, wristSpeed, gripper, durationMs);
    
    // Set stepper base target
    setStepperTargetAngle(baseAngle);
    
    // Set servo targets: [shoulder, elbow]
    float servoAngles[2] = {shoulderAngle, elbowAngle};
    setServoTargets(servoAngles, wristSpeed, gripper);
    
    // Set continuous servo speeds (wrist + gripper)
    setServoSpeeds(wristSpeed, gripper, durationMs);
    
    strcpy(armStatus, "executing");
    strcpy(armMood, "busy");
    strncpy(activeCommand, doc["action"] | "move", 31);
    activeCommand[31] = '\0';
    
    setLEDThinking(true);
    thinkingLedActive = true;
    
    sendCommandAck(cmdId, "accepted");
    
  } else if (strcmp(msgType, "teaching_mode") == 0) {
    bool enabled = doc["enabled"] | false;
    Serial.printf("[CMD] Teaching mode: %s\n", enabled ? "START" : "STOP");
    if (enabled) {
      startTeaching();
      disableStepper();
      strcpy(armStatus, "teaching");
      strcpy(armMood, "confused");
      setLEDMood("confused");
      sendCommandAck(cmdId, "teaching_started");
    } else {
      stopTeaching();
      enableStepper();
      strcpy(armStatus, "idle");
      strcpy(armMood, "curious");
      setLEDMood("curious");
      sendCommandAck(cmdId, "teaching_stopped");
    }
    
  } else if (strcmp(msgType, "save_skill") == 0) {
    const char* skillName = doc["name"] | "unnamed";
    Serial.printf("[CMD] Save skill: '%s'\n", skillName);
    char* trajectory = getRecordedTrajectory();
    if (saveSkill(skillName, trajectory)) {
      clearRecording();
      sendCommandAck(cmdId, "skill_saved");
      Serial.printf("[CMD] Skill '%s' saved OK\n", skillName);
    } else {
      sendCommandAck(cmdId, "skill_save_failed");
      Serial.printf("[CMD] Skill '%s' save FAILED\n", skillName);
    }
    
  } else if (strcmp(msgType, "clear_emergency") == 0) {
    Serial.println("[CMD] Clearing emergency stop...");
    clearEmergencyStop();
    strcpy(armStatus, "idle");
    strcpy(armMood, "curious");
    strcpy(activeCommand, "none");
    setLEDMood("curious");
    sendCommandAck(cmdId, "cleared");
    
  } else if (strcmp(msgType, "learned_skill") == 0) {
    const char* skillName = doc["skill_name"] | "unknown";
    Serial.printf("[CMD] Execute skill: '%s'\n", skillName);
    char skillBuffer[8192];
    if (loadSkill(skillName, skillBuffer, sizeof(skillBuffer))) {
      StaticJsonDocument<8192> skillDoc;
      DeserializationError err = deserializeJson(skillDoc, skillBuffer);
      if (!err) {
        JsonArray trajectory = skillDoc["trajectory"];
        int frameCount = 0;
        for (JsonObject frame : trajectory) {
          float base = frame["base"] | BASE_DEFAULT_ANGLE;
          float shoulder = frame["shoulder"] | JOINT_DEFAULT[0];
          float elbow = frame["elbow"] | JOINT_DEFAULT[1];
          float wrist = frame["wrist"] | CONTINUOUS_STOP;
          float g = frame["gripper"] | 0.5f;
          
          setStepperTargetAngle(base);
          float servoAngles[2] = {shoulder, elbow};
          setServoTargets(servoAngles, wrist, g);
          setServoSpeeds(wrist, g, 200);
          frameCount++;
        }
        Serial.printf("[CMD] Skill '%s': %d frames loaded\n", skillName, frameCount);
        strcpy(armStatus, "executing");
        strcpy(armMood, "busy");
        strncpy(activeCommand, skillName, 31);
        activeCommand[31] = '\0';
        sendCommandAck(cmdId, "skill_executing");
      } else {
        Serial.printf("[CMD] Skill '%s': JSON parse error\n", skillName);
        sendCommandAck(cmdId, "skill_parse_error");
      }
    } else {
      Serial.printf("[CMD] Skill '%s': NOT FOUND on SPIFFS\n", skillName);
      sendCommandAck(cmdId, "skill_not_found");
    }
    
  } else if (strcmp(msgType, "emergency_stop") == 0) {
    Serial.println("[CMD] EMERGENCY STOP command received!");
    triggerEmergencyStop();
    stopStepper();
    sendCommandAck(cmdId, "stopped");
    
  } else if (strcmp(msgType, "set_mood") == 0) {
    const char* mood = doc["mood"] | "curious";
    Serial.printf("[CMD] Set mood: '%s'\n", mood);
    strncpy(armMood, mood, 15);
    armMood[15] = '\0';
    setLEDMood(mood);
    sendCommandAck(cmdId, "mood_set");
    
  } else {
    Serial.printf("[CMD] Unknown command type: '%s'\n", msgType);
  }
}

void sendCommandAck(const char* cmdId, const char* status) {
  StaticJsonDocument<256> doc;
  doc["type"] = "command_ack";
  doc["command_id"] = cmdId;
  doc["status"] = status;
  doc["timestamp"] = millis();
  
  char jsonBuffer[256];
  serializeJson(doc, jsonBuffer);
  Serial.printf("[CMD] >> ACK: %s\n", jsonBuffer);
  sendState(jsonBuffer);
}
