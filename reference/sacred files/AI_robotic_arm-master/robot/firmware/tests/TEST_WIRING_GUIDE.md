# Hardware Test Wiring Guide

> Run these tests **one at a time, in order.** Each test is isolated — you only wire what that specific test needs.

---

## General Rules (For ALL Tests)

| Rule | Why |
|------|-----|
| **Power OFF when wiring** | Prevents shorts while plugging/unplugging |
| **USB powers ESP32 logic only** | Never rely on USB to power motors or multiple LEDs |
| **Shared ground is mandatory** | Every component's GND must connect to ESP32 GND somehow |
| **Check your breadboard rails** | Many breadboards split the power rails in the middle — bridge them with a jumper if needed |

---

## Test 1: Onboard LED + Serial

### What You Need
- ESP32-WROOM-32 DevKit
- Micro-USB cable
- Your PC with Arduino IDE

### Wiring
```
  NOTHING TO WIRE.
  Just plug the ESP32 into your PC via USB.
```

### Steps
1. Open `firmware/tests/test_01_led_serial/test_01_led_serial.ino` in Arduino IDE
2. Select Board: **ESP32 Dev Module**
3. Select the correct COM port
4. Click **Upload**
5. Open Serial Monitor (Tools → Serial Monitor) at **115200 baud**
6. You should see text AND the blue onboard LED should blink every 500ms

### Expected Output
```
========================================
  TEST 01: Onboard LED + Serial
========================================

[PASS] If you can read this, Serial works!
[INFO] Onboard LED (GPIO 2) should blink every 500ms

Starting blink loop...
[LED] ON
[LED] OFF
[LED] ON
...
```

### PASS Criteria
- [ ] Text appears in Serial Monitor
- [ ] Onboard blue LED blinks on/off every 500ms

### FAIL? Check:
- Serial Monitor baud rate is **115200** (not 9600)
- Correct COM port selected
- Try pressing ESP32 **EN** (reset) button

---

## Test 2: Servo Sweep

### What You Need
- ESP32 (still on USB)
- **ONE** servo (MG996R or SG90)
- 5V PSU
- Breadboard
- 1000µF capacitor (optional but recommended)
- Male-to-female jumper wires (for servo signal)
- Male-to-male jumper wires (for power)

### Wiring Diagram

```
  POWER SUPPLY (5V 6A wall adapter)
  ┌─────────────────────────────────────┐
  │  RED (+5V)                          │─────┬──→ Breadboard RED rail (top)
  │  BLACK (GND)                        │─────┼──→ Breadboard BLUE rail (top)
  └─────────────────────────────────────┘     │
                                              │
  BREADBOARD                                  │
  ┌───────────────────────────────────────────┤
  │  RED rail (+5V)                           │
  │  │                                        │
  │  ├──→ 1000µF capacitor (+ leg)            │
  │  │                                        │
  │  ├──→ Servo RED wire                      │
  │  │                                        │
  │  ├──→ (more servos later)                 │
  │                                           │
  │  BLUE rail (GND)                          │
  │  │                                        │
  │  ├──→ 1000µF capacitor (- leg, striped)   │
  │  │                                        │
  │  ├──→ Servo BROWN wire                    │
  │  │                                        │
  │  ├──→ ESP32 GND pin                       │←── IMPORTANT!
  │                                           │
  └───────────────────────────────────────────┘

  SERVO (MG996R or SG90)
  ┌────────────────────────────────────────┐
  │  RED   ─────→ Breadboard RED rail      │  ← Power from PSU
  │  BROWN ─────→ Breadboard BLUE rail     │  ← Ground
  │  ORANGE ────→ ESP32 GPIO 12            │  ← Signal (PWM)
  └────────────────────────────────────────┘
        │
        │  Use male-to-female jumper for signal wire
        └──→ GPIO 12 on ESP32

  ESP32 (USB to PC)
  ┌────────────────────────────────────────┐
  │  GND pin  ──→ Breadboard BLUE rail     │  ← SHARED GROUND
  │  GPIO 12  ←── Servo ORANGE wire        │
  │  USB     ───→ Your PC                  │
  └────────────────────────────────────────┘
```

