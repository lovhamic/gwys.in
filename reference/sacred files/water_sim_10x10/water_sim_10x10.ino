/*
  Water simulation + splash effects
  10x10 WS2812B matrix | ESP32 | MPU6050 (read directly over I2C)

  Library needed: FastLED (Arduino framework)

  How it works
  - ~40 water particles. Gravity comes from the MPU6050 accelerometer.
  - A per-cell density grid gives a simple pressure force, so particles pile up
    like liquid instead of collapsing into one point.
  - SPLASH 1: shake/jolt the matrix -> water is thrown "up" (against gravity)
    and spray droplets are spawned.
  - SPLASH 2: water hitting a wall fast enough throws off a few spray droplets.
  - Serial monitor (115200): send 's' to trigger a test splash,
    'd' to toggle accelerometer debug output.
*/

#include <Arduino.h>
#include <Wire.h>
#include <FastLED.h>

// ===================== CONFIG =====================
#define LED_PIN        5
#define W              10
#define H              10
#define NUM_LEDS       (W * H)
#define BRIGHTNESS     255         // 0-255 (max)
#define MAX_MILLIAMPS  6000        // 100 LEDs x 60 mA = 6 A worst case (full white)

#define SDA_PIN        21
#define SCL_PIN        22
#define MPU_ADDR       0x68

// Wiring / orientation - adjust to your build
#define SERPENTINE          true   // rows alternate direction (zigzag)
#define ROW0_LEFT_TO_RIGHT  true   // first row runs left -> right
#define SWAP_XY             false  // swap sensor X/Y axes
#define INVERT_X            false  // flip if water falls the wrong way (left/right)
#define INVERT_Y            false  // flip if water falls the wrong way (up/down)

// Simulation
#define N_WATER        40
#define N_SPRAY        20
#define GRAV           40.0f       // cells/s^2 at 1 g
#define PRESSURE       70.0f      // higher = stiffer, less compressible water
#define DRAG           1.5f
#define RESTITUTION    0.35f       // wall bounciness

// Splash tuning
#define SHAKE_JERK_G       0.5f    // frame-to-frame accel change (g) that triggers a splash
#define SHAKE_COOLDOWN_MS  250
#define IMPACT_SPEED       15.0f   // wall-impact speed (cells/s) that can spawn spray
#define IMPACT_CHANCE      60      // % chance per qualifying impact
#define FRAME_US           25000   // cap at ~40 fps so physics and shake detection stay consistent
// ==================================================

CRGB leds[NUM_LEDS];

struct Water { float x, y, vx, vy; };
struct Spray { float x, y, vx, vy, life; };

Water water[N_WATER];
Spray spray[N_SPRAY];

uint8_t cnt[NUM_LEDS];   // particles per cell
float   spd[NUM_LEDS];   // summed speed per cell (used for foam)

float gx = 0, gy = GRAV;         // gravity in cells/s^2
float fax = 0, fay = 1;          // low-pass filtered accel (g)
float pax = 0, pay = 0, paz = 0; // previous raw accel for shake detection
uint32_t lastShake = 0;
bool debugPrint = false;

const float XM = W - 0.001f;
const float YM = H - 0.001f;

inline float rnd(float a, float b) {
  return a + (b - a) * (random(10001) / 10000.0f);
}

// Map (x, y) to LED index
uint16_t XY(int x, int y) {
  if (x < 0) x = 0; if (x >= W) x = W - 1;
  if (y < 0) y = 0; if (y >= H) y = H - 1;
  bool reverse = SERPENTINE ? ((y & 1) != 0) : false;
  if (!ROW0_LEFT_TO_RIGHT) reverse = !reverse;
  return y * W + (reverse ? (W - 1 - x) : x);
}

// ---------------- MPU6050 ----------------
void mpuInit() {
  Wire.begin(SDA_PIN, SCL_PIN);
  Wire.setClock(400000);
  Wire.beginTransmission(MPU_ADDR); Wire.write(0x6B); Wire.write(0x00); Wire.endTransmission(); // wake up
  Wire.beginTransmission(MPU_ADDR); Wire.write(0x1A); Wire.write(0x03); Wire.endTransmission(); // ~44 Hz low-pass
}

