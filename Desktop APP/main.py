import os
import sys
import shutil
import subprocess
import time
import qimage2ndarray

import numpy as np
from moviepy.editor import VideoFileClip
import cv2
import pandas as pd
from PyQt5.QtWidgets import QMainWindow, QApplication, QPushButton, QFileDialog, QTableWidgetItem, QWidget, QLabel, \
    QVBoxLayout

from PyQt5 import QtWidgets, QtCore, QtGui, QtMultimedia
from script import Ui_MainWindow

###################

from PyQt5.QtCore import Qt, QUrl, QThread, pyqtSignal
from PyQt5.QtGui import QPixmap, QImage
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QGraphicsScene, QGraphicsView
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent
from PyQt5.QtMultimediaWidgets import QVideoWidget


##############

class VideoThread(QThread):
    change_pixmap_signal = QtCore.pyqtSignal(QtGui.QImage)

    def __init__(self, input_path):
        super(VideoThread, self).__init__()
        self.input_path = input_path

    def run(self):
        cap = cv2.VideoCapture(self.input_path)
        while True:
            ret, frame = cap.read()
            if ret:
                self.change_pixmap_signal.emit(frame)
            else:
                break
        cap.release()


class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        
        self.file_data = None
        self.file_data_1 = None
        self.output_path = "./output_videos_APP/video1708978940.5596116.mp4"

        self.ui.Uploadbtn.setChecked(True)
        self.ui.Livebtn.clicked.connect(self.pagelive)
        self.ui.Uploadbtn.clicked.connect(self.pageupload)
        self.ui.databtn.clicked.connect(self.pagedata)
        self.ui.Aboutusbtn.clicked.connect(self.pageAboutus)

        self.ui.stackedWidget.setCurrentWidget(self.ui.pageupload)

        self.ui.selectfilebtn.clicked.connect(self.choosefile)
        self.ui.selectfolderbtn.clicked.connect(self.choose_folder)
        self.ui.cancelbtn.hide()
        self.ui.cancelbtn.clicked.connect(self.Cancel)
        self.ui.launchprocessbtn.clicked.connect(self.launchprocess)
        self.ui.checkoutputbtn.clicked.connect(self.checkoutput)

        self.ui.shell.setReadOnly(True)
        self.ui.playvideobtn_2.setEnabled(False)
        self.ui.framing.setScaledContents(True)

        ########################################################################
        self.ui.playvideobtn_2.clicked.connect(self.display_video)
        self.ui.pushButton_4.clicked.connect(self.upload_data_file)

        self.th = VideoThread(self)



    @QtCore.pyqtSlot(QtGui.QImage)
    def setImage(self, image):
        self.ui.framing.setPixmap(QtGui.QPixmap.fromImage(image))
    ########################################################################

    def Cancel(self):
        self.ui.filepath.setText("")
        self.ui.folderpath.setText("")
        self.ui.checkoutputbtn.setEnabled(False)
        self.ui.shell.insertPlainText("> Cancelled\n")
        self.ui.cancelbtn.hide()

    def inserttext(self, text):
        self.ui.shell.insertPlainText(f"> {text}\n")
        cursor = self.ui.shell.textCursor()
        cursor.movePosition(cursor.End)
        self.ui.shell.setTextCursor(cursor)

    def choosefile(self):
        self.inserttext("uplaod file :")
        options = QFileDialog.Options()
        file_name, _ = QFileDialog.getOpenFileName(self, "Open Video File", "",
                                                   "Video Files (*.mp4 *.avi *.mkv);;All Files (*)",
                                                   options=options)
        self.ui.filepath.setText(file_name)
        self.inserttext(f"Selected file:{file_name}\nYou are ready to launch the detection")

    def choose_folder(self):
        self.inserttext("Choose folder :")
        options = QFileDialog.Options()
        folder_path = QFileDialog.getExistingDirectory(self, "Select Directory", "", options=options)

        if folder_path:
            print("Selected Folder:", folder_path)
            self.inserttext(f"Selected Folder:{folder_path}\nYou are ready to launch the detection")
            self.ui.folderpath.setText(folder_path)

    def pagelive(self):
        self.ui.stackedWidget.setCurrentIndex(2)

    def pageupload(self):
        self.ui.stackedWidget.setCurrentIndex(0)

    def pagedata(self):
        self.ui.stackedWidget.setCurrentIndex(3)

    def pageAboutus(self):
        self.ui.stackedWidget.setCurrentIndex(4)

    def is_csv_file(self, file_path):
        _, file_extension = os.path.splitext(file_path)
        return file_extension.lower() == '.csv'

    def display_data(self, file_data, tableWidget):
        if file_data is not None:
            # Clear existing items in the table
            tableWidget.clear()

            # Set row and column count based on DataFrame shape
            tableWidget.setRowCount(file_data.shape[0])
            tableWidget.setColumnCount(file_data.shape[1])

            # Set headers
            tableWidget.setHorizontalHeaderLabels(file_data.columns.astype(str))

            # Populate the table with data
            for row in range(file_data.shape[0]):
                for col in range(file_data.shape[1]):
                    item = QTableWidgetItem(str(file_data.iloc[row, col]))
                    tableWidget.setItem(row, col, item)

    def upload_data_file(self):
        print("uplaod file")
        options = QFileDialog.Options()
        file_name, _ = QFileDialog.getOpenFileNames(self, "Open Csv File", "",
                                                    "Csv Files ( *.csv);;All Files (*)", options=options)
        print("done")
        if file_name:
            # Read the Excel file into a Pandas DataFrame
            name1 = file_name[0].split("/")[-1]
            name2 = file_name[1].split("/")[-1]
            full_name = name1 + " || " + name2
            if self.is_csv_file(file_name[0]):
                print("hnaya dkhel")
                try:
                    self.file_data = pd.read_csv(file_name[0])
                    print("file_name 0 :", file_name[0])

                    self.file_data_1 = pd.read_csv(file_name[1])
                    print("file_name 0 :", file_name[1])
                except Exception as e:
                    print(f"Error reading the CSV file: {e}")
                self.ui.lineEdit_11.setText(full_name)
                self.display_data(self.file_data, self.ui.tableWidget)
                self.display_data(self.file_data_1, self.ui.tableWidget_2)
                print("showing data completed")
            else:
                self.inserttext("Error: Invalid file format")

    #######################################################
    def process(self, input_path, output_path):
        pass

    def create_thumbnail(self):
        if self.output_path is None:
            return None
        else:
            video_input_path = self.output_path
            # video_input_path = "./output_videos_APP/video1708978940.5596116.mp4"
            id = video_input_path.split("/")[-1].split(".")[0]
            img_output_path = f'./output_videos_APP/{id}_thumbnail.jpg'

            clip = VideoFileClip(video_input_path)
            thumbnail = clip.get_frame(0)  # Get the first frame as a thumbnail
            cv2.imwrite(img_output_path, cv2.cvtColor(thumbnail, cv2.COLOR_BGR2RGB))
            clip.close()
            return img_output_path

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


    def checkoutput(self):
        try:
            self.ui.stackedWidget.setCurrentIndex(1)
            print("dazt lpage")
            image_path = self.create_thumbnail()
            print("thumbnail created ", image_path)
            self.ui.framing.setScaledContents(True)
            self.ui.framing.setPixmap(QPixmap(image_path))
            self.ui.playvideobtn_2.setEnabled(True)
        except Exception as e:
            self.inserttext(f"Error playing the video: {e}")
            print(f"Error playing the video: {e}")

    def Video_detection(self, file_path):
        self.inserttext("Processing the video")
        os.makedirs("output_videos_APP", exist_ok=True)
        self.inserttext("Folder Output_videos created")
        # self.output_path = f"output_videos_APP/video{time.time()}.mp4"
        # video processing
        self.process(file_path, self.output_path)
        self.inserttext("Processing is Done")

    def launchprocess(self):
        folder_path = self.ui.folderpath.text()
        file_path = self.ui.filepath.text()
        if file_path:
            self.Video_detection(file_path)
            self.ui.checkoutputbtn.setEnabled(True)
        elif folder_path:
            for file_name in os.listdir(folder_path):
                # Obtenez le chemin complet du fichier en utilisant os.path.join
                full_path = os.path.join(folder_path, file_name)
                self.Video_detection(full_path)
                self.ui.checkoutputbtn.setEnabled(True)

        else:
            self.inserttext("Please select a file or a folder to launch the detection")


if __name__ == "__main__":
    app = QApplication(sys.argv)

    ## loading style file
    # with open("style.qss", "r") as style_file:
    #     style_str = style_file.read()
    # app.setStyleSheet(style_str)

    window = MainWindow()
    window.show()

    sys.exit(app.exec())