### Steps
1. **Power OFF the PSU** (unplug from wall or turn off switch)
2. Connect PSU RED to breadboard RED rail
3. Connect PSU BLACK to breadboard BLUE rail
4. Place 1000µF capacitor across RED and BLUE rails (+ to red, - to blue with stripe)
5. Connect breadboard BLUE rail to ESP32 **GND** pin
6. Connect servo RED to breadboard RED rail
7. Connect servo BROWN to breadboard BLUE rail
8. Connect servo ORANGE to ESP32 **GPIO 12** (use male-to-female jumper)
9. **Double-check:** No servo wire goes to ESP32 5V pin
10. Turn ON the PSU
11. Upload `test_02_servo_sweep`
12. Open Serial Monitor at 115200 baud

### Expected Output
```
========================================
  TEST 02: Servo Sweep
========================================

[Servo] Angle: 0 deg | Pulse: 544.0us | Duty: 1783
[Servo] Angle: 1 deg | Pulse: 554.3us | Duty: 1817
...
```

The servo should slowly sweep from 0° to 180° and back.

### PASS Criteria
- [ ] Servo moves smoothly 0° → 180° → 0°
- [ ] No jitter, no buzzing, no ESP32 reboot
- [ ] Serial shows angle and duty values

### FAIL? Check:
| Symptom | Fix |
|---------|-----|
| Servo doesn't move at all | Check PSU is ON, shared ground wire exists, servo plugged in correctly |
| Servo twitches once then stops | PSU too weak — upgrade to 6A+ |
| ESP32 reboots when servo moves | Servo RED wire is on ESP32 5V pin — move it to breadboard RED rail |
| Servo buzzes but doesn't move | Not enough current — check PSU rating |
| Servo gets hot | It's stalled — remove mechanical load |

---

## Test 3: HC-SR04 Ultrasonic Sensor

### What You Need
- ESP32 (still on USB)
- HC-SR04 ultrasonic sensor
- Breadboard
- 1x 1kΩ resistor
- 1x 2kΩ resistor
- Male-to-male jumper wires

### Wiring Diagram

```
  HC-SR04 SENSOR
  ┌─────────────────────────────────────────┐
  │  VCC  ─────→ Breadboard RED rail (+5V)  │  ← Sensor power
  │  GND  ─────→ Breadboard BLUE rail (GND) │  ← Ground
  │  TRIG ─────→ ESP32 GPIO 17              │  ← Trigger (3.3V output OK)
  │  ECHO ─────→ Voltage Divider            │  ← MUST drop 5V to 3.3V!
  └─────────────────────────────────────────┘

  VOLTAGE DIVIDER (on breadboard)
  ┌─────────────────────────────────────────┐
  │                                         │
  │  HC-SR04 ECHO ──[1kΩ]──┬──[2kΩ]── GND   │
  │                        │                │
  │                        └──→ ESP32 GPIO 5 │  ← ~3.3V here, safe!
  │                                         │
  └─────────────────────────────────────────┘

  How the divider works:
    ECHO outputs 5V when echo received.
    The two resistors split it: Vout = 5V * (2k / (1k+2k)) = 3.33V
    ESP32 GPIO 5 sees 3.3V — safe!

  ESP32
  ┌─────────────────────────────────────────┐
  │  GND  ───→ Breadboard BLUE rail         │
  │  GPIO 17 ←── HC-SR04 TRIG               │
  │  GPIO 5  ←── Divider junction (1k+2k)   │
  │  USB     ───→ PC                         │
  └─────────────────────────────────────────┘
```

### Building the Voltage Divider on Breadboard

