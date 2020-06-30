from RP_LIDAR import RPLidar
import time
from TurtleLidarDB import TurtleLidarDB
from circle_fit import hyper_fit
import numpy as np

PORT_NAME = 'COM7'


def run():
    '''Main function'''
    lidar = RPLidar(PORT_NAME, 256000)
    t=time.time()

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
    # create a database connection
    odo = "0"

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

    LidarData = {
        "Lidar": tuple(zip(X[0], X[1])),
        "Time": time.time(),
        "odo": odo,
        "AvgR": np.mean(r),
        "StdRadius": np.std(r)
    }

    with TurtleLidarDB() as db:
        db.create_lidar_data_input(LidarData["Time"], LidarData["odo"], LidarData["Lidar"],
                                   LidarData["AvgR"], LidarData["StdRadius"])

