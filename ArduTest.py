import serial
import re

ser = serial.Serial('COM8', 115200)

while True:
    read_serial = ser.readline()
    # s[0] = str(int(ser.readline(), 16))
    # print(s[0])
    data = read_serial.decode('utf-8')
    data = re.sub(r'[()]', '', data)
    data = data.split(", ")
    if data[0] == "data":
        gyro = (float(data[1]), float(data[2]), float(data[3]))
        enc = float(data[4])
        t = float(data[5])

