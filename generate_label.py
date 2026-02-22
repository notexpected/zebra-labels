#!/usr/bin/env python3
"""Generate a shojo-themed sticker label for Zebra GX420d (203dpi, 4x6)."""

import math
import random
from PIL import Image, ImageDraw, ImageFont

# --- Config ---
DPI = 203
WIDTH = 812   # 4" * 203dpi
HEIGHT = 1218  # 6" * 203dpi

NAME_FONT_PATH = "/usr/share/fonts/OTF/SpaceGrotesk-Bold.otf"
QUOTE_FONT_PATH = "/usr/share/fonts/liberation/LiberationSerif-Italic.ttf"

OUTPUT_ZPL = "adrienne-label.zpl"
OUTPUT_PNG = "adrienne-label-preview.png"

random.seed(77)


# ── Drawing primitives ───────────────────────────────────────────────

def draw_heart(draw, cx, cy, size):
    """Draw a filled heart shape."""
    pts = []
    for deg in range(360):
        t = math.radians(deg)
        x = 16 * math.sin(t) ** 3
        y = -(13 * math.cos(t) - 5 * math.cos(2*t) - 2 * math.cos(3*t) - math.cos(4*t))
        pts.append((cx + x * size / 16, cy + y * size / 16))
    draw.polygon(pts, fill="black")


def draw_heart_outline(draw, cx, cy, size, width=2):
    """Draw a heart outline only."""
    pts = []
    for deg in range(0, 360, 2):
        t = math.radians(deg)
        x = 16 * math.sin(t) ** 3
        y = -(13 * math.cos(t) - 5 * math.cos(2*t) - 2 * math.cos(3*t) - math.cos(4*t))
        pts.append((cx + x * size / 16, cy + y * size / 16))
    pts.append(pts[0])
    draw.line(pts, fill="black", width=width)


def draw_sparkle(draw, cx, cy, size):
    """Draw a 4-pointed sparkle/star."""
    # Vertical spike
    draw.polygon([
        (cx, cy - size),
        (cx + size * 0.15, cy),
        (cx, cy + size),
        (cx - size * 0.15, cy),
    ], fill="black")
    # Horizontal spike
    draw.polygon([
        (cx - size, cy),
        (cx, cy - size * 0.15),
        (cx + size, cy),
        (cx, cy + size * 0.15),
    ], fill="black")
    # Small diagonal ticks
    d = size * 0.5
    w = 1
    draw.line([(cx - d, cy - d), (cx + d, cy + d)], fill="black", width=w)
    draw.line([(cx + d, cy - d), (cx - d, cy + d)], fill="black", width=w)


def draw_star(draw, cx, cy, outer_r, inner_r=None, points=5):
    """Draw a filled star."""
    if inner_r is None:
        inner_r = outer_r * 0.4
    pts = []
    for i in range(points * 2):
        angle = math.pi / 2 + (math.pi / points) * i
        r = outer_r if i % 2 == 0 else inner_r
        pts.append((cx + math.cos(angle) * r, cy - math.sin(angle) * r))
    draw.polygon(pts, fill="black")


def draw_rose(draw, cx, cy, size):
    """Draw a stylized rose with spiral petals."""
    # Outer petals (overlapping circles suggesting petals)
    petal_r = size * 0.45
    for i in range(5):
        angle = (2 * math.pi / 5) * i - math.pi / 2
        px = cx + math.cos(angle) * size * 0.3
        py = cy + math.sin(angle) * size * 0.3
        # Draw petal as an arc/crescent
        bbox = [px - petal_r, py - petal_r, px + petal_r, py + petal_r]
        start = math.degrees(angle) - 60
        draw.arc(bbox, start, start + 120, fill="black", width=2)

    # Inner spiral
    for i in range(3):
        angle = (2 * math.pi / 3) * i
        ir = size * 0.18
        px = cx + math.cos(angle) * ir * 0.5
        py = cy + math.sin(angle) * ir * 0.5
        bbox = [px - ir, py - ir, px + ir, py + ir]
        start = math.degrees(angle)
        draw.arc(bbox, start, start + 200, fill="black", width=2)

    # Center dot
    draw.ellipse([cx - 2, cy - 2, cx + 2, cy + 2], fill="black")


