# vbr json file





# vbr264_cv_temp
Get all non non identical frames for vbr (variable bitrate video).
We avoid the issue of extracting a massive ampount of duplicate frames
when the frames are extracted assuming framrate=max framerate in the vbr. (120 vs 35)
```
ffmpeg -i 20250924_150619.mp4  -vsync vfr 150619_vfr_%06d.png -y -loglevel error
```

the extracted frames will not be 100% evenly spaced. 
make json with frame info vbr h264 using ffprobe
```
ffprobe -v quiet -show_frames -print_format json 20250924_150619.mp4 > 150619_vfr.json
```
# if video is20250924_145147.mp4 then 145147 is the video basename

now create a folder for the video called <basename>
now move the videos to the <basename> folder
clone the repo in the same folder
```
git clone https://github.com/3cnf-f/vbr264_cv_temp.git
```

create virtual env and install required packages
```
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

we can use iter_vbr_fr_by.py to get a list of frames for the framrate we  and then iterate over them with preprocessing, ocr or whatever we need.

change the video basename to the video we are working on.
#from iter_vbr_fr_by.py:

_video_basename = "145147"_
if needed change the frame rate 

_framerate=2_


and run

```
python iter_vbr_fr_by.py
```
now we have a list of video frames that are chosen according to the frame rate we have set, so we know which frames to process. first a new folder is created: 
<basename>_out

then a json with our resultsare saved to:

the outpu
-----------------ej klar
143800 143827 144850 have passed frame selection google ocr, png copy and json correction
145147 gets stuck because a frame is missing. see iter_vbr_fr_by.py for comments

