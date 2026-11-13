# Wiring Guide — AI Robotic Arm (ESP32)

> Read this entire document before touching a single wire.
> One wrong power connection can destroy your ESP32.

---

## What You Need on Your Desk

| Component | Qty | What to Find |
|-----------|-----|-------------|
| ESP32-WROOM-32 DevKit | 1 | The blue board with micro-USB |
| MG996R Servo | 4 | Large, metal gear, red/orange/brown wires |
| SG90 Micro Servo | 1 | Small, plastic gear, same colored wires |
| HC-SR04 Ultrasonic | 1 | Two big cylinders on a blue PCB |
| ACS712 Current Sensor (5A) | 1 | Small module with screw terminals |
| WS2812B RGB LED Strip (16 pixels) | 1 | 16-LED NeoPixel ring or strip |
| 5V 6A Power Supply | 1 | Wall adapter with bare wires or DC barrel jack |
| Breadboard | 1 | 830 tie-points (white/blue) |
| Jumper Wires (Male-Male) | 30+ | Various colors |
| Jumper Wires (Male-Female) | 10+ | For servo signal connections |
| Resistors | 3x 1k, 2x 2k, 2x 10k | 1/4W through-hole |
| 1000uF Electrolytic Capacitor | 1 | 16V or 25V rated, any brand |
| Micro-USB Cable | 1 | For ESP32 programming |

---

## CRITICAL RULES (Read 3 Times)

| Rule | Why It Matters |
|------|---------------|
| **1. ESP32 5V pin != servo power** | ESP32 board 5V pin comes from USB (max ~500mA). 5 servos can draw 3-5A. The USB power supply will burn out or reboot. |
| **2. Servos need their own 5V rail** | Run a thick wire directly from your PSU to the servo power bus. |
| **3. Ground must be shared** | Connect PSU GND to ESP32 GND. Without this, signals have no reference and servos will jitter or not move. |
| **4. NEVER connect 5V logic to ESP32 GPIO** | ESP32 GPIO pins accept 3.3V maximum. The HC-SR04 Echo pin outputs 5V. You must use a voltage divider or the ESP32 will be damaged. |
| **5. Power OFF when wiring** | Only turn on the PSU after you have triple-checked every wire. |

---

## Step-by-Step Wiring Order

Wire in this exact order. Do not skip steps.

### Step 1: Prepare the Power Distribution

```
Your 5V PSU has two wires: RED (+5V) and BLACK (GND)

RED  (+5V) ---|--- Breadboard RED RAIL (top)    <- servo power bus
               |
BLACK (GND) ---|--- Breadboard BLUE RAIL (top)   <- servo ground bus
               |
               |--- Also connect to ESP32 GND pin  <- CRITICAL shared ground
```

**What to do:**
1. Plug your PSU into the wall socket (but keep the switch OFF if it has one).
2. Strip the PSU wires if they are bare.
3. Connect PSU RED (+5V) to the top RED rail of your breadboard.
4. Connect PSU BLACK (GND) to the top BLUE rail of your breadboard.
5. Run a wire from the top BLUE rail (GND) to an ESP32 GND pin (any of: GND pins near Vin, GND near D13, etc.).
6. Place the 1000uF capacitor across the red and blue rails of the breadboard (positive leg = red rail, negative leg = blue rail, marked with a stripe). This capacitor prevents voltage drops when servos start moving.

**Why this order:** You establish the power foundation first. Everything else connects to this.

---

### Step 2: Connect the Servos (Signal Wires Only)

**Servo Wire Colors (MG996R and SG90 are identical):**

| Wire Color | Purpose | Where It Goes |
|------------|---------|---------------|
| RED | Power (+5V) | Breadboard RED rail (top) -- NOT ESP32 |
| BROWN or BLACK | Ground (GND) | Breadboard BLUE rail (top) -- NOT ESP32 |
| ORANGE or YELLOW | Signal (PWM) | ESP32 GPIO pins |

