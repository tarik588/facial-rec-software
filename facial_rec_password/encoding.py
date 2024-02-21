import cv2
import face_recognition

def capture_and_encode_frame():
    cap = cv2.VideoCapture(0)

    ret, frame = cap.read()

    cv2.imwrite("temp_frame.jpg", frame)

    cap.release()

    loaded_frame = face_recognition.load_image_file("temp_frame.jpg")

    face_locations = face_recognition.face_locations(loaded_frame)

    face_encodings = face_recognition.face_encodings(loaded_frame, face_locations)

    if face_encodings:
        print("Face encoding(s) found:", face_encodings)
    else:
        print("No face encoding found.")

    import os
    os.remove("temp_frame.jpg")
    
capture_and_encode_frame()