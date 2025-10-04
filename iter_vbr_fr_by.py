import lib_ffprobe_json as l_ffj
import os
import json
import re

in_ffprobe_json_filepath = "143800_vfr.json"
in_vid_frames_path=""
vid_timestamplist=l_ffj.get_timestamps_from_frames(in_ffprobe_json_filepath)
framelist=l_ffj.framelist_from_timespan(-1,-1,2,vid_timestamplist)

