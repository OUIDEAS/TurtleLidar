import zmq # package is pyzmq
import time
from TurtleDriverClass import TurtleDriver
from TurtleLidarDB import TurtleLidarDB
import numpy as np
import serial
from circle_fit import least_squares_circle, hyper_fit
import re

host = "127.0.0.1"
port = "5001"

context = zmq.Context()
socket = context.socket(zmq.SUB)
pub = context.socket(zmq.PUB)

socket.bind(f"tcp://{host}:{port}")
pub.connect("tcp://{}:{}".format("127.0.0.1", "5002"))
time.sleep(1)

socket.subscribe("motors")
socket.subscribe("scan")

poller = zmq.Poller()
poller.register(socket, zmq.POLLIN)

t = time.time()
tlast = time.time()

motorBuffer = []
n = 10  # length of buffer

td = TurtleDriver()
# td.initServo()
fv = td.publish_firmware_ver()
print("Turtle Shield Firmware Version:", fv)

with TurtleLidarDB as db:
    db.create_table()

for i in range(n):
    # Makes fake buffer
    # motorBuffer.append([i, -i])
    motorBuffer.append([0, 0])

while True:
    evts = dict(poller.poll(timeout=20))

    if socket in evts:
        try:
            topic = socket.recv_string()
            pkt = socket.recv_pyobj()
            print(f"Topic: {topic} => {pkt}")
        except Exception:
            topic = "Bad Input"

        if topic == "motors":
            if len(pkt) == 2:
                if len(motorBuffer) > n:
                    motorBuffer = motorBuffer[-n:]
                    motorBuffer.append([pkt[0], pkt[1]])
                else:
                    motorBuffer.append([pkt[0], pkt[1]])
                tlast = time.time()
        if topic == "scan":
            if pkt[0] != False:
                print("scan")
                td.stopTurtle()
                time.sleep(1)
                ScanTime = time.time()
                scan = td.lidarScan()

                # Find Center of circle and basic data analysis
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
                XY = str((circle[0], circle[1]))

                # Access
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

                LidarData = {
                    "Lidar": tuple(zip(scan[0], scan[1])),
                    "Time": ScanTime,
                    "odo": enc,
                    "AvgR": np.mean(r),
                    "StdRadius": np.std(r),
                    "minR": min(r),
                    "maxR": max(r),
                    "XYcenter": XY
                }

                with TurtleLidarDB as db:
                    db.create_lidar_data_input(LidarData["Time"], LidarData["odo"], LidarData["Lidar"],
                                               LidarData["AvgR"], LidarData["StdRadius"], LidarData["minR"],
                                               LidarData["maxR"], XY, gyro, pkt[1])

    if time.time()-t >= .025:
        # Just to make sure script is working

        # Could just remove the time thing and make it send
        # commands as fast as possible, or pick a specific period
        print("Time Elapsed:", time.time()-t)
        t = time.time()

        if len(motorBuffer) == 0:
            if time.time() - tlast >= .5:
                motorBuffer.append([0, 0])
                print(motorBuffer)
                td.drive(float(motorBuffer[0][0]), float(motorBuffer[0][1]))
                motorBuffer.pop(0)
        else:
            # mbuff = []
            # for i in range(len(motorBuffer)):
            #     a = str(round(float(motorBuffer[i][0]),2))
            #     b = str(round(float(motorBuffer[i][1]),2))
            #     mbuff.append([a, b])
            # print("Buffer:", mbuff)

            print(motorBuffer)
            td.drive(float(motorBuffer[0][0]), float(motorBuffer[0][1]))
            motorBuffer.pop(0)
