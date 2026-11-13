#ifndef LOCAL_MEMORY_H
#define LOCAL_MEMORY_H

#include <Arduino.h>

void initLocalMemory();
bool saveSkill(const char* name, const char* jsonTrajectory);
bool loadSkill(const char* name, char* outBuffer, size_t maxLen);
bool listSkills(char* outBuffer, size_t maxLen);
bool deleteSkill(const char* name);
bool hasSkill(const char* name);

#endif
