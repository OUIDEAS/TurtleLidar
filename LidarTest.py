from RP_LIDAR import RPLidar
import time
from TurtleLidarDB import TurtleLidarDB
from circle_fit import hyper_fit
import numpy as np
import serial
import re
import cv2
import imutils
from imutils.video import VideoStream
# from TurtleDriverClass import TurtleDriver

PORT_NAME = 'COM7'
# PORT_NAME = '/dev/ttyUSB0'



def run():
    '''Main function'''
    lidar = RPLidar(PORT_NAME, 256000)
    t = time.time()

    ang = []
    dis = []

    try:
        print('Recording measurments... Press Crl+C to stop.')
        for measurment in lidar.iter_measures():
            # line = '\t'.join(str(v) for v in measurment)
            ang.append(measurment[2])
            dis.append(measurment[3])
            if time.time() - t >= 3:
                break
    except KeyboardInterrupt:
        print('Stoping.')
    lidar.stop()
    lidar.stop_motor()
    lidar.disconnect()

    X = (ang, dis)

    return X


if __name__ == '__main__':
    X = run()

    # Finding center of circle
    rad2deg = np.pi / 180
    th = np.asarray(X[0]) * rad2deg
    X_lidar = X[1] * np.cos(th)
    Y_lidar = X[1] * np.sin(th)
    coord = []
    for i in range(len(X_lidar)):
        coord.append([X_lidar[i], Y_lidar[i]])
    circle = hyper_fit(coord)
    X_lidar = X_lidar - circle[0]
    Y_lidar = Y_lidar - circle[1]
    r = np.sqrt(np.square(X_lidar) + np.square(Y_lidar))

    # Gathering data from micro controller
    data = ["no"]
    ser = serial.Serial('COM8', 115200)
    # ser = serial.Serial('/dev/ttyACM0', 115200)
    while data[0] != "data":
        read_serial = ser.readline()
        data = read_serial.decode('utf-8')
        data = re.sub(r'[()]', '', data)
        data = data.split(", ")

        if data[0] == "data":
            gyro = (float(data[1]), float(data[2]), float(data[3]))
            enc = float(data[4])
            t = float(data[5])



    # Getting image from camera
    vs = VideoStream(src=0).start()
    frame = vs.read()
    frame = imutils.resize(frame, width=600)

    Save_Image = frame
    Save_Image = cv2.imencode('.png', Save_Image)[1]
    data_encode = np.array(Save_Image)
    str_encode = data_encode.tostring()



    LidarData = {
        "Lidar": tuple(zip(X[0], X[1])),
        "Time": time.time(),
        "odo": enc,
        "AvgR": np.mean(r),
        "StdRadius": np.std(r),
        "minR": min(r),
        "maxR": max(r),
        "xCenter": circle[0],
        "yCenter": circle[1]
    }

    batVolt = 6*3.7

    # td = TurtleDriver()
    # batVolt = td.battery_status()

    with TurtleLidarDB() as db:
        db.create_lidar_table()
        db.create_lidar_data_input(LidarData["Time"], LidarData["odo"], LidarData["Lidar"],
                                   LidarData["AvgR"], LidarData["StdRadius"], LidarData["minR"], LidarData["maxR"],
                                   LidarData["xCenter"], LidarData["yCenter"], gyro, str_encode, batVolt)

    print("Time: ", LidarData["Time"])
    print("Odometer: ", LidarData["odo"])
    print("AvgR: ",LidarData["AvgR"])
    print("stdR: ",LidarData["StdRadius"])
    print("minR: ",LidarData["minR"])
    print("maxR: ",LidarData["maxR"])
    print("xCenter: ",LidarData["xCenter"])
    print("yCenter: ",LidarData["yCenter"])
    print("gyro: ", gyro)
    print("Battery: ", batVolt)
