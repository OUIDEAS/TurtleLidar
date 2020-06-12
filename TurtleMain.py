import zmq # package is pyzmq
import time
from TurtleDriverClass import TurtleDriver

host = "127.0.0.1"
port = "5001"

# Creates a socket instance
context = zmq.Context()
# Sub Socket
socket = context.socket(zmq.SUB)
# Pub Socket
pub = context.socket(zmq.PUB)

# Binds the socket to a predefined port on localhost
socket.bind(f"tcp://{host}:{port}")

# Pub connect
pub.connect("tcp://{}:{}".format("127.0.0.1", "5002"))
time.sleep(1)

# Subscribes to the coffee maker and toaster topic
socket.subscribe("motors")
socket.subscribe("Turtle")

poller = zmq.Poller()
poller.register(socket, zmq.POLLIN)

t = time.time()

motorBuffer = []
n = 10  # length of buffer

td = TurtleDriver()
# td.initServo()
fv = td.publish_firmware_ver()
print("Turtle Shield Firmware Version:", fv)

for i in range(n):
    # Makes fake buffer
    motorBuffer.append([i, -i])

while True:
    evts = dict(poller.poll(timeout=20))

    if socket in evts:
        topic = socket.recv_string()
        pkt = socket.recv_pyobj()
        print(f"Topic: {topic} => {pkt}")

        if len(pkt[0]) == 2:
            if len(motorBuffer) > n:
                motorBuffer = motorBuffer[-n:]
                motorBuffer.append([pkt[0][0], pkt[0][1]])
            else:
                motorBuffer.append([pkt[0][0], pkt[0][1]])

        if pkt[1] != False:

            td.stopTurtle()
            time.sleep(1)
            scan = td.lidarScan()

            d = "LidarData"
            # scan = ([1, 2, 3], [4, 5, 6])
            pub.send_string(d, flags=zmq.SNDMORE)
            pub.send_pyobj(scan)
            print("sent")

    if time.time()-t >= 3:
        # Just to make sure script is working

        # Could just remove the time thing and make it send
        # commands as fast as possible, or pick a specific period
        print(time.time()-t)
        t = time.time()

        if len(motorBuffer) == 0:
            motorBuffer.append([0, 0])
            print(motorBuffer)
            td.drive(motorBuffer[0][0], motorBuffer[0][1])
            motorBuffer.pop(0)
        else:
            print(motorBuffer)
            td.drive(motorBuffer[0][0], motorBuffer[0][1])
            motorBuffer.pop(0)
