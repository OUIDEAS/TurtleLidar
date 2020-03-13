FIRMWARE_VER_PREFIX = 0x01
MOTORS_PREFIX = 0x10
SERVO_PREFIX = 0x80
BATTERY_PREFIX = 0x31

POSTFIX = [0x0D, 0x0A]


def firmware_ver():
    command = bytearray()
    command.append(FIRMWARE_VER_PREFIX)
    command.extend([0x00, 0x00, 0x00, 0x00])
    command.extend(POSTFIX)
    return command


def motors(payload):
    command = bytearray()
    command.append(MOTORS_PREFIX)
    command.extend(payload)
    command.extend(POSTFIX)
    return command


def servo(channel, duty):
    command = bytearray()
    command.append(SERVO_PREFIX + channel)
    command.extend(duty)
    command.extend([0x00, 0x00])
    command.extend(POSTFIX)
    return command


def battery():
    command = bytearray()
    command.append(BATTERY_PREFIX)
    command.extend([0x00, 0x00, 0x00, 0x00])
    command.extend(POSTFIX)
    return command
