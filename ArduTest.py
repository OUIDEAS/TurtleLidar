# from TurtleLidarDB import TurtleLidarDB
import serial
import re
import bz2
import pickle

ser = serial.Serial('COM10', 115200)


while True:
    read_serial = ser.readline()
    # s[0] = str(int(ser.readline(), 16))
    # print(s[0])
    data = read_serial.decode('utf-8')
    # print(data)
    data = re.sub(r'[()]', '', data)
    data = data.split(", ")
    if data[0] == "data":
        euler = (float(data[1]), float(data[2]), float(data[3]))
        gyro = (float(data[4]), float(data[5]), float(data[6]))
        acc = (float(data[7]), float(data[8]), float(data[9]))
        mag = (float(data[10]), float(data[11]), float(data[12]))
        enc = float(data[13])
        t = float(data[14])

        # print(euler, gyro, acc, mag, enc, t)
        data = (euler, gyro, acc, mag)
        print(data)

        pdata = pickle.dumps(data)
        print(pdata)

        bdata = bz2.compress(pdata)
        print(bdata)

        pdatas = bz2.decompress(bdata)
        datas = pickle.loads(pdatas)