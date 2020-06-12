from TurtleDriverClass import TurtleDriver
import numpy as np
import time

td = TurtleDriver()
td.initServo()

while True:
    pan = int(input("Pan how many steps: "))
    td.steplidar(1, pan)

    stop = int(input("Type 7 to stop: "))
    if stop == 7:
        td.shutdownLidar()
        break
