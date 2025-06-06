import re
import json

# === CONFIG ===
ASS_FILE = "clustered_styles1.ass"
WORD_STYLE_JSON = "word_style_data.json"

# === HELPERS ===
def color_to_rgb_vector(ass_color):
    """
    Convert ASS color (&HBBGGRR format) to normalized RGB tuple.
    """
    hex_color = ass_color.replace("&H", "").zfill(8)
    bb = int(hex_color[2:4], 16)
    gg = int(hex_color[4:6], 16)
    rr = int(hex_color[6:8], 16)
    return [rr / 255, gg / 255, bb / 255]

def style_to_vector(style_dict):
    """
    Convert a style dictionary into a feature vector.
    """
    vector = [
        style_dict.get("Fontsize", 0) / 100,
        1 if style_dict.get("Bold", 0) == -1 else 0,
        1 if style_dict.get("Italic", 0) == -1 else 0,
        style_dict.get("Outline", 0) / 5,
        style_dict.get("Shadow", 0) / 5,
        style_dict.get("Alignment", 5) / 9,
        style_dict.get("MarginV", 0) / 100,
    ]
    rgb = color_to_rgb_vector(style_dict.get("PrimaryColour", "&H00FFFFFF"))
    return vector + rgb

def parse_ass_styles(file_path):
    """
    Parse styles from a .ASS file and convert to vectors.
    Returns: dict {style_name: vector}
    """
    style_vectors = {}
    with open(file_path, "r", encoding="utf-8") as f:
        for line in f:
            if line.startswith("Style:"):
                parts = line.strip().split(",")
                if len(parts) < 24:
                    continue
                style = {
                    "Name": parts[0].split(":")[1].strip(),
                    "Fontname": parts[1].strip(),
                    "Fontsize": float(parts[2]),
                    "PrimaryColour": parts[3],
                    "Bold": int(parts[7]),
                    "Italic": int(parts[8]),
                    "Outline": float(parts[16]),
                    "Shadow": float(parts[17]),
                    "Alignment": int(parts[18]),
                    "MarginV": int(parts[21])
                }
                vector = style_to_vector(style)
                style_vectors[style["Name"]] = vector
    return style_vectors

def parse_word_style_data(json_file):
    """
    Parse word style JSON and return list of tuples (word, style_vector, metadata)
    """
    with open(json_file, "r", encoding="utf-8") as f:
        word_data = json.load(f)

    word_vectors = []
    for entry in word_data:
        style = entry.get("style", {})
        word = entry.get("word", "")
        metadata = {
            "figure_of_speech": entry.get("figure_of_speech"),
            "importance_score": entry.get("importance_score")
        }
        vector = style_to_vector(style)
        word_vectors.append((word, vector, metadata))

    return word_vectors
