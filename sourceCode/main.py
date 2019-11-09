import flask
#from pyimagesearch.motion_detection import SingleMotionDetector
from flask import Response
from flask import Flask
from flask import render_template
import cv2
import io
# Imports the Google Cloud client library
from google.cloud import vision
from google.cloud.vision import types

client = vision.ImageAnnotatorClient()

# Clear text file
open('detected_Num.txt', 'w').close()


# ocr_GoogleVision.py
# IrishHacks2019
# Alden Kane, Phil Vlandis, & AJ Jimenez code for smart plastic recycling
#	Author: Alden Kane
#	OCR Code is from SpringML's "Streaming OCR with Google Vision's API and OpenCV tutorial." Modified to fit our purposes for this hackathon

# Set environment variable at beginning of session
# export GOOGLE_APPLICATION_CREDENTIALS=key.json

APP = flask.Flask(__name__)
# video shown on screen
video=cv2.VideoCapture(0)

# background doing recognition
cap = cv2.VideoCapture(0)

@APP.route('/')
def index():
	return flask.render_template('index.html')

def detect_text(path):

	# Detect Text Using Google Cloud API
	with io.open(path, 'rb') as image_file:
		content = image_file.read()

	image = types.Image(content=content)
	response = client.text_detection(image=image)
	texts = response.text_annotations
	string = ''

	for text in texts:
		string+=' ' + text.description
	return string

def gen():
	while True:
		rval,frame_top=video.read()
		cv2.imwrite('t.jpg',frame_top)
		
		# Capture frame-by-frame
		ret, frame = cap.read()
		file = 'current_Frame.png'
		cv2.imwrite(file, frame)

		# print OCR text
		print(detect_text(file))
		text_D = detect_text(file)

		# Text Parsing to find recycling number
		if text_D.find("1") != -1:
			rec_Num = 1
		elif text_D.find("2") != -1:
			rec_Num = 2
		elif text_D.find("3") != -1:
			rec_Num = 3
		elif text_D.find("4") != -1:
			rec_Num = 4
		elif text_D.find("5") != -1:
			rec_Num = 5
		elif text_D.find("6") != -1:
			rec_Num = 6
		elif text_D.find("7") != -1:
			rec_Num = 7
		else:
			rec_Num = "Resin Identification Code (RIC) not detected"

		print(rec_Num)

		yield (b'--frame\r\n'
			   b'Content-Type: image/jpeg\r\n\r\n' + open('t.jpg', 'rb').read() + b'\r\n')

	# Release Capture at End
	cap.release()
	cv2.destroyAllWindows()



@APP.route("/video_feed")
def video_feed():
	return Response(gen(),mimetype="multipart/x-mixed-replace; boundary=frame")

		


if __name__ =='__main__':
	

	APP.debug=True
	APP.run(host='127.0.0.1',threaded=True)

#vs.stop()
