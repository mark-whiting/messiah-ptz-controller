# FIXME

import sys
import time
import logging

from lib.PtzController import *
from lib.PtzCamera import *

CAM_IP='192.168.1.2'
CAM_USER='root'
CAM_PW='Messiah'

HID_VID = 0x07C0
HID_PID = 0x1131
BUTTON_HOLD_TIME = 2.0

###
if __name__ == '__main__':
    controller = None
    camera = None

    logging.basicConfig(level=logging.DEBUG)
    logging.info('Started')

    while True:
        try:
            if controller is None:
                controller = PtzController(HID_VID, HID_PID, BUTTON_HOLD_TIME)

            if camera is None:
                camera = PtzCamera(CAM_IP, CAM_USER, CAM_PW)

            if None not in [controller, camera]:
                events = controller.update()
                if len(events) != 0:
                    for event in events:
                        camera.handle_event(event)

        except HIDException as e:
            logging.error('Failed to open HID device: "%s"', repr(e))
            controller = None
            time.sleep(1)

        # TODO: detect when camera not connected??

        except Exception as e:
            logging.error('Unhandled exception: "%s"', repr(e))
            sys.exit(1)

    logging.info('Finished')
    sys.exit(0)