**Connections:**

| Servo | Role | Signal Pin | Power Pin | Ground Pin |
|-------|------|-----------|-----------|------------|
| Servo 1 | Shoulder | ESP32 GPIO 13 | Breadboard RED rail | Breadboard BLUE rail |
| Servo 2 | Elbow | ESP32 GPIO 14 | Breadboard RED rail | Breadboard BLUE rail |
| Servo 3 | Wrist pitch | ESP32 GPIO 15 | Breadboard RED rail | Breadboard BLUE rail |
| Servo 4 | Gripper | ESP32 GPIO 16 | Breadboard RED rail | Breadboard BLUE rail |

> **Note:** GPIO 12 is freed — it was the base servo but is now used for the A4988 stepper ENABLE pin.

**What to do:**
1. For each servo, connect the RED wire to the breadboard red rail.
2. For each servo, connect the BROWN/BLACK wire to the breadboard blue rail.
3. For each servo, connect the ORANGE/YELLOW wire to the correct ESP32 GPIO using a male-female jumper wire.

**Visual Check:** Your breadboard should now have 4 red wires and 4 brown/black wires in the power rails. The ESP32 should have 4 orange/yellow wires going to GPIO 13, 14, 15, 16.

**DO NOT turn on the PSU yet.**

---

### Step 2B: Connect the A4988 Stepper Driver + NEMA 17 (Base Rotation)

> **This replaces the old base servo.** The A4988 drives a NEMA 17 stepper motor for precise 360° base rotation.

#### A4988 Module Pinout

```
A4988 Stepper Driver:
+------------------------------------------+
| VMOT | GND | 2B | 2A | 1A | 1B | VDD | GND |
|      |     |    |    |    |    |     |     |
| STEP | DIR |EN  |MS1 |MS2 |MS3 | RST | SLP |
+------------------------------------------+
```

#### Power Connections (HIGH CURRENT — Separate 12V Supply Required)

```
12V POWER SUPPLY (separate from servo PSU)
  │
  ├── RED (+12V) ──► A4988 VMOT
  │
  └── BLACK (GND) ──► A4988 GND ──► ALSO connect to Breadboard BLUE rail
                                        (MUST share ground with ESP32!)

NEMA 17 MOTOR WIRES → A4988:
  ├── Motor coil A1  → A4988 1A
  ├── Motor coil A2  → A4988 1B
  ├── Motor coil B1  → A4988 2A
  └── Motor coil B2  → A4988 2B

  (Wire colors vary by manufacturer — check your NEMA 17 datasheet.
   Usually: A1=Black, A2=Green, B1=Red, B2=Blue)
```

#### Signal Connections (to ESP32)

```
A4988 Pin    Connects To         Notes
---------    -----------         -----
STEP         ESP32 GPIO 26       Step pulse (HIGH = step)
DIR          ESP32 GPIO 27       Direction (HIGH = CW, LOW = CCW)
ENABLE       ESP32 GPIO 12       Active LOW (LOW = enabled, HIGH = disabled)
MS1          3.3V or HIGH        Microstepping: 1=full, 0=half
MS2          3.3V or HIGH        Microstepping: 1=full, 0=half
MS3          3.3V or FULL STEP   Microstepping control
RST          3.3V                Keep HIGH (not reset)
SLP          3.3V                Keep HIGH (not sleeping)
```

#### Microstepping Configuration (1/8 step recommended)

```
MS1    MS2    MS3    Resolution
HIGH   HIGH   LOW    1/8 step (1600 steps/rev)  ← RECOMMENDED
HIGH   LOW    LOW    1/4 step
LOW    HIGH   LOW    1/2 step
LOW    LOW    LOW    Full step (200 steps/rev)
HIGH   HIGH   HIGH   1/16 step
```

#### Current Limiting (IMPORTANT — Set before connecting motor!)

