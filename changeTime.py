import io
from subprocess import call


def is_raspberrypi():
    try:
        with io.open('/sys/firmware/devicetree/base/model', 'r') as m:
            if 'raspberry pi' in m.read().lower(): return True
    except Exception:
        pass
    return False


def changeTime(date, time):
    pi = is_raspberrypi()
    timeCMD = "date --set '" + str(date) + ' ' + str(time) + "'"
    if pi:

        try:
            call(timeCMD, shell=True)
        except Exception as e:
            print(e)
        print('Time Changed to ', date, '', time)
    else:
        print("Testing with windows")
        print(timeCMD)


if __name__ == "__main__":
    pi = is_raspberrypi()
    print(pi)