from Raspi_MotorHAT import Raspi_MotorHAT, Raspi_StepperMotor
import numpy as np
import time
from rplidar import RPLidar
from gpiozero import Button
from circle_fit import least_squares_circle


class LidarGimbal:
    def __init__(self, PortName):

        self.DEG2RAD = np.pi / 180
        self.MM2INCH = 1 / 25.4

        self.lidar = RPLidar(PortName)
        self.mh = Raspi_MotorHAT(0x6F)

        self.PanStepper = self.mh.getStepper(200, 2)
        self.PanStepper.setSpeed(10)
        self.TiltStepper = self.mh.getStepper(200, 1)
        self.TiltStepper.setSpeed(10)

    def turnOffMotors(self):
        self.mh.getMotor(1).run(Raspi_MotorHAT.RELEASE)
        self.mh.getMotor(2).run(Raspi_MotorHAT.RELEASE)
        self.mh.getMotor(3).run(Raspi_MotorHAT.RELEASE)
        self.mh.getMotor(4).run(Raspi_MotorHAT.RELEASE)

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
        # steps = steps*3
        if motor == "Pan":
            if steps > 0:
                self.PanStepper.step(abs(steps), Raspi_MotorHAT.FORWARD, Raspi_MotorHAT.MICROSTEP)
            else:
                self.PanStepper.step(abs(steps), Raspi_MotorHAT.BACKWARD, Raspi_MotorHAT.MICROSTEP)
        elif motor == "Tilt":
            if steps > 0:
                self.TiltStepper.step(abs(steps), Raspi_MotorHAT.FORWARD, Raspi_MotorHAT.MICROSTEP)
            else:
                self.TiltStepper.step(abs(steps), Raspi_MotorHAT.BACKWARD, Raspi_MotorHAT.MICROSTEP)
        else:
            print("Invalid input for motor")
            print("Valid inputs are Pan or Tilt")

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
        t1 =time.time()
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
                        self.steplidar("Pan",FinalStep)
                        print("Lidar Zeroed")
                        break
        except Exception as e:
            print("Stopping due to error:", e)

        except KeyboardInterrupt:
            print('Stoping.')
        self.lidar.stop()

    def lidarScanWrite(self, path, NumberOfScans):
        outfile = open(path, 'w')
        i = 0

        try:
            for measurment in self.lidar.iter_measurments():
                for data in measurment:
                    if data[0] == True:
                        i += 1
                    line = '\t'.join(str(measurment))
                    outfile.write(line + '\n')
                if i > NumberOfScans:
                    break

        except Exception as e:
            print("Stopping due to error:", e)

        outfile.close()
        self.lidar.stop()

    def lidarScan(self, NumberOfScans):
        i = 0
        data = []
        t1 = time.time()
        try:
            for scan in self.lidar.iter_measurments():
                data.append(np.array(scan))
                for scanData in scan:
                    if scanData[0] == 1:
                        i += 1
                # if i > NumberOfScans:
                #     break
                if time.time() - t1 > 5:
                    break
        except Exception as e:
            print("Stopping due to error:", e)
        self.lidar.stop()
        return data

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
    lg.zeroLidar(24)
    lg.debuglidar('debug.txt')
    time.sleep(2)
    lg.shutdown()
    quit()