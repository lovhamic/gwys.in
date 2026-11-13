# Architecture Discussion — AI Robotic Arm (Production)

> All 7 hardware tests PASSED. Now we design the final system.
> 
> **Your job:** Read this, ask questions, change anything you don't like, and say **APPROVED** when you're happy.

---

## 1. Final Hardware Wiring (All Components Together)

Since every component works individually, here's the unified wiring diagram for your final robot:

```
  5V 6A POWER SUPPLY
  +-------------------------------------------------+
  |  RED (+5V)                                       |---> Breadboard RED rail
  |  BLACK (GND)                                     |---> Breadboard BLUE rail
  +-------------------------------------------------+

  BREADBOARD POWER RAILS
  +---------------------------------------------------------+
  |  RED rail (+5V)                                         |
  |  +-- 1000uF cap (+)                                    |
  |  +-- 4x MG996R servo RED                               |
  |  +-- 1x SG90 servo RED                                  |
  |  +-- HC-SR04 VCC                                        |
  |  +-- ACS712 VCC                                         |
  |  +-- ACS712 IP- (from high current path)                |
  |                                                         |
  |  BLUE rail (GND)                                        |
  |  +-- 1000uF cap (-)                                     |
  |  +-- ESP32 GND (CRITICAL!)                             |
  |  +-- 5x servo BROWN/BLACK                               |
  |  +-- HC-SR04 GND                                        |
  |  +-- ACS712 GND                                         |
  |  +-- LED GND                                            |
  |  +-- Both voltage dividers GND ends                     |
  +---------------------------------------------------------+

  ACS712 HIGH-CURRENT PATH (optional but recommended)
  PSU RED ---> ACS712 IP+ ---> ACS712 IP- ---> Breadboard RED rail
  (Measures total current to all 5 servos)

  ESP32-WROOM-32 GPIO MAP
  +-------------------------------------------------+
  |  GPIO 2  | Onboard LED (built-in)                |
  |  GPIO 4  | WS2812B DIN (220 ohm inline)          |
  |  GPIO 5  | HC-SR04 ECHO (via 1k+2k divider)      |
  |  GPIO 12 | Servo 1 - Base rotation               |
  |  GPIO 13 | Servo 2 - Shoulder                     |
  |  GPIO 14 | Servo 3 - Elbow                        |
  |  GPIO 15 | Servo 4 - Wrist pitch                  |
  |  GPIO 16 | Servo 5 - Gripper (SG90)               |
  |  GPIO 17 | HC-SR04 TRIG                           |
  |  GPIO 34 | ACS712 OUT (via 10k+10k divider)     |
  |  GND     | Breadboard BLUE rail (shared ground)  |
  |  3.3V    | WS2812B VCC (single pixel OK)        |
  |  USB     | Your PC (programming + Serial)        |
  +-------------------------------------------------+

  VOLTAGE DIVIDERS (on breadboard)
  +-------------------------------------------------+
  |  HC-SR04 ECHO:                                   |
  |    ECHO --[1k]--+--[2k]-- GND                   |
  |                 |                               |
  |                 +-- GPIO 5                      |
  |                                                 |
  |  ACS712 OUT:                                     |
  |    OUT --[10k]--+--[10k]-- GND                  |
  |                 |                               |
  |                 +-- GPIO 34                     |
  +-------------------------------------------------+
```

**Questions for you:**
1. Do you want the ACS712 in series with ALL 5 servos, or just the 4 arm servos (excluding gripper)?
2. Will you mount the ESP32 on the base plate, or keep it on the breadboard?
3. Do you want a physical emergency stop button? If yes, I add a GPIO 27 button.

---

## 2. Data Flow Architecture

When you type a command, this is what happens end-to-end:

