import subprocess

ass_file = "output1.ass"
input_video = "video1.mp4"
output_video = "output_with_captions1.mp4"

cmd = [
    "ffmpeg",
    "-i", input_video,
    "-vf", f"ass={ass_file}",
    "-c:a", "copy",
    output_video
]

subprocess.run(cmd, check=True)
print(" Captions applied and saved to:", output_video)
