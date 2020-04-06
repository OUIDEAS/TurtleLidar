from rplidar import RPLidar
import numpy as np

Port = '/dev/ttyUSB0'
NumberOfScans = 5
lidar = RPLidar(Port)


outfile = open('debug.txt', 'w')
i = 0

try:
    for measurment in lidar.iter_measurments():
        for data in measurment:
            ScanCheck = data[0]
            if ScanCheck == True:
                i += 1
            line = '\t'.join(str(measurment))
            outfile.write(line + '\n')
        if i > NumberOfScans:
            break

except Exception as e:
    print("Stopping due to error:", e)

outfile.close()
lidar.stop()
lidar.stop_motor()
lidar.disconnect()