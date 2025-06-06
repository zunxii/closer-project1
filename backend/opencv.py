import cv2
import numpy as np
from easyocr import Reader

reader = Reader(['en'], gpu=False)

def get_dominant_color(image, bbox):
    mask = np.zeros(image.shape[:2], dtype=np.uint8)
    pts = np.array(bbox, np.int32).reshape((-1, 1, 2))
    cv2.fillPoly(mask, [pts], 255)
    masked_img = cv2.bitwise_and(image, image, mask=mask)
    colors, counts = np.unique(masked_img.reshape(-1, 3), axis=0, return_counts=True)
    dominant_color = colors[np.argmax(counts)]
    return tuple(int(c) for c in dominant_color)

def analyze_video_styles(video_path, fps_sample=2, max_seconds=10):
    cap = cv2.VideoCapture(video_path)
    fps = cap.get(cv2.CAP_PROP_FPS)
    interval = int(fps / fps_sample)
    max_frames = fps_sample * max_seconds

    output = []
    frame_count = 0
    total_frames = 0

    while cap.isOpened() and frame_count < max_frames:
        ret, frame = cap.read()
        if not ret:
            break

        if total_frames % interval == 0:
            print(f"⏱️ Analyzing frame {frame_count} at {round(total_frames / fps, 2)}s")
            results = reader.readtext(frame)
            frame_info = {
                "frame": frame_count,
                "timestamp_sec": round(total_frames / fps, 2),
                "style_data": []
            }

            for (bbox, text, conf) in results:
                x_coords = [p[0] for p in bbox]
                y_coords = [p[1] for p in bbox]
                width = max(x_coords) - min(x_coords)
                height = max(y_coords) - min(y_coords)
                color = get_dominant_color(frame, bbox)

                frame_info["style_data"].append({
                    "text": text,
                    "font_height": round(height, 2),
                    "font_width": round(width, 2),
                    "color_bgr": color,
                    "confidence": round(conf, 2)
                })

            output.append(frame_info)
            frame_count += 1

        total_frames += 1

    cap.release()
    return output

# 🔍 Run this on your local video
video_styles = analyze_video_styles("hook.mp4")

# Optionally print first few frames' style data
import json
print(json.dumps(video_styles[:3], indent=2))
