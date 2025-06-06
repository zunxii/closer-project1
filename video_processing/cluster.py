import re
import numpy as np
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler

# === CONFIG ===
INPUT_FILE = "ass_styles_output.ass"     # Your original .ass file with 50-60 styles
OUTPUT_FILE = "clustered_styles.ass"  # Output file with reduced styles
N_CLUSTERS = 5

# === HELPER FUNCTION: Convert &HAABBGGRR to RGB ===
def extract_rgb(ass_color):
    hex_color = ass_color.replace("&H", "").zfill(8)  # Pad to 8 characters if short
    bb = int(hex_color[2:4], 16)
    gg = int(hex_color[4:6], 16)
    rr = int(hex_color[6:8], 16)
    return rr, gg, bb

# === LOAD STYLES ===
with open(INPUT_FILE, "r", encoding="utf-8") as f:
    lines = f.readlines()

style_lines = []
style_vectors = []

for line in lines:
    if line.strip().startswith("Style:"):
        parts = line.strip().split(",")
        if len(parts) < 23:
            continue  # skip malformed lines

        try:
            name = parts[0].split(":")[1].strip()
            font = parts[1].strip()
            size = float(parts[2])
            primary_color = parts[3].strip()
            bold = int(parts[7])
            italic = int(parts[8])
            outline = float(parts[16])
            shadow = float(parts[17])
            align = int(parts[18])

            r, g, b = extract_rgb(primary_color)

            vector = [
                size / 100,                     # normalize font size
                1 if bold == -1 else 0,         # bold flag
                1 if italic == -1 else 0,       # italic flag
                outline / 5,                    # normalize outline
                shadow / 5,                     # normalize shadow
                align / 9,                      # normalize alignment (1–9)
                r / 255, g / 255, b / 255       # RGB normalized
            ]

            style_lines.append((line.strip(), name))
            style_vectors.append(vector)

        except Exception as e:
            print(f" Skipping line due to parse error: {line.strip()} -> {e}")

# === CLUSTERING ===
print(f"✅ Parsed {len(style_vectors)} styles. Clustering...")

X = np.array(style_vectors)
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

kmeans = KMeans(n_clusters=N_CLUSTERS, random_state=42)
labels = kmeans.fit_predict(X_scaled)

# === GET REPRESENTATIVE STYLES ===
cluster_styles = {}
for idx, label in enumerate(labels):
    if label not in cluster_styles:
        cluster_styles[label] = style_lines[idx]  # take first style in each cluster

# === WRITE NEW .ASS FILE ===
with open(OUTPUT_FILE, "w", encoding="utf-8") as out:
    out.write("[V4+ Styles]\n")
    out.write("Format: Name,Fontname,Fontsize,PrimaryColour,SecondaryColour,OutlineColour,BackColour,Bold,Italic,Underline,StrikeOut,ScaleX,ScaleY,Spacing,Angle,BorderStyle,Outline,Shadow,Alignment,MarginL,MarginR,MarginV,Encoding\n")
    for i, (line, old_name) in enumerate(cluster_styles.values()):
        new_name = f"ClusterStyle{i+1}"
        line = re.sub(r"Style:\s*[^,]+", f"Style: {new_name}", line)
        out.write(f"{line}\n")

print(f"🎉 Output written to {OUTPUT_FILE}")
