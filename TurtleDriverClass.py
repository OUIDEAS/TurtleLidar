from serial_comm import SerialComm
from utils import power_to_motor_payload, reset_STM
import frame
import numpy as np
import time
import struct

class TurtleDriver:
    def __init__(self, SerialPortName = "/dev/ttyAMA0", wheel_radius=0.06, wheel_track=0.33):

        self.serial_device = SerialPortName

        self.comm = SerialComm(self.serial_device)
        reset_STM()
        self.comm.connect()

        self.wheel_radius = wheel_radius
        self.wheel_track = wheel_track

        self.forwardReverse = 0
        self.leftRight = 0

    def set_motors(self, msg):
        if len(msg) < 4:
            print("Wrong array size in motor command")
            raise Exception("Wrong array size in motor command")
            # return

        payload = []
        for p in msg:
            value = power_to_motor_payload(p)
            payload.append(value)

        f = frame.motors(payload)
        status = self.comm.proccess_command(f)

        if not status or not status == " OK \r\n":
            # print("Did not receive a valid response after a motor command")
            raise Exception("Did not receive a valid response after a motor command")

    def battery_status(self):
        status = self.comm.proccess_command(frame.battery())

        if not status or not status.endswith("\r\n"):
            # print("Could not get battery status")
            raise Exception("Could not get battery status")
        else:
            battery_status = struct.unpack("<f", status[:4])[0]
            return battery_status

    def send_motor_command(self, FrontLeft, FrontRight, RearLeft, RearRight):
        # Input Range currently believed to have input range -1 to 1?
        wheel_speeds = [FrontLeft, FrontRight, RearLeft, RearRight]
        self.set_motors(wheel_speeds)

    def read_motor_command(self):
        # Currently assuming two inputs, likely from xbox controller through browser
        self.forwardReverse = 0
        self.leftRight = 0

    def drive(self):
        self.read_motor_command()
        max = (2**16)/2  # assuming 16 bit joystick used as input

        speed = self.forwardReverse / max * .75
        turn = self.leftRight / max

        Rspd = speed + turn
        Lspd = speed - turn

        if abs(Rspd) > max:
            Rspd = max * np.sign(Rspd)
        if abs(Lspd) > max:
            Rspd = max * np.sign(Lspd)

        self.send_motor_command(Lspd, Rspd, Lspd, Rspd)

    def debug(self):
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
                break


if __name__ == "__main__":

    print("Turtle Rover Motor Test")
    td = TurtleDriver()
    time.sleep(3)
    print(td.battery_status())
    time.sleep(2)
    td.debug()
