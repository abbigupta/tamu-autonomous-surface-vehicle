"""Keyboard teleoperation for the ASV's twin thrusters."""

from __future__ import annotations

import select
import sys
import termios
import tty

import rclpy
from rclpy.node import Node
from std_msgs.msg import Float64


HELP = """
Twin-thruster keyboard control

  W / Up Arrow       forward
  S / Down Arrow     reverse
  A / Left Arrow     pivot left
  D / Right Arrow    pivot right
  Space or X         stop
  Q                   stop and quit
"""


def command_for_key(
    key: str,
    forward_thrust: float = 8.0,
    reverse_thrust: float = 6.0,
    turn_thrust: float = 6.0,
) -> tuple[float, float] | None:
    """Return port/starboard thrust for a supported key."""
    commands = {
        'w': (forward_thrust, forward_thrust),
        '\x1b[A': (forward_thrust, forward_thrust),
        's': (-reverse_thrust, -reverse_thrust),
        '\x1b[B': (-reverse_thrust, -reverse_thrust),
        'a': (-turn_thrust, turn_thrust),
        '\x1b[D': (-turn_thrust, turn_thrust),
        'd': (turn_thrust, -turn_thrust),
        '\x1b[C': (turn_thrust, -turn_thrust),
        ' ': (0.0, 0.0),
        'x': (0.0, 0.0),
    }
    return commands.get(key.lower() if len(key) == 1 else key)


def read_key() -> str:
    """Read one key, including a complete terminal arrow-key sequence."""
    if not select.select([sys.stdin], [], [], 0.0)[0]:
        return ''

    key = sys.stdin.read(1)
    if key != '\x1b':
        return key

    # Arrow keys arrive as ESC, [, and a direction letter.
    sequence = key
    for _ in range(2):
        if not select.select([sys.stdin], [], [], 0.02)[0]:
            break
        sequence += sys.stdin.read(1)
    return sequence


class KeyboardTeleop(Node):
    """Publish a latched keyboard command at a watchdog-safe rate."""

    def __init__(self) -> None:
        super().__init__('keyboard_teleop')
        self.declare_parameter('forward_thrust_n', 8.0)
        self.declare_parameter('reverse_thrust_n', 6.0)
        self.declare_parameter('turn_thrust_n', 6.0)
        self.declare_parameter('publish_rate_hz', 10.0)

        self.forward_thrust = float(
            self.get_parameter('forward_thrust_n').value
        )
        self.reverse_thrust = float(
            self.get_parameter('reverse_thrust_n').value
        )
        self.turn_thrust = float(
            self.get_parameter('turn_thrust_n').value
        )
        publish_rate = float(self.get_parameter('publish_rate_hz').value)

        self.port_thrust = 0.0
        self.starboard_thrust = 0.0
        self.port_pub = self.create_publisher(
            Float64, '/asv/thrusters/port/command', 10
        )
        self.starboard_pub = self.create_publisher(
            Float64, '/asv/thrusters/starboard/command', 10
        )
        self.create_timer(1.0 / publish_rate, self.publish_command)

    def set_from_key(self, key: str) -> bool:
        """Apply a key; return True when it requests program exit."""
        if key.lower() == 'q' or key == '\x03':
            self.stop()
            return True

        command = command_for_key(
            key,
            self.forward_thrust,
            self.reverse_thrust,
            self.turn_thrust,
        )
        if command is not None:
            self.port_thrust, self.starboard_thrust = command
            self.publish_command()
        return False

    def publish_command(self) -> None:
        port = Float64()
        port.data = self.port_thrust
        starboard = Float64()
        starboard.data = self.starboard_thrust
        self.port_pub.publish(port)
        self.starboard_pub.publish(starboard)

    def stop(self) -> None:
        self.port_thrust = 0.0
        self.starboard_thrust = 0.0
        # Publish more than once so a final stop is unlikely to be dropped.
        self.publish_command()
        self.publish_command()


def main(args=None) -> None:
    if not sys.stdin.isatty():
        raise RuntimeError('keyboard_teleop must run in an interactive terminal')

    rclpy.init(args=args)
    node = KeyboardTeleop()
    terminal_settings = termios.tcgetattr(sys.stdin)
    print(HELP, flush=True)

    try:
        tty.setraw(sys.stdin.fileno())
        while rclpy.ok():
            rclpy.spin_once(node, timeout_sec=0.05)
            key = read_key()
            if key and node.set_from_key(key):
                break
    except KeyboardInterrupt:
        pass
    finally:
        node.stop()
        termios.tcsetattr(sys.stdin, termios.TCSADRAIN, terminal_settings)
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()
