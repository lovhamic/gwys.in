#include <Adafruit_NeoPixel.h>

#define LED_PIN     5      // GPIO connected to DIN
#define NUM_LEDS    16     // adjust if your ring isn't actually 16 LEDs
#define BRIGHTNESS  50     // 0-255, keep low for USB-only testing

Adafruit_NeoPixel ring(NUM_LEDS, LED_PIN, NEO_GRB + NEO_KHZ800);

void setup() {
  ring.begin();
  ring.setBrightness(BRIGHTNESS);
  ring.show(); // all off initially
}

void loop() {
  // Test 1: Solid colors
  colorWipe(ring.Color(255, 0, 0), 50); // Red
  colorWipe(ring.Color(0, 255, 0), 50); // Green
  colorWipe(ring.Color(0, 0, 255), 50); // Blue
  colorWipe(ring.Color(255, 255, 255), 50); // White

  // Test 2: Rainbow cycle
  rainbowCycle(10);
}

void colorWipe(uint32_t color, int wait) {
  for (int i = 0; i < ring.numPixels(); i++) {
    ring.setPixelColor(i, color);
    ring.show();
    delay(wait);
  }
  delay(500);
}

void rainbowCycle(int wait) {
  for (long firstPixelHue = 0; firstPixelHue < 65536; firstPixelHue += 256) {
    for (int i = 0; i < ring.numPixels(); i++) {
      int pixelHue = firstPixelHue + (i * 65536L / ring.numPixels());
      ring.setPixelColor(i, ring.gamma32(ring.ColorHSV(pixelHue)));
    }
    ring.show();
    delay(wait);
  }
}