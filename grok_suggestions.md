Key Suggestions for Accurate PNG-to-Timestamp Mapping

The discrepancy (3171 extracted PNGs vs. 3377 unique video timestamps from JSON) likely arises from FFmpeg's -vsync vfr dropping frames with non-monotonic or invalid PTS during output sequencing, even if timestamps appear unique in ffprobe (e.g., due to decoding order vs. presentation order mismatches or subtle floating-point issues). This is common in VFR videos, where ffprobe shows all decoded frames, but FFmpeg enforces strict increasing timestamps for the image muxer. Re-extracting with modifications is the most reliable fix, but for your existing PNGs, logging during a dry-run extraction can retroactively map them. Below are practical, low-effort options.
1. Re-Extract with PTS in Filenames (Recommended for Future/Quick Re-Run)

Use -frame_pts 1 to name PNGs directly with their PTS value (in timebase units). No JSON needed—compute time from PTS and the stream's time_base (a fraction like 1/90000).

    Command:
    text

ffprobe -v error -select_streams v:0 -show_entries stream=time_base -of csv=p=0 20250924_145147.mp4

This outputs the time_base (e.g., 1/90000). Note num/den from it.

Then extract:
text

ffmpeg -i 20250924_145147.mp4 -vsync vfr -frame_pts 1 145147_vfr_pts_%d.png -y -loglevel error

    Files become 145147_vfr_pts_123456.png (PTS=123456).
    Time Calculation: seconds = PTS * (time_base.num / time_base.den). For example, if time_base=1/90000, time = 123456 / 90000 ≈ 1.3728s.
    Python Snippet (to batch-compute for all files):
    python

        import os
        import glob

        time_base_num, time_base_den = 1, 90000  # From ffprobe output
        png_files = sorted(glob.glob('145147_vfr_pts_*.png'))
        for file in png_files:
            pts_str = file.split('_')[-1].replace('.png', '')  # Extract PTS from filename
            pts = int(pts_str)
            time_sec = pts * (time_base_num / time_base_den)
            print(f"{file}: PTS={pts}, Time={time_sec:.3f}s")

        Pros: Exact, no duplicates/discrepancies; filenames self-document.
        Cons: Re-extraction time (~1–5 min for short video); ~3171 new files.
        Why It Works: -frame_pts 1 uses the output PTS directly, bypassing JSON parsing issues.

2. Dry-Run Extraction with Frame Logging (For Existing PNGs, No Re-Extraction Needed)

Run FFmpeg in "null" mode (no output files) but log PTS for each processed frame using -vf showinfo. This simulates your extraction and outputs the exact sequence of 3171 PTS values to console/log, which you can index by frame number.

    Command:
    text

ffmpeg -i 20250924_145147.mp4 -vsync vfr -f null - -vf showinfo -loglevel info > extraction_log.txt 2>&1

    showinfo prints details like [Parsed_showinfo_0 @ ...] n:3170 pts:123456 pts_time:1.3728 ... for each frame (n=0-based index).
    Redirect to file for parsing.

Parse Log for Mapping (Python snippet):
python

    import re

    log_file = 'extraction_log.txt'
    pts_pattern = r'n:(\d+) pts:(\d+) pts_time:([\d.]+)'

    frame_pts = {}
    with open(log_file, 'r') as f:
        for line in f:
            match = re.search(pts_pattern, line)
            if match:
                frame_idx = int(match.group(1))  # 0-based
                pts_time = float(match.group(3))
                frame_pts[frame_idx + 1] = pts_time  # 1-based for PNG num

    # For your example PNG (e.g., 003352.png)
    png_num = 3352
    if png_num in frame_pts:
        print(f"145147_vfr_{png_num:06d}.png: {frame_pts[png_num]:.3f}s")
    else:
        print(f"PNG {png_num} not found in log (check index).")

        Pros: Matches exact extraction behavior; no new files; quick (~30s run).
        Cons: Verbose log (~10MB for 3171 frames); requires parsing.
        Why It Works: showinfo logs per-output-frame details, capturing vfr drops in real-time.

3. Debug the JSON Discrepancy (To Understand Why 3377 vs. 3171)

Your method (filter video + OrderedDict) assumes all unique video PTS are output, but FFmpeg may skip frames with missing/negative PTS, non-video packets, or muxer constraints. Run this enhanced Python on your JSON to diagnose:
python

import json
from collections import OrderedDict

with open('145147_vfr.json', 'r') as f:
    data = json.load(f)
frames = data['frames']

# Filter video only
video_frames = [f for f in frames if f.get('media_type') == 'video' and 'pts_time' in f]
print(f"Total video frames in JSON: {len(video_frames)}")

# Extract and dedup timestamps
all_actual_timestamps = [float(f['pts_time']) for f in video_frames]
ts = list(OrderedDict.fromkeys(all_actual_timestamps))
print(f"Unique video timestamps: {len(ts)}")

