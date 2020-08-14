import board
import busio
import time
import rotaryio
import adafruit_bno055

i2c = busio.I2C(board.SCL, board.SDA)
sensor = adafruit_bno055.BNO055_I2C(i2c)

encoder = rotaryio.IncrementalEncoder(board.D10, board.D9)
encoder2 = rotaryio.IncrementalEncoder(board.D11,board.D12)
encoder3 = rotaryio.IncrementalEncoder(board.A2, board.A3)
encoder4 = rotaryio.IncrementalEncoder(board.D3, board.D4)

while True:
    position = (encoder.position, encoder2.position, encoder3.position, encoder4.position)

    print("data","{}".format(sensor.euler), "{}".format(sensor.gyro), "{}".format(sensor.acceleration), "{}".format(sensor.magnetic), position, time.monotonic(), sep = ', ')
    time.sleep(.05)