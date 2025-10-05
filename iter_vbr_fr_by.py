import lib_ffprobe_json as l_ffj
import cv2
import lib_google_ocr as l_gocr
import os
import json
import re

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
dic_pattern_matching_png_files={}
png_files.sort()
print(png_files[-5:])
for filename in png_files:
    if filename.endswith(".png") and filename.startswith(in_frames_basename):
        all_png_files_in_folder.append(filename)
for filename in all_png_files_in_folder:
    match = re.match(rf"{in_frames_basename}([\d]+)\.png", filename)
    if match:
        pattern_matching_png_files.append({"frame_from_filename":int(match.group(1)),"filename":filename})
        dic_pattern_matching_png_files[int(match.group(1))]=filename

# Sort the pattern_matching_png_files list based on the frame_from_filename
# pattern_matching_png_files.sort(key=lambda x: x["frame_from_filename"])

# use lib_ffprobe_json to get timestamps that are unique from a list of video only timestamps from json
# and then specify a timespan and framreate to get the frames you want to ocr
framerate=2
vid_timestamplist=l_ffj.get_timestamps_from_frames(in_ffprobe_json_filepath)
print(f'len timestamps {len(vid_timestamplist)} last timestamp {vid_timestamplist[-1]}')
exit()
framelist=l_ffj.framelist_from_timespan(-1,-1,framerate,vid_timestamplist)
# print(f'len timestamps {len(vid_timestamplist)} len framelist {len(framelist)}')
# for i in range(len(framelist)):
#     print(i)
#     print(f' frame i {i} from framelist {(framelist[i])}')
#
# # now we check that all the frames we need to ocr are in the png_files list
# # for ii in range(6):
# #
# #     print(ii,framelist[ii]["vbr_frameno"],framelist[ii]["pts_time"],pattern_matching_png_files[ii]["frame_from_filename"])
# print(pattern_matching_png_files[-3:])
# exit()
#
#
# # debugging : missmatch bewwen suggested frames and actual frames
# # make iterator for send frames to google
# #first test for 10th frame in our framlist
# testno=3
# test_frame=framelist[testno]
# print(f'the {testno+1}th frame is {test_frame["vbr_frameno"]} and its time is {test_frame["pts_time"]} and the filepath is {in_frames_path+pattern_matching_png_files[test_frame["vbr_frameno"]-1]["filename"]} ')
#
# try:
#     api_key = os.environ.get('gooog')
#     print(api_key)
# except:
#     print("api key error")

out_json_path=f"{out_frames_path}{in_frames_basename}_vbr_ocr.json"
outjson={}
outjson
itertimes=1
print(framelist[-1]["vbr_frameno"])
for iii,frame  in enumerate(framelist[-5:]): 
  frame_no=frame["vbr_frameno"]
  index=frame["index"]
  print(f'vbr frame {frame_no} index from framelist {index} of total {len(framelist)} frames to  ')
print(dic_pattern_matching_png_files[frame_no]["filename"])


  # frame_path=in_frames_path+pattern_matching_png_files[frame_no]["filename"]
  #
  # print(frame_path)
  # with open(frame_path, 'rb') as f:
  #   image_data = f.read()
  #
  # # annot_list=l_gocr.g_cv_doc_text_detect(image_data, api_key)
  # annot_list=[]
  # print(f"{str(itertimes)} of {len(framelist)} done." ) 
  # outjson[frame_no]={}
  # outjson[frame_no]["google_ocr"]=annot_list
  # itertimes=itertimes+1
  #
# with open(out_json_path, 'w') as f:
#     json.dump(outjson, f, indent=4)
