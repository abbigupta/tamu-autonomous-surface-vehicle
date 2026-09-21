"""Unit tests for pure twin-thruster controller helpers."""

from asv_control.twin_thruster_controller import clamp
from asv_control.keyboard_teleop import command_for_key


def test_clamp_keeps_value_inside_limits():
    assert clamp(4.0, -10.0, 20.0) == 4.0


def test_clamp_limits_forward_value():
    assert clamp(30.0, -10.0, 20.0) == 20.0


def test_clamp_limits_reverse_value():
    assert clamp(-15.0, -10.0, 20.0) == -10.0


def test_keyboard_forward_and_reverse_commands():
    assert command_for_key('w') == (8.0, 8.0)
    assert command_for_key('s') == (-6.0, -6.0)


def test_keyboard_pivot_commands():
    assert command_for_key('a') == (-6.0, 6.0)
    assert command_for_key('d') == (6.0, -6.0)


def test_keyboard_stop_and_unknown_commands():
    assert command_for_key(' ') == (0.0, 0.0)
    assert command_for_key('x') == (0.0, 0.0)
    assert command_for_key('z') is None