def draw_rose_filled(draw, cx, cy, size):
    """Draw a more filled/bold rose for the border."""
    # Outer petals
    n_petals = 6
    for i in range(n_petals):
        angle = (2 * math.pi / n_petals) * i
        px = cx + math.cos(angle) * size * 0.35
        py = cy + math.sin(angle) * size * 0.35
        pr = size * 0.38
        draw.ellipse([px - pr, py - pr, px + pr, py + pr], outline="black", width=2)

    # Center filled circle
    cr = size * 0.25
    draw.ellipse([cx - cr, cy - cr, cx + cr, cy + cr], fill="black")
    # White spiral detail
    ir = cr * 0.5
    draw.arc([cx - ir, cy - ir, cx + ir, cy + ir], 0, 270, fill="white", width=1)


def draw_ribbon_bow(draw, cx, cy, size):
    """Draw a cute ribbon/bow."""
    loop_w = size * 0.5
    loop_h = size * 0.35
    # Left loop
    draw.ellipse([cx - loop_w - 2, cy - loop_h, cx - 2, cy + loop_h],
                 outline="black", width=2)
    # Right loop
    draw.ellipse([cx + 2, cy - loop_h, cx + loop_w + 2, cy + loop_h],
                 outline="black", width=2)
    # Center knot
    k = size * 0.1
    draw.ellipse([cx - k, cy - k, cx + k, cy + k], fill="black")
    # Tails
    draw.line([(cx - 3, cy + k), (cx - size * 0.3, cy + size * 0.5)],
              fill="black", width=2)
    draw.line([(cx + 3, cy + k), (cx + size * 0.3, cy + size * 0.5)],
              fill="black", width=2)


def draw_crescent_moon(draw, cx, cy, size):
    """Draw a crescent moon."""
    r = size
    draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill="black")
    # Cut out inner circle offset to the right
    offset = r * 0.45
    cut_r = r * 0.85
    draw.ellipse([cx - cut_r + offset, cy - cut_r,
                  cx + cut_r + offset, cy + cut_r], fill="white")


def draw_manga_flower(draw, cx, cy, size, petals=5):
    """Draw a simple manga-style 5-petal flower."""
    petal_r = size * 0.4
    for i in range(petals):
        angle = (2 * math.pi / petals) * i - math.pi / 2
        px = cx + math.cos(angle) * size * 0.35
        py = cy + math.sin(angle) * size * 0.35
        draw.ellipse([px - petal_r, py - petal_r, px + petal_r, py + petal_r],
                     outline="black", width=2)
    # Center
    cr = size * 0.15
    draw.ellipse([cx - cr, cy - cr, cx + cr, cy + cr], fill="black")


def draw_chibi_cat_face(draw, cx, cy, size):
    """Draw a tiny kawaii cat face."""
    r = size * 0.4
    # Face circle
    draw.ellipse([cx - r, cy - r, cx + r, cy + r], outline="black", width=2)
    # Ears (triangles)
    ear_h = r * 0.7
    ear_w = r * 0.5
    # Left ear
    draw.polygon([
        (cx - r * 0.7, cy - r * 0.6),
        (cx - r * 0.9, cy - r - ear_h),
        (cx - r * 0.1, cy - r * 0.8),
    ], fill="black")
    # Right ear
    draw.polygon([
        (cx + r * 0.7, cy - r * 0.6),
        (cx + r * 0.9, cy - r - ear_h),
        (cx + r * 0.1, cy - r * 0.8),
    ], fill="black")
    # Eyes (dots)
    eye_y = cy - r * 0.1
    draw.ellipse([cx - r * 0.4 - 2, eye_y - 2, cx - r * 0.4 + 2, eye_y + 2],
                 fill="black")
    draw.ellipse([cx + r * 0.4 - 2, eye_y - 2, cx + r * 0.4 + 2, eye_y + 2],
                 fill="black")
    # Mouth (w shape)
    my = cy + r * 0.2
    draw.line([(cx - 3, my), (cx, my + 3), (cx + 3, my)], fill="black", width=1)
    # Whiskers
    wy = cy + r * 0.05
    for sign in [-1, 1]:
        draw.line([(cx + sign * r * 0.3, wy - 2),
                   (cx + sign * r * 0.9, wy - 5)], fill="black", width=1)
        draw.line([(cx + sign * r * 0.3, wy + 1),
                   (cx + sign * r * 0.9, wy + 3)], fill="black", width=1)