```
  Breadboard layout (top view):

      a   b   c   d   e   f   g   h   i   j
    ┌───┬───┬───┬───┬───┬───┬───┬───┬───┬───┐
  1 │ VCC│   │   │1kΩ│   │   │2kΩ│   │   │GND│  ← Rails at top
    ├───┼───┼───┼───┼───┼───┼───┼───┼───┼───┤
  2 │    │   │   │●  │   │●  │●  │   │   │   │  ● = connection points
    ├───┼───┼───┼───┼───┼───┼───┼───┼───┼───┤
  3 │    │   │   │   │   │   │   │   │   │   │
    └───┴───┴───┴───┴───┴───┴───┴───┴───┴───┘

  Connections:
    - 1kΩ between holes d2 and f2
    - 2kΩ between holes f2 and h2
    - HC-SR04 ECHO → d2
    - ESP32 GPIO 5 → f2 (the junction)
    - h2 → Breadboard GND rail
```

### Steps
1. Power OFF everything
2. Wire HC-SR04 VCC to breadboard RED rail (or PSU +5V)
3. Wire HC-SR04 GND to breadboard BLUE rail
4. Build voltage divider:
   - Place 1kΩ resistor on breadboard
   - Place 2kΩ resistor in series with it
   - Junction point (between resistors) goes to ESP32 GPIO 5
   - Free end of 2kΩ goes to GND
   - Free end of 1kΩ goes to HC-SR04 ECHO
5. Wire HC-SR04 TRIG to ESP32 GPIO 17
6. Wire ESP32 GND to breadboard BLUE rail
7. Power ON (PSU + USB)
8. Upload `test_03_ultrasonic`
9. Open Serial Monitor at 115200 baud

### Expected Output
```
========================================
  TEST 03: HC-SR04 Ultrasonic Sensor
========================================

[Ultrasonic] Duration: 1376 us | Distance: 23.6 cm
[Ultrasonic] Duration: 1378 us | Distance: 23.6 cm
[Ultrasonic] Duration: 680 us | Distance: 11.7 cm   <- hand moved closer
```

### PASS Criteria
- [ ] Distance readings appear in Serial Monitor
- [ ] Value changes when you move your hand in front of sensor
- [ ] No "Out of range" messages when object is within 2 meters
- [ ] ESP32 does not get hot or reboot

### FAIL? Check:
| Symptom | Fix |
|---------|-----|
| Always "Out of range" | Sensor is pointed at open space — point at a wall or your hand |
| Always reads 0 | ECHO pin wired directly to GPIO (no divider) — ESP32 GPIO is damaged. Use a different GPIO and ADD the divider |
| Random garbage values | Loose connection in divider — press resistors firmly into breadboard |
| ESP32 gets warm | 5V is going directly to a GPIO — check divider wiring immediately |

---

## Test 4: ACS712 Current Sensor

### What You Need
- ESP32 (still on USB)
- ACS712-5A module
- Breadboard
- 2x 10kΩ resistors
- Male-to-male jumper wires
- (Optional) A running servo or load to measure

### Wiring Diagram

```
  ACS712 MODULE
  ┌─────────────────────────────────────────┐
  │  VCC ─────→ Breadboard RED rail (+5V)   │  ← Powers sensor chip
  │  GND ─────→ Breadboard BLUE rail (GND)  │  ← Ground
  │  OUT ─────→ Voltage Divider ──→ GPIO 34 │  ← Signal (needs divider)
  │  IP+ ─────→ PSU RED (+5V)               │  ← HIGH CURRENT INPUT
  │  IP- ─────→ Breadboard RED rail         │  ← HIGH CURRENT OUTPUT
  └─────────────────────────────────────────┘
               ↑
               │  Current flows through the chip from IP+ to IP-
               │  (This is where servo power runs through)

  VOLTAGE DIVIDER (for ACS712 OUT)
  ┌─────────────────────────────────────────┐
  │                                         │
  │  ACS712 OUT ──[10kΩ]──┬──[10kΩ]── GND  │
  │                       │                │
  │                       └──→ GPIO 34     │  ← ~1.65V at 0A
  │                                         │
  └─────────────────────────────────────────┘

  ESP32
  ┌─────────────────────────────────────────┐
  │  GND  ───→ Breadboard BLUE rail         │
  │  GPIO 34 ←── Divider junction           │
  │  USB     ───→ PC                         │
  └─────────────────────────────────────────┘

  OPTIONAL: Put a load through IP+/IP-
  ┌─────────────────────────────────────────┐
  │  PSU RED ──→ ACS712 IP+                 │
  │  ACS712 IP- ──→ Servo RED wire          │  ← Current measured here
  │  Servo BROWN ──→ PSU GND                │
  └─────────────────────────────────────────┘
```

