# FIXME

from lib.PtzCamera import *

CAM_IP='192.168.1.2'
CAM_USER='root'
CAM_PW='Messiah'

camera = PtzCamera(CAM_IP, CAM_USER, CAM_PW)

camera._go_home()

camera._update_move((1.0, 0.0, 0.0))
time.sleep(1)
camera._update_move((-1.0, 0.0, 0.0))
time.sleep(1)
camera._stop_move()

camera._go_home()