1. Do NOT connect the motor yet
2. Power the A4988 (12V to VMOT, 3.3V/5V to VDD)
3. Measure voltage at the current sense pin (between GND and the small pot on the A4988)
4. Adjust the pot with a small screwdriver until: Vref = Imax × 8 × Rsense
   - For NEMA 17 (1.5A rated): Vref ≈ 0.6V - 0.7V
   - For NEMA 17 (2.0A rated): Vref ≈ 0.8V - 1.0V
5. Now connect the motor

#### Step + Delay Formula

```
Full step:    200 steps/revolution
1/8 step:    1600 steps/revolution

Step delay = microseconds between step pulses
  - 800µs = moderate speed (~1 rotation in 1.3s at 1/8 step)
  - 500µs = faster (~1 rotation in 0.8s)
  - 1500µs = slow/precise

For 360° rotation at 1/8 microstepping:
  Steps needed = 1600
  At 800µs delay = 1600 × 800µs = 1.28 seconds for full rotation
```

---

### Step 3: Connect the HC-SR04 Ultrasonic Sensor

```
HC-SR04 Pins:
+---------------------------------+
| VCC   |  Trig   |  Echo   | GND |
+---------------------------------+
```

**WARNING: VCC and Echo both output 5V. The ECHO pin MUST go through a voltage divider before reaching ESP32.**

#### Voltage Divider Circuit (for ECHO -> ESP32)

```
HC-SR04 Echo pin ---|---[1k]---|--- ESP32 GPIO 5
                    |           |
                    |         [2k]
                    |           |
                    |           |--- GND
                    |
                    |---(Do NOT connect directly to ESP32!)
```

**How to build it on the breadboard:**
1. Place a 1k resistor between two breadboard holes (row A and row B).
2. Place a 2k resistor between one of those holes (row B) and the GND rail.
3. Connect HC-SR04 ECHO to the junction point (row B).
4. Connect the other end of the 1k (row A) to ESP32 GPIO 5.

**Full HC-SR04 Wiring:**

| HC-SR04 Pin | Connects To | Notes |
|-------------|-------------|-------|
| VCC | Breadboard RED rail (+5V) | Powers the sensor |
| Trig | ESP32 GPIO 17 | 3.3V output from ESP32 is fine for trigger |
| Echo | Voltage divider -> ESP32 GPIO 5 | MUST use divider! |
| GND | Breadboard BLUE rail (GND) | Common ground |

---

### Step 4: Connect the ACS712 Current Sensor

```
ACS712 Module Pins:
+----------------------------------------+
|  VCC  |  GND  |  OUT  |  IP+  |  IP-  |
+----------------------------------------+
```

The ACS712 measures current by sitting in series with the load. We put it in the servo power line so it can detect when all servos draw too much current (stall).

#### Wiring the Current Sensing Path (High Current)

```
PSU RED (+5V) --- ACS712 IP+ --- ACS712 IP- --- Breadboard RED rail
                     |
                     |  (The current flows through the chip)
                     |
```

**If your ACS712 has screw terminals:** Use a short wire from PSU RED to IP+, and another from IP- to the breadboard RED rail.

**If your ACS712 has pin headers:** You can use male-male jumper wires, but for the high-current path, thicker wire is better.

#### Wiring the Signal Path (Low Current)

The ACS712 output is 2.5V at 0A and goes up to ~3.4V at 5A. We use a voltage divider to scale it down for the ESP32 ADC.

```
ACS712 OUT pin ---|---[10k]---|--- ESP32 GPIO 34
                  |            |
                  |          [10k]
                  |            |
                  |            |--- GND
                  |
                  |---(Raw ACS712 output, ~2.5V-3.4V)
```

**Full ACS712 Wiring:**

| ACS712 Pin | Connects To | Notes |
|------------|-------------|-------|
| VCC | Breadboard RED rail (+5V) | Powers the sensor chip |
| GND | Breadboard BLUE rail (GND) | Common ground |
| OUT | Voltage divider -> ESP32 GPIO 34 | Divider: 10k + 10k |
| IP+ | PSU RED (+5V) | High current input |
| IP- | Breadboard RED rail | High current output to servos |

