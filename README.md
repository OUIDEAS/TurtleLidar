# Turtle Rover Lidar Pipe Scanner

Repository for Turtle Rover pipe scanning robot with lidar gimbal
 
* [TurtleMain.py](TurtleMain.py) is the main script where functions are called from. Commands for the robot come into this script from the flask web server through pyzmq publishers and subscribers.
* [TurtleDriverClass.py](TurtleDriverClass.py) is the main class where functions for the turtle rover and lidar gimbal are found. Functions include handling motor commands for moving the rover and, zeroing the lidar within the pipe, and scanning the pipe with the lidar. 
* [frame.py](frame.py) is a script containing functions from [turtle rover](https://github.com/TurtleRover/tr_ros/tree/master/tr_hat_bridge) that formats command messages to then send to the Turtle's shield.
* [serial_comm.py](serial_comm.py) is the script containing functions from [turtle rover](https://github.com/TurtleRover/tr_ros/tree/master/tr_hat_bridge) that sends commands to the Turtle's shield through serial communication. 
* [utils.py](utils.py) is the script containing functions from [turtle rover](https://github.com/TurtleRover/tr_ros/tree/master/tr_hat_bridge) containting misc static functions for [TurtleDriverClass](TurtleDriverClass.py) functions.

##### Code Diagram:
![alt_text](docs/Structure.PNG "Code Structure")
