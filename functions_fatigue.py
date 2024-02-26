import csv
import cv2
import dlib
from scipy.spatial import distance
import pygame
import time
import os


def split_video_frames(video_path):
    # Open the video file
    cap = cv2.VideoCapture(video_path)

    # Get the frames per second (fps) and frame width/height
    fps = int(cap.get(cv2.CAP_PROP_FPS))
    frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

    # Calculate the frame interval for every 2 seconds
    frame_interval = int(fps * 2)

    # Lists to store selected frames and all frames
    selected_frames = []
    all_frames = []

    # Counter for frame number
    frame_count = 0

    while True:
        # Read a frame from the video
        ret, frame = cap.read()

        # Break the loop if we have reached the end of the video
        if not ret:
            break

        # Append the frame to the all_frames list
        all_frames.append(frame)

        # If the frame count is a multiple of frame_interval, add it to the selected frames
        if frame_count % frame_interval == 0:
            selected_frames.append(frame)

        # Increment the frame count
        frame_count += 1

    # Release the video capture object
    cap.release()

    # Return the selected frames, all frames, and frame rate
    return selected_frames, all_frames, fps, frame_width, frame_height


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


def image_processing(selected_frames):
    # Create a new directory to store the processed frames
    os.makedirs("output_frames", exist_ok=True)
    os.makedirs("output_frames/canny", exist_ok=True)
    os.makedirs("output_frames/gray", exist_ok=True)
    os.makedirs("output_frames/morphologie", exist_ok=True)
    os.makedirs("output_frames/bilaterale", exist_ok=True)
    os.makedirs("output_frames/egalization", exist_ok=True)
    os.makedirs("output_frames/luminosite", exist_ok=True)
    print("folders created")
    # Process each selected frame
    for i, frame in enumerate(selected_frames):
        # Convert the frame to grayscale
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        bilateral = cv2.bilateralFilter(gray, 9, 75, 75)
        canny = cv2.Canny(gray, 50, 150)
        morph = cv2.morphologyEx(canny, cv2.MORPH_CLOSE, (5, 5))
        # améliorer le contraste global de l'image.
        egalisation = cv2.equalizeHist(gray)
        # améliorer la luminosité de l'image.
        luminosite = cv2.convertScaleAbs(gray, alpha=1.2, beta=30)


        # Save the processed frame to the new directory
        cv2.imwrite(f"output_frames/gray/frame_{i}.jpg", gray)
        cv2.imwrite(f"output_frames/bilaterale/frame_{i}.jpg", bilateral)
        cv2.imwrite(f"output_frames/canny/frame_{i}.jpg", canny)
        cv2.imwrite(f"output_frames/morphologie/frame_{i}.jpg", morph)
        cv2.imwrite(f"output_frames/egalization/frame_{i}.jpg", egalisation)
        cv2.imwrite(f"output_frames/luminosite/frame_{i}.jpg", luminosite)


def Video_detection(video_path):
    # take a video and split it into frames:
    selected_frames, all_frames, frame_rate, frame_width, frame_height = split_video_frames(video_path)

    # Generate a new video with face and age detection
    output_video_path = f"output_video{time.time()}.mp4"
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(output_video_path, fourcc, frame_rate, (frame_width, frame_height))
    counter = []
    image_processing(selected_frames)
    for frame in all_frames:
        # Convert the frame to grayscale
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        # detect faces in the frame:
        faces = face_detection(gray)
        # Process each detected face
        for face in faces:
            face_landmarks = face_landmark(gray, face)
            eye = []
            for n in range(36, 48):
                x = face_landmarks.part(n).x
                y = face_landmarks.part(n).y
                cv2.circle(frame, (x, y), 2, (0, 255, 0), 1)
                eye.append((x, y))
            x1 = face.left()
            y1 = face.top()
            x2 = face.right()
            y2 = face.bottom()
            cv2.rectangle(frame, (x1, y1), (x2, y2), (255, 0, 0), 2)

            ear = eye_aspect_ratio(eye)
            save_to_csv(ear, 'ear.csv')
            if ear < 0.285:
                counter.append(1)
                if len(counter) > 3:
                    save_to_csv(ear, 'detection.csv')
                    cv2.putText(frame, "Fatigue Detected", (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
            else:
                counter = []
            print(ear, "\t", counter)
        # Save the frame to the output video
        out.write(frame)

    out.release()



# initialize the Model :
face_detection = dlib.get_frontal_face_detector()
face_landmark = dlib.shape_predictor("shape_predictor_68_face_landmarks.dat")

# Initialize pygame
pygame.init()
# Load the sound file
sound_file = "alert.wav"
pygame.mixer.music.load(sound_file)
# Set the volume (optional)
pygame.mixer.music.set_volume(1.0)

# test the program :
Video_detection('half.mp4')
