from TurtleDriverClass import TurtleDriver
import time

print("Turtle Rover Motor Test")
time.sleep(1)

td = TurtleDriver()
# td.spinTurtle()
print(td.battery_status())
td.initServo()
td.set_servo(3, -40)
for i in range(-20,20):
    td.set_servo(3, i*2)
    time.sleep(.2)
time.sleep(1)
td.initServo()

print("done")
