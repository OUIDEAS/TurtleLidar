import zmq # package is pyzmq
import time
from TurtleDriverClass import TurtleDriver, TurtleException
from TurtleLidarDB import TurtleLidarDB, printLidarStatus
import numpy as np
from miscFunctions import find_center, ReadSerialTurtle
import utils
# import pretty_errors

host = "127.0.0.1"
port = "5001"

context = zmq.Context()
socket = context.socket(zmq.SUB)

socket.bind(f"tcp://{host}:{port}")
time.sleep(1)

socket.subscribe("motors")
socket.subscribe("scan")
socket.subscribe("shutdown")

poller = zmq.Poller()
poller.register(socket, zmq.POLLIN)

t = time.time()
tlast = time.time()

motorBuffer = []
n = 10  # length of buffer
try:
    td = TurtleDriver()
except:
    td = TurtleDriver(SerialPortName="/dev/serial0", LidarPortName='/dev/ttyUSB0')
fv = td.publish_firmware_ver()
print("Turtle Shield Firmware Version:", fv)

td.initServo()

ser = ReadSerialTurtle()

with TurtleLidarDB() as db:
    db.create_lidar_table()
    db.create_LidarStatus_table()

for i in range(n):
    # Makes fake buffer
    # motorBuffer.append([i, -i])
    motorBuffer.append([0, 0])

try:
    while True:
        evts = dict(poller.poll(timeout=25))

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
                    printLidarStatus("Starting Scan")
                    td.stopTurtle()
                    time.sleep(1)
                    ScanTime = time.time()
                    printLidarStatus("Beginning Zero")
                    td.zeroLidar()
                    printLidarStatus("Lidar Zeroed...Scanning...")
                    scan = td.lidarScan()
                    printLidarStatus("Processing Data")

                    # Adjust data for circle center
                    pipe_scan = find_center(scan)

                    # Access data from micrcontroller
                    data = ser.read_data()

                    LidarData = {
                        "Lidar": tuple(zip(scan[0], scan[1])),
                        "Time": ScanTime,
                        "odo": data[1],
                        "AvgR": np.mean(pipe_scan[0]),
                        "StdRadius": np.std(pipe_scan[0]),
                        "minR": min(pipe_scan[0]),
                        "maxR": max(pipe_scan[0]),
                        "Xcenter": pipe_scan[1][0],
                        "Ycenter": pipe_scan[1][1],
                        "H/W": pipe_scan[3]/pipe_scan[2]
                    }

                    batVolt = td.battery_status()
                    with TurtleLidarDB() as db:
                        db.create_lidar_data_input(LidarData["Time"], LidarData["odo"], LidarData["Lidar"],
                                                   LidarData["AvgR"], LidarData["StdRadius"], LidarData["minR"],
                                                   LidarData["maxR"], LidarData["Xcenter"], LidarData["Ycenter"], data[0],
                                                   pkt[1], batVolt)

                    printLidarStatus("Scan Finished...Ready")
            if topic == "shutdown":
                td.stopTurtle()
                td.shutdownLidar()
                ser.stopRead()
                time.sleep(1)
                raise SystemExit

        if time.time()-t >= .05:
            # print("Time Elapsed:", time.time()-t)
            t = time.time()

            if len(motorBuffer) == 0:
                if time.time() - tlast >= .25:
                    motorBuffer.append([0, 0])
                    # print(motorBuffer)
                    td.drive(float(motorBuffer[0][0]), float(motorBuffer[0][1]))
                    motorBuffer.pop(0)
            else:
                # mbuff = []
                # for i in range(len(motorBuffer)):
                #     a = str(round(float(motorBuffer[i][0]),2))
                #     b = str(round(float(motorBuffer[i][1]),2))
                #     mbuff.append([a, b])
                # print("Buffer:", mbuff)

                # print(motorBuffer)
                td.drive(float(motorBuffer[0][0]), float(motorBuffer[0][1]))
                motorBuffer.pop(0)
except Exception as e:
    print(e)
    td.shutdownLidar()
    ser.stopRead()
    td.stopTurtle()
except KeyboardInterrupt:
    td.shutdownLidar()
    ser.stopRead()
    td.stopTurtle()
