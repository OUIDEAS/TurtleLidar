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

PORT_NAME = 'COM7'


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
            if time.time() - t >=3:
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
    XY = str((circle[0], circle[1]))
    data = ["no"]
    ser = serial.Serial('COM8', 115200)
    while data[0] != "data":
        read_serial = ser.readline()
        data = read_serial.decode('utf-8')
        data = re.sub(r'[()]', '', data)
        data = data.split(", ")

        if data[0] == "data":
            gyro = (float(data[1]), float(data[2]), float(data[3]))
            enc = float(data[4])
            t = float(data[5])

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
        "XYcenter": XY
    }

    with TurtleLidarDB() as db:
        db.create_lidar_table()
        db.create_lidar_data_input(LidarData["Time"], LidarData["odo"], LidarData["Lidar"],
                                   LidarData["AvgR"], LidarData["StdRadius"], LidarData["minR"],LidarData["maxR"], XY, gyro, str_encode)

