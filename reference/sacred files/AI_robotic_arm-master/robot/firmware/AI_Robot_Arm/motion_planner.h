#ifndef MOTION_PLANNER_H
#define MOTION_PLANNER_H

#include <Arduino.h>
#include "config.h"

void initMotionPlanner();
void planTrajectory(float baseAngle, float shoulderAngle, float elbowAngle,
                    float wristSpeed, float gripper, unsigned long durationMs);
void planSkillFrame(float baseAngle, float shoulderAngle, float elbowAngle,
                    float wristSpeed, float gripper);
void updateMotion();
bool isMotionComplete();
void cancelMotion();

#endif