# Check for non-monotonic (possible drop reason)
non_mono = sum(1 for i in range(1, len(ts)) if ts[i] <= ts[i-1])
print(f"Non-monotonic PTS pairs: {non_mono}")

# Frames with invalid PTS (e.g., negative or NaN)
invalid = sum(1 for t in all_actual_timestamps if t < 0 or not (t == t))  # NaN check
print(f"Invalid PTS: {invalid}")

# Sample first/last for verification
print(f"First TS: {ts[0]:.3f}, Last TS: {ts[-1]:.3f}")

    Run this—if non-monotonic >0 or invalid >0, that's your drop culprit (206 frames).
    Pros: Reveals root cause without re-running FFmpeg.
    Cons: Diagnostic only; doesn't fix mapping.

4. Content-Based Matching (Last Resort, If No Re-Run Possible)

If re-extraction/log isn't feasible, hash PNGs and match to JSON frame hashes (via ffprobe -show_frames with -vf showinfo equivalent, but complex). Use Python's imagehash:
python

import imagehash
from PIL import Image
import json  # Load JSON, get video frames

# Assume you extract hashes from JSON frames (requires re-decoding, heavy)
# Or: Run ffprobe on video to get frame hashes, but impractical.

    Pros: Works for existing files.
    Cons: Computationally expensive (re-encode 3377 frames); inaccurate for similar content.

