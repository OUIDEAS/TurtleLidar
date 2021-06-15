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
import sys
from TurtleLidarDB import TurtleLidarDB, printLidarStatus, DebugPrint, create_csv_zip_bytes, clear_db_by_items, delete_db_by_items, deleteplot_db_by_items
import json
import LidarPlot
import io
import os
import bjoern

# initialize the output frame and a lock used to ensure thread-safe
# exchanges of the output frames (useful for multiple browsers/tabs
# are viewing tthe stream)
# outputFrame = None
SendFrame = None
lock = threading.Lock()

# initialize a flask object
app = Flask(__name__)

# initialize the video stream and allow the camera sensor to
# warmup
# vs = VideoStream(src=0).start()
#time.sleep(2.0)

# ZMQ PubSub
host = "127.0.0.1"
port = "5001"

context = zmq.Context()
# Sub Socket
pub = context.socket(zmq.PUB)

pub.connect(f"tcp://{host}:{port}")
time.sleep(.1)
#ZMQ
#with TurtleLidarDB() as db:
#	displayEntries = db.create_debug_table()

print("Turtle Web server started...")
DebugPrint("Turtle Web server ready...")

@app.route("/")
def index():
	# return the rendered template
	DebugPrint("Flask: index requested")
	return render_template("index.html")

@app.route("/sensor-data")
def sensorData():
	displayEntries = []
	with TurtleLidarDB() as db:
		displayEntries = db.get_all_lidar_data()

	# return the rendered template
	return render_template("table.html", displayEntries=displayEntries)

@app.route('/clearplots', methods=['POST'])
def deleteplot_item():
	jsondata = request.get_json(silent=True)
	#print(jsondata)
	if(jsondata is None):
		DebugPrint("Clear plot: Missing selected items in json form")
		return "error"

	idlist = jsondata['selitems']
	DebugPrint("web wants to delete plots")
	for id in idlist:
		DebugPrint(str(id))

	deleteplot_db_by_items(idlist)

	return Response(status=200)

@app.route('/resetdata', methods=['POST'])
def resetdata_item():
	jsondata = request.get_json(silent=True)
	#print(jsondata)
	if(jsondata is None):
		DebugPrint("Missing selected items in json form")
		return "error"

	idlist = jsondata['selitems']
	DebugPrint("web wants to remove items")
	for id in idlist:
		DebugPrint(str(id))

	delete_db_by_items(idlist)
	DebugPrint("DebugLog cleared")

	return Response(status=200)

@app.route('/cleardata', methods=['POST'])
def cleardata_item ():
	jsondata = request.get_json(silent=True)
	#print(jsondata)
	if(jsondata is None):
		DebugPrint("Missing selected items in json form")
		return "error"

	idlist = jsondata['selitems']
	DebugPrint("web wants to remove items")
	for id in idlist:
		DebugPrint(str(id))

	clear_db_by_items(idlist)

	return Response(status=200)


@app.route('/database', methods=['POST'])
def downloadFile():
	jsondata = request.get_json(silent=True)
	#print(jsondata)
	if(jsondata is None):
		DebugPrint("Missing selected items in json form")
		return "error"

	idlist = jsondata['selitems']
	DebugPrint("web wants items")
	for id in idlist:
		DebugPrint(str(id))
	memory_file = create_csv_zip_bytes(idlist=idlist)
	return send_file(memory_file, attachment_filename='Data.zip', as_attachment=True)
	# path = 'LidarData.db'
	# return send_file(path, as_attachment=True)

@app.route("/debug")
def debug():
	# return the rendered template
	DebugPrint("Flask: debug requested")
	return render_template("debug.html")

@app.route("/camerapic/<int:dataid>")
def getcamerapic(dataid):
	print("requested image from data %s" % dataid, file=sys.stdout)
	with TurtleLidarDB() as db:
		ldata = db.get_lidar_data_byID(dataid)
	simage = ldata["image"]
	return send_file(io.BytesIO(simage),
					attachment_filename = 'logo.png',
					mimetype='image/png')

