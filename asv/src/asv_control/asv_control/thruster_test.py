"""Run a short, visible twin-thruster acceptance sequence."""

from __future__ import annotations

import rclpy
from rclpy.node import Node
from std_msgs.msg import Float64


class ThrusterTest(Node):
    """Publish forward, stop, pivot, reverse, and final-stop commands."""

    SEQUENCE = (
        ('forward', 4.0, 8.0, 8.0),
        ('stop', 2.0, 0.0, 0.0),
        ('pivot left', 3.0, -6.0, 6.0),
        ('stop', 2.0, 0.0, 0.0),
        ('reverse', 3.0, -6.0, -6.0),
        ('final stop', 1.0, 0.0, 0.0),
    )

    def __init__(self) -> None:
        super().__init__('thruster_test')
        self.port_pub = self.create_publisher(
            Float64, '/asv/thrusters/port/command', 10
        )
        self.starboard_pub = self.create_publisher(
            Float64, '/asv/thrusters/starboard/command', 10
        )
        self.stage = 0
        self.stage_started_ns = self.get_clock().now().nanoseconds
        self.create_timer(0.1, self._tick)
        self._announce_stage()

    def _announce_stage(self) -> None:
        name, duration, port, starboard = self.SEQUENCE[self.stage]
        self.get_logger().info(
            f'{name}: port={port:.1f} N, starboard={starboard:.1f} N '
            f'for {duration:.1f} s'
        )

    def _publish(self, port: float, starboard: float) -> None:
        port_message = Float64()
        port_message.data = port
        starboard_message = Float64()
        starboard_message.data = starboard
        self.port_pub.publish(port_message)
        self.starboard_pub.publish(starboard_message)

    def _tick(self) -> None:
        name, duration, port, starboard = self.SEQUENCE[self.stage]
        del name
        self._publish(port, starboard)

        elapsed = (
            self.get_clock().now().nanoseconds - self.stage_started_ns
        ) / 1e9
        if elapsed < duration:
            return

        self.stage += 1
        self.stage_started_ns = self.get_clock().now().nanoseconds
        if self.stage >= len(self.SEQUENCE):
            self._publish(0.0, 0.0)
            self.get_logger().info('Thruster test complete.')
            rclpy.shutdown()
            return
        self._announce_stage()


def main(args=None) -> None:
    rclpy.init(args=args)
    node = ThrusterTest()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()
