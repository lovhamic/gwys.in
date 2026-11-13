#ifndef RGB_LED_H
#define RGB_LED_H

#include <Arduino.h>

void initLED();
void setLEDColor(uint32_t color);
void setLEDMood(const char* mood);
void updateLEDAnimation();
void setLEDThinking(bool thinking);

// Flow animations
void flowColor(uint32_t color1, uint32_t color2);
void flowSingle(uint32_t color);
void breatheColor(uint32_t color);
void rainbowFlow();

// Color utilities
uint32_t blendColors(uint32_t c1, uint32_t c2, float ratio);
uint32_t scaleColor(uint32_t color, uint8_t brightness);

#endif
