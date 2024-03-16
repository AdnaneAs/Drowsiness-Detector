def display_video(self):
    # ghadi iqra lina  lvideo kaml
    cap = cv2.VideoCapture(self.output_path)
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        rgb_image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        # display image
        self.ui.framing.setPixmap(QPixmap.fromImage(
            QtGui.QImage(rgb_image, rgb_image.shape[1], rgb_image.shape[0], QtGui.QImage.Format_RGB888)))
    cap.release()


def display_video_2(self):
    clip = VideoFileClip(self.output_path)

    total_frames = int(clip.duration * clip.fps)

    for i in range(total_frames):
        frame = clip.get_frame(i / clip.fps)
        self.ui.framing.setPixmap(QPixmap(frame))

    clip.close()