### Steps
1. Power OFF everything
2. Wire ACS712 VCC to breadboard RED rail (+5V)
3. Wire ACS712 GND to breadboard BLUE rail (GND)
4. Build voltage divider:
   - Place 10kΩ resistor on breadboard
   - Place second 10kΩ in series
   - Junction → ESP32 GPIO 34
   - Free end → GND
   - Other free end → ACS712 OUT
5. Wire ESP32 GND to breadboard BLUE rail
6. (Optional) Route servo power through IP+/IP- for a real load test
7. Power ON
8. Upload `test_04_current_sensor`
9. Open Serial Monitor at 115200 baud

### Expected Output (NO load connected)
```
========================================
  TEST 04: ACS712 Current Sensor
========================================

[Current] Raw ADC: 2047 | Pin: 1.65V | ACS712: 3.30V | Current: 0.000A
[Current] Raw ADC: 2048 | Pin: 1.65V | ACS712: 3.30V | Current: 0.000A
```

### Expected Output (WITH servo running)
```
[Current] Raw ADC: 2150 | Pin: 1.73V | ACS712: 3.46V | Current: 0.432A
[Current] Raw ADC: 2500 | Pin: 2.01V | ACS712: 4.02V | Current: 1.730A
```

### PASS Criteria
- [ ] Raw ADC value is around 2000-2100 with no load (midpoint of 12-bit ADC)
- [ ] Pin voltage is around 1.6-1.7V
- [ ] Calculated ACS712 voltage is around 3.2-3.4V
- [ ] Current reads near 0A with no load
- [ ] Current increases when a servo is running

### FAIL? Check:
| Symptom | Fix |
|---------|-----|
| Raw ADC = 0 | GPIO 34 not connected — check wire |
| Raw ADC = 4095 | ACS712 OUT is floating or shorted to VCC |
| Current reads negative large number | Swap the two wires going to IP+ and IP- |
| Values jump around wildly | Noisy power supply — add more capacitance |

---

## Test 5: WS2812B RGB LED

### What You Need
- ESP32 (still on USB)
- 1x WS2812B LED (single pixel module or bare chip on breakout)
- 1x 220Ω resistor
- 3x Male-to-male jumper wires

### Wiring Diagram

```
  WS2812B LED (single pixel module)
  ┌─────────────────────────────────────────┐
  │                                         │
  │  VCC ─────→ ESP32 3.3V pin              │  ← Power (single pixel OK on 3.3V)
  │  GND ─────→ ESP32 GND pin               │  ← Ground
  │  DIN ─────→ [220Ω] ──→ ESP32 GPIO 4     │  ← Data (through resistor)
  │                                         │
  └─────────────────────────────────────────┘

  CONNECTION:
  ESP32 GPIO 4 ──[220Ω resistor]──→ LED DIN
  ESP32 3.3V   ───────────────────→ LED VCC
  ESP32 GND    ───────────────────→ LED GND
```

### Important: Check Your LED Module Pinout

WS2812B modules come in different layouts. Common ones:

**Type A: 3-pin module (most common)**
```
  ┌─────┬─────┬─────┐
  │ DIN │ VCC │ GND │   ← Check silkscreen on your module!
  └─────┴─────┴─────┘
```

