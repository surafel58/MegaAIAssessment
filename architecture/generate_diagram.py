"""
Generates architecture/system_diagram.png using only Pillow (no external graphviz).
Run: python architecture/generate_diagram.py
"""
from PIL import Image, ImageDraw, ImageFont
import os

W, H = 1200, 720
BG = "#0d1117"
BORDER = "#30363d"
ACCENT = "#00ff41"
BLUE = "#58a6ff"
ORANGE = "#f0883e"
PURPLE = "#bc8cff"
WHITE = "#e6edf3"
GREY = "#8b949e"
DARK = "#161b22"

img = Image.new("RGB", (W, H), BG)
draw = ImageDraw.Draw(img)

try:
    font_sm = ImageFont.truetype("arial.ttf", 13)
    font_md = ImageFont.truetype("arial.ttf", 15)
    font_lg = ImageFont.truetype("arial.ttf", 18)
    font_xl = ImageFont.truetype("arial.ttf", 22)
except Exception:
    font_sm = font_md = font_lg = font_xl = ImageFont.load_default()


def box(x, y, w, h, fill=DARK, outline=BORDER, radius=8):
    draw.rounded_rectangle([x, y, x + w, y + h], radius=radius, fill=fill, outline=outline, width=2)


def label(text, x, y, font=font_md, color=WHITE, anchor="lt"):
    draw.text((x, y), text, fill=color, font=font, anchor=anchor)


def arrow(x1, y1, x2, y2, color=GREY, width=2):
    draw.line([(x1, y1), (x2, y2)], fill=color, width=width)
    # arrowhead
    import math
    angle = math.atan2(y2 - y1, x2 - x1)
    size = 8
    ax1 = x2 - size * math.cos(angle - 0.4)
    ay1 = y2 - size * math.sin(angle - 0.4)
    ax2 = x2 - size * math.cos(angle + 0.4)
    ay2 = y2 - size * math.sin(angle + 0.4)
    draw.polygon([(x2, y2), (ax1, ay1), (ax2, ay2)], fill=color)


# ── Title ─────────────────────────────────────────────────────────────────────
label("Real-Time Face Detection — System Architecture", 40, 18, font=font_xl, color=ACCENT)
label("Docker Compose  ·  FastAPI  ·  MediaPipe BlazeFace  ·  Pillow  ·  PostgreSQL  ·  React",
      44, 48, font=font_sm, color=GREY)

# ── Column headers ─────────────────────────────────────────────────────────────
cols = [("Browser (React)", 40), ("Backend (FastAPI)", 330), ("PostgreSQL", 760), ("Docker", 1000)]
for title, cx in cols:
    color = BLUE if "React" in title else (ORANGE if "FastAPI" in title else (PURPLE if "Post" in title else GREY))
    label(title, cx, 80, font=font_lg, color=color)
    draw.line([(cx, 100), (cx + 220, 100)], fill=color, width=2)

# ── Browser column ─────────────────────────────────────────────────────────────
box(40, 115, 240, 55, outline=BLUE)
label("Webcam (getUserMedia)", 52, 128, font=font_sm, color=BLUE)
label("canvas → JPEG blob", 52, 146, font=font_sm, color=GREY)

box(40, 190, 240, 40, outline=BLUE)
label("WS Ingest Client", 130, 210, font=font_md, color=BLUE, anchor="mm")

box(40, 350, 240, 40, outline=BLUE)
label("Display Canvas", 160, 370, font=font_md, color=BLUE, anchor="mm")

box(40, 420, 240, 40, outline=BLUE)
label("WS Stream Client", 160, 440, font=font_md, color=BLUE, anchor="mm")

box(40, 510, 240, 40, outline=BLUE)
label("ROI Table (polls /api/roi)", 160, 530, font=font_md, color=BLUE, anchor="mm")

# ── Backend column ─────────────────────────────────────────────────────────────
box(330, 115, 380, 50, outline=ORANGE)
label("/ws/ingest", 340, 125, font=font_sm, color=ORANGE)
label("recv bytes → validate → dispatch", 340, 142, font=font_sm, color=GREY)

box(330, 185, 380, 75, outline=ORANGE)
label("frame_processor.py", 340, 195, font=font_sm, color=ORANGE)
label("  1. detect_face() [MediaPipe]", 340, 213, font=font_sm, color=GREY)
label("  2. draw_bounding_box() [Pillow]", 340, 229, font=font_sm, color=GREY)
label("  3. crud.insert_roi()", 340, 245, font=font_sm, color=GREY)

