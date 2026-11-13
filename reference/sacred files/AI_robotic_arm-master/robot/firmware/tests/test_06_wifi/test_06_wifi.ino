/*
  TEST 06 - WiFi Connection
  What this tests: ESP32 connects to your home WiFi
  
  Wire: NOTHING extra. Just ESP32 on USB.
  
  CHANGE THESE before uploading:
*/
#include <WiFi.h>
const char* WIFI_SSID = "Dhilbar";      // <- CHANGE THIS
const char* WIFI_PASSWORD = "freefree";  // <- CHANGE THIS

void setup() {
  Serial.begin(115200);
  while (!Serial) { ; }
  delay(500);

  Serial.println("========================================");
  Serial.println("  TEST 06: WiFi Connection");
  Serial.println("========================================");
  Serial.println("");

  if (String(WIFI_SSID) == "YOUR_WIFI_SSID") {
    Serial.println("[ERROR] You forgot to set WIFI_SSID and WIFI_PASSWORD!");
    Serial.println("[ERROR] Edit this file, change the credentials, re-upload.");
    while (true) { delay(1000); }  // Halt
  }

  Serial.printf("[WiFi] Connecting to: %s\n", WIFI_SSID);
  WiFi.begin(WIFI_SSID, WIFI_PASSWORD);

  int attempts = 0;
  while (WiFi.status() != WL_CONNECTED && attempts < 30) {
    delay(500);
    Serial.print(".");
    attempts++;
  }
  Serial.println();

  if (WiFi.status() == WL_CONNECTED) {
    Serial.println("[PASS] WiFi connected!");
    Serial.printf("[WiFi] IP Address: %s\n", WiFi.localIP().toString().c_str());
    Serial.printf("[WiFi] Signal Strength (RSSI): %d dBm\n", WiFi.RSSI());
    Serial.println("");
    Serial.println("Note this IP address. The ESP32 will use it.");
  } else {
    Serial.println("[FAIL] Could not connect to WiFi.");
    Serial.println("Check:");
    Serial.println("  - SSID and password are correct");
    Serial.println("  - WiFi is 2.4GHz (ESP32 does not support 5GHz)");
    Serial.println("  - Router is not blocking the device");
  }
}

void loop() {
  // Print a heartbeat every 5 seconds
  if (WiFi.status() == WL_CONNECTED) {
    Serial.printf("[WiFi] Still connected. IP: %s | RSSI: %d dBm\n",
                  WiFi.localIP().toString().c_str(), WiFi.RSSI());
  } else {
    Serial.println("[WiFi] DISCONNECTED! Attempting reconnect...");
    WiFi.reconnect();
  }
  delay(5000);
}
