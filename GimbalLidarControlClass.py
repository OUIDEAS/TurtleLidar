from Adafruit_MotorHAT import Adafruit_MotorHAT, Adafruit_DCMotor, Adafruit_StepperMotor
import numpy as np
from rplidar import RPLidar
from gpiozero import Button
import time


class LidarGimbal():
    def __init__(self, PortName):

        self.DEG2RAD = np.pi / 180
        self.MM2INCH = 1 / 25.4

        self.lidar = RPLidar(PortName)
        self.mh = Adafruit_MotorHAT()

        self.PanStepper = self.mh.getStepper(200, 1)
        self.PanStepper.setSpeed(10)
        self.TiltStepper = self.mh.getStepper(200, 2)
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

    def homeLidar(self, panPin, tiltPin):
        # This needs rewritten/finished
        panbtn = Button(panPin)
        tiltbtn = Button(tiltPin)

        print("Homing...")
        while not panbtn.is_pressed():
            self.PanStepper.step(1, Adafruit_MotorHAT.BACKWARD, Adafruit_MotorHAT.MICROSTEP)
        print("...")
        while not tiltbtn.is_pressed():
            self.TiltStepper.step(1, Adafruit_MotorHAT.BACKWARD, Adafruit_MotorHAT.MICROSTEP)
        print("...Homed")

    def zeroLidar(self):
        self.homeLidar(3, 5)  # Change Pins before implementation!!!!!!!!!!!!!!!!!!!!!!!!!

        print("Zeroing Lidar")

        panZero = False
        tiltZero = False

        try:
            for scan in self.lidar.iter_scans(max_buf_meas=0):
                for data in scan:
                    theta = data[1] * self.DEG2RAD
                    R = data[2] * self.MM2INCH
                    X_lidar = R * np.cos(theta)
                    Y_lidar = R * np.sin(theta)

                if panZero != True:
                    # Need Error Function
                    Error = 0
                    if Error != 0:
                        self.PanStepper.step(1, Adafruit_MotorHAT.FORWARD, Adafruit_MotorHAT.MICROSTEP)
                    else:
                        panZero = True

                elif tiltZero != True:
                    # Need Error Function
                    Error = 0
                    if Error != 0:
                        self.TiltStepper.step(1, Adafruit_MotorHAT.FORWARD, Adafruit_MotorHAT.MICROSTEP)
                    else:
                        tiltZero = True
                else:
                    break

        except Exception as e:
            print("Stopping due to error:", e)

    def lidarscan(self, path):
        outfile = open(path, 'w')
        i = 0

        try:
            for measurment in self.lidar.iter_measurments():
                for data in measurment:
                    if data[1]:
                        i += 1
                    line = '\t'.join(str(measurment))
                    outfile.write(line + '\n')
                if i > 20:
                    break

        except Exception as e:
            print("Stopping due to error:", e)


if __name__ == "__main__":
    lg = LidarGimbal("COM9")

    lg.zeroLidar()
    lg.lidarscan("Scan.txt")
    lg.shutdown()
