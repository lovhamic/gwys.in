#ifndef COMMAND_PARSER_H
#define COMMAND_PARSER_H

#include <Arduino.h>

void parseCommand(const char* jsonCmd);
void sendCommandAck(const char* cmdId, const char* status);

#endif