**Important:** The ACS712 VCC and GND are for the sensor electronics. The IP+ and IP- are the high-current path that goes to your servos. These two paths are electrically isolated.

---

### Step 5: Connect the WS2812B RGB LED Strip (16 Pixels — Personality Expressions)

```
WS2812B Strip Pinout (3 wires):
+---------------------------------+
|  VCC  |  DIN  |  GND   |
+---------------------------------+
```

| LED Pin | Connects To | Notes |
|---------|-------------|-------|
| VCC | Breadboard RED rail (+5V) | 16 LEDs can draw ~960mA at full white. Use 5V rail, NOT 3.3V |
| DIN | ESP32 GPIO 4 | Through a 220 resistor for protection |
| GND | Breadboard BLUE rail (GND) | Same ground as everything else |

**Why 5V, not 3.3V:** A single WS2812B works on 3.3V, but 16 LEDs need proper 5V power. A 220 ohm resistor on the data line protects the first LED's data input from the ESP32's 3.3V logic — the WS2812B interprets 3.3V as a valid logic HIGH, so it works without a level shifter.

```
ESP32 GPIO 4 ---[220]--- WS2812B DIN (first LED)
                        WS2812B VCC --- Breadboard RED rail (+5V)
                        WS2812B GND --- Breadboard BLUE rail (GND)
                        WS2812B DOUT --- (next LED DIN, wired internally in strip)
                        ... (16 LEDs daisy-chained internally)
```

**Power note:** At full brightness white, 16 WS2812B LEDs draw ~960mA (60mA x 16). Your 5V 6A PSU can handle this easily. If you notice brownouts when LEDs light up, add a 1000uF capacitor directly across the LED strip's VCC and GND pins.

---

### Step 6: ESP32 USB Power (For Programming Only)

```
Micro-USB cable --- ESP32 USB port
```

This powers the ESP32 logic (3.3V regulator on the board). When you upload code, the ESP32 runs from USB power. The servos are still on the PSU.

**Important:** When testing with USB only (no PSU), the ESP32 will try to drive the servos through its 5V pin, which will fail. Always have the PSU connected when servos should move.

---

### Step 7: Final Visual Inspection Checklist

Before powering on, verify every single connection:

| Check | What to See |
|-------|-------------|
| [ ] 5V PSU RED -> Breadboard RED rail | One thick red wire |
| [ ] 5V PSU BLACK -> Breadboard BLUE rail | One thick black wire |
| [ ] Breadboard BLUE rail -> ESP32 GND | One wire linking grounds |
| [ ] 1000uF cap across RED/BLUE rails | Capacitor installed, polarity correct |
| [ ] 4 servo RED wires -> RED rail | 4 red wires in the rail |
| [ ] 4 servo BROWN wires -> BLUE rail | 4 brown/black wires in the rail |
| [ ] Shoulder servo orange -> GPIO 13 | One wire |
| [ ] Elbow servo orange -> GPIO 14 | One wire |
| [ ] Wrist servo orange -> GPIO 15 | One wire |
| [ ] Gripper servo orange -> GPIO 16 | One wire |
| [ ] A4988 VMOT -> 12V PSU RED | Stepper motor power |
| [ ] A4988 GND -> 12V PSU BLACK + Breadboard BLUE rail | Shared ground! |
| [ ] A4988 STEP -> ESP32 GPIO 26 | Step signal |
| [ ] A4988 DIR -> ESP32 GPIO 27 | Direction signal |
| [ ] A4988 ENABLE -> ESP32 GPIO 12 | Enable (active low) |
| [ ] A4988 MS1/MS2 -> 3.3V | 1/8 microstepping |
| [ ] A4988 MS3 -> GND | 1/8 microstepping |
| [ ] A4988 RST/SLP -> 3.3V | Not reset/sleep |
| [ ] NEMA 17 -> A4988 motor terminals | 4 wires (check datasheet) |
| [ ] HC-SR04 VCC -> RED rail | One wire |
| [ ] HC-SR04 GND -> BLUE rail | One wire |
| [ ] HC-SR04 Trig -> GPIO 17 | One wire |
| [ ] HC-SR04 Echo -> 1k -> 2k -> GND + GPIO 5 | Voltage divider built correctly |
| [ ] ACS712 VCC -> RED rail | One wire |
| [ ] ACS712 GND -> BLUE rail | One wire |
| [ ] ACS712 OUT -> 10k -> 10k -> GND + GPIO 34 | Voltage divider built correctly |
| [ ] ACS712 IP+ -> PSU RED | High current path |
| [ ] ACS712 IP- -> Breadboard RED rail | High current path |
| [ ] LED VCC -> ESP32 3.3V | One wire |
| [ ] LED GND -> ESP32 GND | One wire |
| [ ] LED DIN -> 220 -> GPIO 4 | Resistor inline |
| [ ] ESP32 USB -> Computer | For programming |
| [ ] 12V PSU -> Wall outlet | Stepper motor power (separate from servo PSU) |