**Type B: 4-pin bare chip**
```
  ┌─────────────┐
  │  VSS │  VDD │    VSS = GND, VDD = 5V (or 3.3V), DIN = data in
  │  DOUT│  DIN │    DOUT not used for single LED
  └─────────────┘
```

**If your LED has 4 pins:** Only use VCC, GND, and DIN. Leave DOUT unconnected.

### Steps
1. Power OFF
2. Identify your LED's pins (check silkscreen or datasheet)
3. Connect LED VCC to ESP32 **3.3V** pin
4. Connect LED GND to ESP32 **GND** pin
5. Connect LED DIN to one end of 220Ω resistor
6. Connect other end of resistor to ESP32 **GPIO 4**
7. Power ON (USB only)
8. Upload `test_05_rgb_led`
9. Open Serial Monitor at 115200 baud

### Expected Output
```
========================================
  TEST 05: WS2812B RGB LED
========================================

Wire LED with 220 ohm resistor on DIN!

[LED] Color: RED
[LED] Color: GREEN
[LED] Color: BLUE
...
```

The LED should change color every second.

### PASS Criteria
- [ ] LED lights up in different colors
- [ ] Colors cycle: red → green → blue → cyan → magenta → yellow → white → off

### FAIL? Check:
| Symptom | Fix |
|---------|-----|
| LED completely dark | Try swapping VCC and GND — you may have them reversed |
| LED stuck on one color | DIN might be on wrong pin — try other pins on the module |
| LED flickers random colors | 220Ω resistor is missing — add it |
| LED very dim | Increase brightness in code: `strip.setBrightness(255)` |
| LED gets hot | You connected 5V to a 3.3V-only module — disconnect immediately |

---

## Test 6: WiFi Connection

### What You Need
- ESP32 (still on USB)
- Your home WiFi credentials

### BEFORE Uploading — Edit the Code

Open `test_06_wifi.ino` and change these two lines:

```cpp
const char* WIFI_SSID = "YOUR_WIFI_SSID";          // <- YOUR WiFi NAME
const char* WIFI_PASSWORD = "YOUR_WIFI_PASSWORD";  // <- YOUR WiFi PASSWORD
```

**IMPORTANT:**
- ESP32 only supports **2.4GHz WiFi**. It will NOT connect to 5GHz networks.
- Make sure your router has a 2.4GHz band enabled.
- Guest networks with captive portals (hotels, airports) will NOT work.

### Wiring
```
  NOTHING TO WIRE.
  Just ESP32 on USB.
```

### Steps
1. Edit the WiFi credentials in the code
2. Upload `test_06_wifi`
3. Open Serial Monitor at 115200 baud

### Expected Output
```
========================================
  TEST 06: WiFi Connection
========================================

[WiFi] Connecting to YourWiFiName.....................
[PASS] WiFi connected!
[WiFi] IP Address: 192.168.1.105
[WiFi] Signal Strength (RSSI): -42 dBm

Note this IP address. The ESP32 will use it.
```

### PASS Criteria
- [ ] "WiFi connected!" appears
- [ ] IP address is assigned (e.g., 192.168.x.x)
- [ ] RSSI is reasonable (-30 to -70 dBm)

### FAIL? Check:
| Symptom | Fix |
|---------|-----|
| "Could not connect to WiFi" | Wrong password, or 5GHz only network, or WiFi is too far |
| No networks found | ESP32 antenna issue — try different ESP32 board |
| Keeps disconnecting | Weak signal — move ESP32 closer to router |

---

## Test 7: WebSocket Connection

### What You Need
- ESP32 (still on USB)
- Your PC running the backend server
- Your PC's local IP address

### BEFORE Uploading — Edit the Code

Open `test_07_websocket.ino` and change THREE lines:

```cpp
const char* WIFI_SSID = "YOUR_WIFI_SSID";
const char* WIFI_PASSWORD = "YOUR_WIFI_PASSWORD";
const char* SERVER_HOST = "192.168.1.100";  // <- YOUR PC'S IP (from ipconfig)
```

