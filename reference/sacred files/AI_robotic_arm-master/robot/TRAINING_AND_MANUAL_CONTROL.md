# How Training & Manual Control Work

> Two questions every robotic arm builder asks. Here are the exact answers for YOUR project.

---

## Part 1: How Do You "Train" This AI?

Your robot has **three ways to learn**, from simplest to most advanced:

### Method A: Learning by Chat (Already Works Now)

**What you do:** Talk to it in the dashboard. Every conversation is stored in SQLite on your PC.

**Example:**
```
You: "Pick up the red cube"
AI: [moves arm, succeeds]
You: "Good job!"
AI: [stores this as a positive example]

Later:
You: "Pick up the red cube again"
AI: [already knows what worked, does it faster]
```

**What gets stored:**
- Your command text
- The AI's response
- The motion commands it generated
- Whether it succeeded (you say "good" or "bad")

**Limitation:** This only improves the AI's *prompt understanding* — it gets better at guessing what you mean. It does NOT remember exact joint angles.

---

### Method B: Learning by Demonstration (Phase 5 — "Teaching Mode")

**What you do:** Physically grab the robot arm and move it through a task. The ESP32 records every joint angle.

**Step by step:**
1. You type in dashboard: **"Teach me how to stack two blocks"**
2. AI responds: **"Sure! Put me in teaching mode and guide my arm."**
3. The ESP32 enters **TEACHING MODE:**
   - All servos are de-energized (low torque, you can move them by hand)
   - The ESP32 reads every joint angle every 50ms
   - It stores: `{time: 0.0, joints: [90,45,120,0], gripper: 0.5}`
   - It stores: `{time: 0.05, joints: [90,46,119,1], gripper: 0.5}`
   - ...and so on for the entire demonstration
4. When you finish, you type: **"Save that as 'stack_blocks'"**
5. The server saves the full trajectory to SQLite as a **skill**

**Later, to replay:**
```
You: "Do the stack_blocks skill"
AI: [loads stored trajectory from SQLite]
AI: [sends joint angles to ESP32 step by step]
ESP32: [repeats your exact motion]
```

**What gets stored:**
```json
{
  "skill_id": "stack_blocks",
  "name": "Stack Two Blocks",
  "trajectory": [
    {"t": 0.00, "joints": [90,90,90,0], "gripper": 0.5},
    {"t": 0.05, "joints": [90,85,95,0], "gripper": 0.5},
    {"t": 0.10, "joints": [90,80,100,0], "gripper": 0.5},
    ...
    {"t": 3.50, "joints": [90,90,90,0], "gripper": 0.0}
  ],
  "success_count": 3,
  "failure_count": 0
}
```

**Hardware requirement for teaching mode:** Servos must be able to move freely when unpowered. MG996R servos have some gear resistance, but you can still move them. For smoother teaching, you can add a **physical clutch** or use compliant servos — but for v1, just use muscle power.

---

### Method C: Learning by Correction (Phase 5+ — "No, Lower the Gripper")

**What you do:** Let the robot try a task, then correct it.

**Example:**
```
You: "Pick up the red cube"
AI: [tries, misses the cube]
You: "Lower the gripper by 2 cm before grasping"
AI: [adjusts the approach height in the skill]
AI: [tries again, succeeds]
AI: [saves the corrected approach as the new default]
```

**What gets stored:** A modified parameter (e.g., `approach_height = 5cm` instead of `7cm`).

**This is the most powerful form of learning** because the robot improves from explicit human feedback.

---

### Summary: Which Training Method When?

| Situation | Use Method | What You Do |
|-----------|-----------|-------------|
| Robot doesn't understand your words | A — Chat | Rephrase, give examples, it learns from conversation history |
| Robot needs to copy a physical motion | B — Demonstration | Grab arm, move it, save the trajectory |
| Robot is close but slightly wrong | C — Correction | Tell it what to change, it updates the skill |

---

## Part 2: How Do You Take Manual Control?

You have **three ways** to manually control the arm:

### Method 1: Dashboard Sliders (Immediate — Phase 4)

**What you do:** Add simple angle sliders to the web dashboard.

**How it works:**
1. Open `http://localhost:8000`
2. Drag a slider for "Base" from 90° to 120°
3. The dashboard sends a direct motion command to the ESP32
4. The ESP32 moves the base servo immediately

**Why this is useful:**
- Fine-tuning positions
- Testing range of motion
- Emergency override when AI is confused
- Teaching the robot by setting positions manually

**Implementation:** Add 5 sliders to `dashboard/index.html` that send raw `motion_command` JSON directly, bypassing the LLM.

---

### Method 2: Direct Serial Commands (Immediate — Right Now)

**What you do:** Send JSON commands directly from Serial Monitor.

**How it works:**
1. Open Arduino Serial Monitor (115200 baud)
2. Type a JSON command and press Enter:
```json
{"type":"motion_command","joint_angles":[90,60,110,0],"gripper":0.5,"speed":30}
```
3. The ESP32 parses it and moves

**This is already in your firmware** — the `command_parser` handles any valid JSON.

---

### Method 3: Teaching Mode (Physical — Phase 5)

**What you do:** Grab the arm and move it. It records.

**How it works:**
1. Send command: `{"type":"teaching_mode","enabled":true}`
2. The ESP32 sets all servo PWM to 0% (de-energized)
3. You physically move each joint to the desired position
4. The ESP32 logs every angle every 50ms
5. Send `{"type":"teaching_mode","enabled":false}` to stop recording
6. Send `{"type":"save_skill","name":"my_motion"}` to save

**Why this is useful:**
- You don't need to calculate angles
- Natural human motion is preserved
- Complex motions (drawing, stacking) are easier to demonstrate than describe

---

### Method 4: Emergency Stop (Always Active)

**What you do:** Press the physical emergency stop button (if you wired one) or send a command.

**How it works:**
- Button press → GPIO 27 goes LOW → ESP32 immediately freezes all servos
- Or send: `{"type":"emergency_stop"}` from dashboard
- To resume: `{"type":"clear_emergency"}`

---

## Which Method Should You Use?

| Goal | Best Method | When It's Available |
|------|-------------|-------------------|
| Just test if a servo works | Dashboard sliders | Phase 4 (now) |
| Fine-tune a position | Serial commands | Phase 4 (now) |
| Copy a complex motion exactly | Teaching mode | Phase 5 |
| Improve the AI's understanding | Chat + correction | Phase 4-5 |
| Stop everything immediately | Emergency stop | Phase 4 (now) |

---

## What Gets Built in Each Phase

| Phase | Training Feature | Manual Control Feature |
|-------|-----------------|----------------------|
| **Phase 4** (now) | Conversation history in SQLite | Dashboard sliders + Serial commands + Emergency stop |
| **Phase 5** | Teaching mode (record trajectory) | Teaching mode (de-energized servos) |
| **Phase 5+** | Correction feedback loop | Skill replay + parameter editing |
| **Phase 6** | Personality adapts from interaction history | Mood-based motion speed |

---

## The Short Answer

**"How do I train it?"**
> Talk to it (Phase 4). Grab and move it (Phase 5). Correct it when it's wrong (Phase 5+). All learning stays on your PC in SQLite — nothing goes to the cloud.

**"How do I take manual control?"**
> Dashboard sliders (Phase 4). Serial commands (Phase 4). Grab the arm and move it freely in teaching mode (Phase 5). Emergency stop button always works.

---

*Ready to build the production firmware? Say yes and I'll start writing the modular code.*
