from GimbalLidarControlClass import LidarGimbal
import time

Port = '/dev/ttyUSB0'

lg = LidarGimbal(Port)
lg.lidarHealth()

lg.holdSteppers()
time.sleep(5)
print("scanning")

lg.debuglidar('debug.txt')

lg.shutdown()
quit()
