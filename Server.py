# multi_pub.py

import time
import zmq
import random
from threading import Thread

host = "127.0.0.1"
port = "5001"

ctx = zmq.Context()

def update_smart_mirror(appliance):
    socket = ctx.socket(zmq.PUB)
    socket.connect(f"tcp://{host}:{port}")
    time.sleep(.1)

    status = ([random.random(), random.random()], "False")
    # Sends multipart message to subscriber
    socket.send_string(appliance, flags=zmq.SNDMORE)
    # socket.send_json(status)
    socket.send_pyobj(status)
# coffee_maker = Thread(target=update_smart_mirror, args=("COFFEE MAKER",))
# toaster = Thread(target=update_smart_mirror, args=("TOASTER",))
Turtle = Thread(target=update_smart_mirror, args=("Turtle",))
motors = Thread(target=update_smart_mirror, args=("motors",))
# coffee_maker.start()
# toaster.start()

Turtle.start()
motors.start()

# waits for both to send messages before exiting
# coffee_maker.join()
# toaster.join()
Turtle.join()