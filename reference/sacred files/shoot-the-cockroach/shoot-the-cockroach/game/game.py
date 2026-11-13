"""
Main game logic for Shoot the Cockroach
Handles game states, scoring, levels, and game loop
"""

import pygame
import time
import random
from enum import Enum
from typing import Optional, List, Tuple
from config import *
from cockroach import Cockroach


class GameState(Enum):
    START = "start"
    CALIBRATION = "calibration"
    PLAYING = "playing"
    LEVEL_COMPLETE = "level_complete"
    GAME_OVER = "game_over"


class Game:
    def __init__(self, screen: pygame.Surface):
        self.screen = screen
        self.screen_width = screen.get_width()
        self.screen_height = screen.get_height()

        # Fonts
        self.font_large = pygame.font.Font(None, 72)
        self.font_medium = pygame.font.Font(None, 48)
        self.font_small = pygame.font.Font(None, 32)
        self.font_tiny = pygame.font.Font(None, 24)

        # Game state
        self.state = GameState.START
        self.running = True
        self.calibration_progress = 0.0
        self.calibration_unstable = False
        self.calibration_attempt = 1
        self.calibration_max_attempts = 1

        # Game data
        self.score = 0
        self.lives = STARTING_LIVES
        self.current_level = 0
        self.level_start_time = 0
        self.cockroaches_killed = 0

        # Cockroaches
        self.cockroaches: List[Cockroach] = []

        # Crosshair (set externally from MPU6050)
        self.crosshair_x = self.screen_width // 2
        self.crosshair_y = self.screen_height // 2

        # Shooting effects
        self.shoot_effect_timer = 0
        self.shoot_effect_pos = (0, 0)
        self.hit_effect_timer = 0
        self.hit_effect_pos = (0, 0)
        self.hit_effect_text = ""
        self.miss_effect_timer = 0

        # Timing
        self.last_time = time.time()
        self.dt = 0

        # Input
        self.keys_pressed = set()

        # Load background
        self.background = None
        self._load_background()

        # Sounds
        self.shoot_sound = None
        self.hit_sound = None
        self._load_sounds()

    def _load_background(self):
        try:
            self.background = pygame.image.load(BACKGROUND_IMAGE_FILE).convert()
            self.background = pygame.transform.scale(self.background,
                                                    (self.screen_width, self.screen_height))
        except:
            self.background = None

    def _load_sounds(self):
        if not ENABLE_SOUND:
            return
        try:
            self.shoot_sound = pygame.mixer.Sound(SHOOT_SOUND_FILE)
            self.hit_sound = pygame.mixer.Sound(HIT_SOUND_FILE)
        except:
            pass

    def handle_event(self, event: pygame.event.Event):
        """Handle pygame events"""
        if event.type == pygame.QUIT:
            self.running = False

        elif event.type == pygame.KEYDOWN:
            self.keys_pressed.add(event.key)

            if event.key == pygame.K_ESCAPE:
                self.running = False

            elif event.key == pygame.K_RETURN or event.key == pygame.K_KP_ENTER:
                if self.state == GameState.START:
                    self.start_calibration()
                elif self.state == GameState.GAME_OVER:
                    self.restart_game()
                elif self.state == GameState.LEVEL_COMPLETE:
                    self.next_level()

            elif event.key == pygame.K_c:
                if self.state == GameState.PLAYING:
                    self.start_calibration()

        elif event.type == pygame.KEYUP:
            self.keys_pressed.discard(event.key)

    def start_calibration(self):
        """Start calibration state"""
        self.state = GameState.CALIBRATION
        self.calibration_progress = 0.0
        self.calibration_unstable = False
        self.calibration_attempt = 1
        self.calibration_max_attempts = 1

    def calibration_complete(self):
        """Called when calibration finishes"""
        self.state = GameState.PLAYING
        self.spawn_cockroaches()
        self.level_start_time = time.time()

    def start_game(self):
        """Start a new game"""
        self.score = 0
        self.lives = STARTING_LIVES
        self.current_level = 0
        self.cockroaches_killed = 0
        self.start_calibration()

    def restart_game(self):
        """Restart from game over"""
        self.start_game()

    def next_level(self):
        """Advance to next level"""
        self.current_level += 1
        if self.current_level >= len(LEVEL_CONFIGS):
            self.current_level = len(LEVEL_CONFIGS) - 1
        self.cockroaches_killed = 0
        self.start_calibration()

    def spawn_cockroaches(self):
        """Spawn cockroaches for current level"""
        self.cockroaches.clear()
        config = LEVEL_CONFIGS[self.current_level]
        count = config["cockroach_count"]

        for _ in range(count):
            cockroach = Cockroach(self.screen_width, self.screen_height, config)
            cockroach.spawn()
            self.cockroaches.append(cockroach)

    def update_crosshair(self, x: float, y: float):
        """Update crosshair position from MPU6050 (normalized 0-1)"""
        self.crosshair_x = int(x * self.screen_width)
        self.crosshair_y = int(y * self.screen_height)

    def handle_shoot(self):
        """Handle trigger press from ESP32"""
        if self.state != GameState.PLAYING:
            return

        # Shoot effect
        self.shoot_effect_timer = SHOOT_EFFECT_DURATION
        self.shoot_effect_pos = (self.crosshair_x, self.crosshair_y)

        if self.shoot_sound:
            self.shoot_sound.play()

        # Check hits
        hit_any = False
        for cockroach in self.cockroaches:
            if cockroach.check_hit(self.crosshair_x, self.crosshair_y):
                cockroach.hit()
                hit_any = True

                # Calculate score
                config = LEVEL_CONFIGS[self.current_level]
                time_taken = time.time() - self.level_start_time
                if time_taken < config["fast_hit_threshold"]:
                    points = config["score_per_hit"] + config["fast_hit_bonus"]
                    self.hit_effect_text = "FAST HIT!"
                else:
                    points = config["score_per_hit"]
                    self.hit_effect_text = "HIT!"

                self.score += points
                self.cockroaches_killed += 1

                # Hit effect
                self.hit_effect_timer = HIT_EFFECT_DURATION
                self.hit_effect_pos = (self.crosshair_x, self.crosshair_y)

                if self.hit_sound:
                    self.hit_sound.play()

                # Check level complete
                if self.cockroaches_killed >= config["cockroach_count"]:
                    self.state = GameState.LEVEL_COMPLETE
                break

        if not hit_any:
            self.miss_effect_timer = MISS_EFFECT_DURATION
            self.hit_effect_text = "MISS!"
            self.hit_effect_timer = MISS_EFFECT_DURATION
            self.hit_effect_pos = (self.crosshair_x, self.crosshair_y)

    def update(self):
        """Update game logic"""
        current_time = time.time()
        self.dt = current_time - self.last_time
        self.last_time = current_time

        # Clamp dt
        self.dt = max(0.001, min(self.dt, 0.1))

        if self.state == GameState.PLAYING:
            # Update cockroaches
            for cockroach in self.cockroaches:
                cockroach.update(self.dt)

                # Check if cockroach escaped
                if not cockroach.is_alive() and cockroach.death_animation <= 0:
                    if cockroach.time_remaining() <= 0:
                        self.lose_life()

            # Remove dead cockroaches
            self.cockroaches = [c for c in self.cockroaches if c.is_alive()]

            # Update effects
            if self.shoot_effect_timer > 0:
                self.shoot_effect_timer -= self.dt
            if self.hit_effect_timer > 0:
                self.hit_effect_timer -= self.dt
            if self.miss_effect_timer > 0:
                self.miss_effect_timer -= self.dt

    def lose_life(self):
        """Player loses a life"""
        self.lives -= LIFE_LOST_ON_ESCAPE
        if self.lives <= 0:
            self.state = GameState.GAME_OVER
        else:
            # Respawn cockroaches
            self.spawn_cockroaches()
            self.level_start_time = time.time()

    def draw(self):
        """Render the game"""
        # Background
        if self.background:
            self.screen.blit(self.background, (0, 0))
        else:
            self.screen.fill(DARK_GRAY)

        # Draw based on state
        if self.state == GameState.START:
            self._draw_start_screen()
        elif self.state == GameState.CALIBRATION:
            self._draw_calibration_screen()
        elif self.state == GameState.PLAYING:
            self._draw_gameplay()
        elif self.state == GameState.LEVEL_COMPLETE:
            self._draw_gameplay()  # Draw game in background
            self._draw_level_complete()
        elif self.state == GameState.GAME_OVER:
            self._draw_gameplay()  # Draw game in background
            self._draw_game_over()

        # Always draw HUD during gameplay states
        if self.state in (GameState.PLAYING, GameState.LEVEL_COMPLETE, GameState.GAME_OVER):
            self._draw_hud()

        pygame.display.flip()

    def _draw_start_screen(self):
        """Draw start screen"""
        center_x = self.screen_width // 2
        center_y = self.screen_height // 2

        # Title
        title = self.font_large.render("SHOOT THE COCKROACH", True, WHITE)
        title_rect = title.get_rect(center=(center_x, center_y - 150))
        self.screen.blit(title, title_rect)

        # Instructions
        lines = [
            "Move the gun to aim.",
            "Press the physical trigger to shoot.",
            "",
            "Press ENTER to start.",
            "Press ESC to quit.",
        ]

        y = center_y - 50
        for line in lines:
            if line:
                text = self.font_small.render(line, True, LIGHT_GRAY)
                rect = text.get_rect(center=(center_x, y))
                self.screen.blit(text, rect)
            y += 35

        # Controls hint
        hint = self.font_tiny.render("C = Recalibrate during game", True, CYAN)
        hint_rect = hint.get_rect(center=(center_x, center_y + 200))
        self.screen.blit(hint, hint_rect)

    def _draw_calibration_screen(self):
        """Draw calibration screen"""
        center_x = self.screen_width // 2
        center_y = self.screen_height // 2

        # Title
        title = self.font_large.render("CALIBRATING...", True, YELLOW)
        title_rect = title.get_rect(center=(center_x, center_y - 100))
        self.screen.blit(title, title_rect)

        # Instruction
        instruction = "Movement detected - hold still, restarting..." if self.calibration_unstable else "Keep the gun still"
        instruction_color = YELLOW if self.calibration_unstable else WHITE
        text = self.font_medium.render(instruction, True, instruction_color)
        rect = text.get_rect(center=(center_x, center_y))
        self.screen.blit(text, rect)

        # Attempt counter - only shown once a retry has actually happened,
        # so a normal steady calibration doesn't clutter the screen with
        # "1/4" every time. Makes a retry look like visible progress
        # instead of a frozen/stuck screen.
        if self.calibration_max_attempts > 1:
            attempt_text = self.font_tiny.render(
                f"Attempt {self.calibration_attempt}/{self.calibration_max_attempts}", True, LIGHT_GRAY
            )
            attempt_rect = attempt_text.get_rect(center=(center_x, center_y + 40))
            self.screen.blit(attempt_text, attempt_rect)

        # Progress bar
        bar_width = 400
        bar_height = 20
        bar_x = center_x - bar_width // 2
        bar_y = center_y + 80

        pygame.draw.rect(self.screen, DARK_GRAY, (bar_x, bar_y, bar_width, bar_height), border_radius=10)

        # Progress fill - drawn here, after the background clear earlier in
        # draw(), so it's not immediately wiped out (see set_calibration_progress).
        fill_width = int(bar_width * self.calibration_progress)
        if fill_width > 0:
            pygame.draw.rect(self.screen, GREEN, (bar_x, bar_y, fill_width, bar_height), border_radius=10)

        # Progress text
        progress_text = self.font_small.render(f"{int(self.calibration_progress * 100)}%", True, LIGHT_GRAY)
        progress_rect = progress_text.get_rect(center=(center_x, bar_y + 40))
        self.screen.blit(progress_text, progress_rect)

    def _draw_gameplay(self):
        """Draw gameplay elements"""
        # Draw cockroaches
        for cockroach in self.cockroaches:
            cockroach.draw(self.screen)

        # Draw shoot effect
        if self.shoot_effect_timer > 0:
            self._draw_shoot_effect()

        # Draw hit/miss effect
        if self.hit_effect_timer > 0:
            self._draw_hit_effect()

        # Draw crosshair
        self._draw_crosshair()

    def _draw_crosshair(self):
        """Draw aiming crosshair"""
        x, y = self.crosshair_x, self.crosshair_y
        size = CROSSHAIR_SIZE
        color = CROSSHAIR_COLOR
        thickness = CROSSHAIR_THICKNESS

        # Crosshair lines
        pygame.draw.line(self.screen, color, (x - size, y), (x - size // 2, y), thickness)
        pygame.draw.line(self.screen, color, (x + size // 2, y), (x + size, y), thickness)
        pygame.draw.line(self.screen, color, (x, y - size), (x, y - size // 2), thickness)
        pygame.draw.line(self.screen, color, (x, y + size // 2), (x, y + size), thickness)

        # Center dot
        pygame.draw.circle(self.screen, color, (x, y), 3)

        # Outer circle
        pygame.draw.circle(self.screen, color, (x, y), size, 1)

    def _draw_shoot_effect(self):
        """Draw muzzle flash effect"""
        x, y = self.shoot_effect_pos
        progress = 1.0 - (self.shoot_effect_timer / SHOOT_EFFECT_DURATION)
        radius = int(MUZZLE_FLASH_RADIUS * progress)
        alpha = int(255 * (1 - progress))

        if radius > 0:
            flash_surface = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)
            pygame.draw.circle(flash_surface, (*YELLOW, alpha), (radius, radius), radius)
            self.screen.blit(flash_surface, (x - radius, y - radius))

    def _draw_hit_effect(self):
        """Draw hit/miss text effect"""
        x, y = self.hit_effect_pos
        progress = 1.0 - (self.hit_effect_timer / HIT_EFFECT_DURATION)

        # Floating text
        color = GREEN if "HIT" in self.hit_effect_text else RED
        alpha = int(255 * (1 - progress))
        offset_y = int(30 * progress)

        text = self.font_medium.render(self.hit_effect_text, True, color)
        text.set_alpha(alpha)
        rect = text.get_rect(center=(x, y - offset_y))
        self.screen.blit(text, rect)

    def _draw_hud(self):
        """Draw heads-up display"""
        # Score
        score_text = self.font_small.render(f"SCORE: {self.score}", True, WHITE)
        self.screen.blit(score_text, (20, 20))

        # Lives
        lives_text = self.font_small.render(f"LIVES: ", True, WHITE)
        self.screen.blit(lives_text, (20, 60))
        # Draw heart icons
        heart_x = 20 + lives_text.get_width()
        for i in range(self.lives):
            pygame.draw.polygon(self.screen, RED, [
                (heart_x + i * 30 + 10, 65),
                (heart_x + i * 30 + 15, 55),
                (heart_x + i * 30 + 20, 65),
                (heart_x + i * 30 + 15, 75),
            ])

        # Level
        level_name = LEVEL_CONFIGS[self.current_level]["name"]
        level_text = self.font_small.render(f"LEVEL: {self.current_level + 1} - {level_name}", True, CYAN)
        self.screen.blit(level_text, (20, 100))

        # Cockroach timer (for current cockroach)
        if self.cockroaches:
            cockroach = self.cockroaches[0]
            time_left = cockroach.time_remaining()
            timer_color = GREEN if time_left > 2 else (YELLOW if time_left > 1 else RED)
            timer_text = self.font_small.render(f"TIME: {time_left:.1f}s", True, timer_color)
            self.screen.blit(timer_text, (self.screen_width - 200, 20))

        # Debug info
        if DEBUG_MODE:
            self._draw_debug_info()

    def _draw_debug_info(self):
        """Draw debug overlay"""
        debug_y = self.screen_height - 200
        debug_lines = [
            f"State: {self.state.value}",
            f"Crosshair: ({self.crosshair_x}, {self.crosshair_y})",
            f"Cockroaches: {len(self.cockroaches)}",
            f"FPS: {1/self.dt:.1f}" if self.dt > 0 else "FPS: --",
        ]

        for i, line in enumerate(debug_lines):
            text = self.font_tiny.render(line, True, YELLOW)
            self.screen.blit(text, (20, debug_y + i * 22))

    def _draw_level_complete(self):
        """Draw level complete overlay"""
        self._draw_overlay("LEVEL COMPLETE!", GREEN,
                          f"Score: {self.score}",
                          "Press ENTER for next level")

    def _draw_game_over(self):
        """Draw game over screen"""
        self._draw_overlay("GAME OVER", RED,
                          f"Final Score: {self.score}",
                          "Press ENTER to play again",
                          "Press ESC to quit")

    def _draw_overlay(self, title: str, title_color: Tuple[int, int, int], *lines: str):
        """Draw a centered overlay with title and lines"""
        overlay = pygame.Surface((self.screen_width, self.screen_height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        self.screen.blit(overlay, (0, 0))

        center_x = self.screen_width // 2
        center_y = self.screen_height // 2 - 50

        # Title
        title_surf = self.font_large.render(title, True, title_color)
        title_rect = title_surf.get_rect(center=(center_x, center_y))
        self.screen.blit(title_surf, title_rect)

        # Lines
        y = center_y + 60
        for line in lines:
            text = self.font_medium.render(line, True, WHITE)
            rect = text.get_rect(center=(center_x, y))
            self.screen.blit(text, rect)
            y += 50

    def set_calibration_progress(self, progress: float, unstable: bool = False, attempt: int = 1, max_attempts: int = 1):
        """Store calibration progress (called from main loop, before draw()).

        This used to draw the green fill directly onto self.screen right
        here - but it's called before draw(), and draw() clears the whole
        screen and redraws the (empty) calibration bar right after, so the
        fill was wiped every single frame. The bar looked permanently
        stuck at 0%, even though calibration was progressing normally
        underneath - easy to mistake for a freeze and move/bump the gun
        mid-calibration, which throws off the offsets it's computing.
        Just store the value here; _draw_calibration_screen() draws the
        fill using it, in the correct order.
        """
        if self.state != GameState.CALIBRATION:
            return
        self.calibration_progress = progress
        self.calibration_unstable = unstable
        self.calibration_attempt = attempt
        self.calibration_max_attempts = max_attempts

    def get_state(self) -> GameState:
        return self.state

    def is_running(self) -> bool:
        return self.running