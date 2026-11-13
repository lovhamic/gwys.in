"""
Cockroach enemy class
Handles spawning, movement, and rendering of cockroaches
"""

import random
import time
import math
import pygame
from typing import Tuple, Optional
from config import *


class Cockroach:
    def __init__(self, screen_width: int, screen_height: int, level_config: dict):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.level_config = level_config

        # Visual properties
        self.size = COCKROACH_SIZE
        self.color = BROWN
        self.dark_color = DARK_BROWN

        # Load image if available
        self.image = None
        self._load_image()

        # State
        self.active = False
        self.x = 0
        self.y = 0
        self.vx = 0
        self.vy = 0
        self.target_vx = 0
        self.target_vy = 0

        # Movement
        self.base_speed = COCKROACH_BASE_SPEED * level_config["speed_multiplier"]
        self.max_speed = COCKROACH_MAX_SPEED * level_config["speed_multiplier"]
        self.current_speed = self.base_speed

        # Hitbox
        self.hit_radius = COCKROACH_HIT_RADIUS * level_config["hitbox_multiplier"]

        # Timing
        self.spawn_time = 0
        self.last_direction_change = 0
        self.direction_change_interval = random.uniform(*DIRECTION_CHANGE_INTERVAL)
        self.lifetime = level_config["time_per_cockroach"]

        # Visual effects
        self.hit_flash = 0
        self.death_animation = 0

    def _load_image(self):
        """Try to load cockroach image"""
        try:
            self.image = pygame.image.load(COCKROACH_IMAGE_FILE).convert_alpha()
            self.image = pygame.transform.scale(self.image, (self.size, self.size))
        except:
            self.image = None

    def spawn(self):
        """Spawn cockroach at random position"""
        margin = COCKROACH_SPAWN_MARGIN
        self.x = random.uniform(margin, self.screen_width - margin)
        self.y = random.uniform(margin, self.screen_height - margin)

        # Random initial direction
        angle = random.uniform(0, 2 * math.pi)
        self.vx = math.cos(angle) * self.base_speed
        self.vy = math.sin(angle) * self.base_speed
        self.target_vx = self.vx
        self.target_vy = self.vy

        self.active = True
        self.spawn_time = time.time()
        self.last_direction_change = time.time()
        self.direction_change_interval = random.uniform(*DIRECTION_CHANGE_INTERVAL)
        self.lifetime = self.level_config["time_per_cockroach"]
        self.hit_flash = 0
        self.death_animation = 0

    def update(self, dt: float):
        """Update cockroach position and behavior"""
        if not self.active:
            return

        current_time = time.time()

        # Check lifetime
        if current_time - self.spawn_time > self.lifetime:
            self.active = False
            return

        # Change direction periodically
        if current_time - self.last_direction_change > self.direction_change_interval:
            self._change_direction()
            self.last_direction_change = current_time
            self.direction_change_interval = random.uniform(*DIRECTION_CHANGE_INTERVAL)
            # Increase direction change rate for higher levels
            self.direction_change_interval /= self.level_config["direction_change_rate"]

        # Smoothly interpolate velocity toward target
        accel = COCKROACH_ACCELERATION * dt
        self.vx += (self.target_vx - self.vx) * accel
        self.vy += (self.target_vy - self.vy) * accel

        # Update position
        self.x += self.vx * dt
        self.y += self.vy * dt

        # Bounce off walls
        margin = self.size // 2
        if self.x < margin:
            self.x = margin
            self.vx = abs(self.vx)
            self.target_vx = abs(self.target_vx)
        elif self.x > self.screen_width - margin:
            self.x = self.screen_width - margin
            self.vx = -abs(self.vx)
            self.target_vx = -abs(self.target_vx)

        if self.y < margin:
            self.y = margin
            self.vy = abs(self.vy)
            self.target_vy = abs(self.target_vy)
        elif self.y > self.screen_height - margin:
            self.y = self.screen_height - margin
            self.vy = -abs(self.vy)
            self.target_vy = -abs(self.target_vy)

        # Update visual effects
        if self.hit_flash > 0:
            self.hit_flash -= dt
        if self.death_animation > 0:
            self.death_animation -= dt
            if self.death_animation <= 0:
                self.active = False

    def _change_direction(self):
        """Randomly change movement direction"""
        # Add some randomness to current direction
        angle = math.atan2(self.vy, self.vx)
        angle += random.uniform(-math.pi / 2, math.pi / 2)

        # Vary speed
        speed = random.uniform(self.base_speed * 0.7, self.max_speed)
        self.target_vx = math.cos(angle) * speed
        self.target_vy = math.sin(angle) * speed

    def check_hit(self, crosshair_x: float, crosshair_y: float) -> bool:
        """Check if crosshair is within hit radius"""
        if not self.active or self.death_animation > 0:
            return False

        dx = crosshair_x - self.x
        dy = crosshair_y - self.y
        distance = math.hypot(dx, dy)

        return distance <= self.hit_radius

    def hit(self):
        """Register a hit"""
        self.hit_flash = HIT_EFFECT_DURATION
        self.death_animation = HIT_EFFECT_DURATION
        self.active = False

    def draw(self, screen: pygame.Surface):
        """Draw cockroach on screen"""
        if not self.active:
            return

        # Draw death animation
        if self.death_animation > 0:
            self._draw_death_effect(screen)
            return

        # Draw hit flash
        if self.hit_flash > 0:
            alpha = int(255 * (self.hit_flash / HIT_EFFECT_DURATION))
            flash_surface = pygame.Surface((self.size * 2, self.size * 2), pygame.SRCALPHA)
            pygame.draw.circle(flash_surface, (*WHITE, alpha), (self.size, self.size), self.size)
            screen.blit(flash_surface, (self.x - self.size, self.y - self.size))

        # Draw cockroach
        if self.image:
            rect = self.image.get_rect(center=(int(self.x), int(self.y)))
            screen.blit(self.image, rect)
        else:
            self._draw_procedural(screen)

    def _draw_procedural(self, screen: pygame.Surface):
        """Draw a procedural cockroach shape"""
        cx, cy = int(self.x), int(self.y)
        s = self.size // 2

        # Body (oval)
        pygame.draw.ellipse(screen, self.color, (cx - s, cy - s // 2, s * 2, s))
        # Head
        pygame.draw.circle(screen, self.dark_color, (cx + s, cy), s // 2)
        # Antennae
        pygame.draw.line(screen, self.dark_color,
                        (cx + s, cy - s // 3), (cx + s + 10, cy - s), 2)
        pygame.draw.line(screen, self.dark_color,
                        (cx + s, cy + s // 3), (cx + s + 10, cy + s), 2)
        # Legs
        for i in range(3):
            y_offset = -s // 2 + i * s // 2
            pygame.draw.line(screen, self.dark_color,
                           (cx - s // 2, cy + y_offset), (cx - s, cy + y_offset - 5), 2)
            pygame.draw.line(screen, self.dark_color,
                           (cx - s // 2, cy + y_offset), (cx - s, cy + y_offset + 5), 2)
            pygame.draw.line(screen, self.dark_color,
                           (cx + s // 2, cy + y_offset), (cx + s, cy + y_offset - 5), 2)
            pygame.draw.line(screen, self.dark_color,
                           (cx + s // 2, cy + y_offset), (cx + s, cy + y_offset + 5), 2)

    def _draw_death_effect(self, screen: pygame.Surface):
        """Draw death/squish effect"""
        progress = 1.0 - (self.death_animation / HIT_EFFECT_DURATION)
        cx, cy = int(self.x), int(self.y)
        max_radius = self.size

        # Expanding ring
        radius = int(max_radius * progress)
        alpha = int(255 * (1 - progress))
        if radius > 0:
            pygame.draw.circle(screen, (*RED, alpha), (cx, cy), radius, 3)

        # "X" mark
        x_size = int(self.size * progress)
        pygame.draw.line(screen, RED,
                        (cx - x_size, cy - x_size), (cx + x_size, cy + x_size), 4)
        pygame.draw.line(screen, RED,
                        (cx - x_size, cy + x_size), (cx + x_size, cy - x_size), 4)

    def get_position(self) -> Tuple[float, float]:
        return self.x, self.y

    def is_active(self) -> bool:
        return self.active and self.death_animation <= 0

    def is_alive(self) -> bool:
        return self.active

    def time_remaining(self) -> float:
        if not self.active:
            return 0
        elapsed = time.time() - self.spawn_time
        return max(0, self.lifetime - elapsed)

    def get_lifetime_progress(self) -> float:
        """Return 0.0 to 1.0 representing lifetime progress"""
        if not self.active:
            return 1.0
        elapsed = time.time() - self.spawn_time
        return min(elapsed / self.lifetime, 1.0)