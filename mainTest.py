from GimbalLidarControlClass import LidarGimbal
import numpy as np
import time

Port = '/dev/ttyUSB0'
n = 50

lg = LidarGimbal(Port)
lg.lidarHealth()


try:
    lg.holdSteppers()

    print("Preparing to scan...")
    time.sleep(5)
    print("...Beginning Scan")

    lg.steplidar('Pan', -4)
    lg.debuglidar('Scan1.txt')
    lg.steplidar('Pan', 1)
    lg.debuglidar('Scan2.txt')
    lg.steplidar('Pan', 1)
    lg.debuglidar('Scan3.txt')
    lg.steplidar('Pan', 1)
    lg.debuglidar('Scan4.txt')
    lg.steplidar('Pan', 1)
    lg.debuglidar('Scan5.txt')
    lg.steplidar('Pan', 1)
    lg.debuglidar('Scan6.txt')
    lg.steplidar('Pan', 1)
    lg.debuglidar('Scan7.txt')

except KeyboardInterrupt:
    print('Stoping.')

lg.shutdown()