```
[User types in dashboard]
    |
    v
[Dashboard WebSocket] -----> [FastAPI Server] <----- [Fake ESP32 / Real ESP32]
    |                              |
    |                              v
    |                         [Ollama LLM]
    |                         "pick up the red cube"
    |                              |
    |                              v
    |                         [LLM thinks + generates JSON]
    |                         "response: Sure! I'll reach..."
    |                         "commands: [ {move_to...}, {grip...} ]"
    |                              |
    |                              v
    |                         [Server validates commands]
    |                         [Clamps angles to limits]
    |                         [Adds command_id]
    |                              |
    +------------------------------+
    |                              v
    |                         [WebSocket -> ESP32]
    |                              |
    |                              v
    |                         [ESP32 receives JSON]
    |                         [Parses command]
    |                         [Sets target angles]
    |                         [Smoothly moves servos]
    |                         [Reads sensors]
    |                         [Sends state back]
    |                              |
    +------------------------------+
    v
[Dashboard updates gauges]
[User sees the robot move + AI response text]
```

**Latency budget:**
| Step | Target | Actual | Notes |
|------|--------|--------|-------|
| User types -> Server | 0ms | 0ms | Instant (local) |
| Server -> Ollama | 0ms | 100-3000ms | Depends on prompt complexity |
| Ollama -> Server | 0ms | 0ms | Local PC |
| Server -> ESP32 | 0ms | 5-50ms | WiFi latency |
| ESP32 -> Motion start | 0ms | 0ms | Immediate |
| Motion completion | 0ms | 1-5s | Depends on speed/distance |
| ESP32 -> Server | 0ms | 5-50ms | WiFi |
| Server -> Dashboard | 0ms | 0ms | Local PC |

**Total perceived response:** 2-5 seconds (mostly waiting for Ollama to think)

**Questions for you:**
4. Is the 2-5 second AI response time acceptable? Or should we add a "thinking..." animation on the LED while waiting?
5. Do you want the AI to send ONE command at a time (safer, slower) or a BATCH of commands (faster, riskier)?

---

## 3. AI Backend Functionality

Here's what the backend does, module by module:

### Module A: WebSocket Server (`server.py`)
- **Two endpoints:**
  - `/ws/esp32` — ESP32 connects here. Receives state, sends commands.
  - `/ws/dashboard` — Browser connects here. Receives state, sends user commands.
- **Heartbeat:** Every 5 seconds, check if Ollama is alive. Tell the dashboard.
- **State broadcast:** Every time ESP32 sends state, forward it to all dashboard clients.

### Module B: LLM Agent (`llm_agent.py`)
- **Role:** Talks to Ollama (Llama 3.1 on your PC).
- **System prompt:** Tells the model it's a robot, what joints it has, how to output JSON.
- **Input:** User text + current arm state (joint angles, sensor readings).
- **Output:** JSON with `thought`, `response` (text for user), and `commands` (array for ESP32).
- **Personality injection:** Every prompt includes "Curious Learner" traits so responses match personality.

### Module C: Task Planner (`task_planner.py`)
- **Role:** Breaks complex tasks into motion primitives.
- **Examples:**
  - "pick up the cube" -> `[reach, grasp, lift, retract]`
  - "put it in the bin" -> `[move_to_bin, lower, release, retract]`
- **Current plan:** For v1, the LLM does ALL the planning. We add hardcoded primitives in v2.
- **Future:** "Learn this sequence" -> store it as a named skill.

### Module D: Skill Library (`skill_library.py` + SQLite)
- **Role:** Store and retrieve learned motion sequences.
- **Table structure:**
  ```sql
  skills (id, name, description, trajectory_json, created_at, success_count, last_used)
  ```
- **How it works:**
  - User demonstrates a task by manually guiding the arm.
  - ESP32 records joint angles over time.
  - Server stores this as a "skill" in SQLite.
  - Next time user says "do that again", server loads the skill and sends it.
- **Skill format:** JSON array of `{t, joint_angles, gripper}`

