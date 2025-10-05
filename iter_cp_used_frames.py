import lib_ffprobe_json as l_ffj
import cv2
import lib_google_ocr as l_gocr
import os
import json
import re
import sys
import shutil

# video_basename = "20250924_145147" 145147 is the video basename
video_basename = "145147"

in_ffprobe_json_filepath = f"../{video_basename}/{video_basename}_vfr.json"
in_frames_basename = f"{video_basename}_vfr_"
in_frames_path = f"../{video_basename}/"
out_frames_path = f"../{video_basename}_out/"
os.makedirs(out_frames_path, exist_ok=True)
png_files = os.listdir(in_frames_path)
# Filter the list to only include .png files that match the pattern for the video file we are processing
all_png_files_in_folder = []
pattern_matching_png_files = []

for filename in png_files:
    if filename.endswith(".png") and filename.startswith(in_frames_basename):
        all_png_files_in_folder.append(filename)
for filename in all_png_files_in_folder:
    match = re.match(rf"{in_frames_basename}([\d]+)\.png", filename)
    if match:
        pattern_matching_png_files.append({"frame_from_filename":int(match.group(1)),"filename":filename})

# Sort the pattern_matching_png_files list based on the frame_from_filename
pattern_matching_png_files.sort(key=lambda x: x["frame_from_filename"])

# use lib_ffprobe_json to get timestamps that are unique from a list of video only timestamps from json
# and then specify a timespan and framreate to get the frames you want to ocr
framerate=2
vid_timestamplist=l_ffj.get_timestamps_from_frames(in_ffprobe_json_filepath)
framelist=l_ffj.framelist_from_timespan(-1,-1,framerate,vid_timestamplist)

# now we check that all the frames we need to ocr are in the png_files list
for frame in framelist:
  if frame["vbr_frameno"] not in [f["frame_from_filename"] for f in pattern_matching_png_files]:
    print(f"missing frame {frame['vbr_frameno']}")
    exit(1)
  else:
    print(f"copying {frame['vbr_frameno']}")
    shutil.copyfile(in_frames_path+pattern_matching_png_files[frame["vbr_frameno"]-1]["filename"], out_frames_path+pattern_matching_png_files[frame["vbr_frameno"]-1]["filename"])
    
    # shutil.copyfile(in_frames_path+pattern_matching_png_files[frame["vbr_frameno"]-1]["filename"], out_frames_path+pattern_matching_png_files[frame["vbr_frameno"]-1]["filename"])

