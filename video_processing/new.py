import cv2
import os
import numpy as np
from easyocr import Reader
from PIL import Image
import imagehash


VIDEO_PATH = "hook.mp4"  
OUTPUT_DIR = "selected_frames"
FPS_SAMPLE_RATE = 2  
MAX_SELECTED_FRAMES = 10  
HASH_THRESHOLD = 5  

os.makedirs(OUTPUT_DIR, exist_ok=True)

reader = Reader(['en'])

def get_frame_hash(frame):
    """Compute perceptual hash of the frame."""
    pil_image = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
    return imagehash.phash(pil_image)

def contains_text(frame):
    """Check if frame contains sufficient text using EasyOCR."""
    results = reader.readtext(frame)
    text_area = 0
    for (bbox, text, conf) in results:
        if conf > 0.4:
            x_min = min([pt[0] for pt in bbox])
            x_max = max([pt[0] for pt in bbox])
            y_min = min([pt[1] for pt in bbox])
            y_max = max([pt[1] for pt in bbox])
            area = (x_max - x_min) * (y_max - y_min)
            text_area += area
    return text_area > 5000  

def sample_and_filter_frames(video_path, fps_sample=2, max_frames=10):
    cap = cv2.VideoCapture(video_path)
    video_fps = cap.get(cv2.CAP_PROP_FPS)
    interval = int(video_fps / fps_sample)

    selected_hashes = []
    selected_count = 0
    frame_count = 0
    saved_frames = []

    success, frame = cap.read()
    while success and selected_count < max_frames:
        if frame_count % interval == 0:
            if contains_text(frame):
                frame_hash = get_frame_hash(frame)
                if all(abs(frame_hash - h) > HASH_THRESHOLD for h in selected_hashes):
                    frame_name = f"frame_{frame_count}.jpg"
                    path = os.path.join(OUTPUT_DIR, frame_name)
                    cv2.imwrite(path, frame)
                    saved_frames.append(path)
                    selected_hashes.append(frame_hash)
                    selected_count += 1
        success, frame = cap.read()
        frame_count += 1

    cap.release()
    return saved_frames

selected_frames = sample_and_filter_frames(VIDEO_PATH, FPS_SAMPLE_RATE, MAX_SELECTED_FRAMES)
selected_frames
