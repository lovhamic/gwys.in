#include "wifi_manager.h"
#include "config.h"

void initWiFi() {
  Serial.printf("[WiFi] SSID: '%s'\n", WIFI_SSID);
  Serial.printf("[WiFi] Password: '%s'\n", WIFI_PASSWORD);
  Serial.printf("[WiFi] Starting connection to '%s'...\n", WIFI_SSID);
  
  WiFi.mode(WIFI_STA);
  WiFi.disconnect();
  delay(100);
  
  WiFi.begin(WIFI_SSID, WIFI_PASSWORD);
  
  int attempts = 0;
  while (WiFi.status() != WL_CONNECTED && attempts < 30) {
    delay(500);
    Serial.printf("[WiFi] Attempt %d/30 — status=%d\n", attempts + 1, WiFi.status());
    attempts++;
  }
  
  if (WiFi.status() == WL_CONNECTED) {
    Serial.printf("[WiFi] CONNECTED! IP: %s\n", WiFi.localIP().toString().c_str());
    Serial.printf("[WiFi] RSSI: %d dBm\n", WiFi.RSSI());
    Serial.printf("[WiFi] Gateway: %s\n", WiFi.gatewayIP().toString().c_str());
  } else {
    Serial.printf("[WiFi] FAILED! Final status: %d\n", WiFi.status());
    Serial.println("[WiFi] Status codes: 0=IDLE, 1=NO_SSID, 2=SCAN_COMPLETE, 3=CONNECTED, 4=CONNECT_FAILED, 5=CONNECTION_LOST");
    Serial.println("[WiFi] Check: SSID correct? Password correct? Router on 2.4GHz?");
  }
}

bool isWiFiConnected() {
  return WiFi.status() == WL_CONNECTED;
}

void checkWiFiConnection() {
  if (WiFi.status() != WL_CONNECTED) {
    Serial.printf("[WiFi] Connection lost (status=%d). Reconnecting...\n", WiFi.status());
    WiFi.reconnect();
    delay(500);
    if (WiFi.status() == WL_CONNECTED) {
      Serial.printf("[WiFi] Reconnected! IP: %s\n", WiFi.localIP().toString().c_str());
    } else {
      Serial.println("[WiFi] Reconnect failed. Will retry next loop.");
    }
  }
}
