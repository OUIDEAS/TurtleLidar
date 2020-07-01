from TurtleLidarDB import TurtleLidarDB
import serial
import re
import time

ser = serial.Serial('COM8', 115200)

with TurtleLidarDB() as db:
    db.create_gyro_table()

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

        with TurtleLidarDB() as db:
            db.create_gyro_data_input(time.time(), gyro[0], gyro[1], gyro[2], enc)

