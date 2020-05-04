from serial_comm import SerialComm
from utils import power_to_motor_payload, reset_STM, servo_angle_to_duty, estimateError
import frame
import numpy as np
from rplidar import RPLidar, RPLidarException
import time
import struct


class FinishScan(Exception):
    """Exception class to end the lidar scan"""


class TurtleException(Exception):
    """Basic exception class"""


class TurtleDriver:
    def __init__(self, SerialPortName="/dev/ttyAMA0", LidarPortName='/dev/ttyUSB0',
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
        self.set_servo(1, self.servo_angle)

        # Lidar
        self.DEG2RAD = np.pi / 180
        self.MM2INCH = 1 / 25.4

        self.lidar = RPLidar(LidarPortName)

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

        if not status or not status == " OK \r\n":
            # print("Did not receive a valid response after a motor command")
            raise TurtleException("Did not receive a valid response after a motor command")

    def set_servo(self, channel, msg):
        angle = msg
        duty = servo_angle_to_duty(angle, self.servo_min_angle, self.servo_max_angle,
                                   self.servo_min_duty, self.servo_max_duty)

        f = frame.servo(channel, duty)
        status = self.comm.proccess_command(f)

        if not status or not status == " OK \r\n":
            # rospy.logerr("Did not receive a valid response after servo command")
            raise TurtleException("Did not receive a valid response after servo command")

    def battery_status(self):
        status = self.comm.proccess_command(frame.battery())

        if not status or not status.endswith("\r\n"):
            # print("Could not get battery status")
            raise TurtleException("Could not get battery status")
        else:
            battery_status = struct.unpack("<f", status[:4])[0]
            return battery_status

    def publish_firmware_ver(self):
        firmware_ver = self.comm.proccess_command(frame.firmware_ver())

        if not firmware_ver or not firmware_ver.endswith("\r\n"):
            raise TurtleException("Could not get firmware version")
        else:
            firmware_ver = firmware_ver[:-2]
            print(firmware_ver)

    def send_motor_command(self, FrontLeft, FrontRight, RearLeft, RearRight):
        # Input range = -1 - 1

        wheel_speeds = [FrontLeft, FrontRight, RearLeft, RearRight]
        self.set_motors(wheel_speeds)

    def drive(self, forwardReverse, leftRight):
        # Inputs:
        #       forwardReverse: Range of -32768 - 32768, controls speed robot drives at
        #       leftRight: Range of -32768 - 32768, controls differential speed
        # Outputs:
        #       none
        maxinpt = (2**16)/2  # assuming 16 bit joystick used as input, -32768 - 32768
        maxOutput = 1  # Its either -1 to 1, 0-255 or 0-127, IDK anymore. Figured it out, all are technically correct

        speed = forwardReverse / maxinpt * maxOutput * .75
        turn = leftRight / maxinpt * maxOutput * .75

        Rspd = speed + turn
        Lspd = speed - turn

        # Limiting Output
        if abs(Rspd) > maxOutput:
            Rspd = maxOutput * np.sign(Rspd)
        if abs(Lspd) > maxOutput:
            Rspd = maxOutput * np.sign(Lspd)

        # Formatting to correct output
        # if Rspd >= 0:
        #     Rspd = int(abs(Rspd)) | (0 << 7)
        # else:
        #     Rspd = int(abs(Rspd)) | (1 << 7)
        #
        # if Lspd >= 0:
        #     Lspd = int(abs(Lspd)) | (0 << 7)
        # else:
        #     Lspd = int(abs(Lspd)) | (1 << 7)

        self.send_motor_command(Lspd, Rspd, Lspd, Rspd)

    def spinTurtle(self):
        # spd = 75
        t = time.time()
        while True:
            if time.time() - t < 3:
                Lspd = .5
                Rspd = -.5
                # Lspd = int(abs(spd)) | (0 << 7)
                # Rspd = int(abs(spd)) | (1 << 7)
                self.send_motor_command(Lspd, Rspd, Lspd, Rspd)
            else:
                Lspd = 0
                Rspd = 0
                self.send_motor_command(Lspd, Rspd, Lspd, Rspd)
                time.sleep(.2)
                break

    def steplidar(self, motor, steps):
        self.servo_angle += steps

        if self.servo_angle > self.servo_max_angle:
            self.servo_angle = self.servo_max_angle
        elif self.servo_angle < self.servo_min_angle:
            self.servo_angle = self.servo_min_angle

        self.set_servo(motor, self.servo_angle)

    def zeroLidar(self, Pipe_diamiter):
        self.servo_angle = 0
        self.set_servo(1, self.servo_angle)

        self.steplidar(1, -20)

        print("Zeroing Lidar")

        coord = np.array([0, 0])
        PrevError = np.array([])

        i = 0
        t1 = time.time()
        try:
            for scan in self.lidar.iter_scans(max_buf_meas=0):
                for data in scan:
                    theta = data[1] * self.DEG2RAD
                    R = data[2] * self.MM2INCH
                    X_lidar = R * np.cos(theta)
                    Y_lidar = R * np.sin(theta)
                    coord = np.vstack((coord, [X_lidar, Y_lidar]))
                if time.time() - t1 > 5:
                    if i < 10:
                        Error = estimateError(coord, Pipe_diamiter/2)
                        print(Error)
                        coord = np.array([0, 0])
                        PrevError = np.append(PrevError, Error)
                        self.steplidar(1, 2)
                        i += 1
                        # step = np.append(step, [i])
                        t1 = time.time()
                    else:
                        minVal = np.argmin(PrevError)
                        FinalStep = minVal - i
                        print(FinalStep)
                        self.steplidar(1, FinalStep*2)
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

        for i in range(tries):
            try:
                for measurment in self.lidar.iter_measurments():
                    line = '\t'.join(str(v) for v in measurment)
                    outfile.write(line + '\n')
                    if time.time() - t1 > scanLength:
                        raise FinishScan("Scan Complete")

            except RPLidarException as e:
                print("Retrying due to error:", e)
                continue
            except FinishScan as e:
                print(e)
                break
            except KeyboardInterrupt:
                print("Keyboard Interrupt detected")
                break
            else:
                print("Shouldn't have got here, I think")
                break

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

        ang = []
        dis = []

        t1 = time.time()
        for i in range(tries):
            try:
                for scan in self.lidar.iter_measurments():
                    for data in scan:
                        theta = data[2]
                        R = data[3]

                        ang.append(theta)
                        dis.append(R)
                    if time.time() - t1 > abs(scanLength):
                        raise FinishScan("Scan Complete")

            except RPLidarException as e:
                print("Retrying due to error:", e)
                continue
            except FinishScan as e:
                print(e)
                break
            else:
                break
        self.lidar.stop()
        time.sleep(.5)
        return ang, dis


if __name__ == "__main__":

    print("Turtle Rover Motor Test")
    td = TurtleDriver()
    time.sleep(3)
    print(td.battery_status())
    time.sleep(2)
    td.spinTurtle()
