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

            
def generate_video_feed():
    global latest_frame
    while True:
        ret, frame = camera.read()  
        if ret:

            ret, buffer = cv2.imencode('.jpg', frame)
            if not ret:
                continue
            
            frame_bytes = buffer.tobytes()
            
            # Detect face locations in the frame
            face_locations = face_recognition.face_locations(frame)

            if face_locations:
                # Convert frame to RGB format for face_recognition
                rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)
                encodings_list = [encoding.tolist() for encoding in face_encodings]
                encodings_json = json.dumps(encodings_list)

                # Yield the face encodings along with the frame
                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n' + encodings_json.encode() + b'\r\n')
            
            else:
                # Yield only the frame if no faces are detected
                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
        else:
            continue

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/video_feed')
def video_feed():
    return Response(generate_video_feed(),mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == '__main__':
    #set up different thread for genererate_video_feed 
    capture_thread = threading.Thread(target=generate_video_feed)
    capture_thread.daemon = True
    capture_thread.start()
    
    app.run(debug=True, port=5000, use_reloader=False, threaded=True)