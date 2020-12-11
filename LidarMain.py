import rospy
from sensor_msgs.msg import LaserScan
import numpy as np
import zmq # package is pyzmq
import time

# This script is for python 2


class RosDataStorage(object):
    def __init__(self):
        self.scan_data_sub = rospy.Subscriber('scan', LaserScan, self.get_scan)

    def get_scan(self, LaserScan):
        self.scan_data = LaserScan


if __name__ == "__main__":
    # will need to change these
    host = "127.0.0.1"
    port = "5001"

    # Creates a socket instance
    context = zmq.Context()
    # Sub Socket
    socket = context.socket(zmq.SUB)
    # Pub Socket
    pub = context.socket(zmq.PUB)

    # Binds the socket to a predefined port on localhost
    # socket.bind(f"tcp://{host}:{port}")
    socket.bind("tcp://{}:{}".format(host, port))

    # Pub connect
    pub.connect("tcp://{}:{}".format("127.0.0.1", "5002"))  # Will need to change the IP adress
    time.sleep(1)

    # Subscribes to the coffee maker and toaster topic
    socket.subscribe("Lidar")

    # Poller for timeout
    poller = zmq.Poller()
    poller.register(socket, zmq.POLLIN)

    t = time.time()

    # ROS
    rospy.init_node('listener', anonymous=True)
    Data = RosDataStorage()
    rospy.sleep(5)

    while True:
        # Lidar Data Stream
        scan_message = Data.scan_data
        ranges = scan_message.ranges
        angles_min = scan_message.angle_min
        angles_max = scan_message.angle_max
        angle_array = np.linspace(angles_min, angles_max, np.size(ranges))

        # ZMQ PUB/SUB
        evts = dict(poller.poll(timeout=20))

        if socket in evts:
            topic = socket.recv_string()
            status = socket.recv_pyobj()
            # print(f"Topic: {topic} => {status}")
            print(topic)

            if topic == "Lidar":
                print("Lidar Scan Request")
                pktName = "scan"
                pkt = (angle_array, ranges)
                pub.send_string(pktName, flags=zmq.SNDMORE)
                pub.send_pyobj(pkt)