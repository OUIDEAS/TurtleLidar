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


def encoder_to_odo(enc):
    rot = 12  # https://www.pololu.com/product/3542/resources
    gear = 73.2  # https://docs.leorover.tech/documentation/leo-rover-wheels/motors-specification#buehler-motors-1-61-077-414
    wheelDi = 125  # mm, https://docs.leorover.tech/documentation/leo-rover-wheels/tires-dimensions
    odo = enc / rot / gear * np.pi() * wheelDi
    return odo


class ReadSerialTurtle:
    def __init__(self, port='/dev/ttyACM0', baud=115200):
        try:
            self.ser = serial.Serial(port, baud)
        except serial.SerialException as e:
            print(e)
            self.ser = None

    def read_data(self):
        t1 = time.time()
        if self.ser != None:
            while True:
                read_serial = self.ser.readline()
                data = read_serial.decode('utf-8')
                data = re.sub(r'[()]', '', data)
                data = data.split(", ")

                if data[0] == "data":
                    euler = (float(data[1]), float(data[2]), float(data[3]))
                    gyro = (float(data[4]), float(data[5]), float(data[6]))
                    acc = (float(data[7]), float(data[8]), float(data[9]))
                    mag = (float(data[10]), float(data[11]), float(data[12]))
                    enc = float(data[13])
                    t = float(data[14])
                    IMU = (euler, gyro, acc, mag)
                    break
                elif time.time()-t1 >= .5:
                    IMU = None
                    enc = None
                    t = None
                    break
        else:
            IMU = None
            enc = None
            t = None

        return IMU, enc, t

    def stopRead(self):
        if self.ser != None:
            self.ser.close()


if __name__ == '__main__':
    ser = ReadSerialTurtle('COM10')
