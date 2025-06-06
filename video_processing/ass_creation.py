import json
import os
from sklearn.cluster import KMeans
import numpy as np
import re

# -------------------
def parse_rgb_color(color_str):
    """Parse RGB color string and return (r, g, b) tuple"""
    if not isinstance(color_str, str):
        return (255, 255, 255)  # default to white
    
    # Handle both rgb(r,g,b) and RGB(r,g,b) formats
    match = re.match(r'rgb\((\d+),\s*(\d+),\s*(\d+)\)', color_str.lower())
    if match:
        return (int(match.group(1)), int(match.group(2)), int(match.group(3)))
    
    # If not in RGB format, default to white
    return (255, 255, 255)

def rgb_to_ass_color(r, g, b):
    """Convert RGB values to ASS color format (&HBBGGRR)"""
    return f"&H00{b:02X}{g:02X}{r:02X}"

def style_to_vector(style):
    # Add debugging to see what we're getting
    if not isinstance(style, dict):
        print(f"Error: Expected dict, got {type(style)}: {style}")
        return None
    
    if "position" not in style:
        print(f"Error: No position in style: {style}")
        return None
    
    size_map = {"small": 0, "medium": 1, "large": 2}
    weight_map = {"thin": 0, "regular": 1, "bold": 2}

    top = style["position"]["top"] / 1080
    left = style["position"]["left"] / 1920
    width = style["position"]["width"] / 1920
    height = style["position"]["height"] / 1080

    size = size_map.get(style.get("font_size", "medium").lower(), 1)
    weight = weight_map.get(style.get("font_weight", "regular").lower(), 1)
    
    # Parse RGB color and convert to normalized values for clustering
    r, g, b = parse_rgb_color(style.get("text_color", "rgb(255, 255, 255)"))
    color_r = r / 255.0
    color_g = g / 255.0
    color_b = b / 255.0

    return [
        size,
        weight,
        color_r,
        color_g,
        color_b,
        top,
        left,
        width,
        height,
    ]

# -------------------
def cluster_styles(styles, n_clusters=5):
    # Filter out None values from style_to_vector
    vectors_data = []
    valid_styles = []
    
    for s in styles:
        vector = style_to_vector(s)
        if vector is not None:
            vectors_data.append(vector)
            valid_styles.append(s)
    
    if not vectors_data:
        print("Error: No valid style vectors found")
        return []
    
    vectors = np.array(vectors_data)
    kmeans = KMeans(n_clusters=min(n_clusters, len(vectors)), random_state=42, n_init=10)
    kmeans.fit(vectors)
    labels = kmeans.labels_

    templates = []
    for i in range(kmeans.n_clusters):
        cluster_indices = np.where(labels == i)[0]
        cluster_styles = [valid_styles[idx] for idx in cluster_indices]
        if not cluster_styles:
            continue
            
        avg_vector = np.mean([vectors[idx] for idx in cluster_indices], axis=0)

        def nearest(mapping, val):
            keys = list(mapping.keys())
            vals = list(mapping.values())
            closest = min(vals, key=lambda x: abs(x - val))
            return keys[vals.index(closest)]

        # Convert averaged RGB values back to 0-255 range
        avg_r = int(avg_vector[2] * 255)
        avg_g = int(avg_vector[3] * 255)
        avg_b = int(avg_vector[4] * 255)

        template_style = {
            "font_size": nearest({"small": 0, "medium": 1, "large": 2}, avg_vector[0]),
            "font_weight": nearest({"thin": 0, "regular": 1, "bold": 2}, avg_vector[1]),
            "font_type": cluster_styles[0].get("font_font", cluster_styles[0].get("font_type", "Arial")),  # handle both font_font and font_type
            "text_color_rgb": (avg_r, avg_g, avg_b),  # Store as RGB tuple
            "position": {
                "top": int(avg_vector[5] * 1080),
                "left": int(avg_vector[6] * 1920),
                "width": int(avg_vector[7] * 1920),
                "height": int(avg_vector[8] * 1080),
            },
        }
        templates.append(template_style)
    return templates

