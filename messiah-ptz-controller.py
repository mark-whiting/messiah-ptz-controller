from lib.PtzController import *
from lib.PtzCamera import *

HID_VID = 0x07C0
HID_PID = 0x1131
BUTTON_HOLD_TIME = 2.0

if __name__ == '__main__':
    controller = None
    camera = None

    while True:
        try:
            if controller is None:
                controller = PtzController(HID_VID, HID_PID, BUTTON_HOLD_TIME)

            if camera is None:
                camera = PtzCamera('192.168.1.2', 'root', 'Messiah')

            if None not in [controller, camera]:
                events = controller.update()
                if len(events) != 0:
                    for event in events:
                        camera.handle_event(event)

        except HIDException:
            controller = None

