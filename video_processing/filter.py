import os
import cv2
import pytesseract

input_dir = "frames1"
output_dir = "optimised_frames1"
os.makedirs(output_dir, exist_ok=True)

for filename in os.listdir(input_dir):
    if filename.lower().endswith(('.png', '.jpg', '.jpeg')):
        filepath = os.path.join(input_dir, filename)
        image = cv2.imread(filepath)

        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

        text = pytesseract.image_to_string(gray).strip()

        if text:
            save_path = os.path.join(output_dir, filename)
            cv2.imwrite(save_path, image)
            print(f"Text found in {filename}, saved.")
