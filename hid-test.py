# FIXME

from lib.PtzController import *

HID_VID = 0x07C0
HID_PID = 0x1131
BUTTON_HOLD_TIME = 2.0

controller = PtzController(HID_VID, HID_PID, BUTTON_HOLD_TIME)

while True:
    events = controller.update()
    if len(events) != 0:
        for event in events:
            print(event)
