import time
from TurtleLidarDB import TurtleLidarDB
from miscFunctions import find_center
import numpy as np
import serial
import re
import cv2
import imutils
from imutils.video import VideoStream
from TurtleDriverClass import TurtleDriver
from LidarClass import RPLidarClass


#PORT_NAME = 'COM4'
PORT_NAME = '/dev/ttyUSB0'
print("PORT: " + PORT_NAME)
def doRead(ser):
    tout = 1
    term = '\n'
    matcher = re.compile(term)    #gives you the ability to search for anything
    tic     = time.time()
    buff    = ser.read(128)
    # you can use if not ('\n' in buff) too if you don't like re
    while ((time.time() - tic) < tout) and (not matcher.search(buff)):
       buff += ser.read(128)

    return buff

def run():
    '''Main function'''
    with RPLidarClass() as RP:
        print("getting data")
        X = RP.get_lidar_data(5)
    # X = (ang, dis)
    return X


if __name__ == '__main__':
    X = run()
    print(X)
    print("Scan Finished")
    # Finding center of circle
    print("Adjusting")
    center = find_center(X)
    r = center[0]

    # Gathering data from micro controller
    data = ["no"]
    # ser = serial.Serial('COM10', 115200)
    # ser = serial.Serial('/dev/ttyACM0', 115200)
    # print("Read Serial")
    # ser = serial.Serial('/dev/ttyUSB0', 115200, timeout=1)
    # t1 = time.time()
    # print("reading")
    # while data[0] != "data":
    #     read_serial = ser.readline()
    #     # read_serial = doRead(ser)
    #     # read_serial = b'no'
    #     data = read_serial.decode('utf-8')
    #     data = re.sub(r'[()]', '', data)
    #     data = data.split(", ")
    #     if data[0] == "data":
    #         euler = (float(data[1]), float(data[2]), float(data[3]))
    #         gyro = (float(data[4]), float(data[5]), float(data[6]))
    #         acc = (float(data[7]), float(data[8]), float(data[9]))
    #         mag = (float(data[10]), float(data[11]), float(data[12]))
    #         enc = (float(data[13]), float(data[14]), float(data[15]), float(data[16]))
    #         gdata = (euler, gyro, acc, mag)
    #     elif time.time() - t1 >= 5:
    #         gdata = ((0, 0, 0), (0, 0, 0), (0, 0, 0), (0, 0, 0))
    #         enc = (0, 0, 0, 0)
    #         break

    euler = (0, 0, 0)
    gyro = (0, 0, 0)
    acc = (0, 0, 0)
    mag = (0, 0, 0)
    enc = (0, 0, 0, 0)
    gdata = (euler, gyro, acc, mag)

    # Getting image from camera
    vs = VideoStream(src=0).start()
    frame = vs.read()
    frame = imutils.resize(frame, width=600)
    Save_Image = frame
    Save_Image = cv2.imencode('.png', Save_Image)[1]
    data_encode = np.array(Save_Image)
    str_encode = data_encode.tostring()

    # str_encode = 'Image'
    #
    LidarData = {
        "Lidar": tuple(zip(X[0], X[1])),
        "Time": time.time(),
        "odo": enc,
        "AvgR": np.mean(r),
        "StdRadius": np.std(r),
        "minR": min(r),
        "maxR": max(r),
        "xCenter": center[1][0],
        "yCenter": center[1][1]
    }

    # batVolt = 6*3.7

    td = TurtleDriver()
    batVolt = td.battery_status()
    print("Save Data")
    with TurtleLidarDB() as db:
        db.create_lidar_table()
        db.create_lidar_data_input(LidarData["Time"], LidarData["odo"], LidarData["Lidar"],
                                   LidarData["AvgR"], LidarData["StdRadius"], LidarData["minR"], LidarData["maxR"],
                                   LidarData["xCenter"], LidarData["yCenter"], gdata, str_encode, batVolt)

    print("Time: ", LidarData["Time"])
    # print("Odometer: ", LidarData["odo"])
    print("AvgR: ",LidarData["AvgR"])
    print("stdR: ",LidarData["StdRadius"])
    print("minR: ",LidarData["minR"])
    print("maxR: ",LidarData["maxR"])
    print("xCenter: ",LidarData["xCenter"])
    print("yCenter: ",LidarData["yCenter"])
    print("Battery: ", batVolt)
    print("gyro: ", gyro)

