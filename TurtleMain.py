import zmq  # package is pyzmq
import time
from TurtleDriverClass import TurtleDriver, TurtleException
from TurtleLidarDB import TurtleLidarDB, printLidarStatus, DebugPrint
import numpy as np
from miscFunctions import find_center, ReadSerialTurtle
import utils

# import pretty_errors

DebugPrint("Turtle Main Start...")
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
tbat = time.time()
tlast = time.time()

motorBuffer = []
n = 10  # length of buffer

td = TurtleDriver()

fv = td.publish_firmware_ver()
DebugPrint("Turtle Shield Firmware Version:" + str(fv))

td.initServo()

ser = ReadSerialTurtle()

# todo: not needed because the class init does this?
with TurtleLidarDB() as db:
    db.create_lidar_table()
    db.create_LidarStatus_table()

for i in range(n):
    # Makes fake buffer
    # motorBuffer.append([i, -i])
    print("Stopping motors...")
    motorBuffer.append([0, 0])

printLidarStatus("Turtle Ready")

try:
    while True:
        evts = dict(poller.poll(timeout=1))

        if socket in evts:
            try:
                topic = socket.recv_string()
                pkt = socket.recv_pyobj()
                # print(f"Topic: {topic} => {pkt}")
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
                    try:
                        batVolt = td.battery_status()
                        printLidarStatus(battery_voltage=batVolt)
                    except Exception as e:
                        DebugPrint("Exception when getting battery status: " + str(e))
                        batVolt = 0

                    printLidarStatus("Starting Scan", batVolt)
                    DebugPrint("Beginning Scan")
                    td.stopTurtle()
                    time.sleep(1)
                    ScanTime = time.time()
                    printLidarStatus("Beginning Zero")
                    DebugPrint("Beginning Zero")
                    td.zeroLidar()
                    printLidarStatus("Lidar Zeroed...Scanning...")
                    DebugPrint("Scanning")
                    scan = td.lidarScan(5)
                    printLidarStatus("Processing Data")

                    if len(scan[0]) > 1:
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
                            "H/W": pipe_scan[3] / pipe_scan[2]
                        }

                        with TurtleLidarDB() as db:
                            db.insert_lidar_data(LidarData["Time"], LidarData["odo"], LidarData["Lidar"],
                                                 LidarData["AvgR"], LidarData["StdRadius"], LidarData["minR"],
                                                 LidarData["maxR"], LidarData["Xcenter"], LidarData["Ycenter"], data[0],
                                                 pkt[1], batVolt)

                        printLidarStatus("Scan Finished...Ready", batVolt)
                        DebugPrint("Scan Finished")
                    else:
                        printLidarStatus("Scan Failed")

            if topic == "shutdown":
                td.stopTurtle()
                ser.stopRead()
                time.sleep(1)
                raise SystemExit

        # Battery
        if time.time() - tbat >= 10:
            try:
                batVolt = td.battery_status()
                printLidarStatus(battery_voltage=batVolt)
            except Exception as e:
                DebugPrint("Exception when getting battery status: " + str(e))

            tbat = time.time()


        # Motors
        if time.time() - t >= .05:
            # print("Time Elapsed:", time.time()-t)
            t = time.time()

            if len(motorBuffer) == 0:
                if time.time() - tlast >= .25:
                    motorBuffer.append([0, 0])
                    # print(motorBuffer)
                    td.drive(float(motorBuffer[0][0]), float(motorBuffer[0][1]))
                    motorBuffer.pop(0)
            else:
                # print(motorBuffer)
                td.drive(float(motorBuffer[0][0]), float(motorBuffer[0][1]))
                motorBuffer.pop(0)

except Exception as e:
    # print(e)
    DebugPrint("Turtle Main exception " + str(e))
    printLidarStatus("Exception Occurred")
    td.stopTurtle()
    ser.stopRead()
except KeyboardInterrupt:
    DebugPrint("Turtle Main Keyboard Interrupt")
    printLidarStatus("Keyboard Interrupt")
    td.stopTurtle()
    ser.stopRead()
