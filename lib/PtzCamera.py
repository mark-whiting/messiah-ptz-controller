import sys
import time
from pathlib import Path

sensecam_dir = Path(__file__).resolve().parent / 'sensecam-control'
sys.path.append(str(sensecam_dir))

from sensecam_control import vapix_control, vapix_config
from .PtzController import Buttons, Events, Event

# Camera class
class PtzCamera(object):
    def __init__(self, ip: str, user: str, password: str):
        # Open connection to the camera
        self.camera = vapix_control.CameraControl(ip, user, password)
        self.config = vapix_config.CameraConfiguration(ip, user, password)
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
        self.config.set_server_preset_name(name)

    def _stop_move(self):
        self.camera.stop_move()

    def _update_move(self, joystick_data):
        pan  = int(joystick_data[0] * 100)
        tilt = int(joystick_data[1] * 100)
        zoom = int(joystick_data[2] * 100)
        self.camera.continuous_move(pan, tilt, zoom)

    def _start_focus(self):
        self.config.auto_focus('off')

    def _stop_focus(self):
        self.camera.stop_focus()

    def _reset_focus(self):
        self.config.auto_focus('on')

    def _update_focus(self, joystick_data):
        focus = int(joystick_data[2] * joystick_data[2] * joystick_data[2] * 100)
        self.camera.continuous_focus(focus)

    def _handle_button_press(self, event: Event):
        match event.button:
            case Buttons.J1:
                self._go_to_preset('J1')
            case Buttons.J2:
                self._go_to_preset('J2')
            case Buttons.J3:
                self._go_to_preset('J3')
            case Buttons.J4:
                self._go_to_preset('J4')
            case Buttons.L:
                # FIXME
                pass
            case Buttons.R:
                # FIXME
                pass

    def _handle_button_press_with_mod(self, event: Event):
        match (event.button, event.modifier):
            case (Buttons.J1, Buttons.L):
                # FIXME
                pass
            case (Buttons.J2, Buttons.L):
                # FIXME
                pass
            case (Buttons.J3, Buttons.L):
                # FIXME
                pass
            case (Buttons.J4, Buttons.L):
                # FIXME
                pass
            case (Buttons.J1, Buttons.R):
                self._set_preset('J1')
            case (Buttons.J2, Buttons.R):
                self._set_preset('J2')
            case (Buttons.J3, Buttons.R):
                self._set_preset('J3')
            case (Buttons.J4, Buttons.R):
                self._set_preset('J4')

    def _handle_button_hold(self, event:Event):
        match event.button:
            case Buttons.J1:
                self._go_home()
            case Buttons.J2:
                # FIXME
                pass
            case Buttons.J3:
                # FIXME
                pass
            case Buttons.J4:
                # FIXME
                pass
            case Buttons.L:
                self._reset_focus()
            case Buttons.R:
                # FIXME
                pass

    def _handle_button_event(self, event: Event):
        match event.type:
            case Events.BTN_PRESS:
                self._handle_button_press(event)
            case Events.BTN_PRESS_WITH_MODIFIER:
                self._handle_button_press_with_mod(event)
            case Events.BTN_HOLD:
                self._handle_button_hold(event)

    def handle_event(self, event: Event):
        match event.type:
            # Check for camera pan/tilt/zoom
            case Events.MOVE_START:
                self.moving = True
            case Events.MOVE_END:
                self.moving = False
                self._stop_move()
            # Check for camera focus
            case Events.FOCUS_START:
                self.focus = True
                self._start_focus()
            case Events.FOCUS_END:
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
