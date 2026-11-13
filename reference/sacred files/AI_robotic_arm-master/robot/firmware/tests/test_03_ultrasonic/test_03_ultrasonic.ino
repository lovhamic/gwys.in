/*
  TEST 03 - HC-SR04 Ultrasonic Sensor
  What this tests: Distance measurement works
  
  Wire for THIS TEST ONLY:
    HC-SR04 VCC  -> Breadboard RED rail (+5V)
    HC-SR04 GND  -> Breadboard BLUE rail (GND)
    HC-SR04 TRIG -> ESP32 GPIO 17
    HC-SR04 ECHO -> VOLTAGE DIVIDER -> ESP32 GPIO 5
    
    VOLTAGE DIVIDER (CRITICAL - protects ESP32 from 5V):
      ECHO --[1k resistor]--+--[2k resistor]-- GND
                            |
                            +-- GPIO 5
  
  Expected Serial output:
    [Ultrasonic] Distance: 23.4 cm
    [Ultrasonic] Distance: 23.6 cm
    ...
    
  Point sensor at a wall/object. Distance should change when you move your hand.
*/

#define TRIG_PIN 17
#define ECHO_PIN 5

void setup() {
  Serial.begin(115200);
  while (!Serial) { ; }
  delay(500);

  pinMode(TRIG_PIN, OUTPUT);
  pinMode(ECHO_PIN, INPUT);
  digitalWrite(TRIG_PIN, LOW);

  Serial.println("========================================");
  Serial.println("  TEST 03: HC-SR04 Ultrasonic Sensor");
  Serial.println("========================================");
  Serial.println("");
  Serial.println("Wire HC-SR04 with VOLTAGE DIVIDER on ECHO!");
  Serial.println("ECHO --[1k]--+--[2k]-- GND");
  Serial.println("             |");
  Serial.println("            GPIO 5");
  Serial.println("");
  Serial.println("Move your hand in front of sensor...");
  Serial.println("");
}

void loop() {
  // Trigger pulse
  digitalWrite(TRIG_PIN, LOW);
  delayMicroseconds(2);
  digitalWrite(TRIG_PIN, HIGH);
  delayMicroseconds(10);
  digitalWrite(TRIG_PIN, LOW);

  // Read echo duration
  long duration = pulseIn(ECHO_PIN, HIGH, 30000);  // 30ms timeout

  if (duration == 0) {
    Serial.println("[Ultrasonic] Out of range / No echo");
  } else {
    float distance = duration * 0.0343f / 2.0f;  // cm
    Serial.printf("[Ultrasonic] Duration: %ld us | Distance: %.1f cm\n", duration, distance);
  }

  delay(200);  // 5 readings per second
}
