def display_video_3(self):
    cap = cv2.VideoCapture(self.output_path)
    # Get the frame rate of the video
    fps = cap.get(cv2.CAP_PROP_FPS)

    # Loop through the video frames
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        height, width, channel = frame.shape
        bytes_per_line = 3 * width

        q_img = QImage(frame.data, width, height, bytes_per_line, QImage.Format_RGB888).rgbSwapped()
        pixmap = QPixmap.fromImage(q_img)
        self.ui.framing.setPixmap(pixmap)

        # Break the loop if the 'q' key is pressed
        if cv2.waitKey(int(1000 / fps)) & 0xFF == ord('q'):
            break

    # Release the video capture object and close OpenCV windows
    cap.release()
    cv2.destroyAllWindows()