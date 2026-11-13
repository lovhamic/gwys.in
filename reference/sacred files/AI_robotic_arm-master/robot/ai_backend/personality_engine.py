"""
Personality Engine — Mood system for the robot

Moods: curious, happy, confused, sad, busy, sleeping
- Events trigger mood transitions
- Mood affects LLM prompt, LED color, motion speed
- Auto-transitions back to curious after timeout
"""

import time
from typing import Dict, Any

import config


class PersonalityEngine:
    def __init__(self):
        self.mood = "curious"
        self.mood_since = time.time()
        self.p = config.PERSONALITY
        self.traits = self.p["traits"]
    
    def get_mood(self) -> str:
        return self.mood
    
    def get_mood_response(self) -> str:
        """Return a canned response for the current mood."""
        return self.p["mood_responses"].get(self.mood, "...")
    
    def on_event(self, event: str, data: dict = None):
        """React to events and change mood."""
        old_mood = self.mood
        
        if event == "task_start":
            self.mood = "busy"
        elif event == "task_success":
            self.mood = "happy"
        elif event == "task_failure":
            self.mood = "sad"
        elif event == "ambiguous_command":
            self.mood = "confused"
        elif event == "idle_timeout":
            self.mood = "sleeping"
        elif event == "user_input":
            if self.mood in ("sleeping", "sad"):
                self.mood = "curious"
        elif event == "emergency":
            self.mood = "sad"
        elif event == "emergency_cleared":
            self.mood = "curious"
        
        if self.mood != old_mood:
            self.mood_since = time.time()
    
    def check_auto_transition(self):
        """Auto-transition moods after timeout."""
        elapsed = time.time() - self.mood_since
        
        if self.mood == "happy" and elapsed > 5:
            self.mood = "curious"
            self.mood_since = time.time()
        elif self.mood == "sad" and elapsed > 10:
            self.mood = "confused"
            self.mood_since = time.time()
        elif self.mood == "confused" and elapsed > 30:
            self.mood = "curious"
            self.mood_since = time.time()
        elif self.mood == "busy" and elapsed > 60:
            self.mood = "curious"
            self.mood_since = time.time()
    
    def get_speed_multiplier(self) -> float:
        """Mood affects motion speed."""
        if self.mood == "happy":
            return 1.1
        elif self.mood == "sad":
            return 0.8
        elif self.mood == "busy":
            return 1.0
        else:
            return 1.0
    
    def build_prompt_injection(self) -> str:
        """Extra text to inject into LLM prompt based on mood."""
        injections = {
            "curious": "You are curious and eager to explore. Ask questions if the task is interesting.",
            "happy": "You just succeeded at something! Be enthusiastic and celebratory in your response.",
            "confused": "You are confused about the user's request. Ask a clarifying question politely.",
            "sad": "You made a mistake or failed. Apologize briefly, then ask how to do better.",
            "busy": "You are in the middle of executing a task. Keep your response very short.",
            "sleeping": "You were idle. Wake up with a friendly greeting and ask what to do.",
        }
        return injections.get(self.mood, "")
    
    def to_dict(self) -> dict:
        return {
            "mood": self.mood,
            "since": self.mood_since,
            "traits": self.traits,
        }
