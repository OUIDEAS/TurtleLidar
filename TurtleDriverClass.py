import numpy as np
import time

import frame
from serial_comm import SerialComm
from utils import power_to_motor_payload, reset_STM


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
            # Add raise exception here at some point
            print("Wrong array size in motor command")
            return

        payload = []
        for p in msg:
            value = power_to_motor_payload(p)
            payload.append(value)

        f = frame.motors(payload)
        status = self.comm.proccess_command(f)

        if not status or not status == " OK \r\n":
            # Add raise exception here at some point
            print("Did not receive a valid response after a motor command")

    def send_motor_command(self, FrontLeft, FrontRight, RearLeft, RearRight):
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
