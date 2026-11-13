#ifndef SENSOR_MANAGER_H
#define SENSOR_MANAGER_H

#include <Arduino.h>

void initSensors();
void readSensors();
float getDistanceCm();
float getCurrentA();

#endif
