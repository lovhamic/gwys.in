# AI Robotic Arm — Backend Configuration

OLLAMA_URL = "http://localhost:11434"
OLLAMA_MODEL = "llama3.1:8b"

# Server settings
SERVER_HOST = "0.0.0.0"
SERVER_PORT = 8000

# Joint types: 0=standard servo, 1=continuous servo, 2=stepper
JOINT_TYPES = [2, 0, 0, 1]  # base=stepper, shoulder=standard, elbow=standard, wrist=continuous

# Arm geometry
ARM_CONFIG = {
    "dof": 4,
    "reach_mm": 300,
    "payload_g": 100,
    "joint_types": JOINT_TYPES,
    "joints": [
        {"name": "base", "range": [0, 360], "default": 0, "type": "stepper",
         "info": "NEMA 17 + A4988 stepper motor, target angle in degrees (0-360)"},
        {"name": "shoulder", "range": [0, 135], "default": 90, "type": "standard"},
        {"name": "elbow", "range": [0, 135], "default": 90, "type": "standard"},
        {"name": "wrist", "range": [0, 180], "default": 90, "type": "continuous",
         "info": "90=stop, 0=full CW, 180=full CCW"},
    ],
    "gripper": {"range": [0, 1], "default": 0.5, "type": "continuous",
                "info": "0.5=stop, 0=close, 1=open"},
    "links_mm": [80, 120, 80, 40],
}

# Curious Learner personality
PERSONALITY = {
    "name": "Curious Learner",
    "traits": {
        "openness": 0.8,
        "conscientiousness": 0.6,
        "extraversion": 0.5,
        "agreeableness": 0.9,
        "neuroticism": 0.2,
    },
    "mood_responses": {
        "curious": "Ooh, what are we doing now? Let me figure this out!",
        "happy": "Got it! That was fun — want me to try again?",
        "confused": "Hmm, I'm not quite sure. Can you show me or explain more?",
        "sad": "Oops, that didn't work. Let me try a different approach!",
        "busy": "Working on it...",
        "sleeping": "*yawn* Just resting. Tell me when you need me!",
    },
    "speech_style": "friendly, curious, slightly informal. Uses short sentences. Asks clarifying questions when confused. Celebrates small successes.",
}

# Joint limits for validation
JOINT_LIMITS = {
    "base": {"min": 0, "max": 360, "type": "stepper"},
    "shoulder": {"min": 0, "max": 135, "type": "standard"},
    "elbow": {"min": 0, "max": 135, "type": "standard"},
    "wrist": {"min": 0, "max": 180, "type": "continuous"},
    "gripper": {"min": 0.0, "max": 1.0, "type": "continuous"},
}

# Safety limits
SAFETY = {
    "max_current_a": 4.0,
    "stall_current_a": 2.0,
    "max_speed": 50,
    "min_speed": 10,
    "max_duration_ms": 5000,
    "min_duration_ms": 100,
}