@app.route("/polarplot/<int:dataid>")
def getdataplotpic(dataid):
	print("requested plot from data %s" % dataid, file=sys.stderr)
	pimage = None

	with TurtleLidarDB() as db:
		pimage, lsq_data = db.get_polarplot_by_lidarID(dataid)

	if(pimage is None):
		data = None
		with TurtleLidarDB() as db:
			data = db.get_lidar_data_byID(dataid)
		if(not data):
			return "error getting data"
		pimage, lsq_data = LidarPlot.GenerateDataPolarPlotByData(data)
		if(pimage):
			with TurtleLidarDB() as db:
				db.insert_polarplot(pimage, dataid, lsq_data)
	#image_binary = LidarPlot.GiveTestImg()
	# response = make_response(image_binary)
	# response.headers.set('Content-Type', 'image/png')
	# response.headers.set(
	# 	'Content-Disposition', 'attachment', filename='plot.png')
	# return response
	return send_file(pimage,
					 attachment_filename='logo.png',
					 mimetype='image/png')
	#return 'data %s' % dataid


@app.route("/plot")
def plot():
	image_binary = LidarPlot.GiveTestImg()
	# response = make_response(image_binary)
	# response.headers.set('Content-Type', 'image/png')
	# response.headers.set(
	# 	'Content-Disposition', 'attachment', filename='plot.png')
	# return response
	return send_file(image_binary,
					 attachment_filename='logo.png',
					 mimetype='image/png')

