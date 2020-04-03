from serial_comm import SerialComm
from utils import power_to_motor_payload, reset_STM
import frame
import numpy as np
import time
import struct


class TurtleException(Exception):
    """Basic exception class"""


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
            # print("Wrong array size in motor command")
            raise TurtleException("Wrong array size in motor command")
            # return

        payload = []
        for p in msg:
            value = power_to_motor_payload(p) # converts from -1 to 1, to 8 bit, 0-127, first bit is direction
            payload.append(value)

        f = frame.motors(payload)
        status = self.comm.proccess_command(f)

        if not status or not status == " OK \r\n":
            # print("Did not receive a valid response after a motor command")
            raise TurtleException("Did not receive a valid response after a motor command")

    def battery_status(self):
        status = self.comm.proccess_command(frame.battery())

        if not status or not status.endswith("\r\n"):
            # print("Could not get battery status")
            raise TurtleException("Could not get battery status")
        else:
            battery_status = struct.unpack("<f", status[:4])[0]
            return battery_status

    def send_motor_command(self, FrontLeft, FrontRight, RearLeft, RearRight):
        # Input Range currently believed to be 0 - 127, first bit is direction
        # 0 Forward, 1 backward

        wheel_speeds = [FrontLeft, FrontRight, RearLeft, RearRight]
        self.set_motors(wheel_speeds)

    def drive(self, forwardReverse, leftRight):
        maxinpt = (2**16)/2  # assuming 16 bit joystick used as input, -32768 - 32768
        maxOutput = 1      # Its either -1 to 1, 0-255 or 0-127, IDK anymore. I figured it out, all are true

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
        spd = 75
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


if __name__ == "__main__":

    print("Turtle Rover Motor Test")
    td = TurtleDriver()
    time.sleep(3)
    print(td.battery_status())
    time.sleep(2)
    td.spinTurtle()
