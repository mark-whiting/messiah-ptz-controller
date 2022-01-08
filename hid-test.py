# SPDX-License-Identifier: MIT
################################################################################
# hid-test.py
#
# Copyright (c) 2022, Mark Whiting
#
# This program can be used to test connectivity to the AXIS T8311 joystick. It
# will print out joystick events as input is provided to the joystick to verify
# functionality.
################################################################################

from lib.PtzController import *
from config import *

controller = PtzController(HID_VID, HID_PID, BUTTON_HOLD_TIME)

while True:
    events = controller.update()
    if len(events) != 0:
        for event in events:
            print(event)
