import rospy
from sensor_msgs.msg import LaserScan
import numpy as np
import time
import roslaunch
# import subprocess
# import os, signal


class RPLidarClass:
    def __enter__(self, file="/home/catkin_ws/src/launch/rplidar_s1.launch"):
        print("launch")

        self.scan_data = None

        uuid = roslaunch.rlutil.get_or_generate_uuid(None, False)
        roslaunch.configure_logging(uuid)

        self.launch = roslaunch.parent.ROSLaunchParent(uuid, [file])
        self.launch.start()
        time.sleep(10)

        print("read")

        rospy.init_node('rplidarNode', anonymous=True)
        self.scan_data_sub = rospy.Subscriber('scan', LaserScan, self.get_scan)
        rospy.sleep(1)
        return self

    def get_scan(self, LaserScan):
        self.scan_data = LaserScan

    def get_lidar_data(self, t):
        rospy.sleep(5)
        tscan = time.time()
        ang = np.array([])
        dis = np.array([])
        while time.time() - tscan <= t:
            if self.scan_data is not None:
                msg = self.scan_data
                ranges = msg.ranges
                angles_min = msg.angle_min
                angles_max = msg.angle_max
                angle_inc = msg.angle_increment
                angle_array = np.linspace(angles_min, angles_max, np.size(ranges))
                ranges = np.array(ranges)
                ang = np.append(ang, angle_array[np.isfinite(ranges)])
                dis = np.append(dis, ranges[np.isfinite(ranges)])
            else:
                print("No Data?")
                rospy.sleep(.2)
            rospy.sleep(.1)

        return np.rad2deg(ang), dis*1000

    def __exit__(self, ext_type, exc_value, traceback):
        print("Shutdown")
        time.sleep(5)
        self.launch.shutdown()
        time.sleep(1)


class RPLidarClass2:
    def __init__(self, file="/home/catkin_ws/src/launch/rplidar_s1.launch"):
        print("launch")

        self.scan_data = None

        uuid = roslaunch.rlutil.get_or_generate_uuid(None, False)
        roslaunch.configure_logging(uuid)

        self.launch = roslaunch.parent.ROSLaunchParent(uuid, [file])
        self.launch.start()
        time.sleep(10)

        print("read")

        rospy.init_node('rplidarNode', anonymous=True)
        self.scan_data_sub = rospy.Subscriber('scan', LaserScan, self.get_scan)
        rospy.sleep(1)

    def get_scan(self, LaserScan):
        self.scan_data = LaserScan

    def get_lidar_data(self, t):
        rospy.sleep(5)
        tscan = time.time()
        ang = np.array([])
        dis = np.array([])
        while time.time() - tscan <= t:
            if self.scan_data is not None:
                msg = self.scan_data
                ranges = msg.ranges
                angles_min = msg.angle_min
                angles_max = msg.angle_max
                angle_inc = msg.angle_increment
                angle_array = np.linspace(angles_min, angles_max, np.size(ranges))
                ranges = np.array(ranges)
                ang = np.append(ang, angle_array[np.isfinite(ranges)])
                dis = np.append(dis, ranges[np.isfinite(ranges)])
            else:
                print("No Data?")
                rospy.sleep(.2)
            rospy.sleep(.1)

        return np.rad2deg(ang), dis*1000

    def shutdownLidar(self):
        print("Shutdown")
        time.sleep(5)
        self.launch.shutdown()
        time.sleep(1)


if __name__ == "__main__":
    from matplotlib import pyplot as plt

    with RPLidarClass() as RP:
        print("getting data")
        X = RP.get_lidar_data(5)
        print(X)
        print("end data")

        # ax = plt.subplot(111, projection='polar')
        # ax.plot(X[0], X[1])
        # plt.pause(0.5)

