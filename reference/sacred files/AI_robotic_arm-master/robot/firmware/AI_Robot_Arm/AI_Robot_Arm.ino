/*
  AI_Robot_Arm.ino
  Production firmware — Modular architecture
  
  Modules:
    servo_controller  — PWM for shoulder, elbow, wrist, gripper
    stepper_controller — A4988 + NEMA 17 base rotation
    motion_planner    — Trajectory interpolation + dead reckoning
    sensor_manager    — HC-SR04 + ACS712
    safety_monitor    — Stall detection, emergency stop
    rgb_led           — WS2812B mood expressions
    wifi_manager      — WiFi connection
    comms_websocket   — WebSocket to backend
    command_parser    — Parse JSON commands
    teaching_mode     — De-energize servos, record trajectories
    local_memory      — SPIFFS skill cache
  
  Required Libraries:
    - ArduinoWebsockets by Gil Maimon
    - ArduinoJson by Benoit Blanchon (v6.x)
    - Adafruit NeoPixel by Adafruit
*/

#include <Arduino.h>
#include <ArduinoJson.h>
#include "config.h"
#include "servo_controller.h"
#include "stepper_controller.h"
#include "motion_planner.h"
#include "sensor_manager.h"
#include "safety_monitor.h"
#include "rgb_led.h"
#include "wifi_manager.h"
#include "comms_websocket.h"
#include "command_parser.h"
#include "teaching_mode.h"
#include "local_memory.h"

// Global state
char armStatus[16] = "idle";
char armMood[16] = "curious";
char activeCommand[32] = "none";

// Timing
unsigned long lastSensorReadMs = 0;
unsigned long lastStateSendMs = 0;
unsigned long lastBlinkMs = 0;
unsigned long lastMoodCheckMs = 0;
bool onboardLedState = false;

// State buffer for JSON
char stateJson[512];

void buildStateJson() {
  StaticJsonDocument<512> doc;
  doc["type"] = "state_update";
  doc["timestamp"] = millis();
  
  // Joint angles: [base, shoulder, elbow, wrist]
  JsonArray ja = doc.createNestedArray("joint_angles");
  ja.add((int)round(getStepperCurrentAngle()));
  for (int i = 0; i < 2; i++) {
    ja.add((int)round(getCurrentAngle(i)));
  }
  ja.add((int)round(getCurrentAngle(2)));
  
  doc["gripper"] = round(getCurrentAngle(3) * 100) / 100.0f;
  
  JsonObject sensors = doc.createNestedObject("sensors");
  float dist = getDistanceCm();
  sensors["distance"] = (dist < 0) ? -1 : round(dist * 10) / 10.0f;
  sensors["current"] = round(getCurrentA() * 100) / 100.0f;
  
  doc["status"] = armStatus;
  doc["mood"] = armMood;
  doc["active_cmd"] = activeCommand;
  doc["emergency"] = isEmergencyStopped();
  
  // Base type = 2 (stepper), others: standard=0, continuous=1
  JsonArray st = doc.createNestedArray("joint_types");
  st.add(2);  // base = stepper
  for (int i = 0; i < NUM_SERVOS; i++) {
    st.add(SERVO_TYPES[i]);
  }
  
  serializeJson(doc, stateJson, sizeof(stateJson));
}

void onCommandReceived(const char* jsonCmd) {
  parseCommand(jsonCmd);
}

// Track thinking mode for LED
bool thinkingLedActive = false;

bool isThinkingMode() {
  return thinkingLedActive;
}

void runMoodFlow() {
  if (strcmp(armMood, "curious") == 0) {
    // Cyan flowing left to right
    flowColor(0x00FFFF, 0x003333);
  } else if (strcmp(armMood, "happy") == 0) {
    // Green flowing left to right
    flowColor(0x00FF00, 0x003300);
  } else if (strcmp(armMood, "confused") == 0) {
    // Yellow single dot bouncing
    flowSingle(0xFFFF00);
  } else if (strcmp(armMood, "sad") == 0) {
    // Blue slow breathe
    breatheColor(0x0000FF);
  } else if (strcmp(armMood, "busy") == 0) {
    // White fast chase
    flowSingle(0xFFFFFF);
  } else if (strcmp(armMood, "sleeping") == 0) {
    // Magenta very slow breathe
    breatheColor(0xFF00FF);
  } else {
    // Default: cyan flow
    flowColor(0x00FFFF, 0x003333);
  }
}