**If any check fails, fix it before powering on.**

---

## Power-On Sequence (First Time)

1. Do NOT connect the ESP32 USB yet.
2. Turn on the 5V PSU (servos).
3. Turn on the 12V PSU (stepper motor).
4. Listen for any crackling or smell of burning — if so, IMMEDIATELY turn off and recheck wiring.
5. Measure the breadboard RED rail with a multimeter — should read ~5V.
6. Measure the breadboard BLUE rail — should read 0V (GND).
7. Measure A4988 VMOT — should read ~12V.
8. Now connect the ESP32 USB to your computer.
9. The ESP32 should power up (blue LED on GPIO 2 might blink if code is already loaded).
10. Open Arduino IDE, select the correct COM port, and upload the test code.

---

## Common Mistakes & Fixes

| Symptom | Cause | Fix |
|---------|-------|-----|
| ESP32 gets hot / smoke | 5V on a GPIO pin | Check HC-SR04 Echo voltage divider |
| Servos do not move | No shared ground | Add wire from breadboard GND to ESP32 GND |
| Servos jitter randomly | Weak power supply | Your PSU cannot supply enough current. Upgrade to 6A+ |
| Servos move once then ESP32 reboots | USB power trying to power servos | Servo RED wires must go to PSU, not ESP32 |
| Stepper motor vibrates but doesn't spin | A4988 not enabled or wrong wiring | Check ENABLE pin (GPIO 12, active LOW), check motor wires |
| Stepper motor overheats | Current limit too high | Adjust A4988 pot to reduce Vref (see Step 2B) |
| Stepper motor skips steps | Acceleration too fast or current too low | Increase STEPPER_STEP_DELAY_US in config.h, check current limit |
| HC-SR04 always reads 0 | Echo not connected through divider | Check voltage divider wiring |
| Current sensor reads garbage | Wrong divider or wrong ADC attenuation | Check ACS712 OUT divider, adjust code calibration |
| LED does not light | Wrong power voltage | Single WS2812B needs 3.3V or 5V depending on module |
| ESP32 will not upload | Wrong COM port or boot button | Hold BOOT, click Upload, release when Connecting... appears |

---

## Arduino IDE Library Installation

Before uploading code, install these libraries via Sketch -> Include Library -> Manage Libraries...

| Library | Author | Search Term |
|---------|--------|-------------|
| ArduinoWebsockets | Gil Maimon | ArduinoWebsockets |
| ArduinoJson | Benoit Blanchon | ArduinoJson |
| Adafruit NeoPixel | Adafruit | Adafruit NeoPixel |

---

## Next Step

Once wiring is complete and verified, upload the AI_Robot_Arm.ino firmware.

See the firmware folder for the code.