bool readAccel(float &ax, float &ay, float &az) {
  Wire.beginTransmission(MPU_ADDR);
  Wire.write(0x3B);
  if (Wire.endTransmission(false) != 0) return false;
  if (Wire.requestFrom((uint8_t)MPU_ADDR, (uint8_t)6) != 6) return false;
  int16_t rx = (Wire.read() << 8) | Wire.read();
  int16_t ry = (Wire.read() << 8) | Wire.read();
  int16_t rz = (Wire.read() << 8) | Wire.read();
  ax = rx / 16384.0f;   // +/-2 g range
  ay = ry / 16384.0f;
  az = rz / 16384.0f;
  return true;
}

// ---------------- Spray / splash ----------------
void spawnSpray(float x, float y, float vx, float vy) {
  static uint8_t slot = 0;
  for (uint8_t i = 0; i < N_SPRAY; i++) {
    uint8_t k = (slot + i) % N_SPRAY;
    if (spray[k].life <= 0) {
      spray[k] = {x, y, vx, vy, rnd(0.4f, 0.9f)};
      slot = k + 1;
      return;
    }
  }
}

// Throw water against gravity + spawn droplets
void doSplash(float strength) {
  float len = sqrtf(gx * gx + gy * gy);
  float ux = 0, uy = -1;                       // "up" = opposite of gravity
  if (len > 1.0f) { ux = -gx / len; uy = -gy / len; }

  for (int i = 0; i < N_WATER; i++) {
    if (random(100) < 35) {
      float s = rnd(4, 16) * strength;
      water[i].vx += ux * s + rnd(-3, 3);
      water[i].vy += uy * s + rnd(-3, 3);
    }
  }
  for (int k = 0; k < 8; k++) {
    Water &w = water[random(N_WATER)];
    float s = rnd(9, 25) * strength;
    spawnSpray(w.x, w.y, ux * s + rnd(-6, 6), uy * s + rnd(-6, 6));
  }
}

// Called when a water particle hits a wall. (nx, ny) = wall normal pointing into the display.
void wallImpact(float x, float y, float speed, float nx, float ny) {
  if (speed < IMPACT_SPEED || random(100) >= IMPACT_CHANCE) return;
  int n = 1 + random(2);
  for (int i = 0; i < n; i++) {
    float s = speed * rnd(0.3f, 0.7f);
    float t = rnd(-1, 1) * speed * 0.4f;       // sideways scatter
    spawnSpray(x, y, nx * s - ny * t, ny * s + nx * t);
  }
}

// ---------------- Physics ----------------
void buildCounts() {
  memset(cnt, 0, sizeof(cnt));
  memset(spd, 0, sizeof(spd));
  for (auto &p : water) {
    int i = (int)p.y * W + (int)p.x;
    if (cnt[i] < 255) cnt[i]++;
    spd[i] += sqrtf(p.vx * p.vx + p.vy * p.vy);
  }
}

inline uint8_t cntAt(int cx, int cy, uint8_t own) {
  return (cx < 0 || cx >= W || cy < 0 || cy >= H) ? own : cnt[cy * W + cx];
}

