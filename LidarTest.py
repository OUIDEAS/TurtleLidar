import numpy as np
from rplidar import RPLidar, RPLidarException
import time

class FinishScan(Exception):
    """Exception to end the for loop"""    


PortName = '/dev/ttyUSB0'
path = 'test.txt'

lidar = RPLidar(PortName)
outfile = open(path, 'w')

t1 = time.time()
tries = 100

for i in range(tries):
    try:
        for measurment in lidar.iter_measurments():
            line = '\t'.join(str(v) for v in measurment)
            outfile.write(line + '\n')
            if time.time() - t1 > 5:
                raise FinishScan("Scan Complete")
    except RPLidarException as e:
        print("Retrying due to error:", e)
        continue
    except FinishScan as e:
        print(e)
        break
    except KeyboardInterrupt:
        print("Keyboard Interrupt detected")
        break
    else:
        break
outfile.close()
lidar.stop()
lidar.stop_motor()
lidar.disconnect()
