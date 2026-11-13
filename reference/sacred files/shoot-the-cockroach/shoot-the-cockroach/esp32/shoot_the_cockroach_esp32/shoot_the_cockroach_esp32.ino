/*
 * Shoot the Cockroach - ESP32 Code
 * Reads MPU6050 accelerometer/gyroscope and trigger button
 * Sends data via USB Serial to computer game
 */

#include <Wire.h>

// ==================== CONFIGURATION ====================
#define TRIGGER_PIN 4           // GPIO pin for trigger button
#define MPU6050_ADDR 0x68       // MPU6050 I2C address
#define SERIAL_BAUD 115200      // Serial communication baud rate
#define SEND_INTERVAL_MS 10     // Send sensor data every 10ms (100Hz)
#define DEBOUNCE_MS 50          // Trigger debounce time in ms

// MPU6050 Registers
#define MPU6050_PWR_MGMT_1 0x6B
#define MPU6050_ACCEL_XOUT_H 0x3B

// ==================== GLOBAL VARIABLES ====================
unsigned long lastSendTime = 0;
unsigned long lastTriggerPress = 0;
bool triggerPressed = false;
bool triggerState = false;
int16_t ax, ay, az, gx, gy, gz;

void setup() {
  Serial.begin(SERIAL_BAUD);
  while (!Serial) {
    delay(10);  // Wait for serial connection
  }

  pinMode(TRIGGER_PIN, INPUT_PULLUP);

  Wire.begin();
  Wire.setClock(400000);  // 400kHz I2C

  // Initialize MPU6050
  writeRegister(MPU6050_PWR_MGMT_1, 0x00);  // Wake up MPU6050
  delay(100);

  // Configure accelerometer range (±2g)
  writeRegister(0x1C, 0x00);
  // Configure gyroscope range (±250 deg/s)
  writeRegister(0x1B, 0x00);

  Serial.println("ESP32_READY");
}

void loop() {
  unsigned long currentTime = millis();

  // Read MPU6050 data
  readMPU6050();

  // Send sensor data at regular interval
  if (currentTime - lastSendTime >= SEND_INTERVAL_MS) {
    sendSensorData();
    lastSendTime = currentTime;
  }

  // Check trigger button with debouncing
  checkTrigger();
}

void readMPU6050() {
  Wire.beginTransmission(MPU6050_ADDR);
  Wire.write(MPU6050_ACCEL_XOUT_H);
  Wire.endTransmission(false);
  Wire.requestFrom(MPU6050_ADDR, 14, true);

  if (Wire.available() >= 14) {
    ax = (Wire.read() << 8) | Wire.read();
    ay = (Wire.read() << 8) | Wire.read();
    az = (Wire.read() << 8) | Wire.read();
    Wire.read(); Wire.read();  // Temperature (skip)
    gx = (Wire.read() << 8) | Wire.read();
    gy = (Wire.read() << 8) | Wire.read();
    gz = (Wire.read() << 8) | Wire.read();
  }
}

void sendSensorData() {
  Serial.print("DATA,");
  Serial.print(ax); Serial.print(",");
  Serial.print(ay); Serial.print(",");
  Serial.print(az); Serial.print(",");
  Serial.print(gx); Serial.print(",");
  Serial.print(gy); Serial.print(",");
  Serial.println(gz);
}

void checkTrigger() {
  bool currentState = digitalRead(TRIGGER_PIN) == LOW;  // Active LOW with pullup

  if (currentState && !triggerState) {
    // Button pressed (falling edge)
    if (millis() - lastTriggerPress >= DEBOUNCE_MS) {
      Serial.println("SHOOT");
      lastTriggerPress = millis();
    }
  }

  triggerState = currentState;
}

void writeRegister(uint8_t reg, uint8_t value) {
  Wire.beginTransmission(MPU6050_ADDR);
  Wire.write(reg);
  Wire.write(value);
  Wire.endTransmission(true);
}