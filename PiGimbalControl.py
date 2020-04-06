from GimbalLidarControlClass import LidarGimbal
import numpy as np
import time

lg = LidarGimbal()
lg.holdSteppers()

while True:
    pan = int(input("Pan how many steps: "))
    lg.steplidar("Pan", pan)

    tilt = int(input("Tilt how many steps: "))
    lg.steplidar("Tilt", tilt)

    stop = int(input("Type 7 to stop: "))
    if stop == 7:
        lg.shutdown()
        break
