#ifndef SERVO_CONTROLLER_H
#define SERVO_CONTROLLER_H

#include <Arduino.h>
#include "config.h"

void initServos();
void writeServo(int servoIndex, float value);
void writeAllServos();
void setServoTargets(float angles[2], float wristSpeed, float gripper);
void setServoSpeeds(float wristSpeed, float gripperSpeed, unsigned long durationMs);
void updateServos();
void stopAllServos();
float getCurrentAngle(int servoIndex);
float getTargetAngle(int servoIndex);
bool isServoMoving(int servoIndex);

#endif
