from GimbalLidarControlClass import LidarGimbal
import numpy as np
import time

Port = '/dev/ttyUSB0'

lg = LidarGimbal(Port)
lg.lidarHealth()


try:
    lg.holdSteppers()

    print("Preparing to scan...")
    time.sleep(5)
    print("...Beginning Scan")

    lg.steplidar('Pan', -4)
    lg.lidarScanWrite('Scan1.txt')
    lg.steplidar('Pan', 1)
    lg.lidarScanWrite('Scan2.txt')
    lg.steplidar('Pan', 1)
    lg.lidarScanWrite('Scan3.txt')
    lg.steplidar('Pan', 1)
    lg.lidarScanWrite('Scan4.txt')
    lg.steplidar('Pan', 1)
    lg.lidarScanWrite('Scan5.txt')
    lg.steplidar('Pan', 1)
    lg.lidarScanWrite('Scan6.txt')
    lg.steplidar('Pan', 1)
    lg.lidarScanWrite('Scan7.txt')

except KeyboardInterrupt:
    print('Stopping.')

lg.shutdown()
