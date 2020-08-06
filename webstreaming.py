# USAGE
# python webstreaming.py --ip 0.0.0.0 --port 8000

# import the necessary packages
# from pyimagesearch.motion_detection import SingleMotionDetector
from imutils.video import VideoStream
from flask import Response, Flask, render_template, request, jsonify, send_file
import numpy as np
import threading
import argparse
import datetime
import imutils
import time
import cv2
import zmq
from TurtleLidarDB import TurtleLidarDB

# initialize the output frame and a lock used to ensure thread-safe
# exchanges of the output frames (useful for multiple browsers/tabs
# are viewing tthe stream)
outputFrame = None
SendFrame = None
lock = threading.Lock()

# initialize a flask object
app = Flask(__name__)

# initialize the video stream and allow the camera sensor to
# warmup
#vs = VideoStream(usePiCamera=1).start()
vs = VideoStream(src=0).start()
time.sleep(2.0)

# ZMQ PubSub
host = "127.0.0.1"
port = "5001"

context = zmq.Context()
# Sub Socket
pub = context.socket(zmq.PUB)

pub.connect(f"tcp://{host}:{port}")
time.sleep(.1)
#ZMQ

@app.route("/")
def index():
	# return the rendered template
	return render_template("index.html")

@app.route("/sensor-data")
def sensorData():
	displayEntries = []
	with TurtleLidarDB() as db:
		displayEntries = db.get_table_data()

	# return the rendered template
	return render_template("table.html", displayEntries=displayEntries)

@app.route('/database')
def downloadFile ():
	with TurtleLidarDB() as db:
		db.create_csv()
	path = 'Data.zip'
	return send_file(path, as_attachment=True)

def video_stream(frameCount):
	# grab global references to the video stream, output frame, and
	# lock variables
	global vs, outputFrame, lock, SendFrame

	# # initialize the motion detector and the total number of frames
	# # read thus far
	# md = SingleMotionDetector(accumWeight=0.1)
	# total = 0

	# loop over frames from the video stream
	while True:
		# read the next frame from the video stream, resize it
		frame = vs.read()
		frame = imutils.resize(frame, width=600)

		# grab the current timestamp and draw it on the frame
		timestamp = datetime.datetime.now()
		cv2.putText(frame, timestamp.strftime(
			"%A %d %B %Y %I:%M:%S%p"), (10, frame.shape[0] - 10),
			cv2.FONT_HERSHEY_SIMPLEX, 0.55, (0, 255, 0), 1)
			# cv2.FONT_HERSHEY_SIMPLEX, 0.35, (0, 255, 0), 1)

		# lock
		with lock:
			outputFrame = frame.copy()
			SendFrame = frame
		
def generate():
	# grab global references to the output frame and lock variables
	global outputFrame, lock

	# loop over frames from the output stream
	while True:
		# wait until the lock is acquired
		with lock:
			# check if the output frame is available, otherwise skip
			# the iteration of the loop
			if outputFrame is None:
				continue

			# encode the frame in JPEG format
			(flag, encodedImage) = cv2.imencode(".jpg", outputFrame)

			# ensure the frame was successfully encoded
			if not flag:
				continue

		# yield the output frame in the byte format
		yield(b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' + 
			bytearray(encodedImage) + b'\r\n')

@app.route("/video_feed")
def video_feed():
	# return the response generated along with the specific media
	return Response(generate(),
		mimetype = "multipart/x-mixed-replace; boundary=frame")

# a-button api endpoint
@app.route('/api/scan', methods=['POST'])
def scan_endpoint():
	global SendFrame, lock

	# if not request.json:
	#     print(request.__dict__)
	#     return None, 400
	print(request.method)
	print(request.form)
	print(request.form['hello'])
	print(request.form['world'])
	# print(request.json)
	# print(request.get_json(force=True))
	# response = {
	# 	'json you sent': request.get_json(force=True)
	# 	# 'json you sent': request.json
	# }

	# Grab Image to send to other script
	# if SendFrame != None:
	with lock:  # Unsure if this is needed?
		if SendFrame != None:
			Image = SendFrame
			Image = cv2.imencode('.png', Image)[1]
			data_encode = np.array(Image)
			str_encode = data_encode.tostring()
		else:
			str_encode = None
	# else:
	# 	Image = "null"
	# 	print("No Image...")

	pktName = "scan"
	pkt = ("True", str_encode)
	pub.send_string(pktName, flags=zmq.SNDMORE)
	pub.send_pyobj(pkt)

	return 'hi', 200

# a-button api endpoint
# Joystick api endpoint???
@app.route('/api/drive', methods=['POST'])
def drive_endpoint():
	# if not request.json:
	#     print(request.__dict__)
	#     return None, 400
	print(request.method)
	print(request.form)
	print(request.form['lr'])  # Left Right
	print(request.form['ud'])  # Up Down
	# print(request.json)
	# print(request.get_json(force=True))
	# response = {
	# 	'json you sent': request.get_json(force=True)
	# 	# 'json you sent': request.json
	# }

	# ZMQ PubSub
	lr = request.form['lr']
	ud = request.form['ud']
	pkt = [ud, lr]
	pktName = "motors"
	pub.send_string(pktName, flags=zmq.SNDMORE)
	pub.send_pyobj(pkt)

	return jsonify({'lr': request.form['lr'], 'ud':request.form['ud']}), 200


# check to see if this is the main thread of execution
if __name__ == '__main__':
	# construct the argument parser and parse command line arguments
	ap = argparse.ArgumentParser()
	# ap.add_argument("-i", "--ip", type=str, required=True,
	# 	help="ip address of the device")
	# ap.add_argument("-o", "--port", type=int, required=True,
	# 	help="ephemeral port number of the server (1024 to 65535)")
	ap.add_argument("-f", "--frame-count", type=int, default=32,
		help="# of frames used to construct the background model")
	args = vars(ap.parse_args())

	# start a thread that will perform motion detection
	t = threading.Thread(target=video_stream, args=(
		args["frame_count"],))
	t.daemon = True
	t.start()

	# start the flask app
	# app.run(host=args["ip"], port=args["port"], debug=True,
	# 	threaded=True, use_reloader=False)

	app.run(host="0.0.0.0", port="5555", debug=True,
			threaded=True, use_reloader=False)
# release the video stream pointer
vs.stop()
