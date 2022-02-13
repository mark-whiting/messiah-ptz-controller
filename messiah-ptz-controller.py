# SPDX-License-Identifier: MIT
################################################################################
# messiah-ptz-controller.py
#
# Copyright (c) 2022 Mark Whiting
#
# This program reads data from the AXIS T8311 Joystick and based on the inputs
# sends network commands to an AXIS V5914 PTZ camera.
################################################################################

import sys
import time
import logging
import threading

import netifaces
import ipaddress

from zeroconf import ServiceBrowser, Zeroconf

from lib.PtzController import *
from lib.PtzCamera import *

from config import *


################################################################################
# 
################################################################################
class CameraThread(threading.Thread):
    def __init__(self, ip):
        threading.Thread.__init__(self)
        self._ip = ip
        self._camera = None
        self._controller = None
        self._shutdownEvent = threading.Event()

    def shutdown(self):
        self._shutdownEvent.set()

    def _update(self):
        try:
            if self._controller is None:
                self._controller = PtzController(HID_VID, HID_PID, BUTTON_HOLD_TIME)

            if self._camera is None:
                self._camera = PtzCamera(self._ip, CAM_USER, CAM_PW)

            if None not in [self._controller, self._camera]:
                events = self._controller.update()
                if len(events) != 0:
                    for event in events:
                        self._camera.handle_event(event)

        except HIDException as e:
            logging.error('Failed to open HID device: "%s"', repr(e))
            controller = None
            time.sleep(1)

        # TODO: detect when camera not connected??

        except Exception as e:
            logging.error('Unhandled exception: "%s"', repr(e))
            return False

        return True

    def run(self):
        while True:
            if self._shutdownEvent.wait(0.0):
                break
            if not self._update():
                break

        logging.info('CameraThread: exiting')

        if self._controller is not None:
            self._controller.close()
        if self._camera is not None:
            # Cleanup camera???
            pass


################################################################################
# 
################################################################################
class AxisZeroconfListener:
    def __init__(self):
        self._camera_control_thread = None

    def _start_stop_camera(self, info, action):
        # Check if this is the specific camera we are looking for via MAC address
        if b'macaddress' not in info.properties:
            log.debug('AxisZeroconfListener: Failed to find MAC address')
            return

        if info.properties[b'macaddress'] != CAM_MAC:
            log.debug('AxisZeroconfListener: MAC address mismatch')
            return

        # Get our network info
        host_addr = netifaces.ifaddresses('eth0')[netifaces.AF_INET][0]
        host_ip = host_addr['addr']
        host_netmask = host_addr['netmask']

        host_iface = ipaddress.IPv4Interface('%s/%s' % (host_ip, host_netmask))
        logging.debug('AxisZeroconfListener: Host interface %s', repr(host_iface))

        # Get the ip addresses for this camera
        for cam_address in info.parsed_scoped_addresses():
            cam_ip = ipaddress.ip_address(cam_address)
            if cam_ip in host_iface.network:
                if action == 'start':
                    logging.info('AxisZeroconfListener: Starting camera thread for ip "%s"', cam_ip)
                    self._camera_control_thread = CameraThread(str(cam_ip))
                    self._camera_control_thread.start()
                elif action == 'stop':
                    logging.info('AxisZeroconfListener: Stopping camera thread')
                    self._camera_control_thread.shutdown()
                    self._camera_control_thread.join()
                    self._camera_control_thread = None
                else:
                    logging.error('AxisZeroconfListener: Unknown action "%s"', action);

    def remove_service(self, zeroconf, type, name):
        if self._camera_control_thread is not None:
            info = zeroconf.get_service_info(type, name)
            logging.debug('AxisZeroconfListener: remove_service(), info=%s', str(info))
            self._start_stop_camera(info, 'stop')

    def add_service(self, zeroconf, type, name):
        if self._camera_control_thread is None:
            info = zeroconf.get_service_info(type, name)
            logging.debug('AxisZeroconfListener: add_service(), info=%s', str(info))
            self._start_stop_camera(info, 'start')

    def update_service(self, zeroconf, type, name):
        if not self._camera_control_thread.is_alive():
            info = zeroconf.get_service_info(type, name)
            logging.debug('AxisZeroconfListener: update_service(), info=%s', str(info))
            self._start_stop_camera(info, 'start')


################################################################################
# Main
################################################################################
def main():
    logging.basicConfig(level=logging.DEBUG)
    logging.info('Started')

    zeroconf = Zeroconf()
    listener = AxisZeroconfListener()
    browser = ServiceBrowser(zeroconf, "_axis-video._tcp.local.", listener)

    try:
        while True:
            time.sleep(0.1)
    except KeyboardInterrupt:
        pass
    finally:
        zeroconf.close()

    logging.info('Finished')
    sys.exit(0)


if __name__ == '__main__':
    main()