# ── Border ───────────────────────────────────────────────────────────

def draw_border(draw):
    """Draw a shojo-themed border with roses, hearts, and decorative lines."""
    margin = 40

    # Double-line frame
    draw.rectangle([margin, margin, WIDTH - margin, HEIGHT - margin],
                   outline="black", width=2)
    inner = margin + 8
    draw.rectangle([inner, inner, WIDTH - inner, HEIGHT - inner],
                   outline="black", width=1)

    # Corner roses (large)
    for cx, cy in [(margin, margin), (WIDTH - margin, margin),
                   (margin, HEIGHT - margin), (WIDTH - margin, HEIGHT - margin)]:
        draw_rose_filled(draw, cx, cy, 30)

    # Hearts along top and bottom
    for edge_y in [margin, HEIGHT - margin]:
        spacing = (WIDTH - 2 * margin) / 6
        for i in range(1, 6):
            hx = margin + spacing * i
            s = 10 + (i % 2) * 4
            if i % 2 == 0:
                draw_heart(draw, hx, edge_y, s)
            else:
                draw_heart_outline(draw, hx, edge_y, s)

    # Stars and sparkles along left and right
    for edge_x in [margin, WIDTH - margin]:
        spacing = (HEIGHT - 2 * margin) / 8
        for i in range(1, 8):
            sy = margin + spacing * i
            if i % 3 == 0:
                draw_sparkle(draw, edge_x, sy, 12)
            elif i % 3 == 1:
                draw_star(draw, edge_x, sy, 10)
            else:
                draw_heart(draw, edge_x, sy, 8)

    # Small dots along the inner frame for screen-tone effect
    for edge_y in [inner, HEIGHT - inner]:
        for i in range(0, WIDTH - 2 * inner, 12):
            dx = inner + i
            draw.ellipse([dx - 1, edge_y - 1, dx + 1, edge_y + 1], fill="black")
    for edge_x in [inner, WIDTH - inner]:
        for i in range(0, HEIGHT - 2 * inner, 12):
            dy = inner + i
            draw.ellipse([edge_x - 1, dy - 1, edge_x + 1, dy + 1], fill="black")


# ── Rotated text ─────────────────────────────────────────────────────

def draw_rotated_text(img, text, font, cx, cy, angle_deg):
    """Render text onto img at (cx, cy) rotated by angle_deg.
    Returns bounding box (x0, y0, x1, y1) on img."""
    tmp = Image.new("RGBA", (1, 1), (255, 255, 255, 0))
    tmp_d = ImageDraw.Draw(tmp)
    bbox = tmp_d.textbbox((0, 0), text, font=font)
    tw = bbox[2] - bbox[0] + 4
    th = bbox[3] - bbox[1] + 4

    txt_img = Image.new("RGBA", (tw, th), (255, 255, 255, 0))
    txt_draw = ImageDraw.Draw(txt_img)
    txt_draw.text((-bbox[0] + 2, -bbox[1] + 2), text, fill="black", font=font)

    rotated = txt_img.rotate(angle_deg, expand=True, resample=Image.BICUBIC)
    rw, rh = rotated.size
    px = int(cx - rw / 2)
    py = int(cy - rh / 2)

    img.paste(rotated, (px, py), rotated)
    return (px, py, px + rw, py + rh)


