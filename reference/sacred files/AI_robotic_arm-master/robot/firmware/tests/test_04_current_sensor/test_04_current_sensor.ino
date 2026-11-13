/*
  TEST 04 - ACS712 Current Sensor
  What this tests: Current measurement works
  
  Wire for THIS TEST ONLY:
    ACS712 VCC -> Breadboard RED rail (+5V)
    ACS712 GND -> Breadboard BLUE rail (GND)
    ACS712 OUT -> VOLTAGE DIVIDER -> ESP32 GPIO 34
    
    VOLTAGE DIVIDER:
      OUT --[10k]--+--[10k]-- GND
                   |
                  GPIO 34
    
    HIGH CURRENT PATH (optional for this test):
      PSU RED -> ACS712 IP+ -> ACS712 IP- -> breadboard RED rail
      This routes servo power through the sensor.
  
  Expected Serial output with NO load:
    [Current] Raw ADC: 2048 | Pin Voltage: 1.65V | ACS712: 3.30V | Current: 0.00A
  
  Expected with a servo running:
    [Current] Raw ADC: 2100 | Pin Voltage: 1.69V | ACS712: 3.38V | Current: 0.43A
*/

#define CURRENT_PIN 34

// Calibration constants (from config.h)
const float ADC_TO_VOLTS = 3.3f / 4095.0f;
const float DIVIDER_RATIO = 2.0f;
const float ZERO_OFFSET = 2.5f;
const float SENSITIVITY = 0.185f;

void setup() {
  Serial.begin(115200);
  while (!Serial) { ; }
  delay(500);

  // ESP32 ADC setup: 12-bit resolution, 11dB attenuation
  analogReadResolution(12);
  analogSetAttenuation(ADC_11db);  // 0-3.3V range

  Serial.println("========================================");
  Serial.println("  TEST 04: ACS712 Current Sensor");
  Serial.println("========================================");
  Serial.println("");
  Serial.println("Wire ACS712 OUT with voltage divider to GPIO 34!");
  Serial.println("OUT --[10k]--+--[10k]-- GND");
  Serial.println("             |");
  Serial.println("            GPIO 34");
  Serial.println("");
  Serial.println("Expected: ~0A with no load, positive reading with servo");
  Serial.println("");
}

void loop() {
  // Take 10 samples and average for stability
  long rawSum = 0;
  for (int i = 0; i < 10; i++) {
    rawSum += analogRead(CURRENT_PIN);
    delay(5);
  }
  int raw = rawSum / 10;

  float pinVoltage = raw * ADC_TO_VOLTS;
  float acsVoltage = pinVoltage * DIVIDER_RATIO;
  float current = (acsVoltage - ZERO_OFFSET) / SENSITIVITY;

  Serial.printf("[Current] Raw ADC: %d | Pin: %.2fV | ACS712: %.2fV | Current: %.3fA\n",
                raw, pinVoltage, acsVoltage, current);

  delay(500);
}
