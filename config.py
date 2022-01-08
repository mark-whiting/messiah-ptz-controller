# SPDX-License-Identifier: MIT
################################################################################
# config.py
#
# Copyright (c) 2022, Mark Whiting
#
# This file holds all of the configuration for the messiah-ptz-controller.py
# program.
################################################################################

CAM_IP='192.168.1.2'
CAM_USER='root'
CAM_PW='Messiah'

HID_VID = 0x07C0
HID_PID = 0x1131
BUTTON_HOLD_TIME = 2.0

__all__ = ['CAM_IP', 'CAM_USER', 'CAM_PW', 'HID_VID', 'HID_PID', 'BUTTON_HOLD_TIME']

