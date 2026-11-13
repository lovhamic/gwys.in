#ifndef SAFETY_MONITOR_H
#define SAFETY_MONITOR_H

#include <Arduino.h>

void initSafety();
void checkSafety(float currentA);
bool isEmergencyStopped();
void triggerEmergencyStop();
void clearEmergencyStop();
const char* getSafetyStatus();

#endif
