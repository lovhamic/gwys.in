# Software Setup Guide — AI Robotic Arm

> Run this on **your PC** (not in Kimi Work). Windows, macOS, or Linux all work.

---

## Step 1: Install Python

**Windows:**
1. Download Python 3.10+ from https://python.org/downloads
2. **IMPORTANT:** Check "Add Python to PATH" during install
3. Open Command Prompt and verify:
   ```cmd
   python --version
   pip --version
   ```

**macOS:**
```bash
brew install python
```

**Linux:**
```bash
sudo apt update && sudo apt install python3 python3-pip python3-venv
```

---

## Step 2: Install Ollama (Free Local LLM)

1. Go to https://ollama.com/download and install
2. Open a terminal / command prompt
3. Pull a lightweight model (choose one):
   ```bash
   # Fastest, smallest — good for older PCs
   ollama pull phi3

   # Better quality, still fast on 8GB RAM
   ollama pull qwen2.5:7b

   # Best quality, needs 16GB RAM
   ollama pull llama3.1:8b
   ```
4. Test it:
   ```bash
   ollama run phi3
   ```
   Type a message and press Enter. Press `Ctrl+D` (macOS/Linux) or `Ctrl+Z` then Enter (Windows) to exit.

> Ollama runs as a background service. It will auto-start on boot.

---

## Step 3: Create Project + Install Python Packages

Open a terminal in your project folder (where you copied `ai_backend/`):

**Windows:**
```cmd
cd "G:\Project_robot\AI Robotic Arm\ai_backend"
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

**macOS/Linux:**
```bash
cd ai_backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

---

## Step 4: Test Ollama from Python

```bash
python test_ollama.py
```

You should see a response from the LLM. If you get a connection error, make sure Ollama is running:
```bash
ollama serve
```

---

## Step 5: Start the Backend Server

```bash
python server.py
```

You should see:
```
INFO:     Uvicorn running on http://0.0.0.0:8000
```

Open http://localhost:8000 in your browser to see the dashboard.

---

## Step 6: Install Arduino IDE + ESP32 Support

1. Download Arduino IDE from https://www.arduino.cc/en/software
2. Install it
3. Open Arduino IDE → File → Preferences
4. Add this URL to "Additional Board Manager URLs":
   ```
   https://raw.githubusercontent.com/espressif/arduino-esp32/gh-pages/package_esp32_index.json
   ```
5. Go to Tools → Board → Boards Manager
6. Search "ESP32" and install "ESP32 by Espressif Systems"
7. Connect your ESP32 via USB
8. Select Tools → Board → "ESP32 Dev Module"
9. Select the correct COM port
10. Open File → Examples → Basics → Blink
11. Change LED pin from `13` to `2` (ESP32 built-in LED is GPIO 2)
12. Upload and verify the LED blinks

---

## Step 7: Upload Firmware to ESP32

1. Open the `firmware/AI_Robot_Arm` folder in Arduino IDE
2. Open `AI_Robot_Arm.ino`
3. Update `WIFI_SSID` and `WIFI_PASSWORD` in `config.h`
4. Upload to ESP32
5. Open Serial Monitor (Tools → Serial Monitor, baud rate 115200)
6. You should see WiFi connection messages and WebSocket attempts

---

## Quick Reference: Running Everything

**Terminal 1 — Start Ollama (if not auto-running):**
```bash
ollama serve
```

**Terminal 2 — Start backend:**
```bash
cd ai_backend
venv\Scripts\activate   # Windows
source venv/bin/activate  # macOS/Linux
python server.py
```

**Terminal 3 — Test WebSocket (optional):**
```bash
cd tests
python test_websocket_client.py
```

**Arduino IDE — Upload firmware:**
- Open `firmware/AI_Robot_Arm/AI_Robot_Arm.ino`
- Upload
- Open Serial Monitor at 115200 baud

---

## Troubleshooting

| Problem | Solution |
|---------|----------|
| `python not found` | Reinstall Python and check "Add to PATH" |
| `pip install fails` | Run `python -m pip install --upgrade pip` first |
| `Ollama connection refused` | Run `ollama serve` in another terminal |
| `Module not found` | Make sure virtual environment is activated |
| `ESP32 upload fails` | Hold BOOT button while clicking Upload, release when "Connecting..." appears |
| `Serial Monitor shows garbage` | Set baud rate to 115200 and correct COM port |
| `WebSocket disconnects` | Check PC and ESP32 are on same WiFi network |

---

*Next: Move to Step 2 (FastAPI server) and Step 4 (Arduino firmware) once you have Python and Ollama installed.*
