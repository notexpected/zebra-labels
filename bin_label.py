#!/usr/bin/env python3
"""Generate storage bin labels for Zebra GX420d (203dpi, 4x6 portrait)."""

import argparse
import subprocess
import sys
from PIL import Image, ImageDraw, ImageFont

# --- Config ---
DPI = 203
WIDTH = 812    # 4" * 203dpi
HEIGHT = 1218  # 6" * 203dpi

BOLD_FONT = "/usr/share/fonts/OTF/SpaceGrotesk-Bold.otf"
ITEM_FONT = "/usr/share/fonts/liberation/LiberationSerif-Italic.ttf"

MARGIN = 40
ITEM_LINE_SPACING = 40
BLANK_LINE_SPACING = ITEM_LINE_SPACING * 2
UNDERLINE_OFFSET = 6
UNDERLINE_WIDTH = 2
BULLET = "\u2022 "


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
            byte_str = "".join(row_bits[i:i + 8])
            hex_data.append(f"{int(byte_str, 2):02X}")

    hex_string = "".join(hex_data)
    return (
        f"^XA\n"
        f"~SD25\n"
        f"^PR2,2,2\n"
        f"^FO0,0\n"
        f"^GFA,{total_bytes},{total_bytes},{bytes_per_row},{hex_string}\n"
        f"^FS\n"
        f"^XZ\n"
    )


def get_args():
    parser = argparse.ArgumentParser(description="Generate storage bin labels")
    parser.add_argument("--category", type=str, help="Bin category (e.g. Electronics)")
    parser.add_argument("--subcategory", type=str, help="Bin subcategory (e.g. Cables)")
    parser.add_argument("--item", action="append", dest="items", help="Item (repeatable)")
    parser.add_argument("--print", action="store_true", dest="do_print",
                        help="Send to printer after generation")
    args = parser.parse_args()

    if not args.category:
        args.category = input("Category: ").strip()
    if not args.subcategory:
        args.subcategory = input("Subcategory: ").strip()
    if not args.items:
        args.items = []
        print("Enter items (empty line to finish):")
        while True:
            item = input("  Item: ").strip()
            if not item:
                break
            args.items.append(item)

    return args


def render_label(category, subcategory, items):
    img = Image.new("RGB", (WIDTH, HEIGHT), "white")
    draw = ImageDraw.Draw(img)

    cat_font = ImageFont.truetype(BOLD_FONT, 72)
    sub_font = ImageFont.truetype(BOLD_FONT, 56)
    item_font = ImageFont.truetype(ITEM_FONT, 40)

    x_left = MARGIN
    x_right = WIDTH - MARGIN
    content_width = x_right - x_left
    y = MARGIN

    # Category (centered)
    cat_bbox = draw.textbbox((0, 0), category.upper(), font=cat_font)
    cat_w = cat_bbox[2] - cat_bbox[0]
    cat_x = x_left + (content_width - cat_w) // 2
    draw.text((cat_x, y), category.upper(), fill="black", font=cat_font)
    cat_bbox = draw.textbbox((cat_x, y), category.upper(), font=cat_font)
    y = cat_bbox[3] + 10

    # Subcategory (centered)
    sub_bbox = draw.textbbox((0, 0), subcategory, font=sub_font)
    sub_w = sub_bbox[2] - sub_bbox[0]
    sub_x = x_left + (content_width - sub_w) // 2
    draw.text((sub_x, y), subcategory, fill="black", font=sub_font)
    sub_bbox = draw.textbbox((sub_x, y), subcategory, font=sub_font)
    y = sub_bbox[3] + 24

    # Divider line
    draw.line([(x_left, y), (x_right, y)], fill="black", width=3)
    y += 20

    # Items with bullet and underline
    for item_text in items:
        text = BULLET + item_text
        draw.text((x_left, y), text, fill="black", font=item_font)
        text_bbox = draw.textbbox((x_left, y), text, font=item_font)
        text_bottom = text_bbox[3]
        ul_y = text_bottom + UNDERLINE_OFFSET
        draw.line([(x_left, ul_y), (x_right, ul_y)], fill="black", width=UNDERLINE_WIDTH)
        y = ul_y + ITEM_LINE_SPACING

    # Blank handwriting lines filling remaining space
    bottom_limit = HEIGHT - MARGIN
    while y + BLANK_LINE_SPACING < bottom_limit:
        line_y = y + BLANK_LINE_SPACING
        draw.line([(x_left, line_y), (x_right, line_y)], fill="black", width=UNDERLINE_WIDTH)
        y = line_y

    return img


def main():
    args = get_args()
    img = render_label(args.category, args.subcategory, args.items)

    # Build output filenames from category-subcategory
    slug = f"{args.category}-{args.subcategory}".lower().replace(" ", "-")
    output_zpl = f"{slug}.zpl"
    output_png = f"{slug}-preview.png"

    # Save preview
    img.save(output_png)
    print(f"Preview saved: {output_png}")

    # Convert to 1-bit mono (hard threshold, no dithering)
    gray = img.convert("L")
    mono = gray.point(lambda x: 0 if x < 128 else 255, "1")

    # ZPL
    zpl = image_to_zpl_gf(mono)
    with open(output_zpl, "w") as f:
        f.write(zpl)
    print(f"ZPL saved: {output_zpl} ({len(zpl)} bytes)")

    if args.do_print:
        subprocess.run(["lp", "-d", "ZebraGX420d", "-o", "raw", output_zpl], check=True)
        print("Sent to printer.")
    else:
        print(f"\nTo print: lp -d ZebraGX420d -o raw {output_zpl}")


if __name__ == "__main__":
    main()
