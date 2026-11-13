#ifndef COMMS_WEBSOCKET_H
#define COMMS_WEBSOCKET_H

#include <Arduino.h>
#include <ArduinoWebsockets.h>

typedef void (*CommandCallback)(const char* jsonCmd);

void initWebSocket(CommandCallback callback);
void pollWebSocket();
bool isWebSocketConnected();
void sendState(const char* jsonState);
void checkWebSocketConnection();
unsigned long getLastServerMessageMs();

#endif