void stepWater(float dt) {
  buildCounts();
  const float damp = 1.0f - DRAG * dt;

  for (auto &p : water) {
    int cx = (int)p.x, cy = (int)p.y;
    uint8_t own = cnt[cy * W + cx];

    // pressure: push toward less crowded neighbouring cells
    float fx = (float)cntAt(cx - 1, cy, own) - (float)cntAt(cx + 1, cy, own);
    float fy = (float)cntAt(cx, cy - 1, own) - (float)cntAt(cx, cy + 1, own);

    p.vx += (gx + fx * PRESSURE) * dt;
    p.vy += (gy + fy * PRESSURE) * dt;

    if (own > 3) {                              // break up over-packed cells
      p.vx += rnd(-1, 1) * (own - 3) * 40.0f * dt;
      p.vy += rnd(-1, 1) * (own - 3) * 40.0f * dt;
    }

    p.vx *= damp;
    p.vy *= damp;
    p.x += p.vx * dt;
    p.y += p.vy * dt;

    // walls (+ impact splashes)
    if (p.x < 0) {
      float s = fabsf(p.vx); p.x = 0;  p.vx = s * RESTITUTION;
      wallImpact(p.x, p.y, s, 1, 0);
    } else if (p.x > XM) {
      float s = fabsf(p.vx); p.x = XM; p.vx = -s * RESTITUTION;
      wallImpact(p.x, p.y, s, -1, 0);
    }
    if (p.y < 0) {
      float s = fabsf(p.vy); p.y = 0;  p.vy = s * RESTITUTION;
      wallImpact(p.x, p.y, s, 0, 1);
    } else if (p.y > YM) {
      float s = fabsf(p.vy); p.y = YM; p.vy = -s * RESTITUTION;
      wallImpact(p.x, p.y, s, 0, -1);
    }
  }
}

void stepSpray(float dt) {
  for (auto &s : spray) {
    if (s.life <= 0) continue;
    s.life -= dt;
    s.vx += gx * dt;
    s.vy += gy * dt;
    s.x += s.vx * dt;
    s.y += s.vy * dt;
    if (s.x < 0)       { s.x = 0;  s.vx =  fabsf(s.vx) * 0.3f; }
    else if (s.x > XM) { s.x = XM; s.vx = -fabsf(s.vx) * 0.3f; }
    if (s.y < 0)       { s.y = 0;  s.vy =  fabsf(s.vy) * 0.3f; }
    else if (s.y > YM) { s.y = YM; s.vy = -fabsf(s.vy) * 0.3f; }
  }
}

// ---------------- Rendering ----------------
#define SMOOTH 0.5f   // 0..1, lower = smoother/slower, higher = snappier

static float tgtD[NUM_LEDS], tgtS[NUM_LEDS];   // this frame's density / speed
static float dens[NUM_LEDS], foamS[NUM_LEDS];  // smoothed values actually shown

void render() {
  memset(tgtD, 0, sizeof(tgtD));
  memset(tgtS, 0, sizeof(tgtS));

  // Bilinear splat: each particle is spread over its 4 nearest cells,
  // so brightness changes smoothly instead of cells popping on/off.
  for (auto &p : water) {
    float px = p.x - 0.5f, py = p.y - 0.5f;
    int x0 = (int)floorf(px), y0 = (int)floorf(py);
    float fx = px - x0, fy = py - y0;
    float sp = sqrtf(p.vx * p.vx + p.vy * p.vy);
    for (int j = 0; j < 2; j++) {
      for (int i = 0; i < 2; i++) {
        int cx = x0 + i, cy = y0 + j;
        if (cx < 0 || cx >= W || cy < 0 || cy >= H) continue;
        float w = (i ? fx : 1.0f - fx) * (j ? fy : 1.0f - fy);
        tgtD[cy * W + cx] += w;
        tgtS[cy * W + cx] += w * sp;
      }
    }
  }

  fill_solid(leds, NUM_LEDS, CRGB(0, 0, 3));    // faint background

  for (int y = 0; y < H; y++) {
    for (int x = 0; x < W; x++) {
      int i = y * W + x;

      // temporal smoothing (removes frame-to-frame flicker)
      dens[i]  += SMOOTH * (tgtD[i] - dens[i]);
      foamS[i] += SMOOTH * (tgtS[i] - foamS[i]);

      float d = dens[i];
      if (d < 0.03f) continue;

      float a = constrain(d / 0.5f, 0.0f, 1.0f);              // soft edges
      float t = constrain((d - 0.3f) / 2.0f, 0.0f, 1.0f);     // deeper = darker blue
      float avg = foamS[i] / d;
      float foam = constrain((avg - 12.0f) * 6.0f, 0.0f, 160.0f);

      float r = 10 + 30 * t + foam * 0.8f;
      float g = 50 + 130 * t + foam;
      float b = 150 + 100 * t + foam * 0.5f;
      leds[XY(x, y)] = CRGB((uint8_t)constrain(r * a, 0.0f, 255.0f),
                            (uint8_t)constrain(g * a, 0.0f, 255.0f),
                            (uint8_t)constrain(b * a, 0.0f, 255.0f));
    }
  }

  // spray droplets: bright, fading with life
  for (auto &s : spray) {
    if (s.life <= 0) continue;
    uint8_t v = (uint8_t)(constrain(s.life / 0.5f, 0.0f, 1.0f) * 200);
    leds[XY((int)s.x, (int)s.y)] += CRGB((uint8_t)(v * 0.7f), (uint8_t)(v * 0.9f), v);
  }
}

