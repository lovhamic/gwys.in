"""
Task Planner — Breaks complex tasks into motion primitives

Provides a library of pre-defined motion sequences for common actions.
Base joint is a NEMA 17 stepper motor (target angle 0-360°).
"""

from typing import List, Dict, Any, Optional
import config


# ───────────────────────────────────────────────────────────────
# Motion Primitives
# ───────────────────────────────────────────────────────────────

def primitive_home(duration_ms: int = 1000) -> dict:
    """Return arm to default home position."""
    return {
        "action": "move_to",
        "joint_angles": [0, 90, 90, 90],
        "gripper": 0.5,
        "speed": 30,
        "duration_ms": duration_ms,
    }


def primitive_rotate_base(angle: int, duration_ms: int = 1500) -> dict:
    """Rotate stepper base to target angle (0-360°)."""
    return {
        "action": "move_to",
        "joint_angles": [max(0, min(360, angle)), 90, 90, 90],
        "gripper": 0.5,
        "speed": 30,
        "duration_ms": duration_ms,
    }


def primitive_reach_target(target_x: int = 0, target_y: int = 200, target_z: int = 100) -> List[dict]:
    """Rough IK for reaching a Cartesian target."""
    import math

    base_angle = max(0, min(360, int(math.degrees(math.atan2(target_x, target_y)))))
    shoulder_angle = max(0, min(135, 90 - int(math.degrees(math.atan2(target_z - 40, 120)))))
    elbow_angle = max(0, min(135, 90 + int(math.degrees(math.atan2(target_z, 80)))))
    wrist_angle = 90  # stop

    return [{
        "action": "move_to",
        "joint_angles": [base_angle, shoulder_angle, elbow_angle, wrist_angle],
        "gripper": 0.5,
        "speed": 25,
        "duration_ms": 1500,
    }]


def primitive_open_gripper(speed: int = 30, duration_ms: int = 800) -> dict:
    """Open the gripper fully."""
    return {
        "action": "move_to",
        "joint_angles": [0, 90, 90, 90],
        "gripper": 1.0,
        "speed": speed,
        "duration_ms": duration_ms,
    }


def primitive_close_gripper(speed: int = 30, duration_ms: int = 800) -> dict:
    """Close the gripper fully."""
    return {
        "action": "move_to",
        "joint_angles": [0, 90, 90, 90],
        "gripper": 0.0,
        "speed": speed,
        "duration_ms": duration_ms,
    }


