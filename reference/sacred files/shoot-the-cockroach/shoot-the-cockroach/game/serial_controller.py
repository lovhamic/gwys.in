"""
Serial communication controller for ESP32 connection
Handles connection, data parsing, and error recovery
"""

import serial
import serial.tools.list_ports
import threading
import time
import queue
from typing import Optional, Tuple, List
from config import *


class SerialController:
    def __init__(self, port: str = SERIAL_PORT, baud: int = BAUD_RATE):
        self.port = port
        self.baud = baud
        self.serial_conn: Optional[serial.Serial] = None
        self.running = False
        self.read_thread: Optional[threading.Thread] = None
        self.data_queue = queue.Queue(maxsize=100)
        self.shoot_queue = queue.Queue(maxsize=50)
        self.connected = False
        self.last_error = ""
        self.connecting = False
        self._connect_lock = threading.Lock()

    def list_available_ports(self) -> List[str]:
        """Return list of available serial ports"""
        ports = serial.tools.list_ports.comports()
        return [f"{p.device} - {p.description}" for p in ports]

    def auto_detect_port(self) -> Optional[str]:
        """Try to auto-detect ESP32 port"""
        ports = serial.tools.list_ports.comports()
        for port in ports:
            # Common ESP32 identifiers
            desc = port.description.lower()
            if any(keyword in desc for keyword in ['esp32', 'silicon labs', 'cp210', 'ch340', 'uart', 'usb serial']):
                return port.device
        return None

    def connect(self) -> bool:
        """Connect to ESP32 via serial"""
        try:
            if self.serial_conn and self.serial_conn.is_open:
                self.disconnect()

            self.serial_conn = serial.Serial(
                port=self.port,
                baudrate=self.baud,
                timeout=SERIAL_TIMEOUT,
                write_timeout=1.0
            )

            # Clear stale bytes sitting in the OS buffers *right after
            # opening* - not after waiting for the board to boot. Opening
            # the port toggles DTR/RTS on most ESP32 dev boards, which
            # resets them; the sketch prints "ESP32_READY" once, within a
            # few hundred ms of that reset, then moves on to streaming
            # DATA/SHOOT forever. Flushing the buffer *after* a sleep (the
            # old code did `sleep(2.0)` then `reset_input_buffer()`) throws
            # away that one-time READY line before it's ever read, so the
            # handshake below then waits for a READY that will never come
            # again this boot - it always times out even though the board
            # is working perfectly.
            self.serial_conn.reset_input_buffer()
            self.serial_conn.reset_output_buffer()

            # Wait for the board to boot and start talking. Accept either
            # the one-time "ESP32_READY" line, or a normal DATA/SHOOT line.
            # The latter matters for boards that don't reset on port-open
            # (native-USB ESP32-S2/S3/C3, or auto-reset disabled in the
            # IDE) - they're already mid-loop and will never send READY
            # again, but a DATA line is just as good proof they're alive.
            start_time = time.time()
            got_any_line = False
            while time.time() - start_time < 5.0:
                if self.serial_conn.in_waiting:
                    line = self.serial_conn.readline().decode('utf-8', errors='ignore').strip()
                    if not line:
                        continue
                    got_any_line = True
                    if line == "ESP32_READY" or line.startswith("DATA,") or line == "SHOOT":
                        self.connected = True
                        self.last_error = ""
                        return True
                else:
                    time.sleep(0.01)

            if got_any_line:
                self.last_error = "Received data from device but couldn't recognize it (check baud rate / sketch)"
            else:
                self.last_error = "No response from ESP32 (check port, wiring, and that the sketch is running)"
            return False

        except serial.SerialException as e:
            self.last_error = f"Serial connection failed: {e}"
            self.connected = False
            return False
        except Exception as e:
            self.last_error = f"Connection error: {e}"
            self.connected = False
            return False

    def disconnect(self):
        """Disconnect from ESP32"""
        self.running = False
        if self.read_thread and self.read_thread.is_alive():
            self.read_thread.join(timeout=1.0)
        if self.serial_conn and self.serial_conn.is_open:
            self.serial_conn.close()
        self.connected = False

    def start_reading(self):
        """Start background thread for reading serial data"""
        if not self.connected:
            return
        self.running = True
        self.read_thread = threading.Thread(target=self._read_loop, daemon=True)
        self.read_thread.start()

    def _read_loop(self):
        """Background thread: continuously read and parse serial data"""
        buffer = ""
        while self.running and self.connected:
            try:
                if self.serial_conn and self.serial_conn.in_waiting:
                    data = self.serial_conn.read(self.serial_conn.in_waiting).decode('utf-8', errors='ignore')
                    buffer += data

                    # Process complete lines
                    while '\n' in buffer:
                        line, buffer = buffer.split('\n', 1)
                        line = line.strip()
                        if line:
                            self._parse_line(line)

                else:
                    time.sleep(0.001)  # Small delay to prevent CPU spinning

            except serial.SerialException as e:
                self.last_error = f"Serial read error: {e}"
                self.connected = False
                break
            except Exception as e:
                self.last_error = f"Read loop error: {e}"
                # Continue running, don't break on parse errors

    def _parse_line(self, line: str):
        """Parse a single line from ESP32"""
        if not line:
            return

        parts = line.split(',')
        cmd = parts[0].strip().upper()

        if cmd == "DATA":
            # DATA,ax,ay,az,gx,gy,gz - needs the command plus 6 values
            if len(parts) < 7:
                return
            try:
                sensor_data = tuple(int(parts[i]) for i in range(1, 7))
                if not self.data_queue.full():
                    self.data_queue.put(sensor_data)
            except ValueError:
                pass  # Ignore malformed data

        elif cmd == "SHOOT":
            # The ESP32 sends a bare "SHOOT" with no comma at all, so this
            # must not be gated behind the "at least 2 parts" check above
            # (that check used to run unconditionally before we even looked
            # at cmd, silently dropping every trigger press).
            if not self.shoot_queue.full():
                self.shoot_queue.put(True)

    def get_latest_sensor_data(self) -> Optional[Tuple[int, int, int, int, int, int]]:
        """Get the most recent sensor reading (non-blocking)"""
        latest = None
        while not self.data_queue.empty():
            try:
                latest = self.data_queue.get_nowait()
            except queue.Empty:
                break
        return latest

    def check_shoot(self) -> bool:
        """Check if shoot command received (non-blocking)"""
        try:
            self.shoot_queue.get_nowait()
            return True
        except queue.Empty:
            return False

    def is_connected(self) -> bool:
        return self.connected

    def get_error(self) -> str:
        return self.last_error

    def reconnect(self) -> bool:
        """Attempt to reconnect (BLOCKING - can take several seconds).

        Kept for backwards compatibility / manual use. Prefer
        connect_async()/reconnect_async() from the main game loop so the
        pygame window keeps processing events and stays responsive.
        """
        self.disconnect()
        time.sleep(1.0)
        return self.connect()

    def is_connecting(self) -> bool:
        """True while a background connect/reconnect attempt is in flight."""
        return self.connecting

    def connect_async(self):
        """Attempt to (re)connect on a background thread.

        connect() and reconnect() can block for several seconds (waiting
        for the ESP32 to boot / send its READY signal, or waiting for a
        write/reconnect timeout). Calling that directly from the pygame
        main loop is what causes the whole window to appear frozen /
        "Not Responding" and the crosshair to stop moving. This kicks the
        same work off on a daemon thread and returns immediately so the
        main loop can keep ticking at full FPS. Safe to call repeatedly -
        it's a no-op while already connected or already attempting.
        """
        if self.connected or self.connecting:
            return
        if not self._connect_lock.acquire(blocking=False):
            return

        def _worker():
            try:
                self.connecting = True
                # Make sure any stale connection/thread is torn down first.
                if self.serial_conn and self.serial_conn.is_open:
                    self.disconnect()
                if self.connect():
                    self.start_reading()
            finally:
                self.connecting = False
                self._connect_lock.release()

        threading.Thread(target=_worker, daemon=True).start()

    def reconnect_async(self):
        """Non-blocking alias of connect_async(), kept for readability
        at reconnection call sites."""
        self.connect_async()


def find_esp32_port() -> Optional[str]:
    """Convenience function to find ESP32 port"""
    controller = SerialController()
    return controller.auto_detect_port()