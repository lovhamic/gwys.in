# Shoot the Cockroach

A physical gun game using ESP32, MPU6050 accelerometer/gyroscope, and a push-button trigger. Move the real gun to aim on screen, press the physical trigger to shoot cockroaches!

## Overview

```
┌─────────────────┐     USB Serial     ┌──────────────────┐
│   PHYSICAL GUN  │ ─────────────────► │  COMPUTER GAME   │
│                 │                    │                  │
│  ┌───────────┐  │                    │  • Crosshair     │
│  │  MPU6050  │  │   DATA,ax,ay,az,   │  • Cockroaches   │
│  │ (Aiming)  │──┤   gx,gy,gz         │  • Score/Lives   │
│  └───────────┘  │                    │  • Levels        │
│                 │                    │                  │
│  ┌───────────┐  │                    │  Shoot cockroaches│
│  │ Trigger   │  │       SHOOT        │  before they     │
│  │ (Shoot)   │──┤                    │  escape!         │
│  └───────────┘  │                    │                  │
│                 │                    │                  │
│    ESP32        │                    │   Python/Pygame  │
└─────────────────┘                    └──────────────────┘
```

## Hardware Requirements

| Component | Quantity | Notes |
|-----------|----------|-------|
| ESP32 Development Board | 1 | ESP32 DevKit V1, NodeMCU-32S, or similar |
| MPU6050 Module | 1 | GY-521 breakout board |
| Push Button / Switch | 1 | Momentary push button |
| USB Cable | 1 | Data-capable (not charge-only) |
| Wires | Several | Jumper wires |
| Breadboard/Perfboard | 1 | For prototyping |
| Gun Enclosure | 1 | 3D printed, cardboard, PVC pipe, etc. |

## Wiring Diagram

```
MPU6050 (GY-521)          ESP32
┌──────────────┐          ┌──────────────┐
│ VCC  ────────┼─────────►│ 3.3V         │
│ GND  ────────┼─────────►│ GND          │
│ SDA  ────────┼─────────►│ GPIO 21 (SDA)│
│ SCL  ────────┼─────────►│ GPIO 22 (SCL)│
└──────────────┘          └──────────────┘

Push Button               ESP32
┌──────────────┐          ┌──────────────┐
│ One leg ─────┼─────────►│ GPIO 4       │
│ Other leg ───┼─────────►│ GND          │
└──────────────┘          └──────────────┘
```

### ESP32 Pin Configuration (Default)

| Function | ESP32 Pin | Notes |
|----------|-----------|-------|
| MPU6050 SDA | GPIO 21 | I2C Data (default) |
| MPU6050 SCL | GPIO 22 | I2C Clock (default) |
| Trigger Button | GPIO 4 | Active LOW with internal pullup |
| MPU6050 VCC | 3.3V | **NOT 5V!** |
| MPU6050 GND | GND | Common ground |

> **Important**: The MPU6050 is a 3.3V device. Do NOT connect VCC to 5V. The ESP32 GPIOs are also 3.3V logic.

### Changing Pins

Edit the top of `esp32/shoot_the_cockroach_esp32.ino`:

```cpp
#define TRIGGER_PIN 4        // Change trigger pin here
// I2C pins (SDA/SCL) are default ESP32 I2C pins
// Change with Wire.begin(SDA_PIN, SCL_PIN) in setup() if needed
```

## Software Installation

### 1. Arduino IDE Setup

