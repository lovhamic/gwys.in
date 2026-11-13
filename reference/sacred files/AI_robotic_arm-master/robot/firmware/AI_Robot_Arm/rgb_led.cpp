#include "rgb_led.h"
#include "config.h"
#include <Adafruit_NeoPixel.h>

Adafruit_NeoPixel strip(NUM_LEDS, PIN_LED, NEO_GRB + NEO_KHZ800);

uint32_t currentColor = COLOR_OFF;
bool thinkingMode = false;
unsigned long lastAnimMs = 0;
int animStep = 0;

// Flow speed per mood (ms per step)
const unsigned long FLOW_SPEED_CURIOUS  = 80;
const unsigned long FLOW_SPEED_HAPPY    = 50;
const unsigned long FLOW_SPEED_CONFUSED = 150;
const unsigned long FLOW_SPEED_SAD      = 200;
const unsigned long FLOW_SPEED_BUSY     = 60;
const unsigned long FLOW_SPEED_SLEEPING = 300;

unsigned long flowSpeed = FLOW_SPEED_CURIOUS;

void initLED() {
  Serial.printf("[LED] Initializing %d WS2812B LEDs on GPIO%d...\n", NUM_LEDS, PIN_LED);
  strip.begin();
  strip.setBrightness(80);
  strip.clear();
  strip.show();
  animStep = 0;
  Serial.println("[LED] Init OK.");
}

void setLEDColor(uint32_t color) {
  currentColor = color;
  for (int i = 0; i < NUM_LEDS; i++) {
    strip.setPixelColor(i, color);
  }
  strip.show();
}

void setLEDMood(const char* mood) {
  if (thinkingMode) return;

  if (strcmp(mood, "curious") == 0) {
    flowSpeed = FLOW_SPEED_CURIOUS;
  } else if (strcmp(mood, "happy") == 0) {
    flowSpeed = FLOW_SPEED_HAPPY;
  } else if (strcmp(mood, "confused") == 0) {
    flowSpeed = FLOW_SPEED_CONFUSED;
  } else if (strcmp(mood, "sad") == 0) {
    flowSpeed = FLOW_SPEED_SAD;
  } else if (strcmp(mood, "busy") == 0) {
    flowSpeed = FLOW_SPEED_BUSY;
  } else if (strcmp(mood, "sleeping") == 0) {
    flowSpeed = FLOW_SPEED_SLEEPING;
  } else {
    flowSpeed = FLOW_SPEED_CURIOUS;
  }

  Serial.printf("[LED] Mood '%s' -> flow speed %lums\n", mood, flowSpeed);
}

void setLEDThinking(bool thinking) {
  thinkingMode = thinking;
  animStep = 0;
  if (!thinking) {
    strip.clear();
    strip.show();
  }
}

void flowColor(uint32_t color1, uint32_t color2) {
  unsigned long now = millis();
  if (now - lastAnimMs < flowSpeed) return;
  lastAnimMs = now;

  for (int i = 0; i < NUM_LEDS; i++) {
    int pos = (i + animStep) % NUM_LEDS;
    float ratio = (float)pos / (float)(NUM_LEDS - 1);
    uint32_t c = blendColors(color1, color2, ratio);
    strip.setPixelColor(i, c);
  }
  strip.show();
  animStep = (animStep + 1) % NUM_LEDS;
}

void flowSingle(uint32_t color) {
  unsigned long now = millis();
  if (now - lastAnimMs < flowSpeed) return;
  lastAnimMs = now;

  strip.clear();
  strip.setPixelColor(animStep % NUM_LEDS, color);
  strip.show();
  animStep = (animStep + 1) % NUM_LEDS;
}

void breatheColor(uint32_t color) {
  unsigned long now = millis();
  if (now - lastAnimMs < 10) return;
  lastAnimMs = now;

  float phase = (sin(animStep * 0.1) + 1.0) / 2.0;
  uint8_t bright = (uint8_t)(phase * 80);
  
  for (int i = 0; i < NUM_LEDS; i++) {
    strip.setPixelColor(i, scaleColor(color, bright));
  }
  strip.show();
  animStep++;
}

void rainbowFlow() {
  unsigned long now = millis();
  if (now - lastAnimMs < flowSpeed) return;
  lastAnimMs = now;

  for (int i = 0; i < NUM_LEDS; i++) {
    int hue = (animStep + i * (65536 / NUM_LEDS)) & 0xFFFF;
    strip.setPixelColor(i, strip.ColorHSV(hue));
  }
  strip.show();
  animStep = (animStep + 400) & 0xFFFF;
}

void updateLEDAnimation() {
  unsigned long now = millis();

  if (thinkingMode) {
    if (now - lastAnimMs > 150) {
      strip.clear();
      int lit = animStep % NUM_LEDS;
      strip.setPixelColor(lit, COLOR_CURIOUS);
      strip.show();
      animStep++;
      lastAnimMs = now;
    }
    return;
  }

  // Ambient animation based on current mood
  // We don't call setLEDColor() here — just keep the flow running
}

// ── Color utilities ──

uint32_t blendColors(uint32_t c1, uint32_t c2, float ratio) {
  uint8_t r1 = (c1 >> 16) & 0xFF;
  uint8_t g1 = (c1 >> 8) & 0xFF;
  uint8_t b1 = c1 & 0xFF;
  uint8_t r2 = (c2 >> 16) & 0xFF;
  uint8_t g2 = (c2 >> 8) & 0xFF;
  uint8_t b2 = c2 & 0xFF;

  uint8_t r = r1 + (uint8_t)((r2 - r1) * ratio);
  uint8_t g = g1 + (uint8_t)((g2 - g1) * ratio);
  uint8_t b = b1 + (uint8_t)((b2 - b1) * ratio);

  return strip.Color(r, g, b);
}

uint32_t scaleColor(uint32_t color, uint8_t brightness) {
  uint8_t r = ((color >> 16) & 0xFF) * brightness / 255;
  uint8_t g = ((color >> 8) & 0xFF) * brightness / 255;
  uint8_t b = (color & 0xFF) * brightness / 255;
  return strip.Color(r, g, b);
}
