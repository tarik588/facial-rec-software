from flask import Flask, render_template, Response, request, redirect, url_for, flash
import os
import cv2
import json
import numpy as np
import face_recognition
import threading

app = Flask(__name__, template_folder="templates")
camera = cv2.VideoCapture(0)

# Global variable to store the latest frame from the camera
latest_frame = None

def capture_frames():
    global latest_frame
    while True:
        ret, frame = camera.read()
        if ret:
            latest_frame = frame

def generate_video_feed():
    global latest_frame
    while True:
        ret, frame = camera.read()  # Read frame from the global camera object
        if ret:
            latest_frame = frame  # Update the latest frame

            # Detect face locations in the frame
            face_locations = face_recognition.face_locations(frame)

            if face_locations:
                # Convert frame to RGB format for face_recognition
                rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                # Encode the face(s) in the frame
                face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)
                encodings_list = [encoding.tolist() for encoding in face_encodings]
                encodings_json = json.dumps(encodings_list)
                yield encodings_json  # Yield the face encodings as JSON
            else:
                yield json.dumps([])  # Yield an empty list if no faces are detected
        else:
            continue 
@app.route('/')
def home():
    return render_template('home.html')

@app.route('/')
def video_feed():
    return Response(generate_video_feed(),mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == '__main__':
    capture_thread = threading.Thread(target=capture_frames)
    capture_thread.daemon = True
    capture_thread.start()
    
    app.run(debug=True, port=5000, use_reloader=False, threaded=True)