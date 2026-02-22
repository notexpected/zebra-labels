#!/usr/bin/env python3
"""Generate a cat feeding guide label for Zebra GX420d (203dpi, 4x6 portrait)."""

from PIL import Image, ImageDraw, ImageFont

# --- Config ---
DPI = 203
WIDTH = 812    # 4" * 203dpi
HEIGHT = 1218  # 6" * 203dpi

BOLD_FONT = "/usr/share/fonts/OTF/SpaceGrotesk-Bold.otf"
ITEM_FONT = "/usr/share/fonts/liberation/LiberationSerif-Italic.ttf"

MARGIN = 40
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


def main():
    img = Image.new("RGB", (WIDTH, HEIGHT), "white")
    draw = ImageDraw.Draw(img)

    name_font = ImageFont.truetype(BOLD_FONT, 72)
    subtitle_font = ImageFont.truetype(BOLD_FONT, 66)
    section_font = ImageFont.truetype(BOLD_FONT, 54)
    item_font = ImageFont.truetype(ITEM_FONT, 48)
    note_font = ImageFont.truetype(ITEM_FONT, 28)
    detail_font = ImageFont.truetype(ITEM_FONT, 32)

    x_left = MARGIN
    x_right = WIDTH - MARGIN
    content_width = x_right - x_left

    note = "*A few treats throughout the day is OK"

    def draw_content(draw, y_start):
        y = y_start

        # Names
        names = "MARCELINE & BRISKET"
        bbox = draw.textbbox((0, 0), names, font=name_font)
        name_w = bbox[2] - bbox[0]
        draw.text((x_left + (content_width - name_w) // 2, y), names, fill="black", font=name_font)
        y = draw.textbbox((0, y), names, font=name_font)[3] + 12

        # Subtitle
        subtitle = "Feeding Guide*"
        bbox = draw.textbbox((0, 0), subtitle, font=subtitle_font)
        sub_w = bbox[2] - bbox[0]
        draw.text((x_left + (content_width - sub_w) // 2, y), subtitle, fill="black", font=subtitle_font)
        y = draw.textbbox((0, y), subtitle, font=subtitle_font)[3] + 12

        # Detail line
        detail = "1 scoop total per cat per day"
        bbox = draw.textbbox((0, 0), detail, font=detail_font)
        detail_w = bbox[2] - bbox[0]
        draw.text((x_left + (content_width - detail_w) // 2, y), detail, fill="black", font=detail_font)
        y = draw.textbbox((0, y), detail, font=detail_font)[3] + 24

        # Divider
        draw.line([(x_left, y), (x_right, y)], fill="black", width=3)
        y += 36

        # Fill cups
        draw.text((x_left, y), "Start of Day", fill="black", font=section_font)
        y = draw.textbbox((x_left, y), "Start of Day", font=section_font)[3] + 18
        text = BULLET + "Fill each cup to the line"
        draw.text((x_left + 20, y), text, fill="black", font=item_font)
        y = draw.textbbox((x_left + 20, y), text, font=item_font)[3] + 24
        y += 24

        # Morning
        draw.text((x_left, y), "Morning", fill="black", font=section_font)
        y = draw.textbbox((x_left, y), "Morning", font=section_font)[3] + 18
        text = BULLET + "\u00BC of the cup"
        draw.text((x_left + 20, y), text, fill="black", font=item_font)
        y = draw.textbbox((x_left + 20, y), text, font=item_font)[3] + 24
        y += 24

        # Throughout the day
        draw.text((x_left, y), "Throughout the Day", fill="black", font=section_font)
        y = draw.textbbox((x_left, y), "Throughout the Day", font=section_font)[3] + 18
        text = BULLET + "Small portions from the cup"
        draw.text((x_left + 20, y), text, fill="black", font=item_font)
        y = draw.textbbox((x_left + 20, y), text, font=item_font)[3] + 24
        y += 24

        # End of day
        draw.text((x_left, y), "End of Day", fill="black", font=section_font)
        y = draw.textbbox((x_left, y), "End of Day", font=section_font)[3] + 18
        text = BULLET + "Any remaining"
        draw.text((x_left + 20, y), text, fill="black", font=item_font)
        y = draw.textbbox((x_left + 20, y), text, font=item_font)[3] + 24
        y += 16

        # Note
        bbox = draw.textbbox((0, 0), note, font=note_font)
        note_w = bbox[2] - bbox[0]
        draw.text((x_left + (content_width - note_w) // 2, y), note, fill="black", font=note_font)
        y = draw.textbbox((0, y), note, font=note_font)[3]

        return y

    # Measure on scratch image
    scratch = Image.new("RGB", (WIDTH, HEIGHT), "white")
    scratch_draw = ImageDraw.Draw(scratch)
    total_height = draw_content(scratch_draw, 0)

    # Center vertically
    y_offset = (HEIGHT - total_height) // 2
    draw_content(draw, y_offset)

    # Save
    output_png = "cats-food-preview.png"
    output_zpl = "cats-food.zpl"

    img.save(output_png)
    print(f"Preview saved: {output_png}")

    gray = img.convert("L")
    mono = gray.point(lambda x: 0 if x < 128 else 255, "1")

    zpl = image_to_zpl_gf(mono)
    with open(output_zpl, "w") as f:
        f.write(zpl)
    print(f"ZPL saved: {output_zpl} ({len(zpl)} bytes)")
    print(f"\nTo print: lp -d ZebraGX420d -o raw {output_zpl}")


if __name__ == "__main__":
    main()
