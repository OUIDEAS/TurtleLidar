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
        self.scan_count = 0

        uuid = roslaunch.rlutil.get_or_generate_uuid(None, False)
        roslaunch.configure_logging(uuid)

        self.launch = roslaunch.parent.ROSLaunchParent(uuid, [file])
        self.launch.start()
        time.sleep(10)

        print("read")

        rospy.init_node('rplidarNode', anonymous=True)
        self.scan_data_sub = rospy.Subscriber('scan', LaserScan, self.get_scan)
        rospy.sleep(10)  # Lidar Warmup
        return self

    def get_scan(self, LaserScan):
        self.scan_data = LaserScan
        self.scan_count = self.scan_count + 1

    def get_lidar_data(self, t):
        last_scan = self.scan_count
        numScan = 0
        rospy.sleep(2.5)
        tscan = time.time()
        ang = np.array([])
        dis = np.array([])
        while True:
            if self.scan_data is not None:
                if self.scan_count > last_scan:
                    last_scan = self.scan_count
                    numScan = numScan + 1

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

            if time.time() - tscan >= t:
                break
            # rospy.sleep(.1)

        return np.rad2deg(ang), dis*1000

    def __exit__(self, ext_type, exc_value, traceback):
        print("Shutdown")
        time.sleep(5)
        self.scan_data_sub.unregister()
        self.launch.shutdown()
        time.sleep(5)
        qtime = time.time() + 5
        while True:
            if self.launch.pm.is_shutdown:
                print('graceful ROS exit')
                break
            if time.time() > qtime:
                print('timeout waiting for ROS to quit')
                break
            time.sleep(0.1)


if __name__ == "__main__":
    # from matplotlib import pyplot as plt

    with RPLidarClass() as RP:
        print("getting data")
        X = RP.get_lidar_data(5)
        print(X)
        print("end data")
        # ax = plt.subplot(111, projection='polar')
        # ax.plot(X[0], X[1])
        # plt.pause(0.5)