void setup() {
  Serial.begin(DEBUG_SERIAL_BAUD);
  while (!Serial) { ; }
  delay(500);
  
  pinMode(PIN_ONBOARD_LED, OUTPUT);
  
  Serial.println("\n========================================");
  Serial.println("  AI ROBOTIC ARM — Production Firmware");
  Serial.println("  Base: NEMA 17 + A4988 Stepper");
  Serial.println("========================================");
  
  Serial.printf("[SETUP] WIFI_SSID: %s\n", WIFI_SSID);
  Serial.printf("[SETUP] SERVER_HOST: %s:%d%s\n", SERVER_HOST, SERVER_PORT, SERVER_PATH);
  Serial.printf("[SETUP] Free heap before init: %u bytes\n", ESP.getFreeHeap());
  
  // LED TEST — runs before WiFi so you can see it immediately
  Serial.println("[SETUP] Step 1/10: LED HARDWARE TEST...");
  initLED();
  Serial.println("[LED] TEST: RED (all 6)...");
  setLEDColor(0xFF0000);
  delay(800);
  Serial.println("[LED] TEST: GREEN (all 6)...");
  setLEDColor(0x00FF00);
  delay(800);
  Serial.println("[LED] TEST: BLUE (all 6)...");
  setLEDColor(0x0000FF);
  delay(800);
  Serial.println("[LED] TEST: Flowing CYAN...");
  for (int step = 0; step < 18; step++) {
    flowColor(0x00FFFF, 0x003333);
    delay(100);
  }
  Serial.println("[LED] TEST: Breathe GREEN...");
  for (int step = 0; step < 30; step++) {
    breatheColor(0x00FF00);
    delay(50);
  }
  Serial.println("[LED] TEST DONE — if you saw colors flowing, all 6 LEDs work!");
  Serial.println("[SETUP] Step 2/10: Initializing Stepper...");
  initStepper();
  Serial.println("[SETUP] Step 3/10: Initializing Servos...");
  initServos();
  Serial.println("[SETUP] Step 4/10: Initializing Motion Planner...");
  initMotionPlanner();
  Serial.println("[SETUP] Step 5/10: Initializing Sensors...");
  initSensors();
  Serial.println("[SETUP] Step 6/10: Initializing Safety Monitor...");
  initSafety();
  Serial.println("[SETUP] Step 7/10: Initializing Teaching Mode...");
  initTeachingMode();
  Serial.println("[SETUP] Step 8/10: Initializing Local Memory (SPIFFS)...");
  initLocalMemory();
  Serial.println("[SETUP] Step 9/10: Connecting WiFi...");
  initWiFi();
  Serial.println("[SETUP] Step 10/10: Connecting WebSocket...");
  initWebSocket(onCommandReceived);
  
  // Move to default pose
  Serial.println("[SETUP] Moving to default pose...");
  setStepperTargetAngle(BASE_DEFAULT_ANGLE);
  float servoDefaults[2] = {JOINT_DEFAULT[0], JOINT_DEFAULT[1]};
  setServoTargets(servoDefaults, CONTINUOUS_STOP, GRIPPER_DEFAULT);
  
  Serial.printf("[SETUP] Free heap after init: %u bytes\n", ESP.getFreeHeap());
  Serial.println("[SETUP] Setup complete. Entering main loop...");
  Serial.println("========================================\n");
}

void loop() {
  unsigned long now = millis();
  
  // 1. WebSocket poll
  pollWebSocket();
  
  // 2. Watchdog
  if (isWebSocketConnected() && (now - getLastServerMessageMs() > WATCHDOG_TIMEOUT_MS)) {
    Serial.println("[LOOP] Watchdog timeout! No server message in 5s. Reconnecting WS...");
    checkWebSocketConnection();
  }
  
  // 3. Read sensors
  if (now - lastSensorReadMs >= SENSOR_READ_INTERVAL_MS) {
    readSensors();
    lastSensorReadMs = now;
  }
  
  // 4. Safety check
  checkSafety(getCurrentA());
  if (isEmergencyStopped()) {
    strcpy(armStatus, "error");
    strcpy(armMood, "sad");
    setLEDMood("sad");
  }
  
  // 5. Update motion
  if (!isEmergencyStopped()) {
    if (isTeaching()) {
      recordFrame();
    } else {
      updateStepper();
      updateMotion();
      updateServos();
    }

    // Auto-transition from busy to idle when motion done
    bool anyMoving = isStepperMoving();
    if (!anyMoving) {
      for (int i = 0; i < NUM_SERVOS; i++) {
        if (isServoMoving(i)) { anyMoving = true; break; }
      }
    }
    if (!anyMoving && strcmp(armStatus, "executing") == 0 && isMotionComplete()) {
      strcpy(armStatus, "idle");
      strcpy(armMood, "curious");
      strcpy(activeCommand, "none");
      setLEDThinking(false);
      thinkingLedActive = false;
      setLEDMood("curious");
      Serial.println("[LOOP] Motion finished. Status -> idle");
    }
  }
  
  // 6. Send state to server
  if (now - lastStateSendMs >= STATE_SEND_INTERVAL_MS) {
    buildStateJson();
    if (isWebSocketConnected()) {
      sendState(stateJson);
    }
    lastStateSendMs = now;
  }
  
  // 7. LED animation — ambient flow based on mood
  updateLEDAnimation();
  if (!isThinkingMode()) {
    runMoodFlow();
  }
  
  // 8. Onboard LED heartbeat
  if (now - lastBlinkMs >= LED_BLINK_INTERVAL_MS) {
    onboardLedState = !onboardLedState;
    digitalWrite(PIN_ONBOARD_LED, onboardLedState ? HIGH : LOW);
    lastBlinkMs = now;
  }
  
  // 9. WiFi + WebSocket reconnect
  checkWiFiConnection();
  checkWebSocketConnection();
  
  delay(10);
}
