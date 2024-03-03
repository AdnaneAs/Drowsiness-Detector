import subprocess

import cv2
import ffmpeg

from moviepy.editor import VideoFileClip

video_input_path = "./output_videos_APP/video1708978940.5596116.mp4"
img_output_path = './output_videos_APP/thumbnail.jpg'

clip = VideoFileClip(video_input_path)
thumbnail = clip.get_frame(0)  # Get the first frame as a thumbnail
cv2.imwrite(img_output_path, cv2.cvtColor(thumbnail,cv2.COLOR_BGR2RGB))
clip.close()
