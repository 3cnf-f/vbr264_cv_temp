import lib_ffprobe_json as l_ffj
import lib_google_ocr as l_gocr
import os
import json
import re
import sys
import shutil

# video_basename = "20250924_145147" 145147 is the video basename
video_basename = "143827"

in_ffprobe_json_filepath = f"../{video_basename}/{video_basename}_vfr.json"
in_ffprobe_ocr_json_filepath = f"../{video_basename}_out/{video_basename}_vfr__vbr_ocr.json"

with open(in_ffprobe_ocr_json_filepath, 'r') as f:
    in_ocr_json=json.load(f)
# Filter the list to only include .png files that match the pattern for the video file we are processing
key_list=list(in_ocr_json.keys())
outjson={}
framerate=2
vid_timestamplist=l_ffj.get_timestamps_from_frames(in_ffprobe_json_filepath)
framelist=l_ffj.framelist_from_timespan(-1,-1,framerate,vid_timestamplist)

for ii,key in enumerate(key_list):
    print(f'\n --- ii={ii} key={key} vbr_frameno={framelist[ii]["vbr_frameno"]}  pts_time={framelist[ii]["pts_time"]}  \n ')
    outjson[ii]={}
    outjson[ii]["frame"]=key
    outjson[ii]["google_ocr"]=in_ocr_json[key]["google_ocr"]
    outjson[ii]["vbr_frameno"]=framelist[ii]["vbr_frameno"]
    outjson[ii]["pts_time"]=framelist[ii]["pts_time"]
    outjson[ii]["requested_time"]=framelist[ii]["requested_time"]

    for word in in_ocr_json[key]["google_ocr"]:
        print(f'-------word{word["word"]}  confidence{word["confidence"]}')
print(outjson.keys())
with open(f"../{video_basename}_out/{video_basename}_new_ocr.json", 'w') as f:
    json.dump(outjson, f, indent=4)
