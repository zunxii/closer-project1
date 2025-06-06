import ffmpeg

input_file = 'video1.mp4'
output_file = 'output.mp4'
font_path = 'handwrite.ttf'

try:
    (
        ffmpeg
        .input(input_file)
        .output(
            output_file,
            vf=f"drawtext=fontfile='{font_path}':text='Hello World':fontcolor=white:fontsize=48:x=(w-text_w)/2:y=(h-text_h)/2",
            vcodec='libx264',
            acodec='copy'
        )
        .overwrite_output()
        .run()
    )
    print("✅ Text added successfully!")
except ffmpeg.Error as e:
    print("❌ FFmpeg error:", e.stderr.decode())
