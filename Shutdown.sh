#!/bin/bash
# Bash script to kill TurtleMain.py and Webstreaming.py

kill $(pgrep -f 'TurtleMain.py')
kill $(pgrep -f 'webstreaming.py')

echo "Python Scripts Killed"