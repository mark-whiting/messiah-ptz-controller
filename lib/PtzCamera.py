import sys
import time
import logging

from .vapix import CameraControl
from .PtzController import Buttons, Events, Event

# Camera class
class PtzCamera(object):
    def __init__(self, ip: str, user: str, password: str):
        # Open connection to the camera
        self.camera = CameraControl(ip, user, password)
        self.camera.set_speed(100)

        self.moving = False
        self.focus = False

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        pass

    def _wait_for_movement_end(self):
        last_pos = self.camera.get_ptz()
        while True:
            time.sleep(0.1)
            cur_pos = self.camera.get_ptz()
            if (cur_pos == last_pos):
                break
            last_pos = cur_pos

    def _go_home(self):
        self.camera.go_home_position(100)
        self._wait_for_movement_end()

    def _go_to_preset(self, name):
        self.camera.go_to_server_preset_name(name, 50)
        self._wait_for_movement_end()

    def _set_preset(self, name):
        self._wait_for_movement_end()
        self.camera.set_server_preset_name(name)

    def _stop_move(self):
        self.camera.stop_move()

    def _update_move(self, joystick_data):
        pan  = int(joystick_data[0] * 100)
        tilt = int(joystick_data[1] * 100)
        zoom = int(joystick_data[2] * 100)
        self.camera.continuous_move(pan, tilt, zoom)

    def _start_focus(self):
        self.camera.auto_focus('off')

    def _stop_focus(self):
        self.camera.stop_focus()

    def _reset_focus(self):
        self.camera.auto_focus('on')

    def _update_focus(self, joystick_data):
        focus = int(joystick_data[2] * joystick_data[2] * joystick_data[2] * 100)
        self.camera.continuous_focus(focus)

    def _handle_button_press(self, event: Event):
        if event.button is Buttons.J1:
            logging.info('Going to preset "J1"')
            self._go_to_preset('J1')
        elif event.button is Buttons.J2:
            logging.info('Going to preset "J2"')
            self._go_to_preset('J2')
        elif event.button is Buttons.J3:
            logging.info('Going to preset "J3"')
            self._go_to_preset('J3')
        elif event.button is Buttons.J4:
            logging.info('Going to preset "J4"')
            self._go_to_preset('J4')
        elif event.button is Buttons.L:
            logging.warn('No action for button press "L"') # TODO
        elif event.button is Buttons.R:
            logging.warn('No action for button press "R"') # TODO

    def _handle_button_press_with_mod(self, event: Event):
        value = (event.button, event.modifier)

        if   value == (Buttons.J1, Buttons.L):
            logging.warn('No action for button press "J1" with modifier "L"') # TODO
        elif value == (Buttons.J2, Buttons.L):
            logging.warn('No action for button press "J2" with modifier "L"') # TODO
        elif value == (Buttons.J3, Buttons.L):
            logging.warn('No action for button press "J3" with modifier "L"') # TODO
        elif value == (Buttons.J4, Buttons.L):
            logging.warn('No action for button press "J4" with modifier "L"') # TODO
        elif value == (Buttons.J1, Buttons.R):
            logging.info('Setting preset "J1"')
            self._set_preset('J1')
        elif value == (Buttons.J2, Buttons.R):
            logging.info('Setting preset "J2"')
            self._set_preset('J2')
        elif value == (Buttons.J3, Buttons.R):
            logging.info('Setting preset "J3"')
            self._set_preset('J3')
        elif value == (Buttons.J4, Buttons.R):
            logging.info('Setting preset "J4"')
            self._set_preset('J4')

    def _handle_button_hold(self, event:Event):
        if   event.button is Buttons.J1:
            logging.info('Moving camera to home position')
            self._go_home()
        elif event.button is Buttons.J2:
            logging.warn('No action for button hold "J2"') # TODO
        elif event.button is Buttons.J3:
            logging.warn('No action for button hold "J3"') # TODO
        elif event.button is Buttons.J4:
            logging.warn('No action for button hold "J4"') # TODO
        elif event.button is Buttons.L:
            logging.info('Re-enabling camera auto-focus')
            self._reset_focus()
        elif event.button is Buttons.R:
            logging.warn('No action for button hold "R"') # TODO

    def _handle_button_event(self, event: Event):
        if event.type is Events.BTN_PRESS:
            self._handle_button_press(event)
        elif event.type is Events.BTN_PRESS_WITH_MODIFIER:
            self._handle_button_press_with_mod(event)
        elif event.type is Events.BTN_HOLD:
            self._handle_button_hold(event)

    def handle_event(self, event: Event):
        # Check for camera pan/tilt/zoom
        if event.type is Events.MOVE_START:
            self.moving = True
        elif event.type is Events.MOVE_END:
            self.moving = False
            self._stop_move()

        # Check for camera focus
        if event.type is Events.FOCUS_START:
            self.focus = True
            self._start_focus()
        elif event.type is Events.FOCUS_END:
            self.focus = False
            self._stop_focus()

        if self.moving:
            if event.type is Events.MOVE_UPDATE:
                self._update_move(event.joystick)
        elif self.focus:
            if event.type is Events.FOCUS_UPDATE:
                self._update_focus(event.joystick)
        else:
            self._handle_button_event(event)