### Module E: Personality Engine (`personality_engine.py`)
- **Role:** "Curious Learner" mood system.
- **Mood states:** `curious, happy, confused, sad, busy, sleeping`
- **Triggers:**
  - Task success -> `happy` for 5 seconds -> back to `curious`
  - Task failure -> `sad` for 3 seconds -> `confused` -> asks user to help
  - No input for 5 minutes -> `sleeping` -> LED dim purple
  - New command -> `busy` -> LED white
- **Mood affects:**
  - LLM system prompt (changes how AI responds)
  - LED color on ESP32
  - Motion speed (happy = slightly faster, sad = slightly slower)

### Module F: Memory Store (`memory_store.py` + SQLite)
- **Role:** Remember what happened.
- **Tables:**
  - `conversations`: what the user said, what the AI said, timestamp
  - `commands`: every motion command sent, with result
  - `states`: periodic arm state snapshots
- **Why:** The LLM can say "Last time you asked me to pick up the red cube, it took 3 tries. Want me to try a different approach?"
- **Privacy:** Everything is local SQLite on your PC. Nothing leaves your machine.

### Module G: Web Dashboard (`dashboard/index.html`)
- **Already built.** Shows:
  - Connection status (ESP32 + Ollama)
  - Live joint angle gauges (5 bars)
  - Sensor readings (distance, current)
  - Mood indicator
  - Active command
  - Command input box
  - Live log of all messages

**Questions for you:**
6. Do you want voice commands? (e.g., speak to your PC, it transcribes to text, sends to robot) — adds Whisper (OpenAI) or uses Windows Speech Recognition.
7. Do you want the robot to "speak" back? (Text-to-speech on your PC) — adds Pyttsx3 or similar.
8. Do you want a mobile app interface? Or is the web dashboard on your PC enough?

---

## 4. ESP32 Firmware Architecture (Final)

### Firmware Modules

| Module | File | What It Does |
|--------|------|-------------|
| **Main** | `AI_Robot_Arm.ino` | setup(), loop(), orchestrates everything |
| **Config** | `config.h` | Pins, limits, WiFi, server IP, calibration |
| **WiFi Manager** | `wifi_manager.cpp` | Connect, reconnect, monitor |
| **WebSocket Client** | `comms_websocket.cpp` | Connect to server, send/receive JSON |
| **Servo Controller** | `servo_controller.cpp` | PWM, smoothing, position limits |
| **Kinematics** | `kinematics.cpp` | Forward/inverse kinematics (optional v1) |
| **Motion Planner** | `motion_planner.cpp` | Interpolation, speed profiles |
| **Sensor Manager** | `sensor_manager.cpp` | Read ultrasonic, current, filter noise |
| **Safety Monitor** | `safety_monitor.cpp` | Stall detect, current limits, emergency stop |
| **Command Parser** | `command_parser.cpp` | Parse JSON from server, execute |
| **RGB LED** | `rgb_led.cpp` | Mood-based color, patterns, idle animations |
| **Local Memory** | `local_memory.cpp` | SPIFFS cache for offline skills |

### Loop Frequency (Priority Order)

```
Every 10ms (100 Hz main loop):
  1. WebSocket poll (check for messages)
  2. Safety check (current > threshold?)
  3. Servo update (move 1 step toward target)
  4. Sensor read (every 100ms = every 10th loop)
  5. State send (every 200ms = every 20th loop)
  6. LED update
  7. WiFi reconnect check
  8. WebSocket reconnect check
```

### Emergency Stop Behavior

```
IF current > 2.0A:
  -> STOP all motion (hold current position)
  -> Set status = "error"
  -> Set mood = "sad"
  -> LED = orange (warning)
  -> Send emergency state to server
  -> Wait for "clear_emergency" command from server
  -> Resume normal operation
```

**Questions for you:**
9. Should the emergency stop also CUT POWER to servos? (Harder wiring, but safer)
10. Should the robot automatically retry a failed motion, or wait for user input?

---

## 5. Communication Protocol (Final JSON Schema)

