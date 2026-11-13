/*
  TEST 07 - WebSocket Connection
  What this tests: ESP32 connects to your PC's backend server
  
  BEFORE RUNNING:
    1. Start the backend server on your PC:
       cd ai_backend
       python server.py
    
    2. Find your PC's IP address:
       Windows: open CMD, type: ipconfig
       Look for "IPv4 Address" under your WiFi adapter
    
    3. Change SERVER_HOST below to that IP address.
  
  Wire: NOTHING extra. Just ESP32 on USB.
  
  Expected Serial output:
    [WiFi] Connected! IP: 192.168.x.x
    [WS] Connected to ws://192.168.x.x:8000/ws/esp32
    [WS] TX State: {"type":"state_update",...}
    ...
  
  Check the dashboard (http://localhost:8000) — it should show ESP32: Connected
*/

#include <WiFi.h>
#include <ArduinoWebsockets.h>

using namespace websockets;

// CHANGE THESE:
const char* WIFI_SSID = "Dhilbar";
const char* WIFI_PASSWORD = "freefree";
const char* SERVER_HOST = "10.79.244.223";  // <- YOUR PC'S IP ADDRESS
const int SERVER_PORT = 8000;

WebsocketsClient wsClient;
unsigned long lastStateSend = 0;

void onMessage(WebsocketsMessage msg) {
  Serial.printf("[WS] RX: %s\n", msg.data().c_str());
}

void onEvent(WebsocketsEvent event, String data) {
  if (event == WebsocketsEvent::ConnectionOpened) {
    Serial.println("[WS] Event: Connection Opened");
  } else if (event == WebsocketsEvent::ConnectionClosed) {
    Serial.println("[WS] Event: Connection Closed");
  }
}

void setup() {
  Serial.begin(115200);
  while (!Serial) { ; }
  delay(500);

  Serial.println("========================================");
  Serial.println("  TEST 07: WebSocket Connection");
  Serial.println("========================================");
  Serial.println("");

  // Check credentials
  if (String(WIFI_SSID) == "YOUR_WIFI_SSID" || String(SERVER_HOST) == "192.168.1.100") {
    Serial.println("[ERROR] You must edit this file and set:");
    Serial.println("  - WIFI_SSID");
    Serial.println("  - WIFI_PASSWORD");
    Serial.println("  - SERVER_HOST (your PC's IP from ipconfig)");
    while (true) { delay(1000); }
  }

  // Connect WiFi
  Serial.printf("[WiFi] Connecting to %s...\n", WIFI_SSID);
  WiFi.begin(WIFI_SSID, WIFI_PASSWORD);
  int attempts = 0;
  while (WiFi.status() != WL_CONNECTED && attempts < 30) {
    delay(500);
    Serial.print(".");
    attempts++;
  }
  Serial.println();

  if (WiFi.status() != WL_CONNECTED) {
    Serial.println("[FAIL] WiFi connection failed.");
    while (true) { delay(1000); }
  }
  Serial.printf("[WiFi] Connected! IP: %s\n", WiFi.localIP().toString().c_str());

  // Connect WebSocket
  String url = "ws://" + String(SERVER_HOST) + ":" + String(SERVER_PORT) + "/ws/esp32";
  Serial.printf("[WS] Connecting to %s\n", url.c_str());

  wsClient.onMessage(onMessage);
  wsClient.onEvent(onEvent);

  bool connected = wsClient.connect(url.c_str());
  if (connected) {
    Serial.println("[PASS] WebSocket connected!");
    Serial.println("[INFO] Check dashboard at http://localhost:8000");
    Serial.println("[INFO] ESP32 status should show 'Connected'");
  } else {
    Serial.println("[FAIL] WebSocket connection failed.");
    Serial.println("Check:");
    Serial.println("  - Server is running (python server.py)");
    Serial.println("  - SERVER_HOST matches your PC's IP");
    Serial.println("  - PC and ESP32 are on the same WiFi network");
    Serial.println("  - Windows firewall is not blocking port 8000");
  }
  Serial.println("");
}

void loop() {
  wsClient.poll();

  // Send a fake state update every 500ms
  if (wsClient.available() && millis() - lastStateSend > 500) {
    String state = "{\"type\":\"state_update\",\"timestamp\":" + String(millis()) +
                   ",\"joint_angles\":[90,90,90,0],\"gripper\":0.5," +
                   "\"sensors\":{\"distance\":25.0,\"current\":0.5}," +
                   "\"status\":\"idle\",\"mood\":\"curious\"}";
    wsClient.send(state);
    Serial.println("[WS] TX State sent");
    lastStateSend = millis();
  }

  // Reconnect if lost
  if (!wsClient.available() && WiFi.status() == WL_CONNECTED) {
    Serial.println("[WS] Reconnecting...");
    String url = "ws://" + String(SERVER_HOST) + ":" + String(SERVER_PORT) + "/ws/esp32";
    wsClient.connect(url.c_str());
    delay(1000);
  }

  delay(10);
}
