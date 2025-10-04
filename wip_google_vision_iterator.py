import cv_tools
import json

json_filename="../video/20250924_145147_frames0-100/20250924_145147_frames.json"
with open(json_filename, "r") as f:
    in_frames_json=json.load(f)

print(in_frames_json["frames"][1][1]])
