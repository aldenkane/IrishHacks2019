import flask
from flask import Response
import cv2
import io
from google.cloud import vision
from google.cloud.vision import types
import threading
import json
from collections import defaultdict

# ocr_GoogleVision.py
# IrishHacks2019
# Alden Kane, Phil Vlandis, & AJ Jimenez code for smart plastic recycling
#	OCR Code is from SpringML's "Streaming OCR with Google Vision's API and OpenCV tutorial." Modified to fit our purposes for this hackathon

# Set environment variable at beginning of session
# export GOOGLE_APPLICATION_CREDENTIALS=key.json

recycle_info = defaultdict(dict)

recycle_info[0] = {'code': 0, 'name': 'n/a', 'type': 'n/a', 'rec': 'n/a'}
recycle_info[1] = {'code': 1, 'name': 'PETE', 'type': 'Polyethylene Terephthalate', 'rec': 'Yes'}
recycle_info[2] = {'code': 2, 'name': 'HDPE', 'type': 'High Density Polyethylene', 'rec': 'Yes'}
recycle_info[3] = {'code': 3, 'name': 'PVC', 'type': 'Polyvinyl Chloride', 'rec': 'No'}
recycle_info[4] = {'code': 4, 'name': 'LDPE', 'type': 'Low Density Polyethylene', 'rec': 'Sometimes - Contact Local Recycling'}
recycle_info[5] = {'code': 5, 'name': 'PP', 'type': 'Polypropylene', 'rec': 'Sometimes - Contact Local Recycling'}
recycle_info[6] = {'code': 6, 'name': 'PS', 'type': 'Polystyrene', 'rec': 'Sometimes - Contact Local Recycling'}
recycle_info[7] = {'code': 7, 'name': 'OTHER', 'type': 'Misc Plastics', 'rec': 'Sometimes - Contact Local Recycling'}

client = vision.ImageAnnotatorClient()

# Clear text file
open('detected_Num.txt', 'w').close()

APP = flask.Flask(__name__)
# video shown on screen
video = cv2.VideoCapture(0)

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
        string += ' ' + text.description
    return string

def number_recognition():
    # Capture frame-by-frame
    while True:
        ret, frame = cap.read()
        file = 'current_Frame.png'
        cv2.imwrite(file, frame)

        # print OCR text
        print(detect_text(file))
        text_D = detect_text(file)
        middle_file = open('detected_Num.txt', 'w')

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
            rec_Num = 0
        # "Resin Identification Code (RIC) not detected"

        print(rec_Num)
        middle_file.write(str(rec_Num))

    # Release Capture at End

    cap.release()
    cv2.destroyAllWindows()


def gen():
    while True:
        rval, frame_top = video.read()
        cv2.imwrite('t.jpg', frame_top)

        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + open('t.jpg', 'rb').read() + b'\r\n')


@APP.route("/get_value", methods=['GET'])
def get_value():
    middle_file = open("detected_Num.txt", "r")
    string = middle_file.readline()
    return json.dumps({"code": string, 'name':recycle_info[int(string)]['name'], 'type':recycle_info[int(string)]['type'],'can':recycle_info[int(string)]['rec']})


@APP.route("/video_feed")
def video_feed():
    return Response(gen(), mimetype="multipart/x-mixed-replace; boundary=frame")


if __name__ == '__main__':
    thread = threading.Thread(target=number_recognition)
    thread.start()
    APP.debug = True
    APP.run(host='127.0.0.1', threaded=True)

# vs.stop()
