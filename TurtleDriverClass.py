from serial_comm import SerialComm
from utils import power_to_motor_payload, reset_STM, servo_angle_to_duty, estimateError
import frame
import numpy as np
from RP_LIDAR import RPLidar, RPLidarException
import time
import struct


class TurtleException(Exception):
    """Basic exception class"""


class TurtleDriver:
    def __init__(self, SerialPortName="/dev/ttyS0", LidarPortName='/dev/ttyUSB0',
                 min_ang=-90, max_ang=90, min_duty=2400, max_duty=4800):

        # Turtle Shield
        self.serial_device = SerialPortName
        self.comm = SerialComm(self.serial_device)
        reset_STM()
        self.comm.connect()
        time.sleep(.3)  # No idea if needed

        # Servo Motor
        self.servo_min_angle = min_ang
        self.servo_max_angle = max_ang
        self.servo_min_duty = min_duty
        self.servo_max_duty = max_duty

        self.servo_angle = 0

        # Lidar
        self.DEG2RAD = np.pi / 180
        self.MM2INCH = 1 / 25.4

        self.lidar = RPLidar(LidarPortName, 256000)  # Baud rate must be 256000 for RPlidar S1

    def initServo(self):
        self.servo_angle = 0
        self.set_servo(3, self.servo_angle)

    def shutdownLidar(self):
        self.lidar.stop_motor()
        self.lidar.disconnect()

    def set_motors(self, msg):
        if len(msg) < 4:
            # print("Wrong array size in motor command")
            raise TurtleException("Wrong array size in motor command")
            # return

        payload = []
        for p in msg:
            value = power_to_motor_payload(p)  # converts from -1 to 1, to 8 bit, 0-127, first bit is direction
            payload.append(value)

        f = frame.motors(payload)
        status = self.comm.proccess_command(f)
        status = status.decode('utf-8')

        if not status or not status == " OK \r\n":
            # print("Did not receive a valid response after a motor command")
            raise TurtleException("Did not receive a valid response after a motor command")

    def set_servo(self, channel, msg):
        angle = msg
        duty = servo_angle_to_duty(angle, self.servo_min_angle, self.servo_max_angle,
                                   self.servo_min_duty, self.servo_max_duty)

        f = frame.servo(channel, duty)
        status = self.comm.proccess_command(f)
        status = status.decode('utf-8')

        if not status or not status == " OK \r\n":
            # rospy.logerr("Did not receive a valid response after servo command")
            raise TurtleException("Did not receive a valid response after servo command")

    def battery_status(self):
        status = self.comm.proccess_command(frame.battery())
        try:
            battery_status = struct.unpack("<f", status[:4])[0]
        except Exception as e:
            print(e)
            battery_status = None

        # if not status or not str(status).endswith("\r\n"):
        #     # print("Could not get battery status")
        #     raise TurtleException("Could not get battery status")
        # else:
        #     battery_status = struct.unpack("<f", status[:4])[0]
        return battery_status

    def publish_firmware_ver(self):
        firmware_ver = self.comm.proccess_command(frame.firmware_ver())
        firmware_ver = firmware_ver.decode("utf-8")

        if not firmware_ver or not firmware_ver.endswith("\r\n"):
            raise TurtleException("Could not get firmware version")
        else:
            firmware_ver = firmware_ver[:-2]
            # print(firmware_ver)
            return firmware_ver

    def send_motor_command(self, FrontLeft, FrontRight, RearLeft, RearRight):
        # Input range = -1 - 1

        wheel_speeds = [FrontLeft, FrontRight, RearLeft, RearRight]
        self.set_motors(wheel_speeds)

    def drive(self, forwardReverse, leftRight):
        # Inputs:
        #       forwardReverse: Range of -1 to 1, controls speed robot drives at
        #       leftRight: Range of -1 to 1, controls differential speed
        # Outputs:
        #       none

        if abs(forwardReverse) > 1:
            forwardReverse = 1 * np.sign(forwardReverse)
        if abs(leftRight) > 1:
            leftRight = 1 * np.sign(leftRight)

        maxOutput = 1

        speed = forwardReverse * .75
        turn = leftRight * .75

        Rspd = speed + turn
        Lspd = speed - turn

        # Limiting Output
        if abs(Rspd) > maxOutput:
            Rspd = maxOutput * np.sign(Rspd)
        if abs(Lspd) > maxOutput:
            Rspd = maxOutput * np.sign(Lspd)

        self.send_motor_command(Lspd, Rspd, Lspd, Rspd)

    def spinTurtle(self):
        # spd = 75
        t = time.time()
        while True:
            if time.time() - t < 3:
                Lspd = .5
                Rspd = -.5
                self.send_motor_command(Lspd, Rspd, Lspd, Rspd)
            else:
                Lspd = 0
                Rspd = 0
                self.send_motor_command(Lspd, Rspd, Lspd, Rspd)
                time.sleep(.2)
                break

    def stopTurtle(self):
        # Sends command to stop motors
        self.send_motor_command(0, 0, 0, 0)

    def steplidar(self, motor, steps):
        self.servo_angle += steps

        if self.servo_angle > self.servo_max_angle:
            self.servo_angle = self.servo_max_angle
        elif self.servo_angle < self.servo_min_angle:
            self.servo_angle = self.servo_min_angle

        self.set_servo(motor, self.servo_angle)

    def zeroLidar(self):
        self.servo_angle = 0
        self.set_servo(3, self.servo_angle)
        time.sleep(1)
        self.steplidar(3, -20)

        print("Zeroing Lidar")

        coord = np.array([0, 0])
        PrevError = np.array([])

        i = 0
        t1 = time.time()
        try:
            for scan in self.lidar.iter_measures(max_buf_meas=0):
                if scan[3] != 0:
                    theta = scan[2] * self.DEG2RAD
                    R = scan[3] * self.MM2INCH
                    X_lidar = R * np.cos(theta)
                    Y_lidar = R * np.sin(theta)
                    coord = np.vstack((coord, [X_lidar, Y_lidar]))

                if time.time() - t1 > 5:
                    if i == 0:
                        coord = np.array([0, 0])
                        i += 1
                        t1 = time.time()
                    elif i < 11:
                        Error = estimateError(coord)
                        print(Error)
                        coord = np.array([0, 0])
                        PrevError = np.append(PrevError, Error)
                        self.steplidar(3, 2)
                        i += 1
                        t1 = time.time()
                    else:
                        minVal = np.argmin(abs(PrevError))
                        FinalStep = minVal - i + 1
                        print(FinalStep)
                        self.steplidar(3, FinalStep*2)
                        print("Lidar Zeroed")
                        break
        except RPLidarException as e:
            print("Stopping due to error:", e)
        except KeyboardInterrupt:
            print('Stopping due to keyboard interrupt')

        self.lidar.stop()
        time.sleep(.5)

    def lidarScanWrite(self, path='lidarScan.txt', scanLength=5, tries=100):
        outfile = open(path, 'w')
        t1 = time.time()

        try:
            for measurment in self.lidar.iter_measures():
                line = '\t'.join(str(v) for v in measurment)
                outfile.write(line + '\n')
                if time.time() - t1 > scanLength:
                    break
        except RPLidarException as e:
            print("Stopping due to:", e)
        except KeyboardInterrupt:
            print("Keyboard Interrupt detected")

        outfile.close()
        self.lidar.stop()
        time.sleep(.5)

    def lidarScan(self, scanLength=5, tries=100):
        # Inputs:
        #        scanLength: length of time in seconds that the scan will take, default is 5 seconds
        #        tries: number of tries for successful lidar scan, default is 100
        # Outputs:
        #        ang: list of angles that lidar scanned at
        #        dis: list of distances that lidar scanned at

        # self.zeroLidar(24)  # Need to find pipe Diameter
        # time.sleep(1)

        ang = []
        dis = []

        warmup = 5
        t1 = time.time()
        try:
            print('Recording measurments... Press Crl+C to stop.')
            for data in self.lidar.iter_measures():
                # line = '\t'.join(str(v) for v in measurment)
                if time.time() - t1 >= warmup:
                    if data[3] != 0:
                        ang.append(data[2])
                        dis.append(data[3])
                if time.time() - t1 >= scanLength+warmup:
                    break
        except KeyboardInterrupt:
            print('Stoping.')
        self.lidar.stop()
        time.sleep(.5)
        return ang, dis


if __name__ == "__main__":

    print("Turtle Rover Motor Test")
    td = TurtleDriver()
    print(td.battery_status())
    time.sleep(5)
    td.zeroLidar()
    time.sleep(1)
    td.shutdownLidar()
    print("done")
