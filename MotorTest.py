from TurtleDriverClass import TurtleDriver
import time

print("Turtle Rover Motor Test")
time.sleep(1)

td = TurtleDriver()
# td.spinTurtle()
print(td.battery_status())
print("done")
