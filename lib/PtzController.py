# SPDX-License-Identifier: MIT
################################################################################
# PtzController.py
#
# Copyright (c) 2022 Mark Whiting
#
# This module provides the PtzController class. This class reads the state of
# an AXIS T8311 Joystick and generates events for the PtzCamera class.
################################################################################

import os
import time

from enum import Enum, unique, auto
from dataclasses import dataclass
from collections import namedtuple

if os.name == 'nt':
    from .hid import Device as HIDDevice
    from .hid import HIDException
else:
    from .hidraw import Device as HIDDevice
    from .hidraw import HIDException

__all__ = [ 'HIDException', 'Buttons', 'Events', 'Event', 'PtzController' ]

# Define the available buttons and all state needed to track them
@unique
class Buttons(Enum):
    J1  = 1 << 0
    J2  = 1 << 1
    J3  = 1 << 2
    J4  = 1 << 3
    L   = 1 << 4
    R   = 1 << 5

@unique
class ButtonState(Enum):
    IDLE = auto()
    PRESSED = auto()
    MODIFIER = auto()
    INACTIVE = auto()

@dataclass
class ButtonData:
    type: Buttons
    modifiers: list[Buttons]
    state: ButtonState
    active_modifier: Buttons
    pressed_timestamp: float

# Define the available events and all state needed to track them
@unique
class Events(Enum):
    MOVE_START = auto()
    MOVE_UPDATE = auto()
    MOVE_END = auto()
    FOCUS_START = auto()
    FOCUS_UPDATE = auto()
    FOCUS_END = auto()
    BTN_PRESS = auto()
    BTN_PRESS_WITH_MODIFIER = auto()
    BTN_HOLD = auto()

Event = namedtuple('Event', ['type', 'button', 'modifier', 'joystick', 'timestamp'])

# Controller class
class PtzController(object):
    def __init__(self, vid : int, pid : int, hold_time : float = 2.0):
        # Define the button / modifier relationships
        self.buttons = {
            Buttons.J1 : ButtonData(Buttons.J1, [Buttons.L, Buttons.R], ButtonState.IDLE, None, 0.0),
            Buttons.J2 : ButtonData(Buttons.J2, [Buttons.L, Buttons.R], ButtonState.IDLE, None, 0.0),
            Buttons.J3 : ButtonData(Buttons.J3, [Buttons.L, Buttons.R], ButtonState.IDLE, None, 0.0),
            Buttons.J4 : ButtonData(Buttons.J4, [Buttons.L, Buttons.R], ButtonState.IDLE, None, 0.0),
            Buttons.L  : ButtonData(Buttons.L, [], ButtonState.IDLE, None, 0.0),
            Buttons.R  : ButtonData(Buttons.R, [], ButtonState.IDLE, None, 0.0)
        }

        # Open the controller HID device
        self.hid_device = HIDDevice(vid, pid)

        # Set initial joystick state
        self.min_hold_time = hold_time
        self.last_joystick_data = (0.0, 0.0, 0.0)

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        self.hid_device.close()

    # Button Handling
    def _read_hid_data(self):
        return self.hid_device.read(4)

    def _btn_reset_state(self, button):
        button.state = ButtonState.IDLE
        button.active_modifier = None
        button.pressed_timestamp = 0.0

    def _btn_idle_state(self, button, data):
        if (data & button.type.value):
            button.state = ButtonState.PRESSED
            button.pressed_timestamp = time.monotonic()
            for modifier in button.modifiers:
                if self.buttons[modifier].state in [ButtonState.PRESSED, ButtonState.MODIFIER]:
                    button.active_modifier = modifier
                    self.buttons[modifier].state = ButtonState.MODIFIER
        return []

    def _btn_pressed_state(self, button, data):
        if (data & button.type.value):
            hold_time = time.monotonic() - button.pressed_timestamp
            if hold_time >= self.min_hold_time:
                button.state = ButtonState.INACTIVE
                return [Event(Events.BTN_HOLD, button.type, button.active_modifier, None, time.monotonic())]
        else:
            event_type = Events.BTN_PRESS if button.active_modifier is None else Events.BTN_PRESS_WITH_MODIFIER
            ret = Event(event_type, button.type, button.active_modifier, None, time.monotonic())
            self._btn_reset_state(button)
            return [ret]
        return []

    def _btn_modifier_state(self, button, data):
        # Reset button state once button is release
        if (data & button.type.value) == 0:
            self._btn_reset_state(button)
        return []

    def _btn_inactive_state(self, button, data):
        # Reset button state once button is release
        if (data & button.type.value) == 0:
            self._btn_reset_state(button)
        return []

    def _update_button(self, button, data):
        if button.state == ButtonState.IDLE:
            return self._btn_idle_state(button, data)
        elif button.state == ButtonState.PRESSED:
            return self._btn_pressed_state(button, data)
        elif button.state == ButtonState.MODIFIER:
            return self._btn_modifier_state(button, data)
        elif button.state == ButtonState.INACTIVE:
            return self._btn_inactive_state(button, data)
        else:
            button.state == ButtonState.INACTIVE
            return []

    def _process_buttons(self, data):
        events = []
        for key in self.buttons:
            events.extend(self._update_button(self.buttons[key], data))
        return events

    # Joystick Handling
    def _clamp(self, n, smallest, largest):
        return max(smallest, min(n, largest))

    def _map_float(self, value, min, max, invert):
        # Map the value to the range -1 to 1
        value = self._clamp(value, min, max)
        value = (((value - min) / (max - min)) * 2) - 1
        return value if not invert else -value

    def _map_range(self, value, min, max, deadzone, invert):
        value = self._map_float(value, min, max, invert)
        if (value > -deadzone) and (value < deadzone):
            return 0.0
        return value

    def _map_joystick(self, data):
        pan = self._map_range(data[0], 0, 255, 0.1, False)
        tilt = self._map_range(data[1], 0, 255, 0.1, True)
        zoom = self._map_range(data[2], 0, 255, 0.15, False)
        return (pan, tilt, zoom)

    def _process_joystick(self, data):
        joystick_data = self._map_joystick(data)

        if (self.last_joystick_data != joystick_data):
            modifier = self.buttons[Buttons.L].state in [ButtonState.PRESSED, ButtonState.MODIFIER]
            if modifier:
                self.buttons[Buttons.L].state = ButtonState.MODIFIER

            start = self.last_joystick_data == (0.0, 0.0, 0.0)
            stop = joystick_data == (0.0, 0.0, 0.0)
            self.last_joystick_data = joystick_data

            if start:
                event_type = Events.FOCUS_START if modifier else Events.MOVE_START
                return [Event(event_type, None, None, self.last_joystick_data, time.monotonic())]
            elif stop:
                event_type = Events.FOCUS_END if modifier else Events.MOVE_END
                return [Event(event_type, None, None, self.last_joystick_data, time.monotonic())]
            else:
                event_type = Events.FOCUS_UPDATE if modifier else Events.MOVE_UPDATE
                return [Event(event_type, None, None, self.last_joystick_data, time.monotonic())]

        return []

    def update(self):
        hid_data = self._read_hid_data()

        events = []
        events.extend(self._process_buttons(hid_data[3]))
        events.extend(self._process_joystick(hid_data[:3]))

        return events

