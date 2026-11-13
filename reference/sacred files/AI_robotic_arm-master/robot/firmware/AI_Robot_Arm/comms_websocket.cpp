#include "comms_websocket.h"
#include "config.h"
#include <WiFi.h>

using namespace websockets;

WebsocketsClient wsClient;
CommandCallback cmdCallback = nullptr;
unsigned long lastServerMsgMs = 0;
bool wsConnected = false;

void onMessage(WebsocketsMessage msg) {
  lastServerMsgMs = millis();
  Serial.printf("[WS] << Message received (%d bytes): %s\n", msg.data().length(), msg.data().c_str());
  if (cmdCallback) {
    cmdCallback(msg.data().c_str());
  }
}

void onEvent(WebsocketsEvent event, String data) {
  if (event == WebsocketsEvent::ConnectionOpened) {
    wsConnected = true;
    Serial.println("[WS] >>> EVENT: Connection OPENED");
  } else if (event == WebsocketsEvent::ConnectionClosed) {
    wsConnected = false;
    Serial.printf("[WS] >>> EVENT: Connection CLOSED (code=%s)\n", data.c_str());
  } else if (event == WebsocketsEvent::GotPing) {
    Serial.println("[WS] >>> EVENT: Got PING, sending PONG");
    wsClient.pong();
  } else if (event == WebsocketsEvent::GotPong) {
    Serial.println("[WS] >>> EVENT: Got PONG");
  } else {
    Serial.printf("[WS] >>> EVENT: unknown(%d) data=%s\n", (int)event, data.c_str());
  }
}

void initWebSocket(CommandCallback callback) {
  cmdCallback = callback;
  String url = "ws://" + String(SERVER_HOST) + ":" + String(SERVER_PORT) + String(SERVER_PATH);
  Serial.printf("[WS] Target URL: %s\n", url.c_str());
  Serial.printf("[WS] WiFi status before connect: %d (3=connected)\n", WiFi.status());
  
  wsClient.onMessage(onMessage);
  wsClient.onEvent(onEvent);
  
  Serial.println("[WS] Attempting initial connection...");
  bool result = wsClient.connect(url.c_str());
  if (result) {
    lastServerMsgMs = millis();
    Serial.println("[WS] Initial connection: SUCCESS");
  } else {
    Serial.println("[WS] Initial connection: FAILED (server not running?)");
    Serial.println("[WS] Will retry in background. Make sure server.py is running.");
  }
}

void pollWebSocket() {
  wsClient.poll();
}

bool isWebSocketConnected() {
  return wsConnected && wsClient.available();
}

void sendState(const char* jsonState) {
  if (wsClient.available()) {
    wsClient.send(jsonState);
  } else {
    static unsigned long lastWarnMs = 0;
    if (millis() - lastWarnMs > 5000) {
      Serial.println("[WS] Cannot send — not connected. Waiting for reconnect...");
      lastWarnMs = millis();
    }
  }
}

void checkWebSocketConnection() {
  if (!wsClient.available() && WiFi.status() == WL_CONNECTED) {
    Serial.println("[WS] Reconnecting to server...");
    String url = "ws://" + String(SERVER_HOST) + ":" + String(SERVER_PORT) + String(SERVER_PATH);
    Serial.printf("[WS] URL: %s\n", url.c_str());
    bool result = wsClient.connect(url.c_str());
    if (result) {
      Serial.println("[WS] Reconnect: SUCCESS");
      lastServerMsgMs = millis();
    } else {
      Serial.println("[WS] Reconnect: FAILED");
    }
    delay(500);
  }
}

unsigned long getLastServerMessageMs() {
  return lastServerMsgMs;
}
