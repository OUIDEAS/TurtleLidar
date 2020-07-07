import zmq # package is pyzmq
import time
from TurtleDriverClass import TurtleDriver
from TurtleLidarDB import TurtleLidarDB
import numpy as np
from miscFunctions import find_center, ReadSerialTurtle


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

ser = ReadSerialTurtle()

with TurtleLidarDB() as db:
    db.create_lidar_table()

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

                # Adjust data for circle center
                pipe_scan = find_center(scan)
                r = pipe_scan[1]
                circle = []
                circle[0] = pipe_scan[1]
                circle[1] = pipe_scan[2]

                # Access data from micrcontroller
                data = ser.read_data()
                gyro = data[0]
                enc = data[1]

                LidarData = {
                    "Lidar": tuple(zip(scan[0], scan[1])),
                    "Time": ScanTime,
                    "odo": enc,
                    "AvgR": np.mean(r),
                    "StdRadius": np.std(r),
                    "minR": min(r),
                    "maxR": max(r),
                    "Xcenter": circle[0],
                    "Ycenter": circle[1]
                }

                batVolt = td.battery_status()

                with TurtleLidarDB() as db:
                    db.create_lidar_data_input(LidarData["Time"], LidarData["odo"], LidarData["Lidar"],
                                               LidarData["AvgR"], LidarData["StdRadius"], LidarData["minR"],
                                               LidarData["maxR"], LidarData["Xcenter"], LidarData["Ycenter"], gyro,
                                               pkt[1], batVolt)

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
