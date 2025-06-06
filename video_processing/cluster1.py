import re
import numpy as np
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.decomposition import PCA
import matplotlib.pyplot as plt
import sklearn

# === CONFIG ===
INPUT_FILE = "ass_styles_output.ass"
OUTPUT_FILE = "clustered_styles1.ass"
N_CLUSTERS = 6

def extract_rgb(ass_color):
    hex_color = ass_color.replace("&H", "").zfill(8)
    bb = int(hex_color[2:4], 16)
    gg = int(hex_color[4:6], 16)
    rr = int(hex_color[6:8], 16)
    return rr, gg, bb

# === LOAD STYLES ===
with open(INPUT_FILE, "r", encoding="utf-8") as f:
    lines = f.readlines()

style_lines = []
fonts = []
numeric_vectors = []

for line in lines:
    if line.strip().startswith("Style:"):
        parts = line.strip().split(",")
        if len(parts) < 23:
            continue
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

            numeric_vector = [
                size / 100,                   # normalized font size
                1 if bold == -1 else 0,       # bold flag
                1 if italic == -1 else 0,     # italic flag
                outline / 5,                  # normalized outline
                shadow / 5,                   # normalized shadow
                align / 9,                    # normalized alignment
                r / 255, g / 255, b / 255    # normalized RGB
            ]

            style_lines.append((line.strip(), name))
            fonts.append([font])  # 2D list for encoder
            numeric_vectors.append(numeric_vector)
        except Exception as e:
            print(f"Skipping line due to parse error: {line.strip()} -> {e}")

print(f"Parsed {len(numeric_vectors)} styles.")

# === ENCODE FONT NAMES ===
print(f"scikit-learn version: {sklearn.__version__}")
try:
    onehot_encoder = OneHotEncoder(sparse_output=False)
    font_encoded = onehot_encoder.fit_transform(fonts)
except TypeError:
    onehot_encoder = OneHotEncoder()
    font_encoded_sparse = onehot_encoder.fit_transform(fonts)
    font_encoded = font_encoded_sparse.toarray()

# === COMBINE FEATURES ===
X_numeric = np.array(numeric_vectors)
X_combined = np.hstack((X_numeric, font_encoded))

# === SCALE FEATURES ===
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X_combined)

# === CLUSTERING ===
kmeans = KMeans(n_clusters=N_CLUSTERS, random_state=42)
labels = kmeans.fit_predict(X_scaled)

# === GET REPRESENTATIVE STYLES ===
cluster_styles = {}
for idx, label in enumerate(labels):
    if label not in cluster_styles:
        cluster_styles[label] = style_lines[idx]

# === WRITE NEW .ASS FILE ===
with open(OUTPUT_FILE, "w", encoding="utf-8") as out:
    out.write("[V4+ Styles]\n")
    out.write("Format: Name,Fontname,Fontsize,PrimaryColour,SecondaryColour,OutlineColour,BackColour,Bold,Italic,Underline,StrikeOut,ScaleX,ScaleY,Spacing,Angle,BorderStyle,Outline,Shadow,Alignment,MarginL,MarginR,MarginV,Encoding\n")
    for i, (line, old_name) in enumerate(cluster_styles.values()):
        new_name = f"ClusterStyle{i+1}"
        line = re.sub(r"Style:\s*[^,]+", f"Style: {new_name}", line)
        out.write(f"{line}\n")

print(f"🎉 Output written to {OUTPUT_FILE}")

# === VISUALIZATION ===
pca = PCA(n_components=2)
X_pca = pca.fit_transform(X_scaled)

plt.figure(figsize=(10, 7))
scatter = plt.scatter(X_pca[:, 0], X_pca[:, 1], c=labels, cmap='tab10', alpha=0.7)
plt.legend(*scatter.legend_elements(), title="Clusters")
plt.title("Style Clusters Visualization (PCA 2D)")
plt.xlabel("PCA Component 1")
plt.ylabel("PCA Component 2")
plt.grid(True)
plt.show()
