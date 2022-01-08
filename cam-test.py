# SPDX-License-Identifier: MIT
################################################################################
# cam-test.py
#
# Copyright (c) 2022 Mark Whiting
#
# This program can be used to test network connectivity to the AXIS V5914 PTZ
# camera. It sends a few camera movement commands to verify everything is
# functional.
################################################################################

from lib.PtzCamera import *
from config import *

camera = PtzCamera(CAM_IP, CAM_USER, CAM_PW)

camera._go_home()

camera._update_move((1.0, 0.0, 0.0))
time.sleep(1)
camera._update_move((-1.0, 0.0, 0.0))
time.sleep(1)
camera._stop_move()

camera._go_home()