box(330, 280, 380, 40, outline=ORANGE)
label("asyncio.Queue (maxsize=2)", 520, 300, font=font_md, color=ORANGE, anchor="mm")

box(330, 340, 380, 50, outline=ORANGE)
label("/ws/stream", 340, 350, font=font_sm, color=ORANGE)
label("dequeue → send_bytes() to client", 340, 367, font=font_sm, color=GREY)

box(330, 410, 380, 40, outline=ORANGE)
label("/api/roi  [GET]", 340, 420, font=font_sm, color=ORANGE)
label("crud.get_roi_records() → JSON", 340, 437, font=font_sm, color=GREY)

box(330, 480, 380, 50, outline="#555")
label("MediaPipe BlazeFace  (no cv2)", 340, 490, font=font_sm, color=ACCENT)
label("Pillow ImageDraw.rectangle()", 340, 507, font=font_sm, color=GREY)

# ── DB column ─────────────────────────────────────────────────────────────────
box(760, 185, 200, 90, outline=PURPLE)
label("roi_detections", 860, 200, font=font_md, color=PURPLE, anchor="mm")
for i, col in enumerate(["id  UUID PK", "session_id", "frame_number", "bbox_x/y/w/h", "confidence", "timestamp"]):
    label(col, 772, 218 + i * 14, font=font_sm, color=GREY)

# ── Docker column ─────────────────────────────────────────────────────────────
box(1000, 115, 170, 55, fill="#0d2818", outline=ACCENT)
label("frontend", 1085, 125, font=font_md, color=ACCENT, anchor="mm")
label("node:20 → nginx:1.27", 1012, 143, font=font_sm, color=GREY)

box(1000, 195, 170, 55, fill="#1a1000", outline=ORANGE)
label("backend", 1085, 205, font=font_md, color=ORANGE, anchor="mm")
label("python:3.12-slim", 1018, 222, font=font_sm, color=GREY)

box(1000, 275, 170, 55, fill="#110020", outline=PURPLE)
label("db", 1085, 285, font=font_md, color=PURPLE, anchor="mm")
label("postgres:16-alpine", 1014, 302, font=font_sm, color=GREY)

label("pg_data volume", 1030, 345, font=font_sm, color=GREY)
label("health-check", 1042, 359, font=font_sm, color=GREY)

# Ports
for port, yd in [("3000", 135), ("8000", 215), ("5432", 295)]:
    label(f":{port}", 1175, yd, font=font_sm, color=GREY)

# ── Arrows ─────────────────────────────────────────────────────────────────────
# Webcam → ingest WS
arrow(160, 170, 160, 190, color=BLUE)
# Ingest WS client → /ws/ingest
arrow(280, 210, 330, 140, color=BLUE)
# frame_processor → Queue
arrow(520, 260, 520, 280, color=ORANGE)
# Queue → /ws/stream
arrow(520, 320, 520, 340, color=ORANGE)
# /ws/stream → stream WS client
arrow(330, 365, 280, 440, color=ORANGE)
# Stream client → display canvas
arrow(160, 460, 160, 480, color=GREY)
# ROI table → /api/roi
arrow(280, 530, 330, 430, color=BLUE)
# frame_processor → DB
arrow(710, 230, 760, 230, color=PURPLE)
# /api/roi → DB
arrow(710, 430, 760, 250, color=PURPLE)
# /ws/ingest → frame_processor
arrow(520, 165, 520, 185, color=ORANGE)

# ── Legend ─────────────────────────────────────────────────────────────────────
lx, ly = 40, 630
label("Legend:", lx, ly, font=font_sm, color=GREY)
for col, txt in [(BLUE, "Browser"), (ORANGE, "Backend"), (PURPLE, "Database"), (ACCENT, "No cv2")]:
    lx += 80
    draw.rectangle([lx, ly + 3, lx + 12, ly + 15], fill=col)
    label(txt, lx + 16, ly, font=font_sm, color=col)

# ── Save ───────────────────────────────────────────────────────────────────────
out_path = os.path.join(os.path.dirname(__file__), "system_diagram.png")
img.save(out_path)
print(f"Saved: {out_path}")