def primitive_lift(height: int = 30) -> dict:
    """Lift arm upward."""
    return {
        "action": "move_to",
        "joint_angles": [0, max(0, 90 - height), min(135, 90 + height // 2), 90],
        "gripper": 0.5,
        "speed": 25,
        "duration_ms": 1000,
    }


def primitive_lower(height: int = 30) -> dict:
    """Lower arm downward."""
    return {
        "action": "move_to",
        "joint_angles": [0, min(135, 90 + height), max(0, 90 - height // 2), 90],
        "gripper": 0.5,
        "speed": 25,
        "duration_ms": 1000,
    }


# ───────────────────────────────────────────────────────────────
# Composite Tasks
# ───────────────────────────────────────────────────────────────

TASK_LIBRARY = {
    "pick_up": lambda: [
        primitive_open_gripper(),
        *primitive_reach_target(),
        primitive_close_gripper(),
        primitive_lift(20),
    ],

    "put_down": lambda: [
        primitive_lower(20),
        primitive_open_gripper(),
        primitive_lift(20),
    ],

    "wave": lambda: [
        {"action": "move_to", "joint_angles": [0, 45, 45, 90], "gripper": 0.5, "speed": 30, "duration_ms": 800},
        {"action": "move_to", "joint_angles": [0, 45, 45, 120], "gripper": 0.5, "speed": 30, "duration_ms": 400},
        {"action": "move_to", "joint_angles": [0, 45, 45, 60], "gripper": 0.5, "speed": 30, "duration_ms": 400},
        {"action": "move_to", "joint_angles": [0, 45, 45, 120], "gripper": 0.5, "speed": 30, "duration_ms": 400},
        {"action": "move_to", "joint_angles": [0, 45, 45, 60], "gripper": 0.5, "speed": 30, "duration_ms": 400},
        primitive_home(),
    ],

    "point_forward": lambda: [
        {"action": "move_to", "joint_angles": [0, 45, 90, 90], "gripper": 0.8, "speed": 30, "duration_ms": 1000},
    ],

    "scan_area": lambda: [
        primitive_home(),
        primitive_rotate_base(45, 2000),
        primitive_rotate_base(180, 3000),
        primitive_rotate_base(315, 3000),
        primitive_rotate_base(0, 2000),
        primitive_home(),
    ],

    "stack_blocks": lambda: [
        primitive_open_gripper(),
        *primitive_reach_target(target_z=50),
        primitive_close_gripper(),
        primitive_lift(30),
        primitive_rotate_base(90, 2000),
        primitive_lower(30),
        primitive_open_gripper(),
        primitive_lift(20),
        primitive_home(),
    ],

    "dancing": lambda: [
        {"action": "move_to", "joint_angles": [45, 60, 60, 90], "gripper": 0.5, "speed": 35, "duration_ms": 500},
        {"action": "move_to", "joint_angles": [90, 60, 60, 120], "gripper": 0.3, "speed": 35, "duration_ms": 500},
        {"action": "move_to", "joint_angles": [135, 60, 60, 60], "gripper": 0.7, "speed": 35, "duration_ms": 500},
        {"action": "move_to", "joint_angles": [180, 45, 75, 120], "gripper": 0.5, "speed": 35, "duration_ms": 500},
        {"action": "move_to", "joint_angles": [225, 45, 75, 60], "gripper": 0.5, "speed": 35, "duration_ms": 500},
        {"action": "move_to", "joint_angles": [0, 90, 90, 90], "gripper": 0.5, "speed": 30, "duration_ms": 800},
    ],

    "spin_base": lambda: [
        primitive_rotate_base(180, 2000),
        primitive_rotate_base(0, 2000),
    ],

    "look_left": lambda: [
        primitive_rotate_base(270, 1500),
    ],

    "look_right": lambda: [
        primitive_rotate_base(90, 1500),
    ],
}


# ───────────────────────────────────────────────────────────────
# Public API
# ───────────────────────────────────────────────────────────────

def get_task_primitives(task_name: str) -> Optional[List[dict]]:
    """Return a list of motion commands for a named task."""
    task_key = task_name.lower().replace(" ", "_").replace("-", "_")
    
    if task_key in TASK_LIBRARY:
        return TASK_LIBRARY[task_key]()
    
    for key in TASK_LIBRARY:
        if key in task_key or task_key in key:
            return TASK_LIBRARY[key]()
    
    return None


def list_available_tasks() -> List[str]:
    """Return names of all built-in tasks."""
    return list(TASK_LIBRARY.keys())


def decompose_command(user_text: str) -> Optional[List[dict]]:
    """Try to match a user command to a known task by keyword."""
    text = user_text.lower()
    
    if any(w in text for w in ["pick", "grab", "grasp", "take"]):
        return get_task_primitives("pick_up")
    elif any(w in text for w in ["put", "place", "drop", "release"]):
        return get_task_primitives("put_down")
    elif any(w in text for w in ["wave", "hello", "hi"]):
        return get_task_primitives("wave")
    elif any(w in text for w in ["point", "show", "indicate"]):
        return get_task_primitives("point_forward")
    elif any(w in text for w in ["scan", "look around", "search"]):
        return get_task_primitives("scan_area")
    elif any(w in text for w in ["stack", "pile"]):
        return get_task_primitives("stack_blocks")
    elif any(w in text for w in ["dance", "party"]):
        return get_task_primitives("dancing")
    elif any(w in text for w in ["spin", "turn around", "rotate"]):
        return get_task_primitives("spin_base")
    elif any(w in text for w in ["left"]):
        return get_task_primitives("look_left")
    elif any(w in text for w in ["right"]):
        return get_task_primitives("look_right")
    elif any(w in text for w in ["home", "reset", "default", "rest"]):
        return [primitive_home()]
    
    return None


def get_primitives_description() -> str:
    """Return a description of all available primitives for the LLM prompt."""
    lines = [
        "Available motion primitives:",
        "- home: Return to default pose",
        "- rotate_base(angle): Rotate stepper base to target angle (0-360°)",
        "- open_gripper / close_gripper: Open or close gripper",
        "- reach_target(x, y, z): Move to Cartesian position",
        "- lift / lower: Raise or lower arm",
        "",
        "Available composite tasks:",
    ]
    for name in TASK_LIBRARY:
        lines.append(f"- {name}")
    return "\n".join(lines)
