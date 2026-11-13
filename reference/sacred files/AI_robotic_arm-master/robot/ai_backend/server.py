"""
AI Robotic Arm Backend Server
FastAPI + WebSocket + Ollama (Llama 3.1)

Modules integrated:
  - server.py (this file): WebSocket server, HTTP routes
  - llm_agent.py: Ollama integration, prompt engineering
  - task_planner.py: Motion primitives and task decomposition
  - skill_library.py: SQLite skill storage
  - memory_store.py: SQLite conversation/state history
  - personality_engine.py: Mood system

Run this on your PC:
    python server.py

Then open: http://localhost:8000
"""

import asyncio
import json
import time
import uuid
from typing import Optional, Dict, Any, List

import requests
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse

import config
import llm_agent
import task_planner
import skill_library
import memory_store
from personality_engine import PersonalityEngine

# ───────────────────────────────────────────────────────────────
# FastAPI App
# ───────────────────────────────────────────────────────────────
app = FastAPI(title="AI Robotic Arm Backend")
app.mount("/static", StaticFiles(directory="dashboard"), name="static")

# ───────────────────────────────────────────────────────────────
# Global State
# ───────────────────────────────────────────────────────────────
esp32_socket: Optional[WebSocket] = None
esp32_connected = False
esp32_last_seen = 0.0

arm_state = {
    "joint_angles": [90, 90, 90, 0],
    "gripper": 0.5,
    "sensors": {"distance": 0.0, "current": 0.0},
    "status": "idle",
    "mood": "curious",
    "active_cmd": "none",
    "emergency": False,
    "servo_types": config.JOINT_TYPES,
}

dashboard_sockets: List[WebSocket] = []
command_history: List[Dict[str, Any]] = []

personality = PersonalityEngine()
ollama_available = False


# ───────────────────────────────────────────────────────────────
# Command Processing
# ───────────────────────────────────────────────────────────────

def process_user_command(text: str, source: str = "dashboard") -> dict:
    """Process a user command through LLM or task planner."""
    personality.on_event("user_input")
    personality.check_auto_transition()

    task_commands = task_planner.decompose_command(text)
    if task_commands:
        personality.on_event("task_start")
        commands = task_commands
        result = {
            "thought": f"Matched to built-in task: {task_planner.decompose_command.__name__}",
            "response": f"On it! Let me do that for you.",
            "commands": commands,
        }
    else:
        mood = personality.get_mood()
        result = llm_agent.ask_ollama(text, arm_state, mood)
        commands = llm_agent.validate_commands(result.get("commands", []))
        if commands:
            personality.on_event("task_start")

    response_text = result.get("response", "")
    thought = result.get("thought", "")

    current_mood = personality.get_mood()

    memory_store.log_conversation(
        user_text=text,
        ai_response=response_text,
        mood=current_mood,
        command_count=len(commands),
    )

    return {
        "response": response_text,
        "thought": thought,
        "commands": commands,
        "mood": current_mood,
    }


async def send_commands_to_esp32(commands: list, ws: WebSocket = None) -> int:
    """Send validated commands to ESP32, return count sent."""
    sent = 0
    for cmd in commands:
        cmd_id = str(uuid.uuid4())[:8]
        cmd["command_id"] = cmd_id
        cmd["type"] = "motion_command"
        success = await send_to_esp32(cmd)
        if success:
            sent += 1
        msg = {
            "type": "command_sent",
            "payload": cmd,
        }
        if ws:
            try:
                await ws.send_json(msg)
            except Exception:
                pass
        await broadcast_to_dashboard(msg)

        memory_store.log_command(
            command_text=cmd.get("action", "move"),
            commands_json=[cmd],
            success=success,
        )
    return sent