Quick Tips

    Time Estimate: Re-extraction (#1) takes <5 min; logging (#2) <1 min.
    Prevention: Always use -select_streams v:0 in ffprobe for video-only JSON: ffprobe -v quiet -select_streams v:0 -show_frames -print_format json input.mp4 > json.json.
    Validation: After mapping, check duration: last timestamp ≈ total video length (from ffprobe -show_format).

These should get you exact times within 1–2 tries—start with #2 for your current setup. If the debug code reveals something odd, share output for tweaks.




---- next

Understanding the Discrepancy

The difference between the 3171 PNG frames extracted by FFmpeg with -vsync vfr and the 3377 video frames found in the ffprobe JSON (after filtering for media_type == 'video') is a common issue in variable frame rate (VFR) video processing. FFmpeg's -vsync vfr mode (value 2) passes frames with their original timestamps but drops frames to prevent duplicate timestamps, ensuring each output frame has a unique presentation timestamp (PTS). This is by design to avoid playback issues in the output sequence, such as stuttering or incorrect timing when rebuilding the video.

ffprobe's -show_frames reports all decoded video frames from the input, including those with duplicate or conflicting timestamps that FFmpeg later drops during extraction. Your JSON likely includes ~206 frames (3377 - 3171) that were dropped by -vsync vfr due to repeated PTS values, which is typical in VFR encodings (e.g., from screen recordings or device captures with motion-adaptive rates). These drops don't indicate errors but rather FFmpeg's optimization for clean, unique-timestamp output—especially relevant for your videos reporting max 120 fps but averaging ~35 fps, where low-motion scenes may reuse timestamps.

This makes direct mapping "hard" if you only count total video frames, but it's solvable by deduplicating the timestamps in the JSON to mimic FFmpeg's behavior. The resulting unique list should exactly match your 3171 PNGs, allowing reliable frame-to-time mapping.
Suggestions to Map PNG Frame Numbers to Timestamps

    Deduplicate Video Timestamps in JSON (Primary Recommendation):
        Filter for video frames only, then apply uniqueness while preserving order (as FFmpeg outputs the first occurrence of each timestamp).
        This should yield exactly 3171 unique timestamps, confirming alignment with your PNGs.
        Updated Python Code (run in Colab; adjust path):
        python

    import json
    from collections import OrderedDict

    with open('145147_vfr.json', 'r') as f:
        data = json.load(f)
    frames = data['frames']

    # Filter for video frames only
    video_frames = [frame for frame in frames if frame.get('media_type') == 'video']

    # Extract pts_time as floats
    all_actual_timestamps = [float(frame['pts_time']) for frame in video_frames if 'pts_time' in frame]

    # Deduplicate while preserving first occurrence order (mimics -vsync vfr)
    unique_ts = list(OrderedDict.fromkeys(all_actual_timestamps))

    print(f"Total video frames in JSON: {len(video_frames)}")  # Should be 3377
    print(f"Unique video timestamps: {len(unique_ts)}")  # Should be 3171

    # Map your PNG (e.g., 145147_vfr_003352.png; adjust frame_num as needed)
    frame_num = 3352  # From PNG filename (1-based)
    if frame_num <= len(unique_ts):
        time_sec = unique_ts[frame_num - 1]
        print(f"Timestamp for 145147_vfr_{frame_num:06d}.png: {time_sec:.3f} seconds")
    else:
        print(f"Frame {frame_num} exceeds {len(unique_ts)} unique frames; check extraction.")

    Expected Outcome: len(unique_ts) should match 3171. The timestamp for a PNG is the corresponding index in this list (0-based). If it doesn't match exactly, the drops might include non-duplicate cases (e.g., invalid timestamps or sync adjustments)—proceed to step 2.
    Why This Works: -vsync vfr outputs frames in presentation order, dropping only to resolve timestamp conflicts, so the first unique PTS sequence aligns perfectly.

Verify and Debug the Discrepancy:

    Check for Duplicate Timestamps: After extracting all_actual_timestamps, compute duplicates:
    python

from collections import Counter
duplicates = [ts for ts, count in Counter(all_actual_timestamps).items() if count > 1]
print(f"Number of duplicate timestamps: {len(duplicates)}")  # Should be ~206 unique duplicates, accounting for drops

This confirms if drops are purely duplicate-related (expected in VFR).
Run ffprobe with Video-Only Selection: Regenerate JSON to exclude audio/other streams:
text

ffprobe -v quiet -select_streams v:0 -show_frames -print_format json 20250924_145147.mp4 > 145147_video_only.json

Then re-run the code above—the total video frames should now be closer to 3171 after uniqueness.
Inspect Dropped Frames: Compare PTS patterns:
python

    # After unique_ts
    deltas = [unique_ts[i+1] - unique_ts[i] for i in range(len(unique_ts)-1)]
    print(f"Average delta (1/FPS): {sum(deltas)/len(deltas):.6f} seconds")  # ~1/35 = 0.0286s

    If deltas vary widely, it highlights VFR drops.

Alternative Extraction Methods for Better Mapping:

    Extract with Passthrough (-vsync 0): To get all frames without drops (matching JSON count ~3377):
    text

ffmpeg -i 20250924_145147.mp4 -vsync 0 145147_all_%06d.png -y -loglevel error

This preserves duplicates (potentially redundant images) but allows direct 1:1 mapping to JSON indices (after video filtering). Use if uniqueness isn't critical for your study.
Extract with PTS in Filename: Name PNGs by timestamp units for self-mapping:
text

    ffmpeg -i 20250924_145147.mp4 -vsync vfr -frame_pts 1 145147_pts_%d.png -y -loglevel error

    Filenames become PTS values (e.g., 145147_pts_123456.png). Convert to time: time_sec = pts_filename * your_time_base (~1.70386e-05 from earlier). This avoids JSON dependency but assumes consistent time base.
    Add Metadata to PNGs: Use -metadata:s:v:0 comment=pts_time or tools like exiftool post-extraction to embed timestamps, but PNG metadata is limited—better for debugging.

Watermark Timestamps During Extraction:

    To avoid manual mapping forever, re-extract with overlaid timestamps (as suggested before):
    text

    ffmpeg -i 20250924_145147.mp4 -vf "drawtext=fontfile=/path/to/font.ttf:text='%{pts\\:hms}.%{pts\\:flt\\:%3N}':x=10:y=10:fontsize=24:fontcolor=white:box=1:boxcolor=black@0.5" -vsync vfr 145147_vfr_%06d.png -y -loglevel error

    This burns hh:mm:ss.ms directly on each PNG (top-left; adjust position). For your existing PNGs, batch-overlay using a script that maps via the JSON method above, but it's more work.

If Counts Still Don't Match After Deduplication:

    Non-Duplicate Drops: -vsync vfr might drop frames for other reasons, like invalid PTS (e.g., negative or out-of-order) or muxer adjustments. Check JSON for anomalies:
    python

invalid_ts = [t for t in all_actual_timestamps if t < 0 or (i > 0 and t <= all_actual_timestamps[i-1])]
print(f"Invalid timestamps: {len(invalid_ts)}")

If present, FFmpeg skips them.
Re-Extract with Logging: Run extraction with verbose logs to see drops:
text

        ffmpeg -i 20250924_145147.mp4 -vsync vfr 145147_vfr_%06d.png -y -loglevel verbose 2> extract_log.txt

        Grep for "dup" or "drop" in the log to quantify.
        Use Alternative Sync: Test -vsync passthrough (0) or -fps_mode vfr (modern equivalent) for comparison.
        Tool Assistance: If needed, upload a sample JSON snippet (first 10-20 lines) for further diagnosis, or use MediaInfo (mediainfo --Inform="Video;%FrameCount%" input.mp4) for an independent frame count.

This deduplication method should resolve the mapping issue in most cases, as it replicates FFmpeg's logic. Your videos' VFR nature (from earlier ffprobe: h264, yuv420p, bt709) often leads to such drops in static scenes. If the unique count still exceeds 3171, the extra might be from non-outputtable frames (e.g., corrupted)—share more JSON details for refinement.


