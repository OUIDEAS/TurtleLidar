import board
import busio
import time
import rotaryio
import adafruit_bno055

i2c = busio.I2C(board.SCL, board.SDA)
sensor = adafruit_bno055.BNO055_I2C(i2c)

uart = busio.UART(board.TX, board.RX, baudrate=115200)

encoder = rotaryio.IncrementalEncoder(board.D9, board.D10)
encoder2 = rotaryio.IncrementalEncoder(board.D11,board.D12)
encoder3 = rotaryio.IncrementalEncoder(board.D5, board.D7)
encoder4 = rotaryio.IncrementalEncoder(board.D3, board.D4)
while True:
    position = (encoder.position, encoder2.position, encoder3.position, encoder4.position)

    #print("data","{}".format(sensor.euler), "{}".format(sensor.gyro), "{}".format(sensor.acceleration), "{}".format(sensor.magnetic), position, time.monotonic(), sep = ', ')
    output = "data, " + str(sensor.euler) + ", " + str(sensor.gyro) + ", " + str(sensor.acceleration) + ", " + str(sensor.magnetic) + ", " + str(position) + ", " + str(time.monotonic()) + ", /n"
    #output = "data, " + str(position) + ", " + str(time.monotonic())
    out = bytes(output, 'utf-8')

    uart.write(out)
    print(out)

    time.sleep(.01)