def gen_frames():
	global lock, SendFrame
	camera = cv2.VideoCapture(0)
	max_temp_exceed = False
	while True:
		success, frame = camera.read()  # read the camera frame
		if not success:
			break
		else:
			piTemp = getPiTemp()

			if((piTemp and piTemp < 60.0) and max_temp_exceed):
				max_temp_exceed = False
				DebugPrint("GenFrame: Temp lowered, camera processing back " + str(piTemp))

			if ((piTemp and piTemp > 70.0) or max_temp_exceed):
				DebugPrint("GenFrame: CPU is too HOT! " + str(piTemp))
				time.sleep(1)
				SITE_ROOT = os.path.realpath(os.path.dirname(__file__))
				img_loc = os.path.join(SITE_ROOT, "static/img", "TooHot.png")
				frame = cv2.imread(img_loc)
				max_temp_exceed = True
				#stop motors?
				#continue
			else:
				#DebugPrint("GenFrame: CPU OK " + str(piTemp))
				frame = imutils.resize(frame, width=480)

			# grab the current timestamp and draw it on the frame
			timestamp = datetime.datetime.now()
			cv2.putText(frame, timestamp.strftime(
				"%A %d %B %Y %I:%M:%S%p"), (10, frame.shape[0] - 10),
						cv2.FONT_HERSHEY_SIMPLEX, 0.55, (0, 255, 0), 1)

			ret, buffer = cv2.imencode('.jpg', frame)


			frame = buffer.tobytes()
			with lock:
				SendFrame = frame
			yield (b'--frame\r\n'
				   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')  # concat frame one by one and show result

@app.route('/video_feed')
def video_feed():
	return Response(gen_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

def getPiTemp():
	try:
		tFile = open('/sys/class/thermal/thermal_zone0/temp')
		temp = float(tFile.read())
		tempC = temp / 1000.0
	except:
		tempC = None

	#print(tempC)
	return tempC

@app.route("/scan_status")
def scan_status():
	# printLidarStatus()
	# printLidarStatus("hello0")
	# printLidarStatus(msg="hello1")
	# printLidarStatus(battery_voltage=1200.25)
	# printLidarStatus(msg="hello2", battery_voltage=1200.25)
	# printLidarStatus("hello4", battery_voltage=1200.25)
	# printLidarStatus("hello5", 1200.25)
	# printLidarStatus(64) #do not use, will update string message!
	tempC = getPiTemp()
	if(tempC is None):
		tempC = "N/A"
	DebugPrint("Check: CPU Temp " + str(tempC))

	message = "Error with LidarStatus database"
	fbattery_voltage = -1
	try:
		with TurtleLidarDB() as db:
			message, fbattery_voltage = db.get_lidar_status()
	except Exception as e:
		print(e)
	#print(message)
	return jsonify(
		status_text=message,
		battery_voltage=fbattery_voltage,
		cpu_temp=tempC
	)

@app.route("/debug_feed", methods=['GET', 'POST'])
def debug_feed():

	if(request.method != 'GET'):
		try:
			#print(request.method)
			jsondata = request.get_json()
			#print(jsondata)
			lastID = jsondata['lastID']
			# lastID = request.form['lastID']
		except:
			#print("debug feed id parse error")
			return "ERROR", 400
	else:
		lastID = -1

	data = None
	with TurtleLidarDB() as db:
		if(lastID == -1):
			data = db.get_last_n_debug_msg(50)
			#print("debug: new sending #"+str(len(data)))
			data.insert(0, {"status": "new"})
		elif(lastID >= 0):
			data = db.get_new_debug_msg_from_ID(lastID)
			#print("debug: sending #"+str(len(data)))
			if(len(data) <= 0):
				data = []
				data.insert(0, {"status": "nothingnew"})
		data = json.dumps(data)
	#print("more debug...")
	# DebugPrint("Hi " + str(time.time()))
	# DebugPrint("Testing " + str(time.time()))
	# DebugPrint("Bake " + str(time.time()))
	# DebugPrint("Foo " + str(time.time()))
	# DebugPrint("Bye " + str(time.time()))
	return data

# @app.route("/video_feed")
# def video_feed_old():
# 	# return the response generated along with the specific media
# 	return Response(generate(),
# 		mimetype = "multipart/x-mixed-replace; boundary=frame")

# a-button api endpoint
@app.route('/api/scan', methods=['POST'])
def scan_endpoint():
	global SendFrame, lock

	# if not request.json:
	#     print(request.__dict__)
	#     return None, 400
	print(request.method)
	print(request.form)
	#print("STARTING SCAN...")
	DebugPrint("Flask: STARTING SCAN...")

	# print(request.json)
	# print(request.get_json(force=True))
	# response = {
	# 	'json you sent': request.get_json(force=True)
	# 	# 'json you sent': request.json
	# }

	# Grab Image to send to other script
	# if SendFrame != None:
	with lock:  # Unsure if this is needed?
		if SendFrame is not None:
			Image = SendFrame
			#Image = cv2.imencode('.jpg', Image)[1]
			data_encode = np.array(Image)
			str_encode = data_encode.tostring()
		else:
			str_encode = None
	# else:
	# 	Image = "null"
	# 	print("No Image...")

	pktName = "scan"
	pkt = ("True", str_encode, time.time())
	pub.send_string(pktName, flags=zmq.SNDMORE)
	pub.send_pyobj(pkt)

	return 'Scanning', 200

# a-button api endpoint
# Joystick api endpoint???
@app.route('/api/drive', methods=['POST'])
def drive_endpoint():
	# if not request.json:
	#     print(request.__dict__)
	#     return None, 400
	# print(request.method)
	# print(request.form)
	#print(request.form['lr'])  # Left Right
	#print(request.form['ud'])  # Up Down
	# print(request.json)
	# print(request.get_json(force=True))
	# response = {
	# 	'json you sent': request.get_json(force=True)
	# 	# 'json you sent': request.json
	# }

	# ZMQ PubSub
	lr = request.form['lr']
	ud = request.form['ud']
	pkt = [ud, lr, time.time()]
	pktName = "motors"
	pub.send_string(pktName, flags=zmq.SNDMORE)
	pub.send_pyobj(pkt)

	return jsonify({'lr': request.form['lr'], 'ud':request.form['ud']}), 200


# check to see if this is the main thread of execution
if __name__ == '__main__':
	# # construct the argument parser and parse command line arguments
	# ap = argparse.ArgumentParser()
	#
	# ap.add_argument("-f", "--frame-count", type=int, default=32,
	# 	help="# of frames used to construct the background model")
	# args = vars(ap.parse_args())
	#
	# # start a thread that will perform motion detection
	# t = threading.Thread(target=video_stream, args=(
	# 	args["frame_count"],))
	# t.daemon = True
	# t.start()
	# start the flask app
	# app.run(host=args["ip"], port=args["port"], debug=True,
	# 	threaded=True, use_reloader=False)

	# app.run(host="0.0.0.0", port="5555", debug=False,
	# 		threaded=True, use_reloader=False)

	bjoern.run(app, "0.0.0.0", 5555)

# release the video stream pointer
#vs.stop()
