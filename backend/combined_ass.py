import json
from datetime import timedelta
import subprocess

# --- CONFIGURATION ---
transcript_file = "hook_transcription.json"
style_file = "styles.json"
ass_output_file = "output.ass"
input_video = "hook.mp4"
output_video = "output_with_captions2.mp4"

# --- FUNCTIONS ---

def ms_to_ass_time(ms):
    td = timedelta(milliseconds=ms)
    total_seconds = td.total_seconds()
    hours = int(total_seconds // 3600)
    minutes = int((total_seconds % 3600) // 60)
    seconds = int(total_seconds % 60)
    centiseconds = int((total_seconds * 100) % 100)
    return f"{hours}:{minutes:02d}:{seconds:02d}.{centiseconds:02d}"

# --- LOAD DATA ---
with open(transcript_file, "r", encoding="utf-8") as f:
    transcript_data = json.load(f)

with open(style_file, "r", encoding="utf-8") as f:
    styles_data = json.load(f)

# --- ASS HEADER ---
ass_header = """[Script Info]
Title: Word-level Captions
ScriptType: v4.00+
Collisions: Normal
PlayResY: 1920
PlayResX: 1080
Timer: 100.0000

[V4+ Styles]
Style: Style11,Arial,60,&H00FFFFFF,&H000000FF,&H00000000,&H64000000,-1,0,0,0,100,100,0,0,1,2,0,5,10,10,360,1

[Events]
"""

# --- BUILD ASS BODY ---
ass_lines = []
for word in transcript_data["words"]:
    text = word["text"]
    start = ms_to_ass_time(word["start"])
    end = ms_to_ass_time(word["end"])
    key = f"{text}_{word['end']}"

    style = styles_data.get(key, {})
    pos = style.get("position", "")
    font_color = style.get("font_color", "#FFFFFF")
    ass_color = "&H" + font_color[5:7] + font_color[3:5] + font_color[1:3]  # #RRGGBB to &HBBGGRR

    overrides = f"{{\\an5\\marginV360{pos}\\c{ass_color}}}"
    ass_line = f"Dialogue: 0,{start},{end},Style11,,0,0,0,,{overrides}{text}"
    ass_lines.append(ass_line)

# --- WRITE TO ASS FILE ---
with open(ass_output_file, "w", encoding="utf-8") as f:
    f.write(ass_header + "\n".join(ass_lines))

print(f"✅ ASS subtitle file saved as: {ass_output_file}")

# --- FFMPEG COMMAND TO BURN SUBTITLES ---
cmd = [
    "ffmpeg",
    "-i", input_video,
    "-vf", f"ass={ass_output_file}",
    "-c:a", "copy",
    output_video
]

# --- OPTIONAL: Run FFmpeg ---
subprocess.run(cmd)

print(f"🎬 FFmpeg command prepared to burn subtitles into video:\n{' '.join(cmd)}")
