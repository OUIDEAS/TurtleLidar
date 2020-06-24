import zmq # package is pyzmq
import time
from TurtleDriverClass import TurtleDriver
from TurtleLidarDB import TurtleLidarDB
from datetime import datetime as dt


def getTime():
    now = dt.now()
    date_time = now.strftime("%m/%d/%Y, %H:%M:%S")
    return date_time


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
            if pkt != False:
                print("scan")
                td.stopTurtle()
                time.sleep(1)
                scan = td.lidarScan()

                odometer = 0
                dbInput = (getTime(), odometer, scan[0], scan[1])
                with TurtleLidarDB as db:
                    db.create_data_input(dbInput)

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
