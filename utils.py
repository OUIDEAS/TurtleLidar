import struct
import RPi.GPIO as GPIO
from time import sleep
from circle_fit import least_squares_circle
import numpy as np
from ellipse import LsqEllipse


def clamp(value, mn, mx):
    return max(min(value, mx), mn)


def power_to_motor_payload(power):
    p = clamp(power, -1.0, 1.0)
    value = int(round(p * 0x7F))
    if value < 0:
        value = -value + 0x7F
    return value


def servo_angle_to_duty(angle, min_angle, max_angle, min_duty, max_duty):
    angle = clamp(angle, min_angle, max_angle)
    value = float(angle - min_angle) / float(max_angle - min_angle)
    duty = min_duty + int(value * float(max_duty - min_duty))
    return struct.pack(">H", duty)


def reset_STM():
    try:
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(18, GPIO.OUT)
        GPIO.output(18, GPIO.LOW)
        sleep(0.5)
        GPIO.cleanup()
    except RuntimeError:
        # rospy.logwarn("Could not reset STM on Turtle Hat. No access to GPIO pins. "
        #               "Try running as root!")
        print("Could not reset STM on Turtle Hat. No access to GPIO pins. "
              "Try running as root!")


def estimateError(coord):
    # R_expected = 12
    # circle = least_squares_circle(coord)
    # x = coord[:, 0]
    # y = coord[:, 0]
    # x = x - circle[0]
    # y = y - circle[1]
    # r = np.sqrt(np.square(x)+np.square(y))
    # # remove outliers at some point
    # error = R_expected - r
    # meanError = np.mean(error)

    reg = LsqEllipse().fit(coord)
    center, width, height, phi = reg.as_parameters()
    hw = height/width
    meanError = abs(hw - 1)

    return meanError
