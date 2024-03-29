import cv2
import dlib
from scipy.spatial import distance
import pygame
import numpy as np
import os
import csv
import time


def eye_aspect_ratio(eye):
    # calcul de la distance euclidienne entre les deux points verticaux
    A = distance.euclidean(eye[1], eye[5])
    B = distance.euclidean(eye[2], eye[4])
    # calcul de la distance euclidienne entre les deux points horizontaux
    C = distance.euclidean(eye[0], eye[3])
    # calcul du ratio des yeux
    ear = (A + B) / (2.0 * C)
    return ear


def save_to_csv(ear, filename):
    current_time = time.time()
    # Convertir le temps actuel en une structure de temps locale
    local_time = time.localtime(current_time)

    # Extraire les composants de l'heure
    hours = local_time.tm_hour
    minutes = local_time.tm_min
    seconds = local_time.tm_sec

    # Save the ear values to a CSV file
    with open(filename, 'a', newline='') as file:
        writer = csv.writer(file)
        if file.tell() == 0:
            writer.writerow(['Ear', 'Time'])
        writer.writerow([ear, f"{int(hours)}:{int(minutes)}:{int(seconds)}"])
    file.close()


def detect_fatigue(cap):
    face_detection = dlib.get_frontal_face_detector()
    face_landmark = dlib.shape_predictor("assets/shape_predictor_68_face_landmarks.dat")
    counter = []
    # Initialize pygame
    pygame.init()

    # Load the sound file
    sound_file = "assets/alert.wav"
    pygame.mixer.music.load(sound_file)

    # Set the volume (optional)
    pygame.mixer.music.set_volume(1.0)

    while True:
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = face_detection(gray)
        # bouclé sur les visages détectés
        for face in faces:
            face_landmarks = face_landmark(gray, face)
            eye = []

            for n in range(36, 48):
                x = face_landmarks.part(n).x
                y = face_landmarks.part(n).y
                cv2.circle(frame, (x, y), 2, (0, 255, 0), 1)
                eye.append((x, y))
            # cette partie est pour dessiner les yeux avec des lignes enchainées
            # Convert the list to a NumPy array
            eye_array = np.array(eye, dtype=np.int32)

            # Reshape the array to have two sets of 6 coordinates (2 eyes, each with 6 landmarks)
            eye_array = eye_array.reshape(2, 6, 2)
            for eye_landmarks in eye_array:
                cv2.polylines(frame, [eye_landmarks], isClosed=True, color=(0, 255, 255), thickness=1)

            # Draw rectangles around the face
            x1 = face.left()
            y1 = face.top()
            x2 = face.right()
            y2 = face.bottom()
            cv2.rectangle(frame, (x1, y1), (x2, y2), (255, 0, 0), 2)
            ear = eye_aspect_ratio(eye)

            os.makedirs("output_ear_data_app", exist_ok=True)
            save_to_csv(ear, 'output_ear_data_app/ear_live.csv')
            if ear < 0.22:
                counter.append(1)
                if len(counter) > 2:
                    # Save the detected fatigue data to a CSV file
                    save_to_csv(ear, 'output_ear_data_app/detected_fatigue_data_live.csv')
                    pygame.mixer.music.play()
                    pygame.time.wait(200)
                    cv2.putText(frame, "Fatigue Detected", (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
            else:
                counter = []
            print(counter)
        return frame