// ---------------- Arduino ----------------
void setup() {
  Serial.begin(115200);
  randomSeed(analogRead(34) ^ micros());

  FastLED.addLeds<WS2812B, LED_PIN, GRB>(leds, NUM_LEDS);
  FastLED.setBrightness(BRIGHTNESS);
  FastLED.setDither(0);                         // no temporal dithering = less flicker
  FastLED.setMaxPowerInVoltsAndMilliamps(5, MAX_MILLIAMPS);

  mpuInit();
  float ax, ay, az;
  if (readAccel(ax, ay, az)) {                  // prime filter so we don't get a fake shake
    float sx = SWAP_XY ? ay : ax;
    float sy = SWAP_XY ? ax : ay;
    if (INVERT_X) sx = -sx;
    if (INVERT_Y) sy = -sy;
    fax = sx; fay = sy;
    pax = ax; pay = ay; paz = az;
    gx = fax * GRAV; gy = fay * GRAV;
  }

  for (auto &p : water) {
    p.x = rnd(0, W - 1);
    p.y = rnd(H * 0.55f, H - 1);
    p.vx = p.vy = 0;
  }
  for (auto &s : spray) s.life = 0;
}

void loop() {
  static uint32_t last = micros();
  static uint32_t lastDbg = 0;
  uint32_t now = micros();
  if ((uint32_t)(now - last) < FRAME_US) return;   // cap frame rate
  float dt = (now - last) / 1e6f;
  last = now;
  if (dt > 0.05f) dt = 0.05f;

  float ax, ay, az;
  if (readAccel(ax, ay, az)) {
    float sx = SWAP_XY ? ay : ax;
    float sy = SWAP_XY ? ax : ay;
    if (INVERT_X) sx = -sx;
    if (INVERT_Y) sy = -sy;

    fax += 0.1f * (sx - fax);                   // low-pass filter
    fay += 0.1f * (sy - fay);
    gx = fax * GRAV;
    gy = fay * GRAV;

    float dx = ax - pax, dy = ay - pay, dz = az - paz;
    float jerk = sqrtf(dx * dx + dy * dy + dz * dz);
    pax = ax; pay = ay; paz = az;

    if (jerk > SHAKE_JERK_G && millis() - lastShake > SHAKE_COOLDOWN_MS) {
      lastShake = millis();
      doSplash(constrain(jerk, 0.5f, 2.5f));
    }

    if (debugPrint && millis() - lastDbg > 200) {
      lastDbg = millis();
      Serial.printf("ax=%.2f ay=%.2f az=%.2f  gx=%.1f gy=%.1f  jerk=%.2f\n", ax, ay, az, gx, gy, jerk);
    }
  }

  while (Serial.available()) {
    char c = Serial.read();
    if (c == 's') doSplash(1.5f);
    if (c == 'd') debugPrint = !debugPrint;
  }

  stepWater(dt * 0.5f);                         // two sub-steps = calmer, more stable water
  stepWater(dt * 0.5f);
  stepSpray(dt);
  render();
  FastLED.show();
}
