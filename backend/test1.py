import ffmpeg
import json


ffmpeg.input('video1.mp4').filter('drawtext', text='HELLO', x=100, y=100, fontcolor='white', fontsize=48).output('test1.mp4').overwrite_output().run()

 
ffmpeg.input('video1.mp4').filter('drawtext', text='HELLO', x=100, y=100, fontcolor='white', fontsize=48, enable='between(t,1,3)').output('test2.mp4').overwrite_output().run()