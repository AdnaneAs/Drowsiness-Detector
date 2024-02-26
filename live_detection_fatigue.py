import cv2
import dlib
from scipy.spatial import distance
import pygame
import numpy as np

def eye_aspect_ratio(eye):
    # calcul de la distance euclidienne entre les deux points verticaux
    A = distance.euclidean(eye[1], eye[5])
    B = distance.euclidean(eye[2], eye[4])
    # calcul de la distance euclidienne entre les deux points horizontaux
    C = distance.euclidean(eye[0], eye[3])
    # calcul du ratio des yeux
    ear = (A + B) / (2.0 * C)
    return ear


cap = cv2.VideoCapture(0)
face_detection = dlib.get_frontal_face_detector()
face_landmark = dlib.shape_predictor("shape_predictor_68_face_landmarks.dat")
counter = []
# Initialize pygame
pygame.init()

# Load the sound file
sound_file = "alert.wav"
pygame.mixer.music.load(sound_file)

# Set the volume (optional)
pygame.mixer.music.set_volume(1.0)

while True:
    ret, frame = cap.read()
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces = face_detection(gray)

    for face in faces:
        face_landmarks = face_landmark(gray, face)
        eye = []
        point_before = []
        for n in range(36, 48):
            x = face_landmarks.part(n).x
            y = face_landmarks.part(n).y
            cv2.circle(frame, (x, y), 2, (0, 255, 0), 1)
            eye.append((x, y))
        # Convert the list to a NumPy array
        eye_array = np.array(eye, dtype=np.int32)

        # Reshape the array to have two sets of 6 coordinates (2 eyes, each with 6 landmarks)
        eye_array = eye_array.reshape(2, 6, 2)
        for eye_landmarks in eye_array:
            cv2.polylines(frame, [eye_landmarks], isClosed=True, color=(0, 255, 255), thickness=1)

        x1 = face.left()
        y1 = face.top()
        x2 = face.right()
        y2 = face.bottom()
        cv2.rectangle(frame, (x1, y1), (x2, y2), (255, 0, 0), 2)
        ear = eye_aspect_ratio(eye)
        if ear < 0.22:
            counter.append(1)
            if len(counter) > 2:
                pygame.mixer.music.play()
                pygame.time.wait(200)
                cv2.putText(frame, "Fatigue Detected", (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
        else:
            counter = []
        print(counter)

    cv2.imshow("Frame", frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
