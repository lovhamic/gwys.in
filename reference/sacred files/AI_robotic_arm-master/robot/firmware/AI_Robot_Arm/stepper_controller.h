#ifndef STEPPER_CONTROLLER_H
#define STEPPER_CONTROLLER_H

#include <Arduino.h>
#include "config.h"

void initStepper();
void setStepperTargetAngle(float angleDeg);
float getStepperTargetAngle();
float getStepperCurrentAngle();
bool isStepperMoving();
void updateStepper();
void stopStepper();
void enableStepper();
void disableStepper();
void stepperStep(bool direction, unsigned int stepDelayUs);
long getStepperPosition();
void resetStepperPosition();

#endif
