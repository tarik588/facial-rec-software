from flask import Flask, render_template, Response, request, redirect, url_for, flash
import os
import cv2
import json
import numpy as np
import face_recognition
import threading
import sqlite3 as sl
from sqlite3 import Error
import secrets
import string

def generate_secret_key(length=32):
    characters = string.ascii_letters + string.digits + string.punctuation
    return ''.join(secrets.choice(characters) for _ in range(length))

# Generate a secret key
secret_key = generate_secret_key()

app = Flask(__name__, template_folder="templates")
camera = cv2.VideoCapture(0)
app.secret_key = secret_key 

# Function to create Users table in SQLite database
def create_users_table():
    try:
        # Connect to SQLite database (or create if not exists)
        conn = sl.connect('sqface.db')
        cursor = conn.cursor()

        # SQL code to create Users table
        create_table_sql = '''
        CREATE TABLE IF NOT EXISTS Users (
            user_id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            email TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        '''

        # Execute SQL code
        cursor.execute(create_table_sql)

        # Commit changes and close connection
        conn.commit()
        conn.close()
    except Error as e:
        print("Error:", e)

# Create Users table when the application starts
create_users_table()

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

        if ret:
            image_path = "static/imagestore/captured_image.jpg"
            cv2.imwrite(image_path, frame)
            print("Image saved successfully!")
            return {'status': 'success', 'message': 'Image saved successfully'}
        else:
            print("Failed to capture image.")
            return {'status': 'error', 'message': 'Failed to capture image'}

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/video_feed')
def video_feed():
    return Response(generate_video_feed(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route("/signup", methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        confirm_password = request.form['confirm_password']

        # Validate passwords match
        if password != confirm_password:
            flash('Passwords do not match', 'error')
            return redirect(url_for('signup'))

        try:
            # Connect to SQLite database
            conn = sl.connect('sqface.db')
            cursor = conn.cursor()

            # Insert user into Users table
            cursor.execute('INSERT INTO Users (email, password) VALUES (?, ?)', (email, password))
            conn.commit()
            conn.close()

            flash('User registered successfully', 'success')
            return redirect(url_for('home'))

        except Error as e:
            print("Error:", e)
            flash('Error registering user', 'error')
            return redirect(url_for('signup'))

    return render_template('signup.html')

if __name__ == '__main__':
    capture_thread = threading.Thread(target=generate_video_feed)
    capture_thread.daemon = True
    capture_thread.start()
    
    app.run(debug=True, port=5000, use_reloader=False, threaded=True)
