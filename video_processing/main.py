import cv2
import os

def extract_frames(video_path, output_dir, fps_target=2):
    os.makedirs(output_dir, exist_ok=True)
    cap = cv2.VideoCapture(video_path)
    
    fps = cap.get(cv2.CAP_PROP_FPS)
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    interval = int(fps / fps_target)

    count = 0
    saved = 0

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break
        if count % interval == 0:
            filename = os.path.join(output_dir, f"frame_{saved+1}.png")
            cv2.imwrite(filename, frame)
            print(f"Saved {filename}")
            saved += 1
        count += 1
        if count >= total_frames:
            break

    cap.release()
    print("Frame extraction complete.")

extract_frames("test12.mp4", "frames1", fps_target=2)
