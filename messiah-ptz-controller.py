#import time

#from sensecam_control import vapix_control, vapix_config

from lib.PtzController import *
from lib.PtzCamera import *

HID_VID = 0x07C0
HID_PID = 0x1131
HID_POLL_RATE = 60

BUTTON_HOLD_TIME = 2.0

if __name__ == '__main__':
    controller = None
    camera = None
    #camera = 1

    while True:
        try:
            if controller is None:
                controller = PtzController(HID_VID, HID_PID)

            if camera is None:
                camera = PtzCamera('192.168.1.2', 'root', 'Messiah')

            if None not in [controller, camera]:
                events = controller.update()
                if len(events) != 0:
                    for event in events:
                        camera.handle_event(event)

        except HIDException:
            controller = None

        # TODO: Camera exception

    

# Example usage
#with PtzCamera('169.254.55.228', 'root', 'Messiah') as camera:
    #camera._go_to_preset('first')
    #camera._go_home()
    #camera._go_to_preset('second')
    #camera._go_home()

#    with PtzController(camera) as controller:
#        controller.control_loop()
