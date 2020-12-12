import rospy
from sensor_msgs.msg import LaserScan
import numpy as np
import time
import roslaunch
import subprocess
import os, signal


class RPLidarClass():
    def __enter__(self, FILE = ["/home/theo/catkin_ws/src/rplidar_ros/launch/rplidar.launch"]):

        print("launch")

        uuid = roslaunch.rlutil.get_or_generate_uuid(None, False)
        roslaunch.configure_logging(uuid)

        self.launch = roslaunch.parent.ROSLaunchParent(uuid, FILE)
        self.launch.start()

        # rospy.init_node('rplidarNode', anonymous=True)
        # self.scan_data_sub = rospy.Subscriber('scan', LaserScan, self.get_scan)
        # time.sleep(10)

    # def get_scan(self, LaserScan):
    #     self.scan_data = LaserScan

    def get_lidar_data(self):
        # ang = np.array([])
        # dis = np.array([])
        n = 1
        ang = []
        dis = []
        for i in range(n):
            try:
                msg = rospy.wait_for_message('scan', LaserScan, timeout=1)
                ranges = msg.ranges
                angles_min = msg.angle_min
                angles_max = msg.angle_max
                angle_array = np.linspace(angles_min, angles_max, np.size(ranges))
                ang = ang.append(angle_array)
                dis = dis.append(ranges)
            except Exception as e:
                print(e)
                continue
            time.sleep(.1)

        return ang, dis

    def __exit__(self, ext_type, exc_value, traceback):
        self.launch.shutdown()
        time.sleep(1)


if __name__ == "__main__":
    from matplotlib import pyplot as plt

    with RPLidarClass():
        print("getting data")
        X = RPLidarClass.get_lidar_data()
        print(X)
        print("end data")

        # ax = plt.subplot(111, projection='polar')
        # ax.plot(X[0], X[1])
        # plt.pause(0.5)

