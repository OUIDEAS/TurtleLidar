import zmq # package is pyzmq
import time


host = "127.0.0.1"
port = "5001"

# Creates a socket instance
context = zmq.Context()
socket = context.socket(zmq.SUB)

# Binds the socket to a predefined port on localhost
socket.bind(f"tcp://{host}:{port}")

# Subscribes to the coffee maker and toaster topic
socket.subscribe("motors")

poller = zmq.Poller()
poller.register(socket, zmq.POLLIN)

t = time.time()

motorBuffer = []

n = 10  # length of buffer
for i in range(n):
    # Makes fake buffer
    motorBuffer.append([i, -i])

while True:
    evts = dict(poller.poll(timeout=20))

    if socket in evts:
        topic = socket.recv_string()
        status = socket.recv_pyobj()
        print(f"Topic: {topic} => {status}")

        if topic == "motors":
            if len(motorBuffer) > n:
                motorBuffer = motorBuffer[-n:]
                motorBuffer.append([status[0][0], status[0][1]])
            else:
                motorBuffer.append([status[0][0], status[0][1]])

    if time.time()-t >= 3:
        # Just to make sure script is working
        print(time.time()-t)
        t = time.time()

        if len(motorBuffer) == 0:
            motorBuffer.append([0, 0])
            print(motorBuffer)
            motorBuffer.pop(0)
        else:
            print(motorBuffer)
            motorBuffer.pop(0)

