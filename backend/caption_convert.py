import json
import random
import subprocess

with open("transcription_result.json", "r", encoding="utf-8") as f:
    transcript_data = json.load(f)
words = transcript_data["words"]

with open("style.json", "r", encoding="utf-8") as f:
    styles = json.load(f)

style_names = list(styles.keys())

ass_file = "captions.ass"

ass_header = """
[Script Info]
Title: Styled Captions
ScriptType: v4.00+
PlayResX: 1280
PlayResY: 720
WrapStyle: 2
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, BackColour, Bold, Italic, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
"""

for name, style in styles.items():
    ass_header += (
        f"Style: {name},{style['font']},{style['fontsize']},{style['primary_color']},&H80000000,"
        f"{style['bold']},{style['italic']},{style['border_style']},{style['outline']},{style['shadow']},"
        f"{style['alignment']},10,10,30,1\n"
    )

ass_header += """
[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""

def ms_to_ass_time(ms):
    h = ms // 3600000
    m = (ms % 3600000) // 60000
    s = (ms % 60000) // 1000
    cs = (ms % 1000) // 10
    return f"{h}:{m:02}:{s:02}.{cs:02}"

def make_position_tag():
    return "{\\an5\\marginV360}"

def chunk_words(words, max_words=4, max_gap=300):
    chunks = []
    current_chunk = []
    start_time = 0
    end_time = 0
    for i, word in enumerate(words):
        if not current_chunk:
            current_chunk.append(word)
            start_time = word["start"]
            end_time = word["end"]
            continue
        gap = word["start"] - end_time
        if gap > max_gap or len(current_chunk) >= max_words:
            chunks.append((start_time, end_time, current_chunk))
            current_chunk = [word]
            start_time = word["start"]
            end_time = word["end"]
        else:
            current_chunk.append(word)
            end_time = word["end"]
    if current_chunk:
        chunks.append((start_time, end_time, current_chunk))
    return chunks

chunks = chunk_words(words)

with open(ass_file, "w", encoding="utf-8") as f:
    f.write(ass_header)
    for start_ms, end_ms, chunk_words in chunks:
        style = random.choice(style_names)
        text = " ".join(w["text"].replace("{", "").replace("}", "").replace("\\", "") for w in chunk_words)
        start = ms_to_ass_time(start_ms)
        end = ms_to_ass_time(end_ms)
        pos_tag = make_position_tag()
        styled_text = f"{pos_tag}{text}"
        f.write(f"Dialogue: 0,{start},{end},{style},,0,0,0,,{styled_text}\n")

input_video = "video1.mp4"
output_video = "output_with_captions.mp4"

cmd = [
    "ffmpeg",
    "-i", input_video,
    "-vf", f"ass={ass_file}",
    "-c:a", "copy",
    output_video
]

subprocess.run(cmd, check=True)
print(" Captions applied and saved to:", output_video)
