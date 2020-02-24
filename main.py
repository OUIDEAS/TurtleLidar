from GimbalLidarControlClass import LidarGimbal
import numpy as np


Port = '/dev/ttyUSB0'
txtFile = 'test.txt'

lg = LidarGimbal('Port')

lg.lidarHealth()

lg.holdSteppers()
lg.lidarScanWrite(txtFile, 30)

lg.shutdown()