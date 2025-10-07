from faster_whisper import WhisperModel
import json

# Load model (downloads ~3GB on first run; use int8 for lower RAM/slightly faster on CPU)
model = WhisperModel("KBLab/kb-whisper-large", device="cpu", compute_type="int8")

# Transcribe (outputs segments with timestamps)
segments, info = model.transcribe("audio.wav", language="sv", condition_on_previous_text=False)
print(f"Detected language: {info.language} (prob: {info.language_probability:.2f})")

# Collect into JSON for your parsing/sync needs
output = {
    "language": info.language,
    "segments": [
        {
            "start": segment.start,
            "end": segment.end,
            "text": segment.text.strip()
        } for segment in segments
    ]
}

# Save to JSON
with open("transcription.json", "w", encoding="utf-8") as f:
    json.dump(output, f, ensure_ascii=False, indent=2)

print("Transcription saved to transcription.json")
