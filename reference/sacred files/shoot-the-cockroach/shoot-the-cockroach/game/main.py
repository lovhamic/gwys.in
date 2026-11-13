#!/usr/bin/env python3
"""
Shoot the Cockroach - Main Entry Point
ESP32 + MPU6050 Physical Gun Game
"""

import sys
import time
import pygame
from config import *
from serial_controller import SerialController, find_esp32_port
from mpu6050_controller import MPU6050Controller
from game import Game, GameState


def main():
    # Initialize pygame
    pygame.init()
    pygame.mixer.init()

    # Create screen
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption(WINDOW_TITLE)
    clock = pygame.time.Clock()

    # Create game instance
    game = Game(screen)

    # Create controllers
    mpu_controller = MPU6050Controller()

    # Serial controller
    serial_controller = SerialController(SERIAL_PORT, BAUD_RATE)

    # Try to connect
    print("=" * 50)
    print("SHOOT THE COCKROACH - Starting...")
    print("=" * 50)

    # Auto-detect just enumerates existing COM ports (fast, non-blocking) -
    # safe to do on the main thread before the window loop starts.
    auto_port = find_esp32_port()
    if auto_port:
        print(f"Found likely ESP32 port: {auto_port}")
        serial_controller.port = auto_port
    else:
        print(f"No ESP32 auto-detected, will try configured port {SERIAL_PORT}")

    # The actual serial handshake (opening the port + waiting up to several
    # seconds for the ESP32_READY signal) used to run right here, blocking
    # the main thread. Since pygame never got to process window events or
    # redraw during that time, Windows/macOS would mark it "Not Responding"
    # and the crosshair would appear frozen. Doing it on a background
    # thread fixes both: the window opens and responds immediately, running
    # in mouse/demo mode until the ESP32 connects.
    serial_controller.connect_async()
    print("Connecting to ESP32 in the background...")
    print("Game will run in demo mode (mouse control) until it connects.")

    # Main loop
    running = True
    last_reconnect_attempt = time.time()
    reconnect_interval = 5.0  # seconds
    was_connected = False

    try:
        while running and game.is_running():
            # Console feedback whenever the connection state flips
            if serial_controller.is_connected() != was_connected:
                was_connected = serial_controller.is_connected()
                if was_connected:
                    print("ESP32 connected successfully! Switching to gun control.")
                else:
                    print(f"ESP32 disconnected. Error: {serial_controller.get_error()}")
                    print("Falling back to demo mode (mouse control).")
            # Handle events
            for event in pygame.event.get():
                game.handle_event(event)

                # Allow mouse control for testing without hardware
                if event.type == pygame.MOUSEMOTION:
                    if not serial_controller.is_connected():
                        x, y = event.pos
                        game.update_crosshair(x / SCREEN_WIDTH, y / SCREEN_HEIGHT)

                # Mouse click as shoot for testing
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    if not serial_controller.is_connected():
                        game.handle_shoot()

            # Read serial data
            if serial_controller.is_connected():
                sensor_data = serial_controller.get_latest_sensor_data()
                if sensor_data:
                    # Update MPU6050 controller and get crosshair position
                    crosshair_x, crosshair_y = mpu_controller.update(sensor_data)
                    game.update_crosshair(crosshair_x, crosshair_y)

                # Check for shoot command
                if serial_controller.check_shoot():
                    game.handle_shoot()

            # Handle calibration state
            if game.get_state() == GameState.CALIBRATION:
                if not mpu_controller.is_calibrating():
                    mpu_controller.start_calibration()

                # Update calibration progress
                progress = mpu_controller.get_calibration_progress()
                attempt, max_attempts = mpu_controller.get_calibration_attempt()
                game.set_calibration_progress(progress, mpu_controller.is_calibration_unstable(), attempt, max_attempts)

                if progress >= 1.0 and not mpu_controller.is_calibrating():
                    game.calibration_complete()

            # Update game logic
            game.update()

            # Draw
            game.draw()

            # Cap frame rate
            clock.tick(FPS)

            # Attempt reconnection if disconnected (non-blocking - runs on a
            # background thread so the game keeps rendering/responding at
            # full FPS while it retries).
            if not serial_controller.is_connected() and not serial_controller.is_connecting():
                current_time = time.time()
                if current_time - last_reconnect_attempt > reconnect_interval:
                    print("Attempting reconnection...")
                    serial_controller.connect_async()
                    last_reconnect_attempt = current_time

    except KeyboardInterrupt:
        print("\nInterrupted by user")
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        # Cleanup
        serial_controller.disconnect()
        pygame.quit()
        print("Game ended.")


if __name__ == "__main__":
    main()