### Finding Your PC's IP Address

**Windows:**
1. Press `Win + R`, type `cmd`, press Enter
2. Type: `ipconfig`
3. Look for "IPv4 Address" under your WiFi adapter
4. It looks like: `192.168.1.100` or `10.0.0.5`

**Example output:**
```
Wireless LAN adapter Wi-Fi:
   IPv4 Address. . . . . . . . . . . : 192.168.1.105
   Subnet Mask . . . . . . . . . . . : 255.255.255.0
```

### BEFORE Uploading — Start the Backend Server

Open a terminal on your PC and run:
```bash
cd ai_backend
python server.py
```

Leave it running. You should see:
```
🤖 AI Robotic Arm Backend Started
   Dashboard: http://localhost:8000
```

### Wiring
```
  NOTHING TO WIRE.
  Just ESP32 on USB.
  Your PC runs the server.
```

### Steps
1. Start the backend server on your PC (keep it running)
2. Edit WiFi + server IP in the test code
3. Upload `test_07_websocket`
4. Open Serial Monitor at 115200 baud
5. Open browser to `http://localhost:8000` (on your PC)

### Expected Serial Output
```
========================================
  TEST 07: WebSocket Connection
========================================

[WiFi] Connecting to YourWiFiName.....................
[WiFi] Connected! IP: 192.168.1.106
[WS] Connecting to ws://192.168.1.100:8000/ws/esp32
[PASS] WebSocket connected!
[INFO] Check dashboard at http://localhost:8000
[WS] TX State sent
[WS] TX State sent
...
```

### Expected Dashboard
- Open `http://localhost:8000` in your browser
- You should see: **ESP32 Status: Connected**
- Joint angle gauges should show values
- Distance and current sensors should show readings

### PASS Criteria
- [ ] WebSocket "Connected" message in Serial Monitor
- [ ] Dashboard shows "ESP32: Connected"
- [ ] Dashboard shows live joint angles
- [ ] Sending a command from dashboard shows response

### FAIL? Check:
| Symptom | Fix |
|---------|-----|
| "WebSocket connection failed" | Server not running — start `python server.py` |
| | Wrong IP address — re-check with `ipconfig` |
| | PC and ESP32 not on same WiFi network |
| | Windows Firewall blocking port 8000 — add exception |
| "WiFi connected but WS fails" | Check IP address again — it may have changed |
| Dashboard shows no data | WebSocket not connected — check Serial Monitor |

---

## Complete Wiring Reference (All Components Together)

Once all individual tests pass, this is your final wiring for the full arm:

