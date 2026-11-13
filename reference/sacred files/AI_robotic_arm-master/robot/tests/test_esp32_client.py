"""
Fake ESP32 Client — Simulates the robot for testing without hardware.

Supports: motion_command (stepper base + servos), teaching_mode, save_skill, emergency_stop
Run: python test_esp32_client.py
"""

import asyncio
import websockets
import json
import random
import time

SERVER_URL = "ws://localhost:8000/ws/esp32"

# Joint types: 2=stepper, 0=standard, 1=continuous
JOINT_TYPES = [2, 0, 0, 1]
JOINT_DEFAULTS = [0, 90, 90, 90]  # base=0°, shoulder=90°, elbow=90°, wrist=stop(90)


async def fake_esp32():
    print("[ESP32] Connecting to server...")
    async with websockets.connect(SERVER_URL) as ws:
        print("[ESP32] Connected!")

        state = {
            "type": "state_update",
            "timestamp": int(time.time()),
            "joint_angles": list(JOINT_DEFAULTS),
            "gripper": 0.5,
            "sensors": {"distance": 25.0, "current": 0.5},
            "status": "idle",
            "mood": "curious",
            "active_cmd": "none",
            "emergency": False,
            "joint_types": JOINT_TYPES,
        }
        await ws.send(json.dumps(state))
        print("[ESP32] Sent initial state.")

        last_update = time.time()
        emergency = False

        while True:
            try:
                msg = await asyncio.wait_for(ws.recv(), timeout=1.0)
                data = json.loads(msg)
                msg_type = data.get("type", "")

                if msg_type == "motion_command":
                    if emergency:
                        await ws.send(json.dumps({
                            "type": "command_ack",
                            "command_id": data.get("command_id"),
                            "status": "rejected_emergency"
                        }))
                        continue

                    await ws.send(json.dumps({
                        "type": "command_ack",
                        "command_id": data.get("command_id"),
                        "status": "accepted"
                    }))
                    print(f"[ESP32] Executing: {data.get('action', 'move')} ({data.get('command_id')})")

                    state["status"] = "executing"
                    state["mood"] = "busy"
                    state["active_cmd"] = data.get("action", "move")

                    angles = data.get("joint_angles", [0, 90, 90, 90])
                    state["joint_angles"] = list(angles)
                    if "gripper" in data:
                        state["gripper"] = data["gripper"]
                    state["sensors"]["current"] = round(random.uniform(0.6, 1.2), 2)
                    state["timestamp"] = int(time.time())
                    await ws.send(json.dumps(state))

                    await asyncio.sleep(2)

                    state["status"] = "idle"
                    state["mood"] = "curious"
                    state["active_cmd"] = "none"
                    state["sensors"]["current"] = 0.5
                    state["timestamp"] = int(time.time())
                    await ws.send(json.dumps(state))
                    print("[ESP32] Done.")

                elif msg_type == "teaching_mode":
                    enabled = data.get("enabled", False)
                    state["status"] = "teaching" if enabled else "idle"
                    state["mood"] = "confused" if enabled else "curious"
                    await ws.send(json.dumps({
                        "type": "command_ack",
                        "command_id": data.get("command_id"),
                        "status": "teaching_started" if enabled else "teaching_stopped"
                    }))
                    state["timestamp"] = int(time.time())
                    await ws.send(json.dumps(state))
                    print(f"[ESP32] Teaching mode: {'ON' if enabled else 'OFF'}")

                elif msg_type == "save_skill":
                    await ws.send(json.dumps({
                        "type": "command_ack",
                        "command_id": data.get("command_id"),
                        "status": "skill_saved"
                    }))
                    print(f"[ESP32] Skill saved: {data.get('name', 'unnamed')}")

                elif msg_type == "learned_skill":
                    await ws.send(json.dumps({
                        "type": "command_ack",
                        "command_id": data.get("command_id"),
                        "status": "skill_executing"
                    }))
                    print(f"[ESP32] Playing skill: {data.get('skill_name')}")

                elif msg_type == "emergency_stop":
                    emergency = True
                    state["emergency"] = True
                    state["status"] = "error"
                    state["mood"] = "sad"
                    state["active_cmd"] = "emergency"
                    state["timestamp"] = int(time.time())
                    await ws.send(json.dumps(state))
                    print("[ESP32] EMERGENCY STOP!")

                elif msg_type == "clear_emergency":
                    emergency = False
                    state["emergency"] = False
                    state["status"] = "idle"
                    state["mood"] = "curious"
                    state["active_cmd"] = "none"
                    state["timestamp"] = int(time.time())
                    await ws.send(json.dumps(state))
                    print("[ESP32] Emergency cleared.")

            except asyncio.TimeoutError:
                if time.time() - last_update > 1.0:
                    state["timestamp"] = int(time.time())
                    state["sensors"]["distance"] = round(random.uniform(10, 50), 1)
                    await ws.send(json.dumps(state))
                    last_update = time.time()

            except websockets.exceptions.ConnectionClosed:
                print("[ESP32] Connection closed.")
                break


if __name__ == "__main__":
    asyncio.run(fake_esp32())
