import numpy as np
from circle_fit import least_squares_circle, hyper_fit
import time
import serial
import re

def find_center(scan):
    # Find Center of circle and new radius
    rad2deg = np.pi / 180
    th = np.asarray(scan[0]) * rad2deg
    X_lidar = scan[1] * np.cos(th)
    Y_lidar = scan[1] * np.sin(th)
    coord = []
    for i in range(len(X_lidar)):
        coord.append([X_lidar[i], Y_lidar[i]])
    circle = hyper_fit(coord)
    X_lidar = X_lidar - circle[0]
    Y_lidar = Y_lidar - circle[1]
    r = np.sqrt(np.square(X_lidar) + np.square(Y_lidar))
    return r, circle[0], circle[1]

class ReadSerialTurtle:
    def __init__(self, port='/dev/ttyACM0', baud=115200):
        self.ser = serial.Serial(port, baud)

    def read_data(self):
        t1 = time.time()

        while True:
            read_serial = self.ser.readline()
            data = read_serial.decode('utf-8')
            data = re.sub(r'[()]', '', data)
            data = data.split(", ")

            if data[0] == "data":
                gyro = (float(data[1]), float(data[2]), float(data[3]))
                enc = float(data[4])
                t = float(data[5])
                break
            elif time.time()-t1 >= .5:
                gyro = None
                enc = None
                t = None
                break

        return gyro, enc, t

    def stopRead(self):
        self.ser.close()