### ESP32 → Server (State Update)
```json
{
  "type": "state_update",
  "timestamp": 12345678,
  "joint_angles": [90, 45, 120, 0],
  "gripper": 0.5,
  "sensors": {
    "distance": 23.4,
    "current": 0.82
  },
  "status": "idle",
  "mood": "curious",
  "active_cmd": "none",
  "emergency": false
}
```

### Server → ESP32 (Motion Command)
```json
{
  "type": "motion_command",
  "command_id": "cmd_a7f3",
  "action": "move_to",
  "joint_angles": [90, 60, 110, -15],
  "gripper": 0.7,
  "speed": 30
}
```

### Server → ESP32 (Execute Learned Skill)
```json
{
  "type": "learned_skill",
  "command_id": "cmd_b2e1",
  "skill_name": "pick_up_cube",
  "params": {"target_color": "red"}
}
```

### ESP32 → Server (Command Acknowledgment)
```json
{
  "type": "command_ack",
  "command_id": "cmd_a7f3",
  "status": "accepted"
}
```

### Server → ESP32 (Clear Emergency)
```json
{
  "type": "clear_emergency"
}
```

**Questions for you:**
11. Do you want the ESP32 to send sensor data every 100ms, or only when the sensor value changes? (Less bandwidth vs. more responsive)

---

## 6. Configuration You MUST Set

### `config.h` (ESP32)
```cpp
const char* WIFI_SSID     = "YOUR_WIFI_SSID";        // CHANGE THIS
const char* WIFI_PASSWORD = "YOUR_WIFI_PASSWORD";    // CHANGE THIS
const char* SERVER_HOST   = "192.168.1.100";          // CHANGE THIS (your PC's IP)
```

### `config.py` (Server — already set)
```python
OLLAMA_URL = "http://localhost:11434"  # Already correct
OLLAMA_MODEL = "llama3.1:8b"           # Already correct
SERVER_HOST = "0.0.0.0"                # Already correct
SERVER_PORT = 8000                     # Already correct
```

**Questions for you:**
12. What is your PC's IP address? (Run `ipconfig` in CMD and tell me the IPv4 address)
13. What is your WiFi SSID and password? (Or tell me if you want me to write it as a placeholder and you fill it in)

---

## 7. What Gets Built Next

Once you approve this architecture, here's the build order:

| Step | What I Build | What You Do |
|------|-------------|-------------|
| 1 | Update `config.h` with your real values | Wire all components together using the unified diagram |
| 2 | Build `wifi_manager.cpp` + `comms_websocket.cpp` | Upload test: WiFi + WebSocket together |
| 3 | Build `servo_controller.cpp` + `motion_planner.cpp` | Upload test: Move all 5 servos to default pose |
| 4 | Build `sensor_manager.cpp` + `safety_monitor.cpp` | Upload test: Verify sensors + emergency stop |
| 5 | Build `command_parser.cpp` + `rgb_led.cpp` | Upload test: Full firmware, respond to dashboard commands |
| 6 | Build `local_memory.cpp` (SPIFFS skills) | Test: offline mode, cached skill execution |
| 7 | Integrate everything into `AI_Robot_Arm.ino` | Upload final firmware, test end-to-end |
| 8 | Enhance backend: `personality_engine.py`, `skill_library.py`, `memory_store.py` | Test: personality, learning, memory |

---

## DECISIONS NEEDED FROM YOU

Please answer these 13 questions (or say "use defaults"):

1. ACS712 monitors all 5 servos or just 4 arm servos?
2. ESP32 mounted on base or on breadboard?
3. Physical emergency stop button?
4. "Thinking..." LED animation while waiting for Ollama?
5. One command at a time or batch commands?
6. Voice commands on PC?
7. Text-to-speech robot responses on PC?
8. Mobile app interface?
9. Emergency stop cuts servo power or just stops motion?
10. Auto-retry failed motions or wait for user?
11. Sensor data sent every 100ms or on-change only?
12. Your PC's IP address?
13. WiFi SSID (or use placeholder)?

**Or:** Just tell me "use defaults" and I'll build with my recommended choices.

**I'll wait for your answers before writing any production code.**
