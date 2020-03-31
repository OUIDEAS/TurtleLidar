from __future__ import with_statement
import serial
from threading import Lock
import time


class SerialCommException(Exception):
    """Basic exception class"""


class SerialComm():
    def __init__(self, device, baudrate=115200, timeout=1.0):
        self.device = device
        self.baudrate = baudrate
        self.timeout = timeout
        self.serial = None
        self.lock = Lock()

    def proccess_command(self, data):
        if not self.serial:
            # rospy.logerr("Serial communication not yet initialized")
            # print("Serial communication not yet initialized")
            raise SerialCommException("Serial Communication not yet initialized")
            return None

        with self.lock:
            self.serial.flushInput()
            self.serial.write(data)
            try:
                status = self.serial.readline()
            except serial.SerialException as e:
                print(e)
                return None
            else:
                return status

    def connect(self):
        while self.serial is None:
            try:
                self.serial = serial.Serial(
                    self.device,
                    baudrate=self.baudrate,
                    timeout=self.timeout
                )
                # rospy.loginfo("Connected to serial device %s" % self.device)
                print("Connected to serial device %s" % self.device)
            except serial.SerialException as e:
                print(e)
                print("Waiting for Serial device")
                time.sleep(1)
                # rospy.logerr(e)
                # rospy.loginfo("Waiting for serial device")
                # rospy.sleep(1)
