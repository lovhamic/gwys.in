#ifndef TEACHING_MODE_H
#define TEACHING_MODE_H

#include <Arduino.h>

void initTeachingMode();
void startTeaching();
void stopTeaching();
bool isTeaching();
void recordFrame();
char* getRecordedTrajectory();
void clearRecording();

#endif
