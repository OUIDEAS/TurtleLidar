from Raspi_MotorHAT import Raspi_MotorHAT
import numpy as np
from rplidar import RPLidar
from gpiozero import Button


class LidarGimbal():
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

    def homeLidar(self, panPin, tiltPin):
        # This needs rewritten/finished
        panbtn = Button(panPin)
        tiltbtn = Button(tiltPin)

        print("Homing...")
        while not panbtn.is_pressed():
            self.PanStepper.step(1, Raspi_MotorHAT.BACKWARD, Raspi_MotorHAT.MICROSTEP)
        print("...")
        while not tiltbtn.is_pressed():
            self.TiltStepper.step(1, Raspi_MotorHAT.BACKWARD, Raspi_MotorHAT.MICROSTEP)
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
                        self.PanStepper.step(1, Raspi_MotorHAT.FORWARD, Raspi_MotorHAT.MICROSTEP)
                    else:
                        panZero = True

                elif tiltZero != True:
                    # Need Error Function
                    Error = 0
                    if Error != 0:
                        self.TiltStepper.step(1, Raspi_MotorHAT.FORWARD, Raspi_MotorHAT.MICROSTEP)
                    else:
                        tiltZero = True
                else:
                    break

        except Exception as e:
            print("Stopping due to error:", e)

    def lidarScanWrite(self, path, NumberOfScans):
        outfile = open(path, 'w')
        i = 0

        try:
            for measurment in self.lidar.iter_measurments():
                for data in measurment:
                    if data[1]:
                        i += 1
                    line = '\t'.join(str(measurment))
                    outfile.write(line + '\n')
                if i > NumberOfScans:
                    break

        except Exception as e:
            print("Stopping due to error:", e)

        outfile.close()

    def lidarScan(self, NumberOfScans):
        i = 0
        data = []

        try:
            for scan in self.lidar.iter_measurments():
                data.append(np.array(scan))
                for scandata in scan:
                    if scandata[1]:
                        i += 1
                if i > NumberOfScans:
                    break
        except Exception as e:
            print("Stopping due to error:", e)

        return data


if __name__ == "__main__":
    lg = LidarGimbal("COM9")

    lg.zeroLidar()
    lg.lidarScanWrite("Scan.txt")
    lg.shutdown()