```
  POWER SUPPLY (5V 6A)
  ┌──────────────────────────────────────────────┐
  │  RED (+5V)                                   │──┬──→ Breadboard RED rail
  │  BLACK (GND)                                 │──┼──→ Breadboard BLUE rail
  └──────────────────────────────────────────────┘  │
                                                    │
  BREADBOARD                                        │
  ┌─────────────────────────────────────────────────┤
  │  RED rail (+5V)                                 │
  │  ├──→ 1000µF cap (+)                            │
  │  ├──→ ACS712 IP-                                │
  │  ├──→ 5x Servo RED wires                        │
  │  └──→ HC-SR04 VCC                               │
  │                                                 │
  │  BLUE rail (GND)                                │
  │  ├──→ 1000µF cap (-)                            │
  │  ├──→ ESP32 GND (shared!)                       │
  │  ├──→ 5x Servo BROWN wires                      │
  │  ├──→ HC-SR04 GND                               │
  │  ├──→ ACS712 GND                                │
  │  ├──→ LED GND                                   │
  │  └──→ Voltage divider GNDs                      │
  │                                                 │
  │  VOLTAGE DIVIDERS (built on breadboard)         │
  │  ├── HC-SR04 ECHO: [1k]--+--[2k]--GND          │
  │  │                        └──→ GPIO 5           │
  │  └── ACS712 OUT:    [10k]-+--[10k]-GND         │
  │                           └──→ GPIO 34          │
  │                                                 │
  └─────────────────────────────────────────────────┘

  ACS712 (in series with servo power)
  ┌────────────────────────────────────────┐
  │  IP+ ──→ PSU RED (+5V)                 │
  │  IP- ──→ Breadboard RED rail           │
  │  VCC ──→ Breadboard RED rail           │
  │  GND ──→ Breadboard BLUE rail          │
  │  OUT ──→ Voltage divider → GPIO 34     │
  └────────────────────────────────────────┘

  ESP32-WROOM-32
  ┌────────────────────────────────────────────────┐
  │  GND      ──→ Breadboard BLUE rail             │
  │  3.3V     ──→ LED VCC                          │
  │  GPIO 2   ──→ Onboard LED (internal)           │
  │  GPIO 4   ──→ 220Ω ──→ LED DIN                 │
  │  GPIO 5   ←── HC-SR04 ECHO (through divider)   │
  │  GPIO 12  ──→ Servo 1 (Base)                   │
  │  GPIO 13  ──→ Servo 2 (Shoulder)               │
  │  GPIO 14  ──→ Servo 3 (Elbow)                  │
  │  GPIO 15  ──→ Servo 4 (Wrist)                  │
  │  GPIO 16  ──→ Servo 5 (Gripper)                │
  │  GPIO 17  ──→ HC-SR04 TRIG                     │
  │  GPIO 34  ←── ACS712 OUT (through divider)     │
  │  USB      ──→ Your PC                          │
  └────────────────────────────────────────────────┘

  5 SERVOS (MG996R x4, SG90 x1)
  ┌────────────────────────────────────────┐
  │  All RED   ──→ Breadboard RED rail     │
  │  All BROWN ──→ Breadboard BLUE rail    │
  │  Orange S1 ──→ GPIO 12  (Base)         │
  │  Orange S2 ──→ GPIO 13  (Shoulder)     │
  │  Orange S3 ──→ GPIO 14  (Elbow)        │
  │  Orange S4 ──→ GPIO 15  (Wrist)        │
  │  Orange S5 ──→ GPIO 16  (Gripper)      │
  └────────────────────────────────────────┘

  HC-SR04
  ┌────────────────────────────────────────┐
  │  VCC  ──→ Breadboard RED rail          │
  │  GND  ──→ Breadboard BLUE rail         │
  │  TRIG ──→ GPIO 17                      │
  │  ECHO ──→ [1k+2k divider] → GPIO 5     │
  └────────────────────────────────────────┘

  WS2812B LED
  ┌────────────────────────────────────────┐
  │  VCC  ──→ ESP32 3.3V                   │
  │  GND  ──→ ESP32 GND                    │
  │  DIN  ──→ 220Ω ──→ GPIO 4              │
  └────────────────────────────────────────┘
```

---

## Troubleshooting Quick Reference

| Problem | Most Likely Cause | Fix |
|---------|-------------------|-----|
| ESP32 won't upload | Wrong COM port / BOOT button not pressed | Hold BOOT, click Upload, release when "Connecting..." |
| Serial Monitor shows garbage | Wrong baud rate | Set to **115200** |
| Servos don't move | No shared ground | Add wire from breadboard GND to ESP32 GND |
| ESP32 reboots on servo start | Servos powered from ESP32 5V pin | Move servo RED wires to PSU |
| HC-SR04 always 0 / ESP32 hot | No voltage divider on ECHO | Add 1k+2k divider immediately |
| Current sensor reads nonsense | Wrong divider values | Use 10k+10k for ACS712 |
| LED doesn't light | Reversed VCC/GND | Swap them |
| WiFi won't connect | Wrong password or 5GHz network | Use 2.4GHz network |
| WebSocket fails | Wrong PC IP / firewall / server not running | Check ipconfig, start server, open firewall |

---

*Run Test 1 first. No exceptions.*
