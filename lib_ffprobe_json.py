import json
import numpy as np
import matplotlib.pyplot as plt
from collections import OrderedDict


def get_vid_frame_timestamps(in_ffprobe_json_frames):  
  #make sure only video frames
  video_frames = [frame for frame in in_ffprobe_json_frames if frame.get('media_type') == 'video']

  all_actual_timestamps = [float(frame['pts_time']) for frame in video_frames if 'pts_time' in frame]
  unique_ts = list(OrderedDict.fromkeys(all_actual_timestamps))  # Unique in appearance order
  # print(f'len timestamps{len(all_actual_timestamps)} len unique {len(unique_ts)}')
  # print(unique_ts[:10],video_frames[:10])

  return unique_ts

def what_time_at_frame_no(frameno,vid_ts_list):
  return vid_ts_list[frameno]

def closest_frame_to_time(time,vid_ts_list):
  return np.argmin(np.abs(np.array(vid_ts_list)-time))

def framelist_from_timespan(start_time,end_time,frame_rate,vid_ts_list):
  if end_time==-1:
    end_time=vid_ts_list[-1]
  if start_time==-1:
    start_time=vid_ts_list[0]
  list_of_frametimes = np.arange(start_time,end_time,1/frame_rate)
  list_of_frametimes=list_of_frametimes.tolist()
  list_of_framedics=[]
  for i, frametime in enumerate(list_of_frametimes):
    # print(f"framechoice_no {i} time {frametime}")
    thisframeno=closest_frame_to_time(frametime,vid_ts_list)

    if thisframeno<1:
      # print(f"resulting frame for time {frametime} is less than 1, corrected to 1")
      thisframeno=1
      # print(f"the corrected frame, no 1 is at time {what_time_at_frame_no(thisframeno,vid_timestamplist)}")
    thisframetime=what_time_at_frame_no(thisframeno,vid_ts_list)

    nextframtime=-1
    prevframtime=-1
    # print(f"closest frame to {frametime} is {thisframeno}") #frametime is the requested time
    # print(f"time at frame {thisframeno} is {thisframetime}, diff is {frametime-thisframetime}") #thisframetime is the pts time of the closest frame to the requested time
    if thisframeno<len(vid_ts_list)-1:
      nextframtime=what_time_at_frame_no(thisframeno+1,vid_ts_list)
      # print(f"time at next frame is {nextframtime},diff is {nextframtime-thisframetime}")
    if thisframeno>0:
      prevframtime=what_time_at_frame_no(thisframeno-1,vid_ts_list)
      # print(f"time at prev frame is {prevframtime},diff is {thisframetime-prevframtime}")
    
    list_of_framedics.append({"index":i,"vbr_frameno":int(thisframeno),"requested_time":frametime,"pts_time":thisframetime,"prev_pts_time":prevframtime,"next_pts_time":nextframtime})


              
  return list_of_framedics

def get_timestamps_from_frames(in_ffprobe_json_filepath):
    with open(in_ffprobe_json_filepath, 'r') as f:
        data = json.load(f)
    frames = data.get('frames', [])

    vid_timestamplist=get_vid_frame_timestamps(frames)
    
    return vid_timestamplist

    

if __name__ == '__main__':
    pass
