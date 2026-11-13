/*
  TEST 01 - Onboard LED + Serial
  What this tests: ESP32 powers on, Serial works, onboard LED blinks
  Wire: NOTHING. Just plug ESP32 to USB.
  Expected: LED blinks, text appears in Serial Monitor at 115200 baud
*/

#define LED_BUILTIN 2

void setup() {
  Serial.begin(115200);
  while (!Serial) { ; }
  delay(500);

  pinMode(LED_BUILTIN, OUTPUT);

  Serial.println("========================================");
  Serial.println("  TEST 01: Onboard LED + Serial");
  Serial.println("========================================");
  Serial.println("");
  Serial.println("[PASS] If you can read this, Serial works!");
  Serial.println("[INFO] Onboard LED (GPIO 2) should blink every 500ms");
  Serial.println("");
  Serial.println("Starting blink loop...");
}

void loop() {
  digitalWrite(LED_BUILTIN, HIGH);
  Serial.println("[LED] ON");
  delay(500);
  digitalWrite(LED_BUILTIN, LOW);
  Serial.println("[LED] OFF");
  delay(500);
}
