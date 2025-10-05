import os
import json
import cv2
import numpy as np
import lib_google_ocr as l_gocr

video_basename = "145147"
in_foldername = f"../{video_basename}_2fps/"
png_files = os.listdir(in_frames_path)

# just iter filenames, fix savint to reasonable format
png_files.sort()
for filename in png_files:
    match = re.match(rf"{in_frames_basename}2fps([\d]+)\.png", filename)
    if match:
# om match stoppaa i data ba
