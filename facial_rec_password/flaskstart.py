from flask import Flask, render_template, Response, request, redirect, url_for, flash
import os
import cv2
import json
import numpy as np
import face_recognition
import threading

app = Flask(__name__, template_folder="templates")
camera = cv2.VideoCapture(0)

def signup_facecap():
    ret, frame = camera.read()
    if ret:
        image_path = "static/imagestore/captured_image.jpg"
        cv2.imwrite(image_path, frame)
        print("Image saved successfully!")
        return {'status': 'success', 'message': 'Image saved successfully'}
    else:
        print("Failed to capture image.")
        return {'status': 'error', 'message': 'Failed to capture image'}

def generate_video_feed():
    while True:
        ret, frame = camera.read()  
        if ret:
            ret, buffer = cv2.imencode('.jpg', frame)
            if not ret:
                continue
            
            frame_bytes = buffer.tobytes()
            
            face_locations = face_recognition.face_locations(frame)

            if face_locations:
                rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)
                encodings_list = [encoding.tolist() for encoding in face_encodings]
                encodings_json = json.dumps(encodings_list)

                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n' + encodings_json.encode() + b'\r\n')
            
            else:
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

@app.route("/signup", methods=['POST'])
def signup():
    if 'capture' in request.form and request.form['capture'] == 'true':
        response_data = signup_facecap()  # Call the function to capture and save the image
        return json.dumps(response_data)
    else:
        exit

if __name__ == '__main__':
    capture_thread = threading.Thread(target=generate_video_feed)
    capture_thread.daemon = True
    capture_thread.start()
    
    app.run(debug=True, port=5000, use_reloader=False, threaded=True)
