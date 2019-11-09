import flask
#from pyimagesearch.motion_detection import SingleMotionDetector
from flask import Response
from flask import Flask
from flask import render_template
import cv2


APP = flask.Flask(__name__)
video=cv2.VideoCapture(0)

@APP.route('/')
def index():
	return flask.render_template('index.html')

def gen():
	while True:
		rval,frame=video.read()
		cv2.imwrite('t.jpg',frame)
		yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + open('t.jpg', 'rb').read() + b'\r\n')

@APP.route("/video_feed")
def video_feed():
	return Response(gen(),mimetype="multipart/x-mixed-replace; boundary=frame")





if __name__ =='__main__':
	
	APP.debug=True
	APP.run(host='127.0.0.1',threaded=True)

#vs.stop()
