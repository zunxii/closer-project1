import os
import base64
import json
import re
from openai import OpenAI
from PIL import Image

# === CONFIG ===
OPEN_AI_API_KEY = "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"  # Replace with your key
frames_dir = "optimised_frames1"
output_ass_file = "ass_styles_output.ass"
output_json_file = "word_style_data.json"
model_name = "gpt-4o"

client = OpenAI(api_key=OPEN_AI_API_KEY)

# === PROMPT ===
prompt = """
You are an expert in subtitle typography and linguistics.

For each visible **text block** or word in this image, output the following fields:

1. text: The detected text.
2. Fontname: Most likely font family (e.g., Montserrat, Poppins).
3. Fontsize: Approximate size in points (numeric, e.g., 48, 60).
4. PrimaryColour: Text color in ASS hex format (e.g. &H00FFFFFF for white).
5. Bold: -1 if bold, 0 otherwise.
6. Italic: -1 if italic, 0 otherwise.
7. Outline: Numeric outline thickness (e.g. 1.5).
8. Shadow: Numeric shadow size (e.g. 2).
9. Alignment: Number (1–9) representing ASS alignment code (e.g. 2 for bottom-center).
10. MarginV: Vertical margin in pixels from bottom if Alignment is 2.
11. figure_of_speech: What type of word is it? (e.g., noun, verb, adjective, interjection)if its nothing among them keep it others and if it has more than one break it into two objects of each words of a phrase.
12. importance_score: A float from 0 to 1 representing how visually or contextually important this word is.

Return the output as a JSON array. Each object should contain all 12 fields.
"""

# === HELPERS ===
def image_to_base64(image_path):
    with open(image_path, "rb") as img_file:
        return base64.b64encode(img_file.read()).decode("utf-8")

def extract_json_from_response(response_text):
    try:
        cleaned = re.sub(r"```(?:json)?\n(.*?)```", r"\1", response_text, flags=re.DOTALL).strip()
        cleaned = cleaned.replace("“", "\"").replace("”", "\"").replace("‘", "'").replace("’", "'").strip("`")
        if not cleaned.endswith(']'):
            cleaned += ']'
        if cleaned.count('{') > cleaned.count('}'):
            cleaned += '}' * (cleaned.count('{') - cleaned.count('}'))
        return json.loads(cleaned)
    except Exception as e:
        print("⚠️ JSON parsing failed. Raw response:")
        print(response_text[:300])
        return None

def build_ass_style(index, style):
    name = f"Style{index}"
    return f"Style: {name},{style['Fontname']},{style['Fontsize']},{style['PrimaryColour']},&H000000FF,&H00000000,&H00000000,{style['Bold']},{style['Italic']},0,0,100,100,0,0,1,{style['Outline']},{style['Shadow']},{style['Alignment']},20,20,{style['MarginV']},1"

# === MAIN ===
all_word_data = []
ass_lines = []

for idx, filename in enumerate(sorted(os.listdir(frames_dir))):
    if filename.lower().endswith(".png"):
        print(f"🔍 Processing: {filename}")
        image_path = os.path.join(frames_dir, filename)
        base64_img = image_to_base64(image_path)

        response = client.chat.completions.create(
            model=model_name,
            messages=[
                {"role": "system", "content": "You are an expert in subtitle typography and linguistics."},
                {"role": "user", "content": prompt},
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "image_url",
                            "image_url": {"url": f"data:image/png;base64,{base64_img}"}
                        }
                    ]
                }
            ]
        )

        result_text = response.choices[0].message.content
        parsed = extract_json_from_response(result_text)

        if parsed:
            for i, style in enumerate(parsed):
                try:
                    ass_line = build_ass_style(f"{idx+1}_{i+1}", style)
                    ass_lines.append(ass_line)

                    style["frame_id"] = f"{filename}"  # Add frame info to JSON
                    all_word_data.append(style)
                except Exception as e:
                    print(f"⚠️ Style error: {e}")
        else:
            print(f"⚠️ Skipped {filename} due to parse error.")

# === WRITE ASS FILE ===
if ass_lines:
    with open(output_ass_file, "w", encoding="utf-8") as f:
        f.write("[V4+ Styles]\n")
        f.write("Format: Name,Fontname,Fontsize,PrimaryColour,SecondaryColour,OutlineColour,BackColour,Bold,Italic,Underline,StrikeOut,ScaleX,ScaleY,Spacing,Angle,BorderStyle,Outline,Shadow,Alignment,MarginL,MarginR,MarginV,Encoding\n")
        for line in ass_lines:
            f.write(line + "\n")
    print(f"✅ ASS styles saved to: {output_ass_file}")
else:
    print("⚠️ No ASS lines generated.")

# === WRITE SINGLE JSON FILE ===
with open(output_json_file, "w", encoding="utf-8") as jf:
    json.dump(all_word_data, jf, indent=2)
    print(f"✅ All word data saved to: {output_json_file}")