def boxes_overlap(a, b):
    return not (a[2] < b[0] or b[2] < a[0] or a[3] < b[1] or b[3] < a[1])


# ── ZPL conversion ──────────────────────────────────────────────────

def image_to_zpl_gf(img):
    """Convert a 1-bit PIL Image to ZPL ^GF command."""
    img = img.convert("1")
    width_px = img.width
    height_px = img.height
    bytes_per_row = (width_px + 7) // 8
    total_bytes = bytes_per_row * height_px

    pixels = img.load()
    hex_data = []

    for y in range(height_px):
        row_bits = []
        for x in range(width_px):
            pixel = pixels[x, y]
            row_bits.append("1" if pixel == 0 else "0")
        while len(row_bits) % 8 != 0:
            row_bits.append("0")
        for i in range(0, len(row_bits), 8):
            byte_str = "".join(row_bits[i:i+8])
            hex_data.append(f"{int(byte_str, 2):02X}")

    hex_string = "".join(hex_data)
    zpl = (
        f"^XA\n"
        f"~SD25\n"
        f"^PR2,2,2\n"
        f"^FO0,0\n"
        f"^GFA,{total_bytes},{total_bytes},{bytes_per_row},{hex_string}\n"
        f"^FS\n"
        f"^XZ\n"
    )
    return zpl


# ── Quotes ───────────────────────────────────────────────────────────

SHOJO_QUOTES = [
    # Sailor Moon
    '"In the name of the Moon!"',
    '"Moon Prism Power!"',
    '"Miracle Romance"',
    '"Fighting evil by moonlight"',
    # Cardcaptor Sakura
    '"Everything will be alright"',
    # Fruits Basket
    '"Even so, I will keep trying"',
    '"The most important memories"',
    # Ouran
    '"Kiss kiss fall in love"',
    # Revolutionary Girl Utena
    '"Grant me the power to revolutionize the world"',
    # General shojo vibes
    '"Believe in yourself"',
    '"The power of love"',
    '"Magical Girl"',
    '"Sparkle!"',
    '"Dream on!"',
    # Japanese snippets
    '"愛してる"',
    '"魔法少女"',
    '"月に代わっておしおきよ"',
    '"友情"',
    '"きらきら"',
    '"すてき"',
    '"がんばれ"',
    '"夢"',
    '"希望"',
    '"奇跡"',
    '"かわいい"',
    '"変身!"',
    '"乙女"',
    '"薔薇"',
    '"星の力"',
]


# ── Main ─────────────────────────────────────────────────────────────

