import json
import numpy as np
import matplotlib.pyplot as plt
from collections import defaultdict


def parse_ass_styles(path):
    with open(path, "r", encoding="utf-8") as f:
        lines = f.readlines()
    styles = {}
    for line in lines:
        if line.startswith("Style:"):
            parts = line.strip().split(",")
            name = parts[0].split(":")[1].strip()
            styles[name] = {
                "Fontname": parts[1],
                "Fontsize": float(parts[2]),
                "PrimaryColour": parts[3]
            }
    return styles


def hex_to_rgb(h):
    h = h[2:] if h.startswith("&H") else "FFFFFF"
    if len(h) != 6:
        h = "FFFFFF"
    b, g, r = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
    return r, g, b


def style_to_vector(s):
    fontname_val = sum(ord(c) for c in s.get("Fontname", ""))
    size = s.get("Fontsize", 0)
    r, g, b = hex_to_rgb(s.get("PrimaryColour", "&H00FFFFFF"))
    return np.array([fontname_val, size, r, g, b])


def word_to_vector(word):
    # Convert word's style properties (assumed keys) to vector like styles
    fontname_val = sum(ord(c) for c in word.get("Fontname", ""))
    size = word.get("Fontsize", 0)
    r, g, b = word.get("Color", (255, 255, 255))  # color as RGB tuple expected in JSON
    return np.array([fontname_val, size, r, g, b])


def assign_styles_to_clusters(style_vectors, n_clusters=3, n_iters=10):
    centroids = style_vectors[np.random.choice(len(style_vectors), n_clusters, replace=False)]

    for _ in range(n_iters):
        clusters = defaultdict(list)
        for i, vec in enumerate(style_vectors):
            dists = np.linalg.norm(centroids - vec, axis=1)
            cluster_idx = np.argmin(dists)
            clusters[cluster_idx].append(i)

        new_centroids = []
        for k in range(n_clusters):
            if clusters[k]:
                new_centroids.append(np.mean(style_vectors[clusters[k]], axis=0))
            else:
                new_centroids.append(centroids[k])
        centroids = np.array(new_centroids)

    return clusters, centroids


def assign_words_to_clusters(words, centroids):
    clusters = defaultdict(list)
    for w in words:
        vec = word_to_vector(w)
        dists = np.linalg.norm(centroids - vec, axis=1)
        cluster_idx = np.argmin(dists)
        clusters[cluster_idx].append(w)
    return clusters


def visualize_words_clusters(word_clusters):
    colors = ['r', 'g', 'b', 'c', 'm', 'y']
    plt.figure(figsize=(12, 7))

    for cluster_idx, words in word_clusters.items():
        x = [sum(ord(c) for c in w.get("Fontname", "")) for w in words]
        y = [w.get("Fontsize", 0) for w in words]
        plt.scatter(x, y, color=colors[cluster_idx % len(colors)], label=f"Cluster {cluster_idx}", alpha=0.7)

        for i, w in enumerate(words):
            text = w.get("text", "")  # assuming words have a 'text' field
            plt.annotate(text, (x[i], y[i]), fontsize=7, alpha=0.7)

    plt.xlabel("Fontname Sum (ASCII)")
    plt.ylabel("Font Size")
    plt.title("Words clustered by style")
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.show()


def main():
    styles = parse_ass_styles("clustered_styles1.ass")
    style_vectors = np.array([style_to_vector(s) for s in styles.values()])

    style_clusters, centroids = assign_styles_to_clusters(style_vectors, n_clusters=3, n_iters=20)

    with open("word_style_data.json", "r", encoding="utf-8") as f:
        words = json.load(f)

    word_clusters = assign_words_to_clusters(words, centroids)

    visualize_words_clusters(word_clusters)


if __name__ == "__main__":
    main()
