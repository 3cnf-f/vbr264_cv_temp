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
we can use lib_ffprobe_json.py to get a list of frames for the framrate we  and then iterate over them with preprocessing, ocr or whatever we need.