def main():
    img = Image.new("RGB", (WIDTH, HEIGHT), "white")
    draw = ImageDraw.Draw(img)

    # Border
    draw_border(draw)

    # --- Name centered, rotated 90° ---
    name_font = ImageFont.truetype(NAME_FONT_PATH, 100)
    name_box = draw_rotated_text(
        img, "Adrienne", name_font,
        cx=WIDTH // 2, cy=HEIGHT // 2,
        angle_deg=90,
    )
    draw = ImageDraw.Draw(img)

    # Decorative lines flanking the name
    if name_box:
        pad = 10
        lx_l = name_box[0] - pad
        lx_r = name_box[2] + pad
        ly_t = name_box[1] + 20
        ly_b = name_box[3] - 20
        draw.line([(lx_l, ly_t), (lx_l, ly_b)], fill="black", width=2)
        draw.line([(lx_r, ly_t), (lx_r, ly_b)], fill="black", width=2)
        # Small hearts on the lines
        for ly in [ly_t, (ly_t + ly_b) // 2, ly_b]:
            draw_heart(draw, lx_l, ly, 6)
            draw_heart(draw, lx_r, ly, 6)

    # --- Scatter decorative motifs ---
    margin = 75
    interior = (margin, margin, WIDTH - margin, HEIGHT - margin)

    placed_boxes = []
    if name_box:
        p = 20
        placed_boxes.append((name_box[0] - p, name_box[1] - p,
                             name_box[2] + p, name_box[3] + p))

    motif_funcs = [
        lambda d, x, y, s: draw_heart(d, x, y, s),
        lambda d, x, y, s: draw_heart_outline(d, x, y, s),
        lambda d, x, y, s: draw_sparkle(d, x, y, s),
        lambda d, x, y, s: draw_star(d, x, y, s),
        lambda d, x, y, s: draw_rose(d, x, y, s),
        lambda d, x, y, s: draw_manga_flower(d, x, y, s),
        lambda d, x, y, s: draw_ribbon_bow(d, x, y, s),
        lambda d, x, y, s: draw_crescent_moon(d, x, y, s),
        lambda d, x, y, s: draw_chibi_cat_face(d, x, y, s),
    ]

    # Place ~30 scattered motifs
    for _ in range(40):
        size = random.randint(12, 28)
        func = random.choice(motif_funcs)
        for _attempt in range(30):
            cx = random.randint(interior[0] + size, interior[2] - size)
            cy = random.randint(interior[1] + size, interior[3] - size)
            cand = (cx - size - 4, cy - size - 4, cx + size + 4, cy + size + 4)
            if not any(boxes_overlap(cand, pb) for pb in placed_boxes):
                func(draw, cx, cy, size)
                placed_boxes.append(cand)
                break

    # --- Scatter shojo quotes ---
    font_sizes = [13, 15, 17, 19, 22]
    angles = [90, -90, 90, 0, 45, -45, 90, -90]
    quote_pool = SHOJO_QUOTES * 2
    random.shuffle(quote_pool)

    for quote in quote_pool:
        size = random.choice(font_sizes)
        angle = random.choice(angles)
        font = ImageFont.truetype(QUOTE_FONT_PATH, size)

        tmp = Image.new("RGBA", (1, 1))
        tmp_d = ImageDraw.Draw(tmp)
        bbox = tmp_d.textbbox((0, 0), quote, font=font)
        tw = bbox[2] - bbox[0] + 4
        th = bbox[3] - bbox[1] + 4
        rad = math.radians(angle)
        rw = abs(tw * math.cos(rad)) + abs(th * math.sin(rad))
        rh = abs(tw * math.sin(rad)) + abs(th * math.cos(rad))

        for _attempt in range(30):
            cx = random.randint(int(interior[0] + rw / 2 + 5),
                                int(interior[2] - rw / 2 - 5))
            cy = random.randint(int(interior[1] + rh / 2 + 5),
                                int(interior[3] - rh / 2 - 5))
            cand = (cx - rw / 2 - 3, cy - rh / 2 - 3,
                    cx + rw / 2 + 3, cy + rh / 2 + 3)
            if not any(boxes_overlap(cand, pb) for pb in placed_boxes):
                actual = draw_rotated_text(img, quote, font, cx, cy, angle)
                draw = ImageDraw.Draw(img)
                if actual:
                    placed_boxes.append(actual)
                break

    # Save preview
    img.save(OUTPUT_PNG)
    print(f"Preview saved: {OUTPUT_PNG}")

    # Convert to 1-bit mono (hard threshold, no dithering)
    gray = img.convert("L")
    mono = gray.point(lambda x: 0 if x < 128 else 255, "1")

    # ZPL
    zpl = image_to_zpl_gf(mono)
    with open(OUTPUT_ZPL, "w") as f:
        f.write(zpl)
    print(f"ZPL saved: {OUTPUT_ZPL} ({len(zpl)} bytes)")
    print(f"\nTo print: lp -d ZebraGX420d -o raw {OUTPUT_ZPL}")


if __name__ == "__main__":
    main()