# -------------------
def style_to_ass_style(name, style):
    size_map = {"small": 35, "medium": 50, "large": 65}
    font_size = size_map.get(style["font_size"], 50)

    bold = -1 if style["font_weight"] == "bold" else 0
    italic = 1 if style["font_weight"] == "bold" else 0
    font_family = style.get("font_type", "Arial")

    # Use the exact RGB color from clustering
    r, g, b = style.get("text_color_rgb", (255, 255, 255))
    primary_color = rgb_to_ass_color(r, g, b)

    return (
        f"Style: {name},{font_family},{font_size},{primary_color},&H000000FF,&H00000000,&H64000000,"
        f"{bold},{italic},0,0,100,100,0,0,1,2,0,2,20,20,20,1"
    )

# -------------------
def escape_ass_text(text):
    return text.replace("{", "\\{").replace("}", "\\}").replace("\n", "\\N").replace(",", "\\,")

# -------------------
def group_words_to_lines(words, max_chars_per_line=15, max_lines_per_box=2):
    chunks = []
    current_lines = []
    current_line = ""
    start_time = None
    end_time = None

    def flush_lines():
        nonlocal current_lines, start_time, end_time
        if current_lines:
            text = "\\N".join(current_lines)
            chunks.append({
                "text": text,
                "start": start_time or 0,
                "end": end_time or 0
            })
            current_lines = []
            start_time = None
            end_time = None

    for word in words:
        word_text = word["text"]
        word_len = len(word_text)

        if start_time is None:
            start_time = word["start"] / 1000

        if not current_line:
            if word_len <= max_chars_per_line:
                current_line = word_text
            else:
                current_line = word_text[:max_chars_per_line]  # fallback for extreme cases
        else:
            if len(current_line) + 1 + word_len <= max_chars_per_line:
                current_line += " " + word_text
            else:
                current_lines.append(current_line)
                if len(current_lines) == max_lines_per_box:
                    end_time = word["end"] / 1000
                    flush_lines()
                current_line = word_text

        end_time = word["end"] / 1000

    if current_line:
        current_lines.append(current_line)
    if current_lines:
        flush_lines()

    return chunks

# -------------------
def generate_ass(transcription, templates):
    script_info = (
        "[Script Info]\n"
        "Title: Generated Subtitles\n"
        "ScriptType: v4.00+\n"
        "PlayResX: 1920\n"
        "PlayResY: 1080\n"
        "Timer: 100.0000\n\n"
    )

    styles_header = "[V4+ Styles]\nFormat: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding\n"
    styles = ""
    for i, template in enumerate(templates):
        style_name = f"Style{i+1}"
        styles += style_to_ass_style(style_name, template) + "\n"

    events_header = "[Events]\nFormat: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text\n"
    lines = group_words_to_lines(transcription["words"], max_chars_per_line=15, max_lines_per_box=2)

    dialogues = ""
    for idx, line in enumerate(lines):
        style_name = f"Style{(idx % len(templates)) + 1}"

        def format_time(t):
            h = int(t // 3600)
            m = int((t % 3600) // 60)
            s = int(t % 60)
            cs = int((t - int(t)) * 100)
            return f"{h}:{m:02d}:{s:02d}.{cs:02d}"

        start_str = format_time(line["start"])
        end_str = format_time(line["end"])
        text = escape_ass_text(line["text"])

        dialogues += f"Dialogue: 0,{start_str},{end_str},{style_name},,0,0,0,,{text}\n"

    return script_info + styles_header + styles + "\n" + events_header + dialogues

# -------------------
def main():
    dir_path = os.path.dirname(os.path.realpath(__file__))
    transcription_file = os.path.join(dir_path, "transcription_result.json")
    style_file = os.path.join(dir_path, "style_analysis_all1.json")
    output_ass = os.path.join(dir_path, "output1.ass")

    with open(transcription_file, "r", encoding="utf-8") as f:
        transcription = json.load(f)
    with open(style_file, "r", encoding="utf-8") as f:
        styles_json = json.load(f)

    all_styles = []
    for frame in styles_json:
        all_styles.extend(frame["analysis"])

    templates = cluster_styles(all_styles, n_clusters=5)
    ass_content = generate_ass(transcription, templates)

    with open(output_ass, "w", encoding="utf-8") as f:
        f.write(ass_content)

    print(f".ass subtitle file generated: {output_ass}")

if __name__ == "__main__":
    main()