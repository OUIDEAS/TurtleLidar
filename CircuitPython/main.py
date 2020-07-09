import board
import busio
import time
import rotaryio
import adafruit_bno055

i2c = busio.I2C(board.SCL, board.SDA)
sensor = adafruit_bno055.BNO055_I2C(i2c)

encoder = rotaryio.IncrementalEncoder(board.D10, board.D9)

while True:
    position = encoder.position

    #print("Accelerometer (m/s^2): {}".format(sensor.acceleration))
    #print("Magnetometer (microteslas): {}".format(sensor.magnetic))
    #print("Gyroscope (rad/sec): {}".format(sensor.gyro))
    #print("Euler angle: {}".format(sensor.euler))

    print("data","{}".format(sensor.euler), "{}".format(sensor.gyro), "{}".format(sensor.acceleration), "{}".format(sensor.magnetic), position, time.monotonic(), sep = ', ')
    #time.sleep(.05)