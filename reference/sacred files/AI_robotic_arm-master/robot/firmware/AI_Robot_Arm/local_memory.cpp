#include "local_memory.h"
#include "config.h"
#include <SPIFFS.h>
#include <ArduinoJson.h>

#define SKILLS_DIR "/skills"
#define SKILLS_INDEX "/skills/index.json"

void initLocalMemory() {
  Serial.println("[SPIFFS] Initializing...");
  if (!SPIFFS.begin(true)) {
    Serial.println("[SPIFFS] FAILED to mount! Skills won't be saved.");
    return;
  }
  
  Serial.printf("[SPIFFS] Total: %llu bytes, Used: %llu bytes, Free: %llu bytes\n",
                SPIFFS.totalBytes(), SPIFFS.usedBytes(), 
                SPIFFS.totalBytes() - SPIFFS.usedBytes());
  
  if (!SPIFFS.exists(SKILLS_DIR)) {
    Serial.println("[SPIFFS] Creating /skills directory...");
    SPIFFS.mkdir(SKILLS_DIR);
  }
  
  if (!SPIFFS.exists(SKILLS_INDEX)) {
    Serial.println("[SPIFFS] Creating skills index...");
    File f = SPIFFS.open(SKILLS_INDEX, FILE_WRITE);
    f.print("[]");
    f.close();
  }
  
  Serial.println("[SPIFFS] Local memory ready.");
}

bool saveSkill(const char* name, const char* jsonTrajectory) {
  String path = String(SKILLS_DIR) + "/" + name + ".json";
  Serial.printf("[SPIFFS] Saving skill '%s' to %s (%d bytes)...\n", name, path.c_str(), strlen(jsonTrajectory));
  
  File f = SPIFFS.open(path, FILE_WRITE);
  if (!f) {
    Serial.printf("[SPIFFS] FAILED to open %s for writing!\n", path.c_str());
    return false;
  }
  f.print(jsonTrajectory);
  f.close();
  Serial.printf("[SPIFFS] Skill file written OK.\n");
  
  // Update index
  File idx = SPIFFS.open(SKILLS_INDEX, FILE_READ);
  String content = idx.readString();
  idx.close();
  
  StaticJsonDocument<4096> doc;
  deserializeJson(doc, content);
  JsonArray arr = doc.as<JsonArray>();
  
  bool found = false;
  for (JsonObject obj : arr) {
    if (strcmp(obj["name"] | "", name) == 0) {
      found = true;
      break;
    }
  }
  if (!found) {
    JsonObject entry = arr.createNestedObject();
    entry["name"] = name;
    entry["created"] = millis();
    Serial.printf("[SPIFFS] Skill '%s' added to index.\n", name);
  }
  
  File idxW = SPIFFS.open(SKILLS_INDEX, FILE_WRITE);
  serializeJson(doc, idxW);
  idxW.close();
  
  return true;
}

bool loadSkill(const char* name, char* outBuffer, size_t maxLen) {
  String path = String(SKILLS_DIR) + "/" + name + ".json";
  Serial.printf("[SPIFFS] Loading skill '%s' from %s...\n", name, path.c_str());
  
  File f = SPIFFS.open(path, FILE_READ);
  if (!f) {
    Serial.printf("[SPIFFS] Skill '%s' NOT FOUND\n", name);
    return false;
  }
  size_t n = f.readBytes(outBuffer, maxLen - 1);
  outBuffer[n] = '\0';
  f.close();
  Serial.printf("[SPIFFS] Loaded %d bytes\n", n);
  return true;
}

bool listSkills(char* outBuffer, size_t maxLen) {
  File f = SPIFFS.open(SKILLS_INDEX, FILE_READ);
  if (!f) {
    strncpy(outBuffer, "[]", maxLen);
    Serial.println("[SPIFFS] No skills index found, returning empty.");
    return true;
  }
  size_t n = f.readBytes(outBuffer, maxLen - 1);
  outBuffer[n] = '\0';
  f.close();
  Serial.printf("[SPIFFS] Listed skills index: %d bytes\n", n);
  return true;
}

bool deleteSkill(const char* name) {
  String path = String(SKILLS_DIR) + "/" + name + ".json";
  Serial.printf("[SPIFFS] Deleting skill '%s'...\n", name);
  SPIFFS.remove(path);
  Serial.printf("[SPIFFS] Skill '%s' deleted.\n", name);
  return true;
}

bool hasSkill(const char* name) {
  String path = String(SKILLS_DIR) + "/" + name + ".json";
  return SPIFFS.exists(path);
}