1. Install [Arduino IDE](https://www.arduino.cc/en/software) (v1.8.19+ or v2.x)
2. Add ESP32 board support:
   - File → Preferences → Additional Boards Manager URLs:
     ```
     https://raw.githubusercontent.com/espressif/arduino-esp32/gh-pages/package_esp32_index.json
     ```
   - Tools → Board → Boards Manager → Search "esp32" → Install "esp32 by Espressif Systems"
3. Select your board: Tools → Board → ESP32 Arduino → [Your Board]
4. Select port: Tools → Port → [COM port]

### 2. Upload ESP32 Code

1. Open `esp32/shoot_the_cockroach_esp32.ino` in Arduino IDE
2. Verify wiring matches pin definitions
3. Click **Upload** (Ctrl+U)
4. Open Serial Monitor (115200 baud) - you should see `ESP32_READY`

### 3. Python Environment

```bash
# Option 1: Using pip
pip install -r requirements.txt

# Option 2: Manual install
pip install pygame pyserial
```

### 4. Find Serial Port

**Windows:**
1. Open Device Manager (Win+X → Device Manager)
2. Look under "Ports (COM & LPT)"
3. Find "Silicon Labs CP210x", "CH340", or "USB Serial"
4. Note the COM port (e.g., COM3, COM4)

**Linux/Mac:**
```bash
ls /dev/ttyUSB* /dev/ttyACM* /dev/tty.SLAB*
```

### 5. Configure Game

Edit `game/config.py` and set your serial port:

```python
SERIAL_PORT = "COM3"    # Windows
# SERIAL_PORT = "/dev/ttyUSB0"  # Linux
# SERIAL_PORT = "/dev/tty.SLAB_USBtoUART"  # Mac
```

The game also attempts auto-detection on startup.

## Running the Game

```bash
cd shoot-the-cockroach
python game/main.py
```

### Game Controls

| Key | Action |
|-----|--------|
| ENTER | Start game / Next level / Restart |
| C | Recalibrate MPU6050 (during gameplay) |
| ESC | Quit game |
| Physical Trigger | Shoot! |

### Without Hardware (Demo Mode)

If ESP32 is not connected, the game runs in demo mode:
- **Mouse** moves crosshair
- **Left Click** shoots

## Gameplay

### Levels

| Level | Cockroaches | Speed | Hitbox | Time Limit |
|-------|-------------|-------|--------|------------|
| 1 | 1 | Slow | Large | 8 seconds |
| 2 | 1 | Medium | Medium | 6 seconds |
| 3 | 1 | Fast | Small | 4.5 seconds |

### Scoring

- **Normal Hit**: +10 (L1), +15 (L2), +20 (L3)
- **Fast Hit** (under threshold): Bonus points!
- **Miss**: 0 points
- **Cockroach Escapes**: -1 Life

### Lives

- Start with **3 lives**
- Lose life when cockroach escapes
- Game Over at 0 lives

## Calibration

At game start and when pressing **C**:

1. **"CALIBRATING... Keep the gun still"**
2. Hold gun steady for ~3 seconds
3. **"CALIBRATION COMPLETE"**
4. Move gun to aim, press trigger to shoot

The calibration measures the MPU6050's resting values to remove drift.

## MPU6050 Aiming System

The game uses **gyroscope-based relative aiming**:

```
Gun rotates LEFT  → Crosshair moves LEFT
Gun rotates RIGHT → Crosshair moves RIGHT
Gun rotates UP    → Crosshair moves UP
Gun rotates DOWN  → Crosshair moves DOWN
```

### How It Works

1. **Gyroscope** measures angular velocity (deg/s)
2. **Integration** converts rotation → position change
3. **Deadzone** filters tiny vibrations
4. **Smoothing** prevents jitter
4. **Sensitivity** adjusts speed

### Tuning Sensitivity

Edit `game/config.py`:

```python
SENSITIVITY_X = 0.008   # Horizontal sensitivity
SENSITIVITY_Y = 0.008   # Vertical sensitivity
SMOOTHING_FACTOR = 0.15 # Lower = smoother, higher = responsive
DEADZONE = 50           # Ignore small movements
INVERT_X = False        # Flip horizontal
INVERT_Y = True         # Flip vertical
```

**Tips:**
- Increase sensitivity if crosshair moves too slow
- Decrease if too twitchy
- Increase smoothing if jittery
- Adjust deadzone if drift occurs

## Serial Protocol

### ESP32 → Computer

**Sensor Data (100Hz):**
```
DATA,ax,ay,az,gx,gy,gz
```
Example: `DATA,123,-456,16384,12,-8,5`

**Trigger Press:**
```
SHOOT
```

### Data Format

| Field | Description | Units |
|-------|-------------|-------|
| ax, ay, az | Accelerometer X,Y,Z | Raw LSB (±2g = 16384 LSB/g) |
| gx, gy, gz | Gyroscope X,Y,Z | Raw LSB (±250°/s = 131 LSB/°/s) |

The game only uses **gyroscope (gx, gy)** for aiming. Accelerometer data is transmitted but not used.

## Debug Mode

Enable in `config.py`:
```python
DEBUG_MODE = True
```

Shows:
- Raw sensor values
- Calibrated values
- Crosshair position
- Connection status
- FPS counter

## Troubleshooting

### ESP32 Not Detected
- Check USB cable (must support data)
- Install CP210x or CH340 drivers
- Try different USB port
- Press ESP32 BOOT button during upload if needed

### "ESP32 DISCONNECTED" in Game
- Check serial port in `config.py`
- Close Serial Monitor in Arduino IDE (locks port)
- Reconnect USB cable
- Press reset button on ESP32

### Crosshair Drifts / Moves on Its Own
- Recalibrate (press **C**)
- Increase `DEADZONE` in config
- Check MPU6050 wiring (loose connections cause noise)
- Ensure gun is still during calibration

### Crosshair Too Fast / Slow
- Adjust `SENSITIVITY_X` / `SENSITIVITY_Y`
- Check `INVERT_X` / `INVERT_Y` if axes are swapped

### Trigger Not Working
- Check button wiring (GPIO 4 to GND)
- Verify `TRIGGER_PIN` in ESP32 code
- Check debounce timing (`DEBOUNCE_MS = 50`)

### Multiple Shots Per Press
- Increase `DEBOUNCE_MS` in ESP32 code
- Check button hardware (add 10kΩ pullup if needed)

### Game Crashes / Freezes
- Check Python console for error messages
- Ensure all dependencies installed
- Try running with `python -v game/main.py` for verbose output

## Project Structure

```
shoot-the-cockroach/
│
├── esp32/
│   └── shoot_the_cockroach_esp32.ino    # ESP32 Arduino code
│
├── game/
│   ├── main.py                          # Entry point
│   ├── config.py                        # All configuration
│   ├── serial_controller.py             # Serial communication
│   ├── mpu6050_controller.py            # MPU6050 processing
│   ├── cockroach.py                     # Enemy logic
│   └── game.py                          # Game state/logic
│
├── assets/
│   ├── cockroach.png       (optional)
│   ├── shoot.wav           (optional)
│   └── background.png      (optional)
│
├── requirements.txt
└── README.md
```

## Customization

### Add Cockroach Image
Place `cockroach.png` (40x40px, transparent background) in `assets/`

### Add Sounds
Place `shoot.wav` and `hit.wav` in `assets/`

### Modify Levels
Edit `LEVEL_CONFIGS` in `config.py`:

```python
LEVEL_CONFIGS = [
    {"name": "Level 1", "speed_multiplier": 1.0, "hitbox_multiplier": 1.5, ...},
    {"name": "Level 2", "speed_multiplier": 1.5, "hitbox_multiplier": 1.2, ...},
    # Add more levels!
]
```

## Technical Details

### MPU6050 Register Configuration
- **Accelerometer**: ±2g range (16384 LSB/g)
- **Gyroscope**: ±250°/s range (131 LSB/°/s)
- **I2C Speed**: 400kHz
- **Sample Rate**: ~100Hz (10ms interval)

### Coordinate System
```
MPU6050 (on gun)          Screen
     +Z (up)                    ^
      |                         |
      |   +X (forward)   →   +X (right)
      |                         |
      +---- +Y (left)         +Y (down)
```

Gyro X (roll) → Vertical aim
Gyro Y (pitch) → Horizontal aim

### Smoothing Algorithm
Exponential moving average:
```
smooth = smooth + (target - smooth) * SMOOTHING_FACTOR
```

## License

MIT License - Feel free to use for educational projects!

## Credits

Created as a college hardware/software project demonstrating:
- ESP32 + MPU6050 sensor integration
- Real-time serial communication
- Game programming with Pygame
- Sensor fusion and signal processing basics

---

**Have fun shooting cockroaches!** 🪳🔫