async def broadcast_to_dashboard(msg: dict):
    """Send a message to all connected dashboard clients."""
    dead = []
    for ws in dashboard_sockets:
        try:
            await ws.send_json(msg)
        except Exception:
            dead.append(ws)
    for ws in dead:
        if ws in dashboard_sockets:
            dashboard_sockets.remove(ws)


async def send_to_esp32(msg: dict) -> bool:
    """Send a command to the ESP32 via WebSocket."""
    if esp32_socket and esp32_connected:
        try:
            await esp32_socket.send_json(msg)
            return True
        except Exception:
            return False
    return False


async def send_mood_to_esp32(mood: str):
    """Push mood change to ESP32 so it updates the LED."""
    cmd = {
        "type": "set_mood",
        "command_id": str(uuid.uuid4())[:8],
        "mood": mood,
    }
    sent = await send_to_esp32(cmd)
    print(f"[Mood] -> ESP32: '{mood}' (sent={sent})")
    await broadcast_to_dashboard({"type": "mood_change", "payload": {"mood": mood}})


# ───────────────────────────────────────────────────────────────
# HTTP Routes
# ───────────────────────────────────────────────────────────────

@app.get("/", response_class=HTMLResponse)
async def serve_dashboard(request: Request):
    """Serve the web dashboard."""
    try:
        with open("dashboard/index.html", "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        return "<h1>Dashboard not found.</h1><p>Make sure dashboard/index.html exists.</p>"


@app.get("/api/status")
async def get_status():
    """Return current arm and server status."""
    return {
        "esp32_connected": esp32_connected,
        "esp32_last_seen": esp32_last_seen,
        "arm_state": arm_state,
        "ollama_available": ollama_available,
        "ollama_model": config.OLLAMA_MODEL,
        "mood": personality.get_mood(),
        "memory_stats": memory_store.get_stats(),
        "available_skills": [s["skill_id"] for s in skill_library.list_skills()],
        "available_tasks": task_planner.list_available_tasks(),
    }


@app.post("/api/command")
async def post_command(request: Request):
    """Send a command via HTTP (useful for testing)."""
    body = await request.json()
    text = body.get("text", "")
    if not text:
        return {"error": "No text provided"}

    result = process_user_command(text)
    await send_commands_to_esp32(result["commands"])
    await send_mood_to_esp32(result["mood"])

    await broadcast_to_dashboard({
        "type": "llm_response",
        "payload": {"message": result["response"], "thought": result["thought"]},
    })

    return {
        "response": result["response"],
        "commands_sent": len(result["commands"]),
        "mood": result["mood"],
    }


@app.post("/api/manual")
async def post_manual_command(request: Request):
    """Direct servo control — bypasses LLM."""
    body = await request.json()
    angles = body.get("joint_angles", [90, 90, 90, 0])
    gripper = body.get("gripper", 0.5)
    speed = body.get("speed", 30)
    duration_ms = body.get("duration_ms", 1000)

    cmd = {
        "type": "motion_command",
        "command_id": str(uuid.uuid4())[:8],
        "action": "manual",
        "joint_angles": angles,
        "gripper": gripper,
        "speed": speed,
        "duration_ms": duration_ms,
    }

    await send_to_esp32(cmd)
    await broadcast_to_dashboard({"type": "command_sent", "payload": cmd})

    memory_store.log_command("manual", [cmd], success=True)
    return {"status": "sent", "command": cmd}


@app.post("/api/teaching")
async def post_teaching_mode(request: Request):
    """Toggle teaching mode on/off."""
    body = await request.json()
    enabled = body.get("enabled", False)

    cmd = {
        "type": "teaching_mode",
        "command_id": str(uuid.uuid4())[:8],
        "enabled": enabled,
    }

    await send_to_esp32(cmd)
    await broadcast_to_dashboard({"type": "teaching_mode", "payload": {"enabled": enabled}})
    return {"status": "ok", "teaching": enabled}


@app.post("/api/save_skill")
async def post_save_skill(request: Request):
    """Save the last recorded trajectory as a named skill."""
    body = await request.json()
    name = body.get("name", "unnamed_skill")

    cmd = {
        "type": "save_skill",
        "command_id": str(uuid.uuid4())[:8],
        "name": name,
    }

    await send_to_esp32(cmd)
    return {"status": "ok", "skill_name": name}


@app.post("/api/emergency_stop")
async def post_emergency_stop():
    """Trigger emergency stop."""
    personality.on_event("emergency")
    cmd = {
        "type": "emergency_stop",
        "command_id": str(uuid.uuid4())[:8],
    }
    await send_to_esp32(cmd)
    await send_mood_to_esp32(personality.get_mood())
    await broadcast_to_dashboard({"type": "emergency_stop", "payload": True})
    return {"status": "stopped"}


@app.post("/api/clear_emergency")
async def post_clear_emergency():
    """Clear emergency stop."""
    personality.on_event("emergency_cleared")
    cmd = {
        "type": "clear_emergency",
        "command_id": str(uuid.uuid4())[:8],
    }
    await send_to_esp32(cmd)
    await send_mood_to_esp32(personality.get_mood())
    await broadcast_to_dashboard({"type": "emergency_stop", "payload": False})
    return {"status": "cleared"}


@app.get("/api/skills")
async def get_skills():
    """List all stored skills."""
    return {"skills": skill_library.list_skills()}


@app.get("/api/tasks")
async def get_tasks():
    """List available built-in tasks."""
    return {"tasks": task_planner.list_available_tasks()}


@app.get("/api/stats")
async def get_stats():
    """Return memory and performance statistics."""
    return memory_store.get_stats()


@app.get("/api/history")
async def get_history(limit: int = 20):
    """Return recent conversation history."""
    return {"history": memory_store.get_conversation_history(limit)}


@app.post("/api/play_skill")
async def post_play_skill(request: Request):
    """Execute a stored skill on the ESP32."""
    body = await request.json()
    skill_id = body.get("skill_id", "")
    skill = skill_library.load_skill(skill_id)
    if not skill:
        return {"error": f"Skill '{skill_id}' not found"}

    cmd = {
        "type": "learned_skill",
        "command_id": str(uuid.uuid4())[:8],
        "skill_name": skill_id,
    }

    await send_to_esp32(cmd)
    personality.on_event("task_start")
    await send_mood_to_esp32(personality.get_mood())
    return {"status": "playing", "skill": skill_id}


# ───────────────────────────────────────────────────────────────
# WebSocket: ESP32 Connection
# ───────────────────────────────────────────────────────────────

@app.websocket("/ws/esp32")
async def ws_esp32(websocket: WebSocket):
    """ESP32 connects here. Receives commands, sends state updates."""
    global esp32_socket, esp32_connected, esp32_last_seen
    await websocket.accept()
    esp32_socket = websocket
    esp32_connected = True
    esp32_last_seen = time.time()
    print("[ESP32] CONNECTED")
    await broadcast_to_dashboard({
        "type": "state",
        "payload": {**arm_state, "connected": True},
    })

    try:
        while True:
            msg = await websocket.receive_json()
            esp32_last_seen = time.time()

            if msg.get("type") == "state_update":
                for key in ["joint_angles", "gripper", "sensors", "status", "mood", "active_cmd", "emergency"]:
                    if key in msg:
                        arm_state[key] = msg[key]

                memory_store.log_state(
                    joint_angles=arm_state.get("joint_angles", []),
                    gripper=arm_state.get("gripper", 0.5),
                    distance=arm_state.get("sensors", {}).get("distance", 0),
                    current=arm_state.get("sensors", {}).get("current", 0),
                    mood=arm_state.get("mood", "curious"),
                    status=arm_state.get("status", "idle"),
                )

                current_mood = arm_state.get("mood", "curious")
                if personality.get_mood() != current_mood:
                    personality.on_event(f"mood_update_{current_mood}")

                if arm_state.get("status") == "idle" and personality.get_mood() == "busy":
                    personality.on_event("task_success")
                    await send_mood_to_esp32(personality.get_mood())

                await broadcast_to_dashboard({
                    "type": "state",
                    "payload": {**arm_state, "connected": True},
                })

            elif msg.get("type") == "command_ack":
                status = msg.get("status", "")
                cmd_id = msg.get("command_id", "")
                print(f"[ESP32] ACK: {status} ({cmd_id})")
                if "error" in status or "failed" in status:
                    personality.on_event("task_failure")
                    await send_mood_to_esp32(personality.get_mood())

    except WebSocketDisconnect:
        print("[ESP32] DISCONNECTED")
    except Exception as e:
        print(f"[ESP32] Error: {e}")
    finally:
        esp32_connected = False
        esp32_socket = None
        await broadcast_to_dashboard({
            "type": "state",
            "payload": {**arm_state, "connected": False},
        })


# ───────────────────────────────────────────────────────────────
# WebSocket: Dashboard Connection
# ───────────────────────────────────────────────────────────────

@app.websocket("/ws/dashboard")
async def ws_dashboard(websocket: WebSocket):
    """Web dashboard connects here. Sends commands, receives state."""
    await websocket.accept()
    dashboard_sockets.append(websocket)
    print("[Dashboard] CONNECTED")

    await websocket.send_json({
        "type": "state",
        "payload": {**arm_state, "connected": esp32_connected},
    })
    await websocket.send_json({
        "type": "ollama_status",
        "payload": {"connected": ollama_available, "model": config.OLLAMA_MODEL},
    })

    try:
        while True:
            msg = await websocket.receive_json()

            if msg.get("type") == "user_command":
                text = msg.get("payload", {}).get("text", "")
                print(f"[Dashboard] Command: {text}")

                result = process_user_command(text)
                await send_commands_to_esp32(result["commands"], ws=websocket)
                await send_mood_to_esp32(result["mood"])

                await websocket.send_json({
                    "type": "llm_response",
                    "payload": {"message": result["response"], "thought": result["thought"]},
                })

                command_history.append({
                    "timestamp": time.time(),
                    "text": text,
                    "response": result["response"],
                    "commands": result["commands"],
                })

            elif msg.get("type") == "manual_control":
                payload = msg.get("payload", {})
                cmd = {
                    "type": "motion_command",
                    "command_id": str(uuid.uuid4())[:8],
                    "action": "manual",
                    "joint_angles": payload.get("joint_angles", [90, 90, 90, 0]),
                    "gripper": payload.get("gripper", 0.5),
                    "speed": payload.get("speed", 30),
                    "duration_ms": payload.get("duration_ms", 1000),
                }
                personality.on_event("task_start")
                success = await send_to_esp32(cmd)
                await send_mood_to_esp32(personality.get_mood())
                await websocket.send_json({"type": "command_sent", "payload": cmd})
                if not success:
                    await websocket.send_json({
                        "type": "error",
                        "payload": "ESP32 not connected.",
                    })

            elif msg.get("type") == "emergency_stop":
                personality.on_event("emergency")
                cmd = {"type": "emergency_stop", "command_id": str(uuid.uuid4())[:8]}
                await send_to_esp32(cmd)
                await send_mood_to_esp32(personality.get_mood())
                await broadcast_to_dashboard({"type": "emergency_stop", "payload": True})

            elif msg.get("type") == "clear_emergency":
                personality.on_event("emergency_cleared")
                cmd = {"type": "clear_emergency", "command_id": str(uuid.uuid4())[:8]}
                await send_to_esp32(cmd)
                await send_mood_to_esp32(personality.get_mood())
                await broadcast_to_dashboard({"type": "emergency_stop", "payload": False})

            elif msg.get("type") == "toggle_teaching":
                enabled = msg.get("payload", {}).get("enabled", False)
                cmd = {
                    "type": "teaching_mode",
                    "command_id": str(uuid.uuid4())[:8],
                    "enabled": enabled,
                }
                await send_to_esp32(cmd)
                if enabled:
                    personality.on_event("ambiguous_command")
                else:
                    personality.on_event("user_input")
                await send_mood_to_esp32(personality.get_mood())
                await broadcast_to_dashboard({"type": "teaching_mode", "payload": {"enabled": enabled}})

            elif msg.get("type") == "save_skill":
                name = msg.get("payload", {}).get("name", "unnamed")
                cmd = {"type": "save_skill", "command_id": str(uuid.uuid4())[:8], "name": name}
                await send_to_esp32(cmd)

            elif msg.get("type") == "play_skill":
                skill_id = msg.get("payload", {}).get("skill_id", "")
                skill = skill_library.load_skill(skill_id)
                if skill:
                    cmd = {
                        "type": "learned_skill",
                        "command_id": str(uuid.uuid4())[:8],
                        "skill_name": skill_id,
                    }
                    await send_to_esp32(cmd)
                    personality.on_event("task_start")
                    await send_mood_to_esp32(personality.get_mood())
                    await websocket.send_json({"type": "skill_playing", "payload": skill_id})

    except WebSocketDisconnect:
        print("[Dashboard] DISCONNECTED")
    except Exception as e:
        print(f"[Dashboard] Error: {e}")
    finally:
        if websocket in dashboard_sockets:
            dashboard_sockets.remove(websocket)


# ───────────────────────────────────────────────────────────────
# Health Check Loop
# ───────────────────────────────────────────────────────────────

async def health_check_loop():
    """Periodically check Ollama and ESP32 status."""
    global ollama_available, esp32_connected
    while True:
        await asyncio.sleep(5)
        old_mood = personality.get_mood()
        personality.check_auto_transition()
        new_mood = personality.get_mood()
        
        if old_mood != new_mood:
            print(f"[Mood] Auto-transition: {old_mood} -> {new_mood}")
            await send_mood_to_esp32(new_mood)

        try:
            r = requests.get(f"{config.OLLAMA_URL}/api/tags", timeout=2)
            was_avail = ollama_available
            ollama_available = r.status_code == 200
            if ollama_available != was_avail:
                await broadcast_to_dashboard({
                    "type": "ollama_status",
                    "payload": {"connected": ollama_available, "model": config.OLLAMA_MODEL},
                })
        except Exception:
            if ollama_available:
                ollama_available = False
                await broadcast_to_dashboard({
                    "type": "ollama_status",
                    "payload": {"connected": False, "model": config.OLLAMA_MODEL},
                })

        if esp32_connected and (time.time() - esp32_last_seen) > 10:
            print("[ESP32] Timeout — no messages for 10s")


# ───────────────────────────────────────────────────────────────
# Startup
# ───────────────────────────────────────────────────────────────

@app.on_event("startup")
async def on_startup():
    memory_store.init_db()
    skill_library.init_db()
    asyncio.create_task(health_check_loop())
    print(f"\n{'='*50}")
    print(f"  AI Robotic Arm Backend Started")
    print(f"  Model:      {config.OLLAMA_MODEL}")
    print(f"  Dashboard:  http://localhost:{config.SERVER_PORT}")
    print(f"  ESP32 WS:   ws://localhost:{config.SERVER_PORT}/ws/esp32")
    print(f"  Dashboard:  ws://localhost:{config.SERVER_PORT}/ws/dashboard")
    print(f"  Skills DB:  {len(skill_library.list_skills())} skills loaded")
    print(f"  Tasks:      {len(task_planner.list_available_tasks())} built-in tasks")
    print(f"{'='*50}\n")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "server:app",
        host=config.SERVER_HOST,
        port=config.SERVER_PORT,
        reload=True,
    )
