#include "sensor_manager.h"
#include "config.h"

float lastDistance = -1.0f;
float lastCurrent = 0.0f;
unsigned long lastReadMs = 0;

float readUltrasonic();
float readCurrent();

void initSensors() {
  Serial.println("[Sensor] Initializing HC-SR04 + ACS712...");
  Serial.printf("[Sensor]   TRIG=GPIO%d ECHO=GPIO%d CURRENT=GPIO%d\n", 
                PIN_ULTRASONIC_TRIG, PIN_ULTRASONIC_ECHO, PIN_CURRENT_SENSOR);
  
  pinMode(PIN_ULTRASONIC_TRIG, OUTPUT);
  pinMode(PIN_ULTRASONIC_ECHO, INPUT);
  digitalWrite(PIN_ULTRASONIC_TRIG, LOW);
  
  analogReadResolution(12);
  analogSetAttenuation(ADC_11db);
  
  Serial.println("[Sensor] Init OK.");
}

void readSensors() {
  lastDistance = readUltrasonic();
  lastCurrent = readCurrent();
}

float readUltrasonic() {
  digitalWrite(PIN_ULTRASONIC_TRIG, LOW);
  delayMicroseconds(2);
  digitalWrite(PIN_ULTRASONIC_TRIG, HIGH);
  delayMicroseconds(10);
  digitalWrite(PIN_ULTRASONIC_TRIG, LOW);
  
  long duration = pulseIn(PIN_ULTRASONIC_ECHO, HIGH, 30000);
  if (duration == 0) {
    return -1.0f;
  }
  
  float distance = duration * ULTRASONIC_CM_PER_US;
  if (distance > ULTRASONIC_MAX_RANGE_CM) return -1.0f;
  return distance;
}

float readCurrent() {
  long rawSum = 0;
  for (int i = 0; i < 10; i++) {
    rawSum += analogRead(PIN_CURRENT_SENSOR);
    delay(5);
  }
  int raw = rawSum / 10;
  
  float pinVoltage = raw * CURRENT_ADC_TO_VOLTS;
  float acsVoltage = pinVoltage * CURRENT_DIVIDER_RATIO;
  float current = (acsVoltage - CURRENT_ZERO_OFFSET) / CURRENT_SENSITIVITY;
  
  return current;
}

float getDistanceCm() { return lastDistance; }
float getCurrentA() { return lastCurrent; }
