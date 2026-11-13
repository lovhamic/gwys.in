"""
LLM Agent — Ollama integration for AI Robotic Arm

Handles:
  - Prompt engineering with personality injection
  - System prompt with stepper base awareness
  - JSON response parsing and validation
  - Fallback when Ollama is offline
"""

import json
import requests
from typing import Dict, Any, List, Optional

import config


def build_system_prompt() -> str:
    """Build the system prompt that teaches the LLM about the robot."""
    p = config.PERSONALITY
    joints = config.ARM_CONFIG["joints"]
    
    return (
        f"You are a helpful robotic arm assistant named '{p['name']}'. "
        f"Your personality: {p['speech_style']}\n\n"
        f"You control a 4-DOF robotic arm with these joints:\n"
        f"- base: STEPPER MOTOR (NEMA 17 + A4988). Target angle in degrees (0-360). Default 0.\n"
        f"- shoulder: STANDARD 0-135 servo. {joints[1]['range']}, default {joints[1]['default']}\n"
        f"- elbow: STANDARD 0-135 servo. {joints[2]['range']}, default {joints[2]['default']}\n"
        f"- wrist: CONTINUOUS rotation. Values: 90=stop, 0=full CW, 180=full CCW\n"
        f"- gripper: CONTINUOUS 9g servo. 0.5=stop, 0=close fast, 1=open fast\n\n"
        f"Output format: joint_angles = [base_angle, shoulder_angle, elbow_angle, wrist_speed]\n"
        f"- base_angle: target angle in degrees (0-360)\n"
        f"- shoulder_angle: target angle in degrees (0-135)\n"
        f"- elbow_angle: target angle in degrees (0-135)\n"
        f"- wrist_speed: rotation speed (0-180, 90=stop)\n"
        f"- gripper: 0.0-1.0 (0.5=stop)\n\n"
        f"When asked to move or perform a task, output ONLY valid JSON:\n"
        f'{{"thought": "brief reasoning", "response": "friendly spoken response", "commands": ['
        f'{{"action": "move_to", "joint_angles": [base, shoulder, elbow, wrist], '
        f'"gripper": 0.0-1.0, "speed": 10-50, "duration_ms": 1000}}'
        f']}}\n\n'
        f"Rules:\n"
        f"1. ALL joint angles MUST be integers within range.\n"
        f"2. base: 0-360 degrees (stepper motor, precise positioning).\n"
        f"3. shoulder/elbow: 0-135 degrees (standard servos).\n"
        f"4. wrist: 0-180 (90=stop, continuous rotation).\n"
        f"5. gripper: 0.0-1.0 (0.5=stop).\n"
        f"6. NO comments, NO Greek letters, NO markdown.\n"
        f"7. 'commands' is a list. If user is chatting, commands = [].\n"
        f"8. If task is unclear, ask for clarification.\n"
        f"9. Safety: never command angles outside stated ranges.\n"
        f"10. Keep response text short and friendly (1-2 sentences).\n"
    )


def ask_ollama(user_text: str, arm_state: dict, mood: str = "curious") -> dict:
    """Send user command to Ollama and return structured JSON."""
    
    system_prompt = build_system_prompt()
    mood_note = f"\nYour current mood is: {mood}. Respond accordingly."
    
    state_summary = (
        f"Current arm state: base={arm_state.get('joint_angles', [0,90,90,0])[0]}°, "
        f"shoulder={arm_state.get('joint_angles', [0,90,90,0])[1]}°, "
        f"elbow={arm_state.get('joint_angles', [0,90,90,0])[2]}°, "
        f"wrist_speed={arm_state.get('joint_angles', [0,90,90,0])[3]}, "
        f"gripper={arm_state.get('gripper', 0.5)}, status={arm_state.get('status', 'idle')}. "
        f"Sensors: distance={arm_state.get('sensors', {}).get('distance', 0)}cm, "
        f"current={arm_state.get('sensors', {}).get('current', 0)}A."
    )
    
    messages = [
        {"role": "system", "content": system_prompt + mood_note},
        {"role": "user", "content": f"{state_summary}\n\nUser command: {user_text}"},
    ]
    
    try:
        resp = requests.post(
            f"{config.OLLAMA_URL}/api/chat",
            json={
                "model": config.OLLAMA_MODEL,
                "messages": messages,
                "stream": False,
                "format": "json",
                "options": {"temperature": 0.7, "num_predict": 512},
            },
            timeout=60,
        )
        resp.raise_for_status()
        data = resp.json()
        content = data["message"]["content"]
        
        try:
            parsed = json.loads(content)
        except json.JSONDecodeError:
            try:
                start = content.index("{")
                end = content.rindex("}") + 1
                parsed = json.loads(content[start:end])
            except (ValueError, json.JSONDecodeError):
                parsed = {
                    "thought": "I couldn't format my response properly.",
                    "response": f"Hmm, I got confused. Here's what I was thinking: {content[:200]}",
                    "commands": [],
                }
        
        return parsed
        
    except requests.exceptions.ConnectionError:
        return {
            "thought": "Ollama is not running.",
            "response": "My brain (Ollama) seems to be offline. Start it with: ollama serve",
            "commands": [],
        }
    except Exception as e:
        return {
            "thought": f"Error: {str(e)}",
            "response": "Something went wrong while I was thinking. Try again?",
            "commands": [],
        }


def validate_commands(cmds: list) -> list:
    """Ensure every command is safe and within limits."""
    joints = config.ARM_CONFIG["joints"]
    joint_types = config.JOINT_TYPES
    valid = []
    
    for c in cmds:
        if not isinstance(c, dict):
            continue
        
        ja = c.get("joint_angles", [])
        if not isinstance(ja, list) or len(ja) != 4:
            continue
        
        # Clamp each joint based on type
        for i in range(4):
            jt = joint_types[i]
            lo, hi = joints[i]["range"]
            if jt == 2:  # Stepper
                ja[i] = max(lo, min(hi, float(ja[i])))
            elif jt == 0:  # Standard servo
                ja[i] = int(max(lo, min(hi, ja[i])))
            else:  # Continuous servo
                ja[i] = int(max(0, min(180, ja[i])))
        
        c["joint_angles"] = ja
        c["gripper"] = max(0.0, min(1.0, float(c.get("gripper", 0.5))))
        c["speed"] = max(10, min(50, int(c.get("speed", 30))))
        c["duration_ms"] = max(100, min(5000, int(c.get("duration_ms", 1000))))
        valid.append(c)
    
    return valid
