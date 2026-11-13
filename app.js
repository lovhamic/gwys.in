/**
 * GUYWITHYELLOWSCREWDRIVER // DEEP INTERACTIVE MOTION ENGINE
 * Emil Kowalski Spring Mechanics · Magnetic Buttons · Hardware Simulators · Web Audio
 */

(function () {
  "use strict";

  // ---------------------------------------------------------------------------
  // STATE MANAGEMENT
  // ---------------------------------------------------------------------------
  const state = {
    soundEnabled: true,
    audioCtx: null,
    heroMode: "photo",
    activeWorkstation: null, // 1 | 2 | 3 | null
    armSpeed: 1.0,
    benchActive: true,
    telemetry: {
      voltage: 24.12,
      current: 1.84,
      temp: 38.6,
      packets: 48210
    }
  };

  // ---------------------------------------------------------------------------
  // 1. ADVANCED PROCEDURAL WEB AUDIO SYNTHESIZER
  // ---------------------------------------------------------------------------
  function getAudioContext() {
    if (!state.audioCtx) {
      const AudioCtx = window.AudioContext || window.webkitAudioContext;
      if (AudioCtx) state.audioCtx = new AudioCtx();
    }
    if (state.audioCtx && state.audioCtx.state === "suspended") {
      state.audioCtx.resume();
    }
    return state.audioCtx;
  }

  const Sound = {
    click: function() {
      if (!state.soundEnabled) return;
      try {
        const ctx = getAudioContext();
        if (!ctx) return;
        const osc = ctx.createOscillator();
        const gain = ctx.createGain();
        const now = ctx.currentTime;

        osc.type = "sine";
        osc.frequency.setValueAtTime(1200, now);
        osc.frequency.exponentialRampToValueAtTime(180, now + 0.025);

        gain.gain.setValueAtTime(0.04, now);
        gain.gain.exponentialRampToValueAtTime(0.0001, now + 0.025);

        osc.connect(gain);
        gain.connect(ctx.destination);
        osc.start(now);
        osc.stop(now + 0.025);
      } catch (e) {}
    },

    relay: function() {
      if (!state.soundEnabled) return;
      try {
        const ctx = getAudioContext();
        if (!ctx) return;
        const now = ctx.currentTime;

        // Double mechanical pulse (relay armature snap)
        [0, 0.016].forEach((delay) => {
          const osc = ctx.createOscillator();
          const gain = ctx.createGain();
          osc.type = "triangle";
          osc.frequency.setValueAtTime(320, now + delay);
          osc.frequency.exponentialRampToValueAtTime(80, now + delay + 0.018);

          gain.gain.setValueAtTime(0.05, now + delay);
          gain.gain.exponentialRampToValueAtTime(0.001, now + delay + 0.018);

          osc.connect(gain);
          gain.connect(ctx.destination);
          osc.start(now + delay);
          osc.stop(now + delay + 0.018);
        });
      } catch (e) {}
    },

    probe: function(freq = 1400) {
      if (!state.soundEnabled) return;
      try {
        const ctx = getAudioContext();
        if (!ctx) return;
        const now = ctx.currentTime;
        const osc = ctx.createOscillator();
        const gain = ctx.createGain();

        osc.type = "sine";
        osc.frequency.setValueAtTime(freq, now);
        gain.gain.setValueAtTime(0.03, now);
        gain.gain.exponentialRampToValueAtTime(0.0001, now + 0.045);

        osc.connect(gain);
        gain.connect(ctx.destination);
        osc.start(now);
        osc.stop(now + 0.045);
      } catch (e) {}
    },

    chirp: function() {
      if (!state.soundEnabled) return;
      try {
        const ctx = getAudioContext();
        if (!ctx) return;
        const now = ctx.currentTime;
        const osc = ctx.createOscillator();
        const gain = ctx.createGain();

        osc.type = "sine";
        osc.frequency.setValueAtTime(800, now);
        osc.frequency.exponentialRampToValueAtTime(2400, now + 0.06);

        gain.gain.setValueAtTime(0.02, now);
        gain.gain.exponentialRampToValueAtTime(0.0001, now + 0.06);

        osc.connect(gain);
        gain.connect(ctx.destination);
        osc.start(now);
        osc.stop(now + 0.06);
      } catch (e) {}
    },

    microStep: function(pitch = 520) {
      if (!state.soundEnabled) return;
      try {
        const ctx = getAudioContext();
        if (!ctx) return;
        const now = ctx.currentTime;
        const osc = ctx.createOscillator();
        const gain = ctx.createGain();

        osc.type = "sine";
        osc.frequency.setValueAtTime(pitch, now);
        osc.frequency.exponentialRampToValueAtTime(pitch * 0.7, now + 0.015);

        gain.gain.setValueAtTime(0.012, now);
        gain.gain.exponentialRampToValueAtTime(0.0001, now + 0.015);

        osc.connect(gain);
        gain.connect(ctx.destination);
        osc.start(now);
        osc.stop(now + 0.015);
      } catch (e) {}
    }
  };

  function initAudioHeader() {
    const soundBtn = document.getElementById("sound-toggle-btn");
    const soundText = document.getElementById("sound-toggle-text");

    if (soundBtn && soundText) {
      soundBtn.addEventListener("click", () => {
        state.soundEnabled = !state.soundEnabled;
        soundText.textContent = state.soundEnabled ? "Audio On" : "Audio Off";
        soundBtn.classList.toggle("opacity-50", !state.soundEnabled);
        if (state.soundEnabled) Sound.relay();
      });
    }

    document.querySelectorAll("button, a, .btn-pill-primary, .btn-pill-secondary, .btn-pill-yellow").forEach((el) => {
      el.addEventListener("mousedown", () => Sound.click());
    });
  }

  // ---------------------------------------------------------------------------
  // 2. MAGNETIC BUTTONS (Emil Kowalski Springs)
  // ---------------------------------------------------------------------------
  function initMagneticButtons() {
    const magneticElements = document.querySelectorAll(
      ".btn-pill-primary, .btn-pill-secondary, .btn-pill-yellow, .magnetic-btn"
    );

    magneticElements.forEach((btn) => {
      let bounds = null;

      btn.addEventListener("mouseenter", () => {
        bounds = btn.getBoundingClientRect();
      });

      btn.addEventListener("mousemove", (e) => {
        if (!bounds) bounds = btn.getBoundingClientRect();
        const centerX = bounds.left + bounds.width / 2;
        const centerY = bounds.top + bounds.height / 2;
        const deltaX = (e.clientX - centerX) * 0.28;
        const deltaY = (e.clientY - centerY) * 0.28;

        btn.style.transform = `translate(${deltaX}px, ${deltaY}px)`;
      });

      btn.addEventListener("mouseleave", () => {
        btn.style.transition = "transform 360ms cubic-bezier(0.34, 1.56, 0.64, 1)";
        btn.style.transform = "translate(0px, 0px)";
        setTimeout(() => {
          btn.style.transition = "";
          bounds = null;
        }, 360);
      });
    });
  }

  // ---------------------------------------------------------------------------
  // 3. CURSOR FOLLOWER & CONTEXT BADGE
  // ---------------------------------------------------------------------------
  function initCursorFollower() {
    const dot = document.querySelector(".cursor-dot");
    const label = document.querySelector(".cursor-label");
    if (!dot || window.matchMedia("(pointer: coarse)").matches) return;

    let mouseX = -100;
    let mouseY = -100;
    let dotX = -100;
    let dotY = -100;

    window.addEventListener("mousemove", (e) => {
      mouseX = e.clientX;
      mouseY = e.clientY;
    });

    function loop() {
      dotX += (mouseX - dotX) * 0.22;
      dotY += (mouseY - dotY) * 0.22;

      dot.style.transform = `translate(${dotX}px, ${dotY}px)`;
      if (label) {
        label.style.transform = `translate(${dotX}px, ${dotY + 28}px)`;
      }

      requestAnimationFrame(loop);
    }
    loop();

    // Hover triggers for custom cursor states
    document.querySelectorAll("[data-cursor]").forEach((el) => {
      el.addEventListener("mouseenter", () => {
        const text = el.getAttribute("data-cursor");
        dot.classList.add("cursor-hover");
        if (label && text) {
          label.textContent = text;
          label.style.opacity = "1";
        }
      });
      el.addEventListener("mouseleave", () => {
        dot.classList.remove("cursor-hover");
        if (label) label.style.opacity = "0";
      });
    });
  }

  // ---------------------------------------------------------------------------
  // 4. HERO STAGE: WORKBENCH VISUAL & INTERACTIVE HOTSPOTS
  // ---------------------------------------------------------------------------
  function initHeroStage() {
    // Hotspot clicks on Workbench Visual
    document.querySelectorAll(".photo-hotspot").forEach((spot) => {
      spot.addEventListener("click", () => {
        Sound.probe(1600);
      });
    });
  }

  // ---------------------------------------------------------------------------
  // 5. INTERACTIVE "HOW I WORK" PROCESS SEQUENCER & 4-PHASE CARDS
  // ---------------------------------------------------------------------------
  function initHowIWorkSection() {
    const trigger = document.getElementById("how-i-work-interactive");
    const cards = document.querySelectorAll(".hiw-card");
    const stepIndicators = document.querySelectorAll(".hiw-step-indicator");
    const badgeStatus = document.getElementById("hiw-badge-status");

    let isSequencing = false;

    // A. Step Indicators Click: Jump to Phase
    stepIndicators.forEach((btn) => {
      btn.addEventListener("click", () => {
        const step = parseInt(btn.getAttribute("data-step"), 10);
        activatePhase(step);
        Sound.microStep(440 + step * 80);
      });
    });

    // B. Card Hover and Click Interactions
    cards.forEach((card) => {
      const phase = parseInt(card.getAttribute("data-phase"), 10);

      card.addEventListener("mouseenter", () => {
        if (!isSequencing) {
          stepIndicators.forEach((ind, i) => {
            ind.classList.toggle("active", i === phase);
          });
          Sound.microStep(500 + phase * 65);
        }
      });

      card.addEventListener("click", () => {
        activatePhase(phase);
        Sound.click();
      });
    });

    function activatePhase(phaseIndex) {
      cards.forEach((c, idx) => {
        c.classList.toggle("active-phase", idx === phaseIndex);
      });
      stepIndicators.forEach((ind, idx) => {
        ind.classList.toggle("active", idx === phaseIndex);
      });
    }

    // C. Click Title: Run Sequential Machine Sweep Loop
    if (trigger) {
      trigger.addEventListener("click", () => {
        if (isSequencing) return;
        isSequencing = true;
        Sound.relay();

        if (badgeStatus) badgeStatus.textContent = "Running Loop...";

        const pitches = [440, 554, 659, 880];

        cards.forEach((card, idx) => {
          setTimeout(() => {
            // Un-sequence others
            cards.forEach(c => c.classList.remove("sequencing"));
            stepIndicators.forEach(s => s.classList.remove("active"));

            card.classList.add("sequencing");
            if (stepIndicators[idx]) stepIndicators[idx].classList.add("active");

            Sound.microStep(pitches[idx]);

            // When last card completes
            if (idx === cards.length - 1) {
              setTimeout(() => {
                Sound.chirp();
                cards.forEach(c => c.classList.remove("sequencing"));
                activatePhase(3); // Land on 'Figuring out'
                if (badgeStatus) badgeStatus.textContent = "Figuring Out!";

                setTimeout(() => {
                  if (badgeStatus) badgeStatus.textContent = "4-Stage Loop";
                  isSequencing = false;
                }, 2200);
              }, 400);
            }
          }, idx * 260);
        });
      });
    }
  }

  // ---------------------------------------------------------------------------
  // 6. SACRED FILES PROJECT DATABASE & QUICK SPEC MODAL
  // ---------------------------------------------------------------------------
  const projectDatabase = {
    "blackbox": {
      id: "blackbox",
      numericId: 1,
      title: "Black Box · Magnetometer-Free GPS Navigator",
      hook: "Can an ESP32 navigate waypoints without a magnetic compass?",
      subtitle: "Black Box · Magnetometer-Free GPS Waypoint Navigator",
      category: "Hardware & IoT | ESP32-C3 | Kalman",
      discipline: "Hardware & Sensor Fusion",
      status: "Active Build",
      description: `The Lock-On: When powered up, the device waits for a clear GPS signal. It then mathematically checks your distance against a saved list of coordinates and automatically targets the closest one.

The Calibration: Because it doesn't use a standard magnetic compass, the device initially doesn't know which way you are facing. It prompts you to "Start Walking." Once you reach a normal walking pace, the GPS detects your physical trajectory and locks in your starting direction.

The Navigation: This is where the sensor fusion happens. An arrow appears on the screen pointing directly toward your destination.

If you are standing still and turning around, the internal gyroscope smoothly rotates the arrow to match your hand movements.

When you are walking, the GPS secretly checks your heading in the background and corrects the gyroscope so the arrow never drifts off course.

The Arrival: Once you are within 15 meters of your target, the screen announces that you have arrived. A simple press of the physical reset button clears the memory and starts the cycle over to find the next nearest location.`,
      descriptionHtml: `
        <p><strong class="font-bold text-neutral-900">The Lock-On:</strong> When powered up, the device waits for a clear GPS signal. It then mathematically checks your distance against a saved list of coordinates and automatically targets the closest one.</p>
        <p><strong class="font-bold text-neutral-900">The Calibration:</strong> Because it doesn't use a standard magnetic compass, the device initially doesn't know which way you are facing. It prompts you to &ldquo;Start Walking.&rdquo; Once you reach a normal walking pace, the GPS detects your physical trajectory and locks in your starting direction.</p>
        <p><strong class="font-bold text-neutral-900">The Navigation:</strong> This is where the sensor fusion happens. An arrow appears on the screen pointing directly toward your destination.</p>
        <p class="pl-4 border-l-2 border-neutral-300 text-neutral-700 text-base">If you are standing still and turning around, the internal gyroscope smoothly rotates the arrow to match your hand movements.</p>
        <p class="pl-4 border-l-2 border-neutral-300 text-neutral-700 text-base">When you are walking, the GPS secretly checks your heading in the background and corrects the gyroscope so the arrow never drifts off course.</p>
        <p><strong class="font-bold text-neutral-900">The Arrival:</strong> Once you are within 15 meters of your target, the screen announces that you have arrived. A simple press of the physical reset button clears the memory and starts the cycle over to find the next nearest location.</p>
      `,
      heroImg: "assets/projects/blackbox/01.png",
      teardownImg: "assets/projects/blackbox/02.png",
      teardownCaption: "Everything that goes inside · ESP32-C3, NEO-6M GPS & MPU6050",
      madeWith: [
        "ESP32-C3 Supermini",
        "NEO-6M GPS (UART 9600)",
        "MPU6050 6-Axis IMU (Raw I2C)",
        "1.3\" OLED (SH1106 Driver)",
        "5V Power Source"
      ],
      githubUrl: "https://github.com/lovhamic",
      specs: [
        { label: "Core MCU", val: "ESP32-C3 RISC-V 160MHz" },
        { label: "IMU Fusion", val: "1D Kalman (100Hz Gyro + 1Hz GPS)" },
        { label: "Display Driver", val: "1.3\" SH1106 I2C (128x64)" },
        { label: "Target Lock", val: "Haversine Auto-Targeting" }
      ],
      codeSnippet: `// 1D Kalman Sensor Fusion State Machine (ESP32-C3)
void updateKalman(double gyroYawRate, double gpsCog, double dt) {
    // 1. Predict state from 100Hz gyro
    yawAngle += gyroYawRate * dt;
    P += Q;

    // 2. Snap to GPS COG once walking speed > 2 km/h
    if (gps.speed.kmph() > 2.0 && gps.course.isValid()) {
        double diff = gpsCog - yawAngle;
        while (diff > 180.0) diff -= 360.0;
        while (diff < -180.0) diff += 360.0;

        double K = P / (P + R);
        yawAngle += K * diff;
        P = (1.0 - K) * P;
    }
}`
    },
    "memeglove": {
      id: "memeglove",
      numericId: 2,
      title: "Meme Glove · IoT RFID Wearable Soundboard",
      hook: "Can an RFID-tagged glove trigger comedic sound effects with zero latency?",
      subtitle: "Meme Glove · IoT Wireless RFID/NFC Soundboard Wearable",
      category: "Wearable & IoT | ESP32 | RC522 SPI",
      discipline: "Wearable IoT & Telemetry",
      status: "Active Build",
      description: `Basically, you wear a glove that has a tiny sensor hidden inside, and you get a bunch of cards that you can put inside pocket.

When you tap or grab one of those cards, the glove reads the cards. It immediately sends a Wi-Fi signal to your computer or phone.

That signal tells your device to do something funny—like pop up a specific meme, play a sound effect, or flash a joke on the screen. Each card has its own taste`,
      descriptionHtml: `
        <p>Basically, you wear a glove that has a tiny sensor hidden inside, and you get a bunch of cards that you can put inside pocket.</p>
        <p>When you tap or grab one of those cards, the glove reads the cards. It immediately sends a Wi-Fi signal to your computer or phone.</p>
        <p>That signal tells your device to do something funny—like pop up a specific meme, play a sound effect, or flash a joke on the screen. Each card has its own taste.</p>
      `,
      heroImg: "assets/projects/meme-glove/hero.jpg",
      teardownImg: "assets/projects/meme-glove/teardown.jpg",
      teardownCaption: "Hardware testing on workbench · ESP32 wrist mount, LiPo cell & RC522 sensor",
      madeWith: [
        "ESP32 NodeMCU (2.4GHz Wi-Fi)",
        "RC522 RFID/NFC Reader (13.56MHz SPI)",
        "13.56MHz MIFARE Classic / NTAG",
        "3.7V LiPo Battery & Wrist Strap",
        "Node.js Express / Python Flask",
        "C++ (Arduino ESP32)"
      ],
      githubUrl: "https://github.com/lovhamic/meme-glove",
      specs: [
        { label: "Microcontroller", val: "ESP32 NodeMCU (Dual-Core)" },
        { label: "RFID Protocol", val: "13.56 MHz SPI (RC522)" },
        { label: "Network Protocol", val: "HTTP POST over 2.4GHz Wi-Fi" },
        { label: "PC Audio Bridge", val: "Node.js Express / Python Flask" }
      ],
      codeSnippet: `// ESP32 RFID Scan & Instant Wi-Fi HTTP Trigger
if (mfrc522.PICC_IsNewCardPresent() && mfrc522.PICC_ReadCardSerial()) {
    String uid = "";
    for (byte i = 0; i < mfrc522.uid.size; i++) {
        uid += (mfrc522.uid.uidByte[i] < 0x10 ? "0" : "");
        uid += String(mfrc522.uid.uidByte[i], HEX);
    }
    uid.toUpperCase();

    HTTPClient http;
    http.begin(client, String("http://") + SERVER_IP + ":" + SERVER_PORT + "/tag");
    http.addHeader("Content-Type", "application/json");
    http.POST("{\\"uid\\":\\"" + uid + "\\"}");
    http.end();
}`
    },
    "cockroach": {
      id: "cockroach",
      numericId: 3,
      title: "Shoot the Cockroach · ESP32 Physical IMU Arcade Gun",
      hook: "Can an ESP32 and 6-axis IMU turn physical pointing into an arcade gun game?",
      subtitle: "Shoot the Cockroach · ESP32 Physical IMU Arcade Shooter",
      category: "Physical Gaming | ESP32 | Pygame",
      discipline: "Hardware & Game Physics",
      status: "Bench Validated",
      description: "A physical hardware arcade gun game bridging embedded telemetry and desktop gaming. The custom gun enclosure houses an ESP32 and an MPU6050 6-axis motion tracking module, paired with a tactile momentary trigger microswitch. Moving the physical gun streams high-rate raw accelerometer and gyroscope vectors over USB Serial at 115200 baud to a custom Python Pygame engine. The game maps angular velocity into crosshair coordinates with dynamic smoothing, spawning cockroaches with erratic behaviors and registering physical trigger interrupts.",
      heroImg: "assets/projects/cockroach/03.jpg",
      teardownImg: "assets/projects/cockroach/04.jpg",
      teardownCaption: "Gun controller architecture · ESP32 I2C sensor bus & Pygame serial bridge",
      madeWith: [
        "ESP32 Development Board",
        "MPU6050 6-DOF IMU (GY-521)",
        "Hardware Trigger Microswitch",
        "USB Serial Protocol (115200 Baud)",
        "Python 3 & Pygame Engine",
        "Custom Gun Enclosure"
      ],
      githubUrl: "https://github.com/lovhamic",
      specs: [
        { label: "Baud Rate", val: "115200 Baud USB Serial" },
        { label: "Sensor Cadence", val: "100Hz (10ms interval)" },
        { label: "Trigger Pin", val: "GPIO 4 (Active LOW Pullup)" },
        { label: "I2C Bus Clock", val: "400 kHz Fast I2C" }
      ],
      codeSnippet: `// 100Hz IMU Packet Streaming over USB Serial
void loop() {
    unsigned long now = millis();
    if (now - lastSendTime >= SEND_INTERVAL_MS) {
        lastSendTime = now;
        readMPU6050Raw(ax, ay, az, gx, gy, gz);
        
        Serial.printf("DATA,%d,%d,%d,%d,%d,%d\\n", ax, ay, az, gx, gy, gz);
    }

    if (digitalRead(TRIGGER_PIN) == LOW && !triggerPressed) {
        triggerPressed = true;
        Serial.println("SHOOT");
    }
}`
    },
    "watersim": {
      id: "watersim",
      numericId: 4,
      title: "Water Sim · NeoPixel Particle Fluid Physics",
      hook: "Can 100 addressable LEDs simulate real fluid pressure and splash physics?",
      subtitle: "Water Sim · ESP32 NeoPixel Particle Fluid Engine",
      category: "Simulation & Hardware | FastLED | MPU6050",
      discipline: "Fluid Physics & Embedded Graphics",
      status: "Active Build",
      description: `Tilt: A small sensor feels which way the display is tilted. Tilt it left and the water flows left.

Moving: There are 851 pixels . Gravity pulls them, they slow down a little as they move, and they bounce softly off the edges.

Pooling: The drops push away from each other when they get too crowded. That’s why they spread out into a pool instead of piling up in one spot.

Splashes: If you shake the display, the water jumps up and a few droplets fly out. If the water hits an edge hard, it also throws off a few small droplets. The droplets fade away quickly.

Lighting: The more water in a spot, the deeper the blue. Fast-moving water turns whiter, like foam. The lights change smoothly so they don’t flicker`,
      descriptionHtml: `
        <p><strong class="font-bold text-neutral-900">Tilt:</strong> A small sensor feels which way the display is tilted. Tilt it left and the water flows left.</p>
        <p><strong class="font-bold text-neutral-900">Moving:</strong> There are 851 pixels . Gravity pulls them, they slow down a little as they move, and they bounce softly off the edges.</p>
        <p><strong class="font-bold text-neutral-900">Pooling:</strong> The drops push away from each other when they get too crowded. That’s why they spread out into a pool instead of piling up in one spot.</p>
        <p><strong class="font-bold text-neutral-900">Splashes:</strong> If you shake the display, the water jumps up and a few droplets fly out. If the water hits an edge hard, it also throws off a few small droplets. The droplets fade away quickly.</p>
        <p><strong class="font-bold text-neutral-900">Lighting:</strong> The more water in a spot, the deeper the blue. Fast-moving water turns whiter, like foam. The lights change smoothly so they don’t flicker.</p>
      `,
      heroImg: "assets/projects/watersim/hero.png",
      teardownImg: "assets/projects/watersim/teardown.png",
      teardownCaption: "Internal enclosure wiring: ESP32 controller, MPU6050 6-axis IMU on breadboard, power regulation, and battery pack",
      madeWith: [
        "ESP32 Microcontroller",
        "WS2812B NeoPixel Matrix Display",
        "MPU6050 6-Axis IMU (Raw I2C)",
        "FastLED Library (255 Brightness / 6A Max)",
        "Eulerian-Lagrangian Particle Solver",
        "C++ Embedded Firmware"
      ],
      githubUrl: "https://github.com/lovhamic",
      specs: [
        { label: "Fluid Particles", val: "40 Water + 20 Spray Droplets" },
        { label: "Frame Rate", val: "40 FPS (25,000 µs frame cap)" },
        { label: "LED Power Rail", val: "5V 6A Regulated + 1000uF Cap" },
        { label: "Shake Detection", val: "Jerk Threshold > 0.5g" }
      ],
      codeSnippet: `// Eulerian-Lagrangian Particle Pressure & Density Solver
void stepWater(float dt) {
    buildCounts();
    for (auto &p : water) {
        int cx = (int)p.x, cy = (int)p.y;
        uint8_t own = cnt[cy * W + cx];

        // Pressure gradient: push toward less crowded cells
        float fx = (float)cntAt(cx - 1, cy, own) - (float)cntAt(cx + 1, cy, own);
        float fy = (float)cntAt(cx, cy - 1, own) - (float)cntAt(cx, cy + 1, own);

        p.vx += (gx + fx * PRESSURE) * dt;
        p.vy += (gy + fy * PRESSURE) * dt;
    }
}`
    },
    "robotarm": {
      id: "robotarm",
      numericId: 5,
      title: "AI Robotic Arm · 4-DOF Vision Manipulator",
      hook: "Can an on-device local LLM control a 4-DOF robotic arm with computer vision?",
      subtitle: "AI Robotic Arm · Vision & Local LLM Autonomous Manipulator",
      category: "Robotics & AI | ESP32 | Ollama",
      discipline: "Robotics & Edge AI",
      status: "Bench Validated",
      description: "An autonomous 4-DOF robotic manipulator combining physical kinematic actuation with local machine intelligence. An ESP32-WROOM-32 controls 4 MG996R metal-gear servos for base, shoulder, elbow, and wrist joints alongside an SG90 gripper. The controller continuously samples an ACS712 Hall-effect sensor for current load and mechanical stall detection, and an HC-SR04 sonar for proximity limits. A host AI backend running local LLMs via Ollama (Phi-3, Qwen 2.5) evaluates spatial tasks and executes multi-step pick-and-place trajectories.",
      heroImg: "assets/projects/robotarm/hero.jpg",
      teardownImg: "assets/projects/robotarm/teardown.jpg",
      teardownCaption: "Physical 4-DOF robotic arm hardware & joint linkage assembly",
      madeWith: [
        "ESP32-WROOM-32",
        "4x MG996R High-Torque Servos",
        "1x SG90 Micro Gripper",
        "ACS712 Current Sensor (Stall Protection)",
        "HC-SR04 Ultrasonic Sonar",
        "Ollama Local LLM & Python Backend"
      ],
      githubUrl: "https://github.com/lovhamic",
      specs: [
        { label: "Joint Actuators", val: "4x MG996R (11 kg-cm) + 1x SG90" },
        { label: "Current Sense", val: "ACS712 (Stall Threshold > 3.8A)" },
        { label: "Local AI Brain", val: "Ollama Phi-3 / Qwen 2.5:7b" },
        { label: "Safety Cutoff", val: "Hardware Over-Current Auto Dump" }
      ],
      codeSnippet: `// Real-Time Stall Detection & Servo Safety Loop
float readBusCurrent() {
    int raw = analogRead(ACS712_PIN);
    float voltage = (raw / 4095.0f) * 3.3f * 2.0f; // 10k:10k divider
    return (voltage - 2.5f) / 0.185f; // ACS712-05B sensitivity
}

void checkSafetyLimits() {
    if (readBusCurrent() > STALL_CURRENT_THRESHOLD_A) {
        detachAllServos(); // Emergency torque dump
        setLedColor(CRGB::Red);
    }
}`
    },
    "navigator": {
      id: "navigator",
      numericId: 6,
      title: "Navigator 01 · ESP32 Smart OLED Companion",
      hook: "Can a miniature desk display blend turn-by-turn navigation with Spotify telemetry?",
      subtitle: "Navigator 01 · ESP32 Smart OLED Companion & Telemetry Display",
      category: "Hardware & IoT | ESP32 | OLED",
      discipline: "Embedded Firmware & IoT Display",
      status: "Active Build",
      description: "A multi-function smart desktop companion and vehicle telemetry unit built on an ESP32 and SSD1306 128x64 OLED display. Features capacitive touch switching between 7 procedural pixel-art animation states (Mochi, Orbit, Eyes, Compass, Hands, Flag). When paired with a phone via a companion web app, it relays real-time Google Maps turn-by-turn directions and distances over Wi-Fi. Simultaneously connects to Spotify API via OAuth bounce to render live track titles, artists, and playback state directly on the monochrome display.",
      heroImg: "assets/projects/navigator/hero.svg",
      teardownImg: "assets/projects/navigator/teardown.svg",
      teardownCaption: "SSD1306 I2C display wiring and multi-frame bitmap animation pipeline",
      madeWith: [
        "ESP32 Dual-Core (Wi-Fi + BLE)",
        "SSD1306 128x64 I2C OLED",
        "Capacitive Touch Sensor (GPIO 33)",
        "Spotify Web API (OAuth2 PKCE)",
        "Google Maps Geolocation Relay",
        "U8g2 Graphics Library"
      ],
      githubUrl: "https://github.com/lovhamic",
      specs: [
        { label: "Display Driver", val: "SSD1306 128x64 HW I2C (U8g2)" },
        { label: "Animation Engine", val: "7-Mode Procedural Bitmap FSM" },
        { label: "Touch Input", val: "GPIO 33 Capacitive Debounce 50ms" },
        { label: "Web Server", val: "ESP32 SoftAP WebServer(80)" }
      ],
      codeSnippet: `// Capacitive Touch State Transition across 7 Animation Frames
void handleTouchCycle() {
    bool touchState = (touchRead(TOUCH_PIN) < TOUCH_THRESHOLD);
    if (touchState && !lastTouchRead && (millis() - lastTouchChangeMs > TOUCH_DEBOUNCE_MS)) {
        currentAnimationMode = (currentAnimationMode + 1) % NUM_ANIMATIONS;
        lastTouchChangeMs = millis();
        u8g2.clearBuffer();
    }
    lastTouchRead = touchState;
}`
    },
    "spectrometer": {
      id: "spectrometer",
      numericId: 7,
      title: "PySpectrometer · Optical Emission Spectrum Analysis",
      hook: "Can a webcam and diffraction grating accurately measure light wavelengths?",
      subtitle: "PySpectrometer · Diffraction Optical Spectrum Analysis Suite",
      category: "Optics & Physics | Python | OpenCV",
      discipline: "Optical Physics & Computer Vision",
      status: "Bench Validated",
      description: "A precision optical emission spectroscopy suite built with Python, OpenCV, and SciPy to analyze spectral photographs captured through diffraction gratings. Features dual-point wavelength calibration (e.g. 405nm violet laser and 532nm green laser benchmarks) converting pixel spatial coordinates to absolute nanometers. Applies Savitzky-Golay digital filtering to eliminate sensor noise, runs PeakUtils detection algorithms to identify atomic emission lines, accumulates peak hold over exposure time, and exports calibrated CSV spectral plots.",
      heroImg: "assets/projects/spectrometer/hero.jpg",
      teardownImg: "assets/projects/spectrometer/spectrum.png",
      teardownCaption: "Optical bench test · 532nm laser emission diffraction line & live calibration spectrum",
      madeWith: [
        "Python 3 & Tkinter GUI",
        "OpenCV Video/Image Processing",
        "SciPy (Savitzky-Golay Filtering)",
        "PeakUtils Peak Detection",
        "Diffraction Grating Optics (1000 lines/mm)",
        "NumPy Numerical Array Math"
      ],
      githubUrl: "https://github.com/lovhamic",
      specs: [
        { label: "Wavelength Fit", val: "Two-Point Dual Laser Benchmark" },
        { label: "Filtering", val: "Savitzky-Golay Digital Window" },
        { label: "Peak Detector", val: "PeakUtils Centroid Interpolation" },
        { label: "Data Export", val: "Calibrated CSV + Matplotlib Plot" }
      ],
      codeSnippet: `// Dual-Point Nanometer Wavelength Calibration Curve
def compute_wavelength(x_pixel, calib_points=((72, 405), (304, 532))):
    (x1, w1), (x2, w2) = calib_points
    dispersion = (w2 - w1) / (x2 - x1) # nm per pixel
    return w1 + (x_pixel - x1) * dispersion

# Savitzky-Golay noise filtering & peak detection
smoothed_intensity = savgol_filter(raw_intensity, window_length=11, polyorder=3)
peak_indices = peakutils.indexes(smoothed_intensity, thres=0.15, min_dist=10)`
    },
    "webcamtracker": {
      id: "webcamtracker",
      numericId: 8,
      title: "Webcam Coordinate Tracker · Optical 2D Measuring",
      hook: "Can a standard overhead webcam become a sub-centimeter coordinate measuring machine?",
      subtitle: "Webcam Object Coordinate Tracker · 2D Metric Spatial Measurement",
      category: "Vision & Sensing | OpenCV | Python",
      discipline: "Computer Vision & Spatial Measurement",
      status: "Bench Validated",
      description: "A computer vision spatial tracking tool in Python and OpenCV that transforms any overhead camera—including mobile phone cameras streamed over Wi-Fi via IP video—into an optical 2D coordinate-measuring station. Using pinhole camera projection math [X_cm = (u - cx) * H / f], it maps pixel coordinates to physical centimeters relative to a centered virtual origin (0,0). Includes an interactive two-point ruler calibration tool with live cursor zoom inset to compute focal length f with sub-millimeter precision, tracking object contours in real time.",
      heroImg: "assets/projects/webcamtracker/hero.jpg",
      teardownImg: "assets/projects/webcamtracker/hero.jpg",
      teardownCaption: "Overhead optical tracking interface · Centimeter coordinate mapping & object tracking",
      madeWith: [
        "Python 3 & OpenCV",
        "NumPy Linear Algebra",
        "Pinhole Camera Geometry",
        "Wi-Fi IP Camera Stream (MJPEG/HTTP)",
        "Interactive Magnifier Zoom Inset",
        "JSON Calibration Persistence"
      ],
      githubUrl: "https://github.com/lovhamic",
      specs: [
        { label: "Projection Model", val: "Pinhole Geometry (X = (u - cx)*H/f)" },
        { label: "Calibration", val: "6X Magnified Ruler Inset (Key 'k')" },
        { label: "Motion Rejection", val: "MOG2 Background Subtraction" },
        { label: "Video Source", val: "Wi-Fi IP Camera (HTTP) / USB UVC" }
      ],
      codeSnippet: `// Overhead Pinhole Inverse Metric Projection
def pixel_to_world_cm(u, v, cx, cy, H_cm, focal_px):
    # Standard pinhole inverse transformation
    X_cm = (u - cx) * H_cm / focal_px
    Y_cm = (v - cy) * H_cm / focal_px
    resultant_cm = math.sqrt(X_cm**2 + Y_cm**2)
    return X_cm, Y_cm, resultant_cm`
    },
    "gitpatchwave": {
      id: "gitpatchwave",
      numericId: 9,
      title: "Git:Patch Wave · Wave Superposition Engine",
      hook: "Can trigonometric wave superposition be visualised through a Git version-control paradigm?",
      subtitle: "Git:Patch Wave · Wave Superposition & Interference Engine",
      category: "Simulation & Math | Python Flask | Canvas",
      discipline: "Mathematical Simulation & WebGL",
      status: "Active Build",
      description: "An interactive wave-superposition and harmonic interference simulator engineered with a dark Git-branch terminal paradigm. Users create equations as 'Branches' [e.g. A * sin(k*x - w*t)] and variables as 'Commits' [A, k, w], manipulating parameters with live sliders. A Python Flask backend uses NumPy vectorized mathematics to compute wave amplitudes across dynamic x-ranges, while a high-performance HTML5 Canvas renders individual harmonics and overlays their merged superposition sum in real time with pan, zoom, and time-evolution animation.",
      heroImg: "assets/projects/gitpatchwave/hero.svg",
      teardownImg: "assets/projects/gitpatchwave/teardown.svg",
      teardownCaption: "Live canvas wave interference solver with dynamic branch equation parser",
      madeWith: [
        "Python 3 & Flask",
        "NumPy Vectorized Mathematics",
        "HTML5 Canvas & Vanilla JS",
        "Standalone PyInstaller Desktop Binary",
        "Custom Expression Parser",
        "Real-Time Harmonic Synthesis"
      ],
      githubUrl: "https://github.com/lovhamic",
      specs: [
        { label: "Math Engine", val: "NumPy Vectorized Linspace (1000 pts)" },
        { label: "Frontend", val: "HTML5 Canvas 60 FPS RequestAnimationFrame" },
        { label: "Packaging", val: "Standalone PyInstaller Executable" },
        { label: "Interaction", val: "Dynamic Git Branch Equation Tree" }
      ],
      codeSnippet: `// NumPy Vectorized Wave Calculation Endpoint
@app.route('/calculate_wave')
def calculate_wave():
    min_x = float(request.args.get('minX', -15))
    max_x = float(request.args.get('maxX', 15))
    t_val = float(request.args.get('t', 0))
    x = np.linspace(min_x, max_x, 1000)

    total_y = np.zeros_like(x)
    for eq_str in active_branches:
        y = eval(sanitize(eq_str), {"x": x, "t": t_val, "np": np})
        total_y += y
    return jsonify({"superposition": total_y.tolist()})`
    },
    "robotdog": {
      id: "robotdog",
      numericId: 10,
      title: "Voice Quadruped · On-Device AI Robot Dog",
      hook: "Can an ultra-compact microcontroller run neural wake-word detection for quadruped gait?",
      subtitle: "Voice Quadruped · On-Device Neural Speech Recognition Robot Dog",
      category: "Robotics & Audio | XIAO ESP32S3 | ESP-SR",
      discipline: "Acoustic Neural Models & Robotics",
      status: "Active Build",
      description: "An autonomous voice-controlled quadruped robot powered by a Seeed Studio XIAO ESP32S3 (with onboard PSRAM) and an INMP441 digital I2S MEMS microphone. Running Espressif's ESP-SR speech recognition neural model locally in firmware without internet access, it detects the acoustic wake-word 'Hi ESP' and processes six kinematic command routines ('good boy', 'sit down', 'lie down', 'stretch', 'walk', 'dance'). Drives 4 micro-servos through parameterized inverse gait kinematics with real-time audio gain calibration.",
      heroImg: "assets/projects/robotdog/hero.jpg",
      teardownImg: "assets/projects/robotdog/teardown.mp4",
      teardownCaption: "Voice-activated 8-DOF quadruped robot dog walking demo & gait kinematics",
      madeWith: [
        "Seeed Studio XIAO ESP32S3",
        "INMP441 I2S MEMS Digital Microphone",
        "ESP-SR On-Device Neural Model",
        "4x Micro Servos Kinematic Gait",
        "FreeRTOS Multi-Tasking Firmware",
        "Separate 5V High-Current Rail"
      ],
      githubUrl: "https://github.com/lovhamic",
      specs: [
        { label: "Core Board", val: "Seeed Studio XIAO ESP32S3 (OPI PSRAM)" },
        { label: "Microphone", val: "INMP441 I2S 24-bit Digital MEMS" },
        { label: "Speech Model", val: "On-Chip ESP-SR (Wake-Word: 'Hi ESP')" },
        { label: "Gait Controller", val: "4-Channel PWM Kinematic Trot Engine" }
      ],
      codeSnippet: `// On-Device Neural Wake-Word & Kinematic Dispatch
void audioTask(void *pvParameters) {
    while (true) {
        size_t bytesRead = 0;
        i2s_read(I2S_NUM_0, audioBuffer, sizeof(audioBuffer), &bytesRead, portMAX_DELAY);
        
        int cmd = esp_sr_process(audioBuffer, bytesRead);
        if (cmd == CMD_WAKE_WORD) {
            triggerPose(POSE_ALERT);
        } else if (cmd == CMD_WALK) {
            executeTrotGait(STEPS_FORWARD);
        }
    }
}`
    }
  };

  // Map numerical ID keys (1..10) to the same object for backwards compatibility
  Object.values(projectDatabase).forEach(item => {
    projectDatabase[item.numericId] = item;
  });

  // ---------------------------------------------------------------------------
  // 6b. BUILD DETAIL PAGE INITIALIZER (build.html dynamic renderer)
  // ---------------------------------------------------------------------------
  window.initBuildDetailPage = function() {
    const params = new URLSearchParams(window.location.search);
    const requestedId = params.get("id") || "blackbox";
    const project = projectDatabase[requestedId] || projectDatabase["blackbox"];
    if (!project) return;

    // Set page title
    document.title = `${project.subtitle} · guywithyellowscrewdriver`;

    // Elements
    const elHook = document.getElementById("build-hook");
    const elSubtitle = document.getElementById("build-subtitle");
    const elHeroImg = document.getElementById("build-hero-img");
    const elDesc = document.getElementById("build-description");
    const elTeardownImg = document.getElementById("build-teardown-img");
    const elTeardownCap = document.getElementById("build-teardown-caption");
    const elMadeWith = document.getElementById("build-made-with-list");
    const elGithub = document.getElementById("build-github-link");
    const elDiscipline = document.getElementById("build-spec-discipline");
    const elStatus = document.getElementById("build-spec-status");
    const elCode = document.getElementById("build-code-snippet");
    const elCopyBtn = document.getElementById("build-copy-code-btn");
    const elPrevLink = document.getElementById("build-prev-link");
    const elNextLink = document.getElementById("build-next-link");
    const elQuickPills = document.getElementById("build-quick-pills");

    // Animated Typography Entrance & Interaction for Build Titles
    animateBuildTitles(project);
    if (elSubtitle) elSubtitle.textContent = project.subtitle;
    if (elHeroImg) {
      elHeroImg.src = project.heroImg;
      elHeroImg.alt = project.subtitle;
    }
    if (elDesc) {
      if (project.descriptionHtml) {
        elDesc.innerHTML = project.descriptionHtml;
      } else if (project.description) {
        elDesc.innerHTML = project.description
          .split("\n\n")
          .map(p => `<p>${p.replace(/\n/g, "<br>")}</p>`)
          .join("");
      }
    }
    const teardownContainer = document.getElementById("build-teardown-container");
    if (teardownContainer && project.teardownImg) {
      if (project.teardownImg.endsWith(".mp4")) {
        teardownContainer.innerHTML = `
          <video id="build-teardown-video" 
                 src="${project.teardownImg}" 
                 controls 
                 autoplay 
                 muted 
                 loop 
                 playsinline 
                 class="w-full h-auto block object-contain">
          </video>
        `;
        const video = document.getElementById("build-teardown-video");
        if (video) {
          const applyVideoRatio = () => {
            if (video.videoWidth && video.videoHeight) {
              teardownContainer.style.aspectRatio = `${video.videoWidth} / ${video.videoHeight}`;
            }
          };
          video.addEventListener("loadedmetadata", applyVideoRatio, { once: true });
        }
      } else {
        teardownContainer.innerHTML = `
          <img id="build-teardown-img" 
               src="${project.teardownImg}" 
               alt="${project.teardownCaption || 'Component Breakdown'}" 
               class="w-full h-auto block object-contain transition-all duration-300">
        `;
        const img = document.getElementById("build-teardown-img");
        if (img) {
          const applyRatio = () => {
            if (img.naturalWidth && img.naturalHeight) {
              teardownContainer.style.aspectRatio = `${img.naturalWidth} / ${img.naturalHeight}`;
            }
          };
          if (img.complete && img.naturalWidth) {
            applyRatio();
          } else {
            img.addEventListener("load", applyRatio, { once: true });
          }
        }
      }
    }
    if (elTeardownCap) elTeardownCap.textContent = project.teardownCaption;
    if (elDiscipline) elDiscipline.textContent = project.discipline;
    if (elStatus) elStatus.textContent = project.status;
    if (elCode) elCode.textContent = project.codeSnippet;

    if (elMadeWith) {
      elMadeWith.innerHTML = project.madeWith.map(item => `
        <li class="py-3 font-mono text-xs sm:text-sm font-semibold text-neutral-900 flex items-center justify-between">
          <span>${item}</span>
          <span class="w-1.5 h-1.5 bg-neutral-300 rounded-full"></span>
        </li>
      `).join("");
    }

    if (elGithub) {
      elGithub.href = project.githubUrl;
      elGithub.title = `View source code for ${project.title}`;
    }

    if (elCopyBtn && elCode) {
      elCopyBtn.addEventListener("click", () => {
        navigator.clipboard.writeText(project.codeSnippet).then(() => {
          const original = elCopyBtn.textContent;
          elCopyBtn.textContent = "Copied to Clipboard!";
          Sound.relay();
          setTimeout(() => { elCopyBtn.textContent = original; }, 1800);
        });
      });
    }

    // Previous & Next navigation
    const keys = ["blackbox", "memeglove", "cockroach", "watersim", "robotarm", "navigator", "spectrometer", "webcamtracker", "gitpatchwave", "robotdog"];
    const currentIndex = keys.indexOf(project.id);
    const prevKey = keys[(currentIndex - 1 + keys.length) % keys.length];
    const nextKey = keys[(currentIndex + 1) % keys.length];

    if (elPrevLink) {
      elPrevLink.href = `build.html?id=${prevKey}`;
      elPrevLink.innerHTML = `← Prev: ${projectDatabase[prevKey].title.split("·")[0].trim()}`;
    }
    if (elNextLink) {
      elNextLink.href = `build.html?id=${nextKey}`;
      elNextLink.innerHTML = `Next: ${projectDatabase[nextKey].title.split("·")[0].trim()} →`;
    }

    // Quick jump pills
    if (elQuickPills) {
      elQuickPills.innerHTML = keys.map((k, idx) => {
        const item = projectDatabase[k];
        const isCurrent = (k === project.id);
        const num = String(idx + 1).padStart(2, '0');
        const shortName = item.title.split("·")[0].trim();
        return `
          <a href="build.html?id=${k}" 
             class="px-2.5 py-1 text-[11px] font-mono font-bold transition-all ${
               isCurrent 
                 ? 'bg-black text-white border border-black shadow-[2px_2px_0px_#ffd600]' 
                 : 'bg-neutral-100 hover:bg-neutral-200 text-neutral-700 border border-neutral-300'
             }">
            ${num} ${shortName}
          </a>
        `;
      }).join("");
    }

    Sound.relay();
  };

  // ---------------------------------------------------------------------------
  // INTERACTIVE KINETIC TITLE ANIMATION (Emil Kowalski Philosophy)
  // ---------------------------------------------------------------------------
  function animateBuildTitles(project) {
    const elHook = document.getElementById("build-hook");
    const elSubtitle = document.getElementById("build-subtitle");
    if (!elHook) return;

    const rawText = project ? project.hook : elHook.textContent.trim();
    const words = rawText.split(/\s+/).filter(Boolean);

    // Wrap words in kinetic spans while preserving natural spacing
    elHook.innerHTML = words.map((w, idx) => `
      <span class="build-title-word" data-word-idx="${idx}">${w}</span>
    `).join(" ");

    const wordEls = elHook.querySelectorAll(".build-title-word");
    const prefersReducedMotion = window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches;

    if (!prefersReducedMotion) {
      // Hardware-accelerated WAAPI Stagger Entrance
      wordEls.forEach((wordEl, idx) => {
        wordEl.animate([
          { opacity: 0, transform: "translateY(16px) scale(0.97)" },
          { opacity: 1, transform: "translateY(0) scale(1)" }
        ], {
          duration: 320,
          delay: idx * 24,
          easing: "cubic-bezier(0.23, 1, 0.32, 1)",
          fill: "forwards"
        });
      });

      // Subtitle entrance
      if (elSubtitle) {
        elSubtitle.animate([
          { opacity: 0, transform: "translateY(8px)" },
          { opacity: 1, transform: "translateY(0)" }
        ], {
          duration: 380,
          delay: 100,
          easing: "cubic-bezier(0.23, 1, 0.32, 1)",
          fill: "forwards"
        });
      }
    }

    // Interactive scrub & magnetic neighbor deflection
    wordEls.forEach((wordEl, idx) => {
      wordEl.addEventListener("mouseenter", () => {
        wordEls.forEach(el => el.classList.remove("neighbor-lift"));
        const prev = wordEls[idx - 1];
        const next = wordEls[idx + 1];
        if (prev) prev.classList.add("neighbor-lift");
        if (next) next.classList.add("neighbor-lift");

        // Subtle micro-pitch acoustic response
        Sound.microStep(1600 + (idx % 8) * 85);
      });

      wordEl.addEventListener("mouseleave", () => {
        wordEls.forEach(el => el.classList.remove("neighbor-lift"));
      });

      // Click: send an elastic ripple wave outward through the sentence
      wordEl.addEventListener("click", () => {
        Sound.chirp();
        wordEls.forEach((el, i) => {
          const dist = Math.abs(i - idx);
          setTimeout(() => {
            el.animate([
              { transform: "translateY(-6px) scale(1.04)" },
              { transform: "translateY(0) scale(1)" }
            ], {
              duration: 250,
              easing: "cubic-bezier(0.23, 1, 0.32, 1)"
            });
          }, dist * 28);
        });
      });
    });
  }

  function initCardTiltAndModal() {
    const cards = document.querySelectorAll(".work-card-tilt");

    cards.forEach((card) => {
      let rect = null;

      card.addEventListener("mouseenter", () => {
        rect = card.getBoundingClientRect();
      });

      card.addEventListener("mousemove", (e) => {
        if (!rect) rect = card.getBoundingClientRect();
        const x = e.clientX - rect.left;
        const y = e.clientY - rect.top;
        const centerX = rect.width / 2;
        const centerY = rect.height / 2;

        const rotX = ((y - centerY) / centerY) * -7;
        const rotY = ((x - centerX) / centerX) * 7;

        card.style.transform = `perspective(1000px) rotateX(${rotX}deg) rotateY(${rotY}deg) scale3d(1.015, 1.015, 1.015)`;
      });

      card.addEventListener("mouseleave", () => {
        card.style.transform = "perspective(1000px) rotateX(0deg) rotateY(0deg) scale3d(1, 1, 1)";
        rect = null;
      });

      // Direct navigation to the full build breakdown
      card.addEventListener("click", (e) => {
        const id = card.getAttribute("data-project-id");
        if (id) {
          Sound.relay();
          if (card.tagName.toLowerCase() !== "a") {
            window.location.href = `build.html?id=${id}`;
          }
        }
      });
    });
  }

  // ---------------------------------------------------------------------------
  // 7. LIVE BENCH TELEMETRY SIMULATOR (Field Logs Status Widget)
  // ---------------------------------------------------------------------------
  function initBenchTelemetry() {
    const elVoltage = document.getElementById("telemetry-voltage");
    const elCurrent = document.getElementById("telemetry-current");
    const elPackets = document.getElementById("telemetry-packets");
    const btnSpike = document.getElementById("telemetry-spike-btn");
    const statusLed = document.getElementById("telemetry-status-led");

    let isSpiking = false;

    setInterval(() => {
      if (!isSpiking) {
        // Natural small jitter
        const v = 24.12 + (Math.random() - 0.5) * 0.06;
        const a = 1.84 + (Math.random() - 0.5) * 0.12;
        state.telemetry.packets += Math.floor(Math.random() * 4) + 1;

        if (elVoltage) elVoltage.textContent = `${v.toFixed(2)} V`;
        if (elCurrent) elCurrent.textContent = `${a.toFixed(2)} A`;
        if (elPackets) elPackets.textContent = state.telemetry.packets.toLocaleString();
      }
    }, 600);

    if (btnSpike) {
      btnSpike.addEventListener("click", () => {
        isSpiking = true;
        Sound.relay();

        if (statusLed) {
          statusLed.classList.remove("bg-emerald-500");
          statusLed.classList.add("bg-amber-500", "animate-ping");
        }
        if (elVoltage) elVoltage.textContent = "22.45 V";
        if (elCurrent) elCurrent.textContent = "18.62 A";

        setTimeout(() => {
          if (elVoltage) elVoltage.textContent = "23.80 V";
          if (elCurrent) elCurrent.textContent = "4.20 A";
        }, 500);

        setTimeout(() => {
          isSpiking = false;
          if (statusLed) {
            statusLed.classList.remove("bg-amber-500", "animate-ping");
            statusLed.classList.add("bg-emerald-500");
          }
          Sound.probe(1400);
        }, 1200);
      });
    }
  }

  // ---------------------------------------------------------------------------
  // 9. FILTER PILLS
  // ---------------------------------------------------------------------------
  function initFilterPills() {
    const pills = document.querySelectorAll(".filter-pill");
    const cards = document.querySelectorAll(".work-card");

    pills.forEach((pill) => {
      pill.addEventListener("click", () => {
        const filter = pill.getAttribute("data-filter");

        pills.forEach((p) => {
          p.classList.remove("bg-black", "text-white");
          p.classList.add("bg-white", "text-black");
        });
        pill.classList.add("bg-black", "text-white");
        pill.classList.remove("bg-white", "text-black");

        Sound.click();

        cards.forEach((card) => {
          const cat = card.getAttribute("data-category");
          if (filter === "all" || cat === filter) {
            card.style.display = "block";
            card.style.opacity = "0";
            card.style.transform = "translateY(8px)";
            setTimeout(() => {
              card.style.transition = "opacity 240ms cubic-bezier(0.16, 1, 0.3, 1), transform 240ms cubic-bezier(0.16, 1, 0.3, 1)";
              card.style.opacity = "1";
              card.style.transform = "translateY(0)";
            }, 10);
          } else {
            card.style.display = "none";
          }
        });
      });
    });
  }

  // ---------------------------------------------------------------------------
  // 10. INTERACTIVE KINETIC HEADLINE (guywithyellowscrewdriver)
  // ---------------------------------------------------------------------------
  function initInteractiveTitle() {
    const titleEl = document.getElementById("hero-interactive-title");
    if (!titleEl) return;

    const chars = titleEl.querySelectorAll(".title-char");
    const caliperHud = document.getElementById("title-caliper-hud");
    const screwDot = titleEl.querySelector(".title-screw-dot");
    if (!chars.length) return;

    let isCalibrating = false;
    let isDragging = false;
    let dragStartX = 0;
    let currentKerning = -0.045;
    let lastCharIndex = -1;

    // A. Proximity Spring Wave on Mouse Move
    titleEl.addEventListener("mousemove", (e) => {
      if (isCalibrating || isDragging) return;

      let closestDist = Infinity;
      let closestIdx = -1;

      chars.forEach((char, idx) => {
        const rect = char.getBoundingClientRect();
        const charCenterX = rect.left + rect.width / 2;
        const charCenterY = rect.top + rect.height / 2;
        const dx = e.clientX - charCenterX;
        const dy = e.clientY - charCenterY;
        const dist = Math.hypot(dx, dy);

        if (dist < closestDist) {
          closestDist = dist;
          closestIdx = idx;
        }

        const maxDist = 130;
        if (dist < maxDist) {
          const factor = 1 - dist / maxDist;
          // Smoothstep
          const smooth = factor * factor * (3 - 2 * factor);
          const transY = -smooth * 15;
          const scale = 1 + smooth * 0.12;
          const rot = (dx / maxDist) * -6;

          char.style.transform = `translateY(${transY.toFixed(1)}px) scale(${scale.toFixed(3)}) rotate(${rot.toFixed(1)}deg)`;

          if (char.classList.contains("char-yellow")) {
            if (factor > 0.3) char.classList.add("highlighted");
            else char.classList.remove("highlighted");
          }
        } else {
          char.style.transform = "";
          if (char.classList.contains("char-yellow")) {
            char.classList.remove("highlighted");
          }
        }
      });

      // Micro-stepper tone when crossing letters
      if (closestIdx !== -1 && closestIdx !== lastCharIndex && closestDist < 80) {
        lastCharIndex = closestIdx;
        const pitch = 440 * Math.pow(2, closestIdx / 23);
        Sound.microStep(pitch);
      }
    });

    // B. Reset on Mouse Leave
    titleEl.addEventListener("mouseleave", () => {
      if (isCalibrating || isDragging) return;
      chars.forEach((char) => {
        char.style.transform = "";
        if (char.classList.contains("char-yellow")) {
          char.classList.remove("highlighted");
        }
      });
      lastCharIndex = -1;
    });

    // C. Click Calibration: Hardware Glyph Scramble & Torque Lock
    titleEl.addEventListener("click", () => {
      if (isCalibrating) return;
      isCalibrating = true;
      Sound.relay();

      if (caliperHud) {
        caliperHud.textContent = "[CALIBRATING TORQUE MATRIX // SCANNING 23 BYTES...]";
      }

      if (screwDot) {
        screwDot.style.transform = "rotate(360deg) scale(1.3)";
      }

      const glyphPool = ["0", "1", "x", "7", "E", "9", "B", "4", "A", "F", "#", "°", "Ω", "μ", "T", "8"];

      chars.forEach((char, idx) => {
        const originalChar = char.getAttribute("data-char") || char.textContent;
        let counter = 0;
        const totalScrambles = 7 + idx;

        char.classList.add("scrambled");
        char.style.transform = "translateY(-6px) scale(1.08)";

        const interval = setInterval(() => {
          char.textContent = glyphPool[Math.floor(Math.random() * glyphPool.length)];
          counter++;

          if (counter >= totalScrambles) {
            clearInterval(interval);
            char.textContent = originalChar;
            char.classList.remove("scrambled");
            char.style.transform = "translateY(0px) scale(1)";

            // Step tone on lock
            Sound.microStep(320 + idx * 24);

            // When last character locks
            if (idx === chars.length - 1) {
              setTimeout(() => {
                Sound.chirp();
                if (caliperHud) {
                  caliperHud.textContent = "[TORQUE LOCKED: 0.42 Nm · 23 BYTES CALIBRATED · 100% NOMINAL]";
                }
                if (screwDot) {
                  screwDot.style.transform = "rotate(0deg) scale(1)";
                }
                setTimeout(() => {
                  if (caliperHud) {
                    caliperHud.textContent = "[KERNING: -0.045em · TORQUE: NOMINAL · CLICK TO CALIBRATE]";
                  }
                  isCalibrating = false;
                }, 2800);
              }, 60);
            }
          }
        }, 36);
      });
    });

    // D. Drag-to-Adjust Kerning / Tracking
    titleEl.addEventListener("mousedown", (e) => {
      isDragging = true;
      dragStartX = e.clientX;
      titleEl.style.transition = "none";
    });

    window.addEventListener("mousemove", (e) => {
      if (!isDragging) return;
      const dx = e.clientX - dragStartX;
      currentKerning = Math.max(-0.065, Math.min(0.04, -0.045 + dx * 0.0003));
      titleEl.style.letterSpacing = `${currentKerning.toFixed(4)}em`;
      if (caliperHud) {
        caliperHud.textContent = `[DYNAMIC KERNING: ${currentKerning.toFixed(3)}em · TIGHTEN/LOOSEN]`;
      }
    });

    window.addEventListener("mouseup", () => {
      if (!isDragging) return;
      isDragging = false;
      titleEl.style.transition = "letter-spacing 360ms cubic-bezier(0.34, 1.56, 0.64, 1)";
      titleEl.style.letterSpacing = "-0.045em";
      currentKerning = -0.045;
      Sound.probe(900);
      setTimeout(() => {
        titleEl.style.transition = "";
        if (caliperHud && !isCalibrating) {
          caliperHud.textContent = "[KERNING: -0.045em · TORQUE: NOMINAL · CLICK TO CALIBRATE]";
        }
      }, 360);
    });
  }

  // ---------------------------------------------------------------------------
  // 11. INTERACTIVE "JACK OF ALL TRADES" KINETIC TEXT ANIMATION
  // ---------------------------------------------------------------------------
  function initJackOfAllTrades() {
    const container = document.getElementById("jack-trades-interactive");
    if (!container) return;

    const chars = container.querySelectorAll(".jack-char");
    const brackets = document.querySelectorAll(".quote-bracket");
    let isRippling = false;
    let lastCharIndex = -1;

    // A. Proximity Spring Wave on Hover
    container.addEventListener("mousemove", (e) => {
      if (isRippling) return;

      let closestDist = Infinity;
      let closestIdx = -1;

      chars.forEach((char, idx) => {
        const rect = char.getBoundingClientRect();
        const charCenterX = rect.left + rect.width / 2;
        const charCenterY = rect.top + rect.height / 2;
        const dx = e.clientX - charCenterX;
        const dy = e.clientY - charCenterY;
        const dist = Math.hypot(dx, dy);

        if (dist < closestDist) {
          closestDist = dist;
          closestIdx = idx;
        }

        const maxDist = 70;
        if (dist < maxDist) {
          const factor = 1 - dist / maxDist;
          const smooth = factor * factor * (3 - 2 * factor);
          const transY = -smooth * 8;
          const scale = 1 + smooth * 0.1;

          char.style.transform = `translateY(${transY.toFixed(1)}px) scale(${scale.toFixed(3)})`;
          char.style.color = "#000000";
        } else {
          char.style.transform = "";
          char.style.color = "";
        }
      });

      // Subtle stepper tick when traversing letters
      if (closestIdx !== -1 && closestIdx !== lastCharIndex && closestDist < 45) {
        lastCharIndex = closestIdx;
        Sound.microStep(560 + closestIdx * 18);
      }
    });

    container.addEventListener("mouseleave", () => {
      if (isRippling) return;
      chars.forEach((char) => {
        char.style.transform = "";
        char.style.color = "";
      });
      lastCharIndex = -1;
    });

    // B. Elastic Kinetic Ripple Wave on Click (No Text Change)
    container.addEventListener("click", () => {
      if (isRippling) return;
      isRippling = true;
      Sound.click();

      // Brackets spring pulse
      brackets.forEach((b, i) => {
        const dir = i === 0 ? -6 : 6;
        b.style.transform = `translateX(${dir}px)`;
        setTimeout(() => {
          b.style.transform = "";
        }, 280);
      });

      // Wave ripple through each character
      chars.forEach((char, idx) => {
        setTimeout(() => {
          char.style.transition = "transform 140ms ease-out, color 140ms ease";
          char.style.transform = "translateY(-10px) scale(1.18)";
          char.style.color = "var(--screwdriver-yellow)";
          Sound.microStep(480 + idx * 24);

          setTimeout(() => {
            char.style.transition = "transform 260ms cubic-bezier(0.34, 1.56, 0.64, 1), color 200ms ease";
            char.style.transform = "translateY(0px) scale(1)";
            char.style.color = "";

            if (idx === chars.length - 1) {
              setTimeout(() => {
                isRippling = false;
              }, 260);
            }
          }, 140);
        }, idx * 24);
      });
    });
  }

  // ---------------------------------------------------------------------------
  // 12. INTERACTIVE AXIOM QUOTES (Stress Breaking Point & Unexpected Outcomes)
  // ---------------------------------------------------------------------------
  function initAxiomCards() {
    const cardBreak = document.getElementById("axiom-card-breaking");
    const cardOutcome = document.getElementById("axiom-card-outcomes");

    // 1. Setup Card 1: Breaking Point
    if (cardBreak) {
      const quoteEl = document.getElementById("axiom-quote-1");
      const strainBar = document.getElementById("axiom-strain-bar");
      const readout = document.getElementById("axiom-stress-readout");

      // Wrap words in spans for individual deflection
      if (quoteEl) {
        const rawText = quoteEl.textContent.trim().replace(/^“|”$/g, "");
        quoteEl.innerHTML = "&ldquo;" + rawText.split(/\s+/).map(w => `<span class="axiom-word">${w}</span>`).join(" ") + "&rdquo;";
      }

      const words = quoteEl ? quoteEl.querySelectorAll(".axiom-word") : [];
      let isBroken = false;
      let lastStepTone = 0;

      cardBreak.addEventListener("mousemove", (e) => {
        if (isBroken) return;
        const rect = cardBreak.getBoundingClientRect();
        const pct = Math.max(8, Math.min(100, Math.round(((e.clientX - rect.left) / rect.width) * 100)));

        if (strainBar) strainBar.style.transform = `scaleX(${pct / 100})`;
        if (readout) {
          readout.textContent = `LOAD: ${pct}% · ${pct > 80 ? 'CRITICAL STRAIN' : 'STABLE'}`;
          readout.style.color = pct > 80 ? '#b45309' : '';
        }

        // Stress jitter when load > 75%
        if (pct > 75) {
          words.forEach(w => {
            const jx = (Math.random() - 0.5) * 3;
            const jy = (Math.random() - 0.5) * 3;
            w.style.transform = `translate(${jx.toFixed(1)}px, ${jy.toFixed(1)}px)`;
          });
          if (Date.now() - lastStepTone > 100) {
            lastStepTone = Date.now();
            Sound.microStep(700 + pct * 2);
          }
        } else {
          words.forEach(w => { w.style.transform = ""; });
        }
      });

      cardBreak.addEventListener("mouseleave", () => {
        if (isBroken) return;
        if (strainBar) strainBar.style.transform = "scaleX(0.12)";
        if (readout) {
          readout.textContent = "LOAD: 12% · STABLE";
          readout.style.color = "";
        }
        words.forEach(w => { w.style.transform = ""; });
      });

      cardBreak.addEventListener("click", () => {
        if (isBroken) return;
        isBroken = true;
        Sound.relay();
        setTimeout(() => Sound.probe(2200), 40);

        cardBreak.classList.add("shattered");
        if (strainBar) strainBar.style.transform = "scaleX(1)";
        if (readout) {
          readout.textContent = "BREAKING POINT ACHIEVED // 48.2 MPa";
          readout.style.color = "#d97706";
        }

        // Explosive spring deflection
        words.forEach((w) => {
          const dy = -6 - Math.random() * 8;
          const rot = (Math.random() - 0.5) * 8;
          w.style.transform = `translateY(${dy}px) rotate(${rot}deg) scale(1.06)`;
          w.style.color = "var(--screwdriver-yellow)";
        });

        setTimeout(() => {
          words.forEach(w => {
            w.style.transform = "";
            w.style.color = "";
          });
          cardBreak.classList.remove("shattered");
          if (readout) {
            readout.textContent = "SYSTEM NOMINAL // RESET";
            readout.style.color = "";
          }
          if (strainBar) strainBar.style.transform = "scaleX(0.12)";
          isBroken = false;
        }, 1800);
      });
    }

    // 2. Setup Card 2: Unexpected Outcomes
    if (cardOutcome) {
      const quoteEl = document.getElementById("axiom-quote-2");
      const outcomeBar = document.getElementById("axiom-outcome-bar");
      const readout = document.getElementById("axiom-outcome-readout");

      if (quoteEl) {
        const rawText = quoteEl.textContent.trim().replace(/^“|”$/g, "");
        quoteEl.innerHTML = "&ldquo;" + rawText.split(/\s+/).map(w => `<span class="axiom-word">${w}</span>`).join(" ") + "&rdquo;";
      }

      const words = quoteEl ? quoteEl.querySelectorAll(".axiom-word") : [];
      let isProbing = false;

      cardOutcome.addEventListener("mousemove", (e) => {
        if (isProbing) return;
        const rect = cardOutcome.getBoundingClientRect();
        const pct = Math.max(15, Math.min(100, Math.round(((e.clientX - rect.left) / rect.width) * 100)));
        if (outcomeBar) outcomeBar.style.transform = `scaleX(${pct / 100})`;

        // Wave lift near cursor
        words.forEach(w => {
          const wRect = w.getBoundingClientRect();
          const dist = Math.abs(e.clientX - (wRect.left + wRect.width / 2));
          if (dist < 80) {
            const f = 1 - dist / 80;
            w.style.transform = `translateY(-${f * 5}px)`;
          } else {
            w.style.transform = "";
          }
        });
      });

      cardOutcome.addEventListener("mouseleave", () => {
        if (isProbing) return;
        if (outcomeBar) outcomeBar.style.transform = "scaleX(0.15)";
        words.forEach(w => { w.style.transform = ""; });
      });

      cardOutcome.addEventListener("click", () => {
        if (isProbing) return;
        isProbing = true;
        Sound.chirp();

        if (outcomeBar) outcomeBar.style.transform = "scaleX(1)";
        if (readout) {
          readout.textContent = "UNEXPECTED DATA DETECTED // +4.28σ";
          readout.style.color = "#059669";
        }

        // Ripple pulse through words
        words.forEach((w, idx) => {
          setTimeout(() => {
            w.style.transform = "translateY(-8px) scale(1.12)";
            w.style.color = "var(--screwdriver-yellow)";
            Sound.microStep(520 + idx * 24);

            setTimeout(() => {
              w.style.transform = "";
              w.style.color = "";
            }, 180);
          }, idx * 22);
        });

        setTimeout(() => {
          if (outcomeBar) outcomeBar.style.transform = "scaleX(0.15)";
          if (readout) {
            readout.textContent = "STATUS: OBSERVING";
            readout.style.color = "";
          }
          isProbing = false;
        }, 1900);
      });
    }
  }


  // ---------------------------------------------------------------------------
  // 12. JOURNAL SYSTEM: DATABASE, DETAIL PAGE & THUMBNAIL 3D MOTION
  // ---------------------------------------------------------------------------
  const JOURNAL_DATABASE = {
  "claude-hackathon": {
    "id": "claude-hackathon",
    "numericId": 1,
    "folder": "claude hackathon ( oct 3 2026)",
    "title": "Hacking Human Ability: Taking First Place at Superhuman Lab",
    "date": "03 October 2026",
    "category": "Hackathon & Assistive AI",
    "location": "TinkerSpace, Calicut",
    "award": "First Place Trophy",
    "badge": "WINNER · 1ST PLACE",
    "md": "hacking_human_ability.md",
    "thumb": "assets/journals/claude-hackathon/thumb.jpg",
    "photos": [
      {
        "src": "assets/journals/claude-hackathon/photo-1.jpg",
        "caption": "Bagging first place trophy with the team at TinkerSpace Calicut"
      },
      {
        "src": "assets/journals/claude-hackathon/photo-2.jpg",
        "caption": "Hardware prototyping setup, wire harnesses and CAD testing"
      }
    ],
    "excerpt": "Our team just bagged first place at the Superhuman Lab hackathon at TinkerSpace Calicut! We spent the first weekend of October completely immersed in this event, and it wasn't your usual demo-day...",
    "paragraphs": [
      "Our team just bagged first place at the Superhuman Lab hackathon at TinkerSpace Calicut! We spent the first weekend of October completely immersed in this event, and it wasn't your usual demo-day theater. The whole goal was to hack human ability by using AI and hardware to turn assistive tech into actual upgrades instead of just basic medical devices. It was an amazing environment with engineers, designers, and people with lived experiences sitting down together to build prototypes that actually matter.",
      "After 48 hours of heavy CAD modeling, wiring up microcontrollers, and surviving on basically zero sleep, seeing our project take the top spot felt incredible. It was the perfect chance to put my usual electronics and 3D printing tinkering into something with a real, tangible impact. Really proud of everyone on the team for pulling this build together over the weekend."
    ]
  },
  "walking-ferns": {
    "id": "walking-ferns",
    "numericId": 2,
    "folder": "walking ferns (sep 19 2026)",
    "title": "Experiencing Outdoor Learning: Volunteering with Walking Ferns",
    "date": "19 September 2026",
    "category": "Field Volunteering & Mentorship",
    "location": "Calicut Outskirts",
    "award": "Community Volunteer",
    "badge": "FIELD MENTORSHIP",
    "md": "walking_ferns_volunteer_journal.md",
    "thumb": "assets/journals/walking-ferns/thumb.jpg",
    "photos": [
      {
        "src": "assets/journals/walking-ferns/photo-1.jpg",
        "caption": "Mentoring and climbing trees with children in nature"
      },
      {
        "src": "assets/journals/walking-ferns/photo-2.jpg",
        "caption": "Group selfies and shared outdoor curiosity with parents and kids"
      },
      {
        "src": "assets/journals/walking-ferns/photo-3.jpg",
        "caption": "Indoor huddles and experiential nature discovery activities"
      }
    ],
    "excerpt": "Spending the day volunteering with Walking Ferns was a great experience. The initiative focuses on experiential, outdoor learning, helping kids build curiosity by getting them out of formal class...",
    "paragraphs": [
      "Spending the day volunteering with Walking Ferns was a great experience. The initiative focuses on experiential, outdoor learning, helping kids build curiosity by getting them out of formal classrooms and into nature. It was really interesting to step into a mentoring role in such an unstructured environment, where the focus is on letting children explore and figure things out hands-on rather than just feeding them information.",
      "The day was a mix of quiet indoor moments and a lot of outdoor energy. We spent time sitting on the floor in group huddles for shared activities, but the highlight was definitely getting outside and climbing trees with the kids. It was a very grounded, community-driven space, and just hanging out in the branches and taking group selfies with the parents and children made the whole learning process feel completely natural and fun."
    ]
  },
  "useless-project": {
    "id": "useless-project",
    "numericId": 3,
    "folder": "usless project( sep 12 2026)",
    "title": "Why I Built a Useless Cyber-Glove (And Won Second Place)",
    "date": "12 September 2026",
    "category": "Hardware Hacking & Wearables",
    "location": "TinkerSpace, Calicut",
    "award": "Second Place Award",
    "badge": "WINNER · 2ND PLACE",
    "md": "useless_projects_hackathon_report.md",
    "thumb": "assets/journals/useless-project/thumb.jpg",
    "photos": [
      {
        "src": "assets/journals/useless-project/photo-1.jpg",
        "caption": "Wearing the chaotic latex cyber-glove wired with microcontrollers and jumpers"
      },
      {
        "src": "assets/journals/useless-project/photo-2.jpg",
        "caption": "Debugging serial signals and firmware on the laptop workbench"
      }
    ],
    "excerpt": "I just grabbed second place this weekend at Useless Projects 3.0, which turned out to be exactly what a maker event at TinkerSpace Calicut should look like. Hosted by TinkerHub, the whole premise...",
    "paragraphs": [
      "I just grabbed second place this weekend at Useless Projects 3.0, which turned out to be exactly what a maker event at TinkerSpace Calicut should look like. Hosted by TinkerHub, the whole premise of the hackathon was to celebrate the joy of building things purely for fun, without worrying about whether they actually solve a real-world problem. It was great to see such a solid group of creators show up, spending the weekend experimenting, breaking things, and showing off some genuinely quirky ideas in a totally pressure-free environment.",
      "My entry for the weekend was a wonderfully impractical wearable hardware setup. I strapped a microcontroller to my wrist, ran a bunch of exposed jumper wires down a latex glove, and spent way too long actively debugging the whole thing on my laptop. It took some seriously chaotic hardware hacking to get it running, but the messy build process completely paid off in the end. Taking home a prize for something intentionally useless was a pretty amazing way to wrap up the weekend."
    ]
  },
  "nit-physics-visit": {
    "id": "nit-physics-visit",
    "numericId": 4,
    "folder": "nit physics dept visit ( oct 24 2025)",
    "title": "A Day at NITC: Inside the Advanced Physics Labs",
    "date": "24 October 2025",
    "category": "Physics & Advanced Instrumentation",
    "location": "Department of Physics, NIT Calicut",
    "award": "Industrial Research Visit",
    "badge": "RESEARCH VISIT",
    "md": "nitc_physics_iv_report.md",
    "thumb": "assets/journals/nit-physics-visit/thumb.jpg",
    "photos": [
      {
        "src": "assets/journals/nit-physics-visit/photo-1.jpg",
        "caption": "Inside the advanced physics lab with precision superconducting instrumentation"
      },
      {
        "src": "assets/journals/nit-physics-visit/photo-2.jpg",
        "caption": "Inspecting specialized materials chemistry and applied polymer setups"
      },
      {
        "src": "assets/journals/nit-physics-visit/photo-3.jpg",
        "caption": "The JEOL 500 NMR spectrometer for molecular characterization"
      }
    ],
    "excerpt": "Our recent industrial visit to the Department of Physics at NIT Calicut offered an excellent look into the practical side of advanced physical sciences. The department clearly prioritizes high-le...",
    "paragraphs": [
      "Our recent industrial visit to the Department of Physics at NIT Calicut offered an excellent look into the practical side of advanced physical sciences. The department clearly prioritizes high-level research, which was evident from their strong focus on publishing in specialized fields like materials chemistry and applied polymers. It was inspiring to experience an academic environment so deeply committed to pushing the boundaries of fundamental and applied physics, while actively preparing students to step into innovation and leadership roles within the scientific community.",
      "The absolute highlight of the tour was getting to see the department's high-end instrumentation firsthand. Walking into the lab and observing the JEOL 500 NMR spectrometer in person really put our theoretical studies into perspective. This sophisticated, superconducting equipment is crucial for complex molecular characterization and structural analysis. Having the chance to see the real-world infrastructure required to run such advanced spectroscopy experiments gave us a much better understanding of what it actually takes to conduct professional, cutting-edge research."
    ]
  },
  "nss-state-camp": {
    "id": "nss-state-camp",
    "numericId": 5,
    "folder": "Nss state level camp (oct 19 2025)",
    "title": "NSS State Camp Diaries: Three Days at CM College",
    "date": "19 October 2025",
    "category": "Leadership & Community Development",
    "location": "CM College of Arts and Science",
    "award": "State Leadership Camp",
    "badge": "STATE LEADERSHIP",
    "md": "nss_camp_report.md",
    "thumb": "assets/journals/nss-state-camp/thumb.jpg",
    "photos": [
      {
        "src": "assets/journals/nss-state-camp/photo-1.jpg",
        "caption": "State level camp volunteers gathered at CM College of Arts and Science"
      },
      {
        "src": "assets/journals/nss-state-camp/photo-2.jpg",
        "caption": "Field activities, team-building sessions, and open project panels"
      }
    ],
    "excerpt": "The NSS State Level Leadership Camp wrapped up after a busy three days at CM College of Arts and Science. Held from October 17th to 19th, 2025, the event brought together student volunteers under...",
    "paragraphs": [
      "The NSS State Level Leadership Camp wrapped up after a busy three days at CM College of Arts and Science. Held from October 17th to 19th, 2025, the event brought together student volunteers under the University of Calicut and the Kerala Higher Education Department. Things kicked off with an introductory session where local police officers spoke to the crowd about stepping up as youth leaders and taking responsibility in their communities. The main goal of the weekend was to take the NSS motto of \"Not Me But You\" and turn it into practical skills, giving volunteers a space to figure out how to manage projects and communicate better when they get back to their home units.",
      "Over the three days, the schedule was packed with a mix of indoor discussions and outdoor team-building sessions. Instead of just sitting through lectures, volunteers spent time out in the field working on group tasks, which really helped break the ice and build connections among students from all over the state. Evenings usually shifted toward cultural programs and open panels where everyone could share what was actually working in their local community drives. By the time the closing session rolled around, the volunteers were heading home with a lot more confidence, a solid network of friends, and a clearer game plan for their upcoming campus initiatives."
    ]
  },
  "nss-university-camp": {
    "id": "nss-university-camp",
    "numericId": 6,
    "folder": "nss university level camp (march 23 2025)",
    "title": "Less Plastic, More Memories: Wrapping Up the 3-Day NSS University Camp",
    "date": "24 March 2025",
    "category": "Social Service & Ecology",
    "location": "Chaliyam Beach & University of Calicut",
    "award": "Calicut Swachhata Camp",
    "badge": "ECO INITIATIVE",
    "md": "nss_camp_report.md",
    "thumb": "assets/journals/nss-university-camp/thumb.jpg",
    "photos": [
      {
        "src": "assets/journals/nss-university-camp/photo-1.jpg",
        "caption": "Volunteers participating in Destination Swachhata plastic cleanup drive"
      },
      {
        "src": "assets/journals/nss-university-camp/photo-2.jpg",
        "caption": "Closing ceremony and group memories by Chaliyam Beach"
      },
      {
        "src": "assets/journals/nss-university-camp/photo-3.jpg",
        "caption": "Interactive environmental seminars and ice-breaker team games"
      }
    ],
    "excerpt": "From March 22 to 24, 2025, the University of Calicut's NSS department hosted a three-day residential camp called \"Calicut Swachhata\". The event brought together 100 volunteers selected from 100 d...",
    "paragraphs": [
      "From March 22 to 24, 2025, the University of Calicut's NSS department hosted a three-day residential camp called \"Calicut Swachhata\". The event brought together 100 volunteers selected from 100 different colleges across the region. The camp kicked off with an inauguration and featured several seminars focused on waste management and everyday cleanliness. Along with these sessions, a typical camp like this would also include morning warm-ups, ice-breaker games, and evening cultural programs where students get to showcase their talents and bond with volunteers from other colleges.",
      "The main highlight of the three days was the \"Destination Swachhata\" campaign, where the students headed out for a major beach cleaning drive at Chaliyam Beach. Working under the \"Life is Beautiful\" project, the volunteers teamed up to pick up plastic and clear debris from the coastline. This hands-on work helped spread public awareness about keeping our public spaces and oceans clean. After three days of hard work and learning, the camp wrapped up with a closing ceremony and a big group photo by the beach, sending everyone home with great memories and a fresh mindset for social service."
    ]
  },
  "microcontroller-physics": {
    "id": "microcontroller-physics",
    "numericId": 7,
    "folder": "micro-controller experiments on physics (sep 11 2024)",
    "title": "Hands-on Physics: Bringing Experiments to Life with SEELab",
    "date": "11 September 2024",
    "category": "Embedded Electronics & Physics",
    "location": "Physics Laboratory Workshop",
    "award": "Hands-on Workshop",
    "badge": "HARDWARE WORKSHOP",
    "md": "workshop_report.md",
    "thumb": "assets/journals/microcontroller-physics/thumb.jpg",
    "photos": [
      {
        "src": "assets/journals/microcontroller-physics/photo-1.jpg",
        "caption": "Students wiring resistors and sensors onto the SEELab 3.0 breadboard"
      },
      {
        "src": "assets/journals/microcontroller-physics/photo-2.jpg",
        "caption": "Projected software telemetry interface logging physical sensor values"
      },
      {
        "src": "assets/journals/microcontroller-physics/photo-3.jpg",
        "caption": "Analyzing operational amplifier gain alongside kinematics equations"
      },
      {
        "src": "assets/journals/microcontroller-physics/photo-4.jpg",
        "caption": "Student hardware presentations demonstrating functional circuit builds"
      }
    ],
    "excerpt": "A recent educational workshop on microcontroller-based physics experiments provided students with a practical way to connect classroom theory with modern electronics. Instructors walked the class...",
    "paragraphs": [
      "A recent educational workshop on microcontroller-based physics experiments provided students with a practical way to connect classroom theory with modern electronics. Instructors walked the class through key principles, exploring concepts like operational amplifier gain alongside kinematics equations used to calculate gravity. To bring these ideas to life and bridge the gap between theory and application, digital software interfaces were projected on screen, showing students exactly how to monitor and log data directly from their upcoming physical setups.",
      "The bulk of the session was highly collaborative and hands-on. Students teamed up to build their own circuits using the SEELab 3.0 open-source science kit, carefully wiring components like resistors directly onto the device's integrated breadboard to connect with various sensors. The environment was engaging and supportive, ultimately culminating in students confidently stepping up to present their completed hardware setups and explain their experimental processes to both the instructors and their peers."
    ]
  },
  "optica-students": {
    "id": "optica-students",
    "numericId": 8,
    "folder": "optica for students (aug 14 2024)",
    "title": "Inspiring Young Minds: Optics and Light Exploration Outreach",
    "date": "14 August 2024",
    "category": "Photonics & Optics Outreach",
    "location": "School Science Center",
    "award": "Student Outreach Program",
    "badge": "SCIENCE OUTREACH",
    "md": "optica_outreach_report.md",
    "thumb": "assets/journals/optica-students/thumb.jpg",
    "photos": [
      {
        "src": "assets/journals/optica-students/photo-1.jpg",
        "caption": "School students testing optical dispersion with glass prisms"
      },
      {
        "src": "assets/journals/optica-students/photo-2.jpg",
        "caption": "Demonstrating light wave convergence and divergence using convex lenses"
      },
      {
        "src": "assets/journals/optica-students/photo-3.jpg",
        "caption": "Hands-on diffraction gratings revealing the visible rainbow spectrum"
      }
    ],
    "excerpt": "Recently, the Muhammed Abdurahiman Memorial Orphanage College Chapter of OPTICA organized an engaging educational outreach program designed to advance the understanding of optics and photonics am...",
    "paragraphs": [
      "Recently, the Muhammed Abdurahiman Memorial Orphanage College Chapter of OPTICA organized an engaging educational outreach program designed to advance the understanding of optics and photonics among school students. The initiative brought together a large, enthusiastic audience of young learners for interactive presentations, including a detailed exploration of the properties of white light. Driven by a dedicated organizing committee and student volunteers, the event successfully fostered a collaborative and interactive environment for the students to explore complex scientific concepts.",
      "During the session, attendees were introduced to foundational science gadgets that transform abstract optical theories into observable physical phenomena. The physics of optical dispersion was demonstrated using glass prisms, which slow down and bend passing light rays at varying angles to separate white light into a visible rainbow spectrum. The program also explored the core principles of refraction using convex and concave lenses to show how light waves can be manipulated to converge at a single focal point or diverge. By interacting with these optical tools alongside diffraction gratings, the students gained a practical, hands-on understanding of photonics and the fundamental behavior of light."
    ]
  },
  "optica-session": {
    "id": "optica-session",
    "numericId": 9,
    "folder": "optica session ( july 18 2024)",
    "title": "Exploring Photonics: A Hands-on Look at Optical Gadgets",
    "date": "18 July 2024",
    "category": "Photonics & Optical Gadgets",
    "location": "MAMO College, OPTICA Student Chapter",
    "award": "Chapter Practical Session",
    "badge": "PHOTONICS SESSION",
    "md": "event_outlook_report.md",
    "thumb": "assets/journals/optica-session/thumb.jpg",
    "photos": [
      {
        "src": "assets/journals/optica-session/photo-1.jpg",
        "caption": "Participants wearing specialized spectral viewing glasses to observe light diffraction"
      },
      {
        "src": "assets/journals/optica-session/photo-2.jpg",
        "caption": "Exploring optical tool mechanics with The Optics Suitcase in classroom"
      }
    ],
    "excerpt": "The OPTICA Student Chapter at Muhammed Abdurahiman Memorial Orphanage College recently hosted an interactive session focused on the mechanics and real-world applications of optical gadgets. Cente...",
    "paragraphs": [
      "The OPTICA Student Chapter at Muhammed Abdurahiman Memorial Orphanage College recently hosted an interactive session focused on the mechanics and real-world applications of optical gadgets. Centered around practical demonstrations using \"The Optics Suitcase,\" the program was designed to bring complex concepts in optics and photonics out of theoretical textbooks and into an accessible classroom environment. The workshop provided a collaborative space for students to explore the fundamental principles governing light and vision.",
      "Throughout the event, attendees gained firsthand experience by wearing specialized optical viewing glasses to observe light behavior and spectral patterns. This practical setup allowed the group to test different optical tools simultaneously and actively discuss the visual phenomena unfolding right before their eyes. By bridging the gap between theoretical physics and tangible applications, the chapter successfully fostered a deeper, more engaging understanding of photonics among the participants."
    ]
  }
};

  function initJournalThumbnailMotion() {
    if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) return;
    if (window.matchMedia('(pointer: coarse)').matches) return;

    const cards = document.querySelectorAll('.journal-card');
    if (!cards.length) return;

    cards.forEach((card) => {
      const thumb = card.querySelector('.journal-thumb-container');
      if (!thumb) return;

      let isHovered = false;
      let rafId = null;
      let currentTiltX = 0;
      let currentTiltY = 0;
      let targetTiltX = 0;
      let targetTiltY = 0;

      function updateTilt() {
        if (!isHovered) {
          currentTiltX += (0 - currentTiltX) * 0.15;
          currentTiltY += (0 - currentTiltY) * 0.15;
          thumb.style.transform = `perspective(800px) rotateX(${currentTiltX.toFixed(2)}deg) rotateY(${currentTiltY.toFixed(2)}deg)`;
          if (Math.abs(currentTiltX) > 0.05 || Math.abs(currentTiltY) > 0.05) {
            rafId = requestAnimationFrame(updateTilt);
          } else {
            thumb.style.transform = '';
          }
          return;
        }

        currentTiltX += (targetTiltX - currentTiltX) * 0.15;
        currentTiltY += (targetTiltY - currentTiltY) * 0.15;
        thumb.style.transform = `perspective(800px) rotateX(${currentTiltX.toFixed(2)}deg) rotateY(${currentTiltY.toFixed(2)}deg)`;
        rafId = requestAnimationFrame(updateTilt);
      }

      card.addEventListener('mouseenter', () => {
        isHovered = true;
        cancelAnimationFrame(rafId);
        rafId = requestAnimationFrame(updateTilt);
      });

      card.addEventListener('mousemove', (e) => {
        const rect = thumb.getBoundingClientRect();
        const x = e.clientX - rect.left;
        const y = e.clientY - rect.top;
        const centerX = rect.width / 2;
        const centerY = rect.height / 2;

        // Subtle, physical tilt clamp (max ±5 degrees)
        targetTiltX = -((y - centerY) / centerY) * 5;
        targetTiltY = ((x - centerX) / centerX) * 5;
      });

      card.addEventListener('mouseleave', () => {
        isHovered = false;
        targetTiltX = 0;
        targetTiltY = 0;
      });
    });
  }

  function initJournalDetailPage() {
    const titleEl = document.getElementById('journal-title');
    if (!titleEl) return; // Not on journal detail page

    const urlParams = new URLSearchParams(window.location.search);
    const id = urlParams.get('id') || 'claude-hackathon';
    const journal = JOURNAL_DATABASE[id] || JOURNAL_DATABASE['claude-hackathon'];

    // Update document & meta titles
    document.title = `${journal.title} // gwys.in`;
    const metaTitle = document.getElementById('journal-meta-title');
    if (metaTitle) metaTitle.textContent = `${journal.title} · gwys.in`;

    // Metadata chips
    const categoryPill = document.getElementById('journal-category-pill');
    if (categoryPill) categoryPill.textContent = journal.category;

    const awardPill = document.getElementById('journal-award-pill');
    if (awardPill) {
      if (journal.badge) {
        awardPill.textContent = journal.badge;
        awardPill.style.display = 'inline-block';
      } else if (journal.award) {
        awardPill.textContent = journal.award;
        awardPill.style.display = 'inline-block';
      } else {
        awardPill.style.display = 'none';
      }
    }

    const dateText = document.getElementById('journal-date-text');
    if (dateText) dateText.textContent = journal.date;

    const locationText = document.getElementById('journal-location-text');
    if (locationText) locationText.textContent = journal.location;

    // Main Title
    titleEl.textContent = journal.title;

    // Hero image
    const heroImg = document.getElementById('journal-hero-img');
    const heroCaption = document.getElementById('journal-hero-caption');
    const heroContainer = document.getElementById('journal-hero-container');

    const primaryPhoto = (journal.photos && journal.photos.length > 0)
      ? journal.photos[0]
      : { src: journal.thumb, caption: journal.title };

    if (heroImg) {
      heroImg.src = primaryPhoto.src;
      heroImg.alt = primaryPhoto.caption || journal.title;
    }
    if (heroCaption) {
      heroCaption.textContent = primaryPhoto.caption || `${journal.title} // Field visual`;
    }

    // Body content with drop-cap on opening paragraph
    const bodyContent = document.getElementById('journal-body-content');
    if (bodyContent && journal.paragraphs) {
      bodyContent.innerHTML = '';
      journal.paragraphs.forEach((para, idx) => {
        const p = document.createElement('p');
        if (idx === 0) {
          p.className = 'text-lg sm:text-xl text-neutral-900 leading-relaxed font-sans first-letter:float-left first-letter:text-5xl sm:first-letter:text-6xl first-letter:font-serif first-letter:font-bold first-letter:pr-3.5 first-letter:pt-1 first-letter:text-ink';
        } else {
          p.className = 'text-base sm:text-lg text-neutral-700 leading-relaxed';
        }
        p.textContent = para;
        bodyContent.appendChild(p);
      });
    }

    // Blueprint Card Metadata
    const metaDate = document.getElementById('meta-date');
    if (metaDate) metaDate.textContent = journal.date;
    const metaLocation = document.getElementById('meta-location');
    if (metaLocation) metaLocation.textContent = journal.location;
    const metaCategory = document.getElementById('meta-category');
    if (metaCategory) metaCategory.textContent = journal.category;
    const metaAward = document.getElementById('meta-award');
    if (metaAward) metaAward.textContent = journal.award || journal.badge || 'Field Activity';

    // Documentation Gallery
    const galleryGrid = document.getElementById('journal-gallery-grid');
    const galleryCount = document.getElementById('gallery-count-badge');
    const photosList = journal.photos || [];

    if (galleryCount) {
      galleryCount.textContent = `[ ${photosList.length} Photo${photosList.length === 1 ? '' : 's'} ]`;
    }

    if (galleryGrid) {
      galleryGrid.innerHTML = '';
      photosList.forEach((photo, idx) => {
        const figure = document.createElement('figure');
        figure.className = 'journal-gallery-item group rounded-xl overflow-hidden border border-black/20 bg-neutral-900 flex flex-col cursor-pointer transition-all duration-300';
        figure.setAttribute('data-cursor', 'Expand Photo');
        figure.innerHTML = `
          <div class="overflow-hidden bg-neutral-950 relative aspect-[4/3] flex items-center justify-center">
            <img src="${photo.src}" alt="${photo.caption}" class="w-full h-full object-cover group-hover:scale-105 transition-transform duration-300 ease-out" loading="lazy">
            <div class="absolute inset-0 bg-black/30 opacity-0 group-hover:opacity-100 transition-opacity flex items-center justify-center pointer-events-none">
              <span class="font-mono text-xs text-white bg-black/80 px-3 py-1.5 rounded-full border border-white/20">Click to expand</span>
            </div>
          </div>
          <figcaption class="p-3 bg-white font-mono text-xs text-neutral-700 border-t border-black/10 flex items-center justify-between">
            <span class="truncate pr-2">${photo.caption}</span>
            <span class="text-neutral-400 font-bold flex-shrink-0">0${idx + 1}</span>
          </figcaption>
        `;

        figure.addEventListener('click', () => {
          Sound.click();
          openPhotoLightbox(photo.src, photo.caption, idx + 1, photosList.length);
        });

        galleryGrid.appendChild(figure);
      });
    }

    // Hero image also clickable for lightbox
    if (heroContainer) {
      heroContainer.style.cursor = 'pointer';
      heroContainer.setAttribute('data-cursor', 'Expand Photo');
      heroContainer.addEventListener('click', () => {
        Sound.click();
        openPhotoLightbox(primaryPhoto.src, primaryPhoto.caption, 1, photosList.length || 1);
      });
    }

    // Next & Previous Pagination
    const journalKeys = Object.keys(JOURNAL_DATABASE);
    const currentIndex = journalKeys.indexOf(journal.id);
    const safeIndex = currentIndex !== -1 ? currentIndex : 0;
    const prevIndex = (safeIndex - 1 + journalKeys.length) % journalKeys.length;
    const nextIndex = (safeIndex + 1) % journalKeys.length;
    const prevJournal = JOURNAL_DATABASE[journalKeys[prevIndex]];
    const nextJournal = JOURNAL_DATABASE[journalKeys[nextIndex]];

    const prevBtn = document.getElementById('journal-prev-btn');
    const prevTitle = document.getElementById('journal-prev-title');
    if (prevBtn && prevTitle) {
      prevBtn.href = `journal.html?id=${prevJournal.id}`;
      prevTitle.textContent = prevJournal.title;
    }

    const nextBtn = document.getElementById('journal-next-btn');
    const nextTitle = document.getElementById('journal-next-title');
    if (nextBtn && nextTitle) {
      nextBtn.href = `journal.html?id=${nextJournal.id}`;
      nextTitle.textContent = nextJournal.title;
    }
  }

  // ---------------------------------------------------------------------------
  // 13. PHOTO LIGHTBOX MODAL
  // ---------------------------------------------------------------------------
  function openPhotoLightbox(src, caption, index, total) {
    let lightbox = document.getElementById('journal-lightbox');
    if (!lightbox) {
      lightbox = document.createElement('div');
      lightbox.id = 'journal-lightbox';
      lightbox.className = 'fixed inset-0 z-50 bg-black/90 backdrop-blur-md flex flex-col items-center justify-center p-4 opacity-0 pointer-events-none transition-opacity duration-200';
      lightbox.innerHTML = `
        <div class="absolute top-4 right-4 flex items-center gap-3">
          <span id="lightbox-counter" class="font-mono text-xs text-white/60"></span>
          <button id="lightbox-close-btn" class="w-10 h-10 rounded-full bg-white/10 hover:bg-white/20 text-white flex items-center justify-center font-mono text-lg transition-colors border border-white/20 cursor-pointer" aria-label="Close">
            ✕
          </button>
        </div>
        <div class="max-w-5xl max-h-[82vh] flex flex-col items-center">
          <img id="lightbox-img" src="" alt="" class="max-w-full max-h-[75vh] object-contain rounded-lg shadow-2xl border border-white/10">
          <p id="lightbox-caption" class="mt-4 font-mono text-xs sm:text-sm text-neutral-300 text-center max-w-2xl px-2"></p>
        </div>
      `;
      document.body.appendChild(lightbox);

      const closeBtn = lightbox.querySelector('#lightbox-close-btn');
      closeBtn.addEventListener('click', closeLightbox);
      lightbox.addEventListener('click', (e) => {
        if (e.target === lightbox) closeLightbox();
      });
      window.addEventListener('keydown', (e) => {
        if (e.key === 'Escape' && !lightbox.classList.contains('pointer-events-none')) {
          closeLightbox();
        }
      });
    }

    const img = lightbox.querySelector('#lightbox-img');
    const cap = lightbox.querySelector('#lightbox-caption');
    const counter = lightbox.querySelector('#lightbox-counter');

    img.src = src;
    img.alt = caption || '';
    cap.textContent = caption || '';
    if (counter) counter.textContent = `[ ${index} / ${total} ]`;

    lightbox.classList.remove('pointer-events-none');
    requestAnimationFrame(() => {
      lightbox.classList.add('opacity-100');
    });
  }

  function closeLightbox() {
    const lightbox = document.getElementById('journal-lightbox');
    if (!lightbox) return;
    lightbox.classList.remove('opacity-100');
    lightbox.classList.add('pointer-events-none');
  }

  // ---------------------------------------------------------------------------
  // INITIALIZE ON DOM READY
  // ---------------------------------------------------------------------------
  document.addEventListener("DOMContentLoaded", () => {
    initAudioHeader();
    initMagneticButtons();
    initCursorFollower();
    initInteractiveTitle();
    initJackOfAllTrades();
    initHeroStage();
    initHowIWorkSection();
    initAxiomCards();
    initCardTiltAndModal();
    initBenchTelemetry();
    initFilterPills();
    initJournalThumbnailMotion();
    initJournalDetailPage();
  });
})();
