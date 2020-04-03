from Adafruit_MotorHAT import Adafruit_MotorHAT, Adafruit_StepperMotor
import numpy as np
from rplidar import RPLidar, RPLidarException
from gpiozero import Button
from circle_fit import least_squares_circle
import time
import json


class FinishScan(Exception):
    """Exception class to end the lidar scans"""


class LidarGimbal:
    def __init__(self, PortName = '/dev/ttyUSB0'):

        self.DEG2RAD = np.pi / 180
        self.MM2INCH = 1 / 25.4

        self.lidar = RPLidar(PortName)
        self.mh = Adafruit_MotorHAT()

        self.PanStepper = self.mh.getStepper(200, 2)
        self.PanStepper.setSpeed(10)
        self.TiltStepper = self.mh.getStepper(200, 1)
        self.TiltStepper.setSpeed(10)

    def turnOffMotors(self):
        self.mh.getMotor(1).run(Adafruit_MotorHAT.RELEASE)
        self.mh.getMotor(2).run(Adafruit_MotorHAT.RELEASE)
        self.mh.getMotor(3).run(Adafruit_MotorHAT.RELEASE)
        self.mh.getMotor(4).run(Adafruit_MotorHAT.RELEASE)

    def turnOffLidar(self):
        self.lidar.stop()
        self.lidar.stop_motor()

    def shutdown(self):
        self.turnOffLidar()
        self.lidar.disconnect()
        self.turnOffMotors()
        quit()

    def lidarHealth(self):
        info = self.lidar.get_info()
        print(info)
        health = self.lidar.get_health()
        print(health)

    def steplidar(self, motor, steps):
        # steps = steps*16 # ???
        if motor == "Pan":
            if steps > 0:
                self.PanStepper.step(abs(steps), Adafruit_MotorHAT.FORWARD, Adafruit_MotorHAT.MICROSTEP)
            else:
                self.PanStepper.step(abs(steps), Adafruit_MotorHAT.BACKWARD, Adafruit_MotorHAT.MICROSTEP)
        elif motor == "Tilt":
            if steps > 0:
                self.TiltStepper.step(abs(steps), Adafruit_MotorHAT.FORWARD, Adafruit_MotorHAT.MICROSTEP)
            else:
                self.TiltStepper.step(abs(steps), Adafruit_MotorHAT.BACKWARD, Adafruit_MotorHAT.MICROSTEP)
        else:
            # print("Invalid input for motor")
            # print("Valid inputs are Pan or Tilt")
            raise Exception("Invalid Inputs for Motor")

    def holdSteppers(self):
        self.steplidar('Pan', 1)
        self.steplidar('Pan', -1)
        self.steplidar('Tilt', 1)
        self.steplidar('Tilt', -1)

    def homeLidar(self, panPin, tiltPin):
        # This needs rewritten/finished
        panbtn = Button(panPin)
        tiltbtn = Button(tiltPin)

        print("Homing...")
        while not panbtn.is_pressed():
            self.steplidar("Pan", 1)
        print("...")
        while not tiltbtn.is_pressed():
            self.steplidar("Tilt", 1)
        print("...Homed")

    def estimateError(self, coord, R_expected):
        circle = least_squares_circle(coord)
        x = coord[:, 0]
        y = coord[:, 0]
        x = x - circle[0]
        y = y - circle[0]
        r = np.sqrt(np.square(x)+np.square(y))
        # remove outliers at some point
        error = R_expected - r
        meanError = np.mean(error)
        return meanError

    def zeroLidar(self, Pipe_diamiter):
        # self.homeLidar(3, 5)  # Change Pins before implementation!!!!!!!!!!!!!!!!!!!!!!!!!

        print("Zeroing Lidar")

        panZero = False
        tiltZero = False

        coord = np.array([0, 0])
        PrevError = np.array([])
        # step = np.array([])
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
                    if i < 7:
                        Error = self.estimateError(coord, Pipe_diamiter/2)
                        print(Error)
                        coord = np.array([0, 0])
                        PrevError = np.append(PrevError, Error)
                        self.steplidar('Pan', 1)
                        i += 1
                        # step = np.append(step, [i])
                        t1 = time.time()
                    else:
                        min = np.argmin(PrevError)
                        FinalStep = min - i
                        print(FinalStep)
                        self.steplidar("Pan", FinalStep)
                        print("Lidar Zeroed")
                        break
        except RPLidarException as e:
            print("Stopping due to error:", e)
        except KeyboardInterrupt:
            print('Stopping due to keyboard interrupt')

        self.lidar.stop()
        time.sleep(.5)

    def lidarScanWrite(self, path='lidarScan.txt', tries=100):
        outfile = open(path, 'w')
        t1 = time.time()

        for i in range(tries):
            try:
                for measurment in self.lidar.iter_measurments():
                    line = '\t'.join(str(v) for v in measurment)
                    outfile.write(line + '\n')
                    if time.time() - t1 > 5:
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

    def lidarScan(self, tries=100):
        data = []
        t1 = time.time()
        for i in range(tries):
            try:
                for scan in self.lidar.iter_measurments():
                    data.append(np.array(scan))
                    if time.time() - t1 > 5:
                        raise FinishScan("Scan Complete")

            except RPLidarException as e:
                print("Retrying due to error:", e)
                continue
            except FinishScan as e:
                break
            else:
                break
        self.lidar.stop()
        time.sleep(.5)
        return data

    def lidarScanJSON(self):

        t1 = time.time

        X = []
        Y = []

        try:
            for scan in self.lidar.iter_scans(max_buf_meas=0):
                for data in scan:
                    theta = data[1] * self.DEG2RAD
                    R = data[2] * self.MM2INCH
                    X_lidar = R * np.cos(theta)
                    Y_lidar = R * np.sin(theta)

                    X.append(X_lidar)
                    Y.append(Y_lidar)

                if time.time() - t1 > 5:

                    ScanData = {"X": X,
                                "Y": Y}

                    with open('LidarScanData.txt', 'w') as json_file:
                        json.dump(ScanData, json_file)

                    break
        except Exception as e:
            print("Stopping due to error:", e)


    def debuglidar(self, path):
        outfile = open(path, 'w')
        try:
            t1 = time.time()
            for measurment in self.lidar.iter_measurments():
                line = '\t'.join(str(v) for v in measurment)
                outfile.write(line + '\n')
                if time.time() - t1 > 5:
                    break
        except Exception as e:
            print("Stopping due to error:", e)
        self.lidar.stop()


if __name__ == "__main__":
    lg = LidarGimbal('/dev/ttyUSB0')
    lg.holdSteppers()

    print("Preparing to Zero")
    time.sleep(3)
    print("Zeroing")

    lg.zeroLidar(24)
    lg.debuglidar('debug.txt')
    time.sleep(2)
    lg.shutdown()
    quit()
