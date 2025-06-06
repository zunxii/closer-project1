import json
import random

fonts = [
    "Arial", "Verdana", "Georgia", "Tahoma", "Comic Sans MS",
    "Times New Roman", "Courier New", "Impact", "Trebuchet MS"
]

colors = [
    "&H00FF00FF",  # Magenta
    "&H0000FFFF",  # Yellow
    "&H00FF8000",  # Orange
    "&H0000FF00",  # Green
    "&H00FF0000",  # Blue
    "&H00800080",  # Purple
    "&H000080FF",  # Gold
    "&H000000FF",  # Red
    "&H00FFFFFF",  # White
    "&H00000000",  # Black
]

# Optional animated effects
animations = [
    "\\t(0,500,\\fs48)",         # grow size quickly
    "\\move(100,600,600,600)",  # move left to right
    "\\fad(200,200)",            # fade in/out
    "\\t(0,500,\\bord5)",        # expand border
    "\\t(0,500,\\blur3)"         # blur briefly
]

# Optional positions (x, y)
positions = [
    "\\pos(640,360)",  # center
]

styles = {}

for i in range(1, 13):  # Generate 12 styles
    style_name = f"Style{i}"
    styles[style_name] = {
        "font": random.choice(fonts),
        "fontsize": random.randint(28, 44),
        "primary_color": random.choice(colors),
        "bold": random.choice([0, 1]),
        "italic": random.choice([0, 1]),
        "border_style": 1,
        "outline": random.randint(1, 3),
        "shadow": random.randint(0, 2),
        "alignment": random.choice([1, 2, 3]),  # left, center, right
        "position": random.choice(positions),
        "animation": random.choice(animations)
    }

# Save to JSON
with open("style.json", "w", encoding="utf-8") as f:
    json.dump(styles, f, indent=2)

print("✅ style.json with 12 enhanced styles (with animation and positioning) created!")
