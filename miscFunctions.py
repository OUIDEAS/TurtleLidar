import numpy as np
import time
import serial
import re
from ellipse import LsqEllipse


def find_center(scan):
    # Find Center of circle and new radius
    rad2deg = np.pi / 180
    th = np.asarray(scan[0]) * rad2deg
    X_lidar = scan[1] * np.cos(th)
    Y_lidar = scan[1] * np.sin(th)
    # coord = []
    # for i in range(len(X_lidar)):
    #     coord.append([X_lidar[i], Y_lidar[i]])

    coord = np.array(list(zip(X_lidar, Y_lidar)))
    # circle = hyper_fit(coord)
    reg = LsqEllipse().fit(coord)
    center, width, height, phi = reg.as_parameters()
    X_lidar = X_lidar - center[0]
    Y_lidar = Y_lidar - center[1]
    r = np.sqrt(np.square(X_lidar) + np.square(Y_lidar))
    return r, center, width, height


def encoder_to_odo(enc):
    rot = 12  # https://www.pololu.com/product/3542/resources
    gear = 73.2  # https://docs.leorover.tech/documentation/leo-rover-wheels/motors-specification#buehler-motors-1-61-077-414
    wheelDi = 125  # mm, https://docs.leorover.tech/documentation/leo-rover-wheels/tires-dimensions
    odo = enc / rot / gear * np.pi * wheelDi
    return odo


class ReadSerialTurtle:
    # def __init__(self, port='/dev/ttyACM0', baud=115200):
    def __init__(self, port='/dev/turtle/USB_micro', baud=115200):
        try:
            self.ser = serial.Serial(port, baud, timeout=5)
        except serial.SerialException as e:
            print(e)
            self.ser = None

    def read_data(self):
        # t1 = time.time()
        data = [0]
        while data[0] != 'data':
            if self.ser is not None:
                self.ser.flushInput()
                read_serial = self.ser.readline()
                # read_serial = self.doRead()
                data = read_serial.decode('utf-8')
                data = re.sub(r'[()]', '', data)
                data = data.split(", ")

                if data[0] == "data":
                    euler = (float(data[1]), float(data[2]), float(data[3]))
                    gyro = (float(data[4]), float(data[5]), float(data[6]))
                    acc = (float(data[7]), float(data[8]), float(data[9]))
                    mag = (float(data[10]), float(data[11]), float(data[12]))
                    enc_all = (float(data[13]), float(data[14]), float(data[15]), float(data[16]))
                    t = float(data[17])
                    IMU = (euler, gyro, acc, mag)
                    enc = (encoder_to_odo(enc_all[0]), encoder_to_odo(enc_all[1]), encoder_to_odo(enc_all[2]), encoder_to_odo(enc_all[3]))
                    # enc = enc_all[0] + enc_all[1] + enc_all[2] + enc_all[3]
                    # enc = enc/4
                    break
                else:
                    IMU = ((0,0,0), (0,0,0), (0,0,0),(0,0,0))
                    enc = (0,0,0,0)
                    t = 0
                    break
            else:
                IMU = ((0,0,0), (0,0,0), (0,0,0),(0,0,0))
                enc = (0,0,0,0)
                t = None
                break

        return IMU, enc, t

    def doRead(self):
        tout = 1
        term = '\n'
        matcher = re.compile(term)  # gives you the ability to search for anything
        tic = time.time()
        buff = self.ser.read(128)
        # you can use if not ('\n' in buff) too if you don't like re
        while ((time.time() - tic) < tout) and (not matcher.search(buff)):
            buff += self.ser.read(128)

        return buff

    def stopRead(self):
        if self.ser is not None:
            self.ser.close()


if __name__ == '__main__':
    #ser = ReadSerialTurtle('COM8')
    ser = ReadSerialTurtle()
    while True:
        # print(ser.read_data())
        X = ser.read_data()
        print(X[1])