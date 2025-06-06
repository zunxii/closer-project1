import json
import numpy as np
import matplotlib.pyplot as plt
from collections import defaultdict, Counter


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
    if len(h) != 6: h = "FFFFFF"
    b, g, r = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
    return r, g, b


def style_to_vector(s):
    fontname = sum(ord(c) for c in s.get("Fontname", ""))
    size = s.get("Fontsize", 0)
    r, g, b = hex_to_rgb(s.get("PrimaryColour", "&H00FFFFFF"))
    return np.array([fontname, size, r, g, b])


def load_word_data(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def createWordDataVector(obj, all_figures=["noun", "verb", "adjective", "adverb", "pronoun", "preposition"]):
    vec = np.zeros(len(all_figures), dtype=int)
    fos = obj.get("figure_of_speech")
    if fos in all_figures:
        idx = all_figures.index(fos)
        vec[idx] = 1
    return vec

def assign_clusters(word_data, style_vectors):
    clusters = defaultdict(list)
    for w in word_data:
        vec = style_to_vector(w)
        word_vector = createWordDataVector(w,all_figures=["noun", "verb", "adjective", "adverb", "pronoun", "preposition"])
        
        dists = [np.linalg.norm(vec - v) for v in style_vectors]
        idx = np.argmin(dists)


        clusters[idx].append(word_vector)
    return clusters


def calc_centroids(clusters):
    centroids = {}
    for k, words in clusters.items():
        scores = [w.get("importance_score", 0) for w in words if w.get("importance_score") is not None]
        figs = [w["figure_of_speech"] for w in words if "figure_of_speech" in w]
        avg_score = sum(scores) / len(scores) if scores else None
        top_fig = Counter(figs).most_common(1)[0][0] if figs else None
        centroids[k] = {"importance_score": avg_score, "figure_of_speech": top_fig}
    return centroids


def visualize(clusters):
    colors = ['r','g','b','c','m','y']
    plt.figure()
    # for i, (k, words) in enumerate(clusters.items()):
    #     x = [sum(ord(c) for c in w.get("Fontname", "")) for w in words]
    #     y = [w.get("importance_score", 0) for w in words]
    #     plt.scatter(x, y, c=colors[i%6], label=f"Cluster {k}")

    for x in clusters:

        x_scores = [w[0] for w in clusters[x]]
        y_scores = [w[1] for w in clusters[x]]
        plt.scatter(x_scores, y_scores, c=colors[x % len(colors)], label=f"Cluster {x}", alpha=0.6)

    plt.legend()
    plt.xlabel("Font Name Score")
    plt.ylabel("Importance Score")
    plt.title("Word Clusters")
    plt.tight_layout()
    plt.show()


def main():
    styles = parse_ass_styles("clustered_styles1.ass")
    style_vectors = [style_to_vector(s) for s in styles.values()]
    words = load_word_data("word_style_data.json")
    clusters = assign_clusters(words, style_vectors) 
    # centroids = calc_centroids(clusters)
    # for k, c in centroids.items():
    #     print(f"Cluster {k}: Score={c['importance_score']}, POS={c['figure_of_speech']}")
    visualize(clusters)


if __name__ == "__main__":
    main()
