/*
  TEST 01b - Servo Type Identification
  Wire ONE servo to GPIO 12: RED->PSU+5V, BROWN->GND, ORANGE->GPIO 12

  This sends a sequence of FIXED pulse widths and holds each for 3 seconds.
  WATCH THE SERVO PHYSICALLY and read the Serial output to judge behavior.
*/

#include <Arduino.h>

#define SERVO_PIN 12
#define PWM_FREQ 50
#define PWM_RES 16
#define HOLD_MS 3000

void writePulse(float pulseUs, const char* label) {
  uint32_t duty = (uint32_t)((pulseUs / 20000.0f) * 65535.0f);
  ledcWrite(SERVO_PIN, duty);
  Serial.printf("\n>>> Sending %s (%.0fus) — watch servo for %d sec <<<\n", label, pulseUs, HOLD_MS / 1000);
}

void setup() {
  Serial.begin(115200);
  while (!Serial) { ; }
  delay(500);

  ledcAttach(SERVO_PIN, PWM_FREQ, PWM_RES);

  Serial.println("========================================");
  Serial.println("  TEST 01b: Servo Type Identification");
  Serial.println("========================================");
  Serial.println("");
  Serial.println("HOW TO READ THE RESULT:");
  Serial.println("- If servo MOVES to a position then STOPS/HOLDS");
  Serial.println("  at each step -> POSITIONAL servo (0-180deg)");
  Serial.println("- If servo KEEPS SPINNING at 1000/2000us and");
  Serial.println("  only STOPS at 1500us -> CONTINUOUS ROTATION servo");
  Serial.println("");
  delay(2000);

  writePulse(1500, "CENTER/STOP (1500us)");
  delay(HOLD_MS);

  writePulse(1000, "MIN (1000us)");
  delay(HOLD_MS);

  writePulse(1500, "CENTER/STOP (1500us) - check if it stopped");
  delay(HOLD_MS);

  writePulse(2000, "MAX (2000us)");
  delay(HOLD_MS);

  writePulse(1500, "CENTER/STOP (1500us) - check if it stopped");
  delay(HOLD_MS);

  Serial.println("");
  Serial.println("========================================");
  Serial.println("TEST COMPLETE.");
  Serial.println("Did it hold distinct positions? -> POSITIONAL");
  Serial.println("Did it spin continuously except at 1500us? -> CONTINUOUS");
  Serial.println("========================================");
}

void loop() {
  // nothing — one-shot test, sequence runs once in setup()
}