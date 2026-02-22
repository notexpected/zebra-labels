# Zebra GX420d Label Printer Scripts

Generate and print labels on a Zebra GX420d (203dpi, 4×6" direct thermal) using Python + Pillow rendered to ZPL `^GF` bitmaps.

## Setup

```bash
python3 -m venv .venv
.venv/bin/pip install Pillow
```

### Fonts

These scripts expect the following fonts installed on the system:

- **Space Grotesk Bold** — `/usr/share/fonts/OTF/SpaceGrotesk-Bold.otf`
- **Liberation Serif Italic** — `/usr/share/fonts/liberation/LiberationSerif-Italic.ttf`

### Printer

The printer should be configured via CUPS as `ZebraGX420d`. Verify with:

```bash
lpstat -p ZebraGX420d
```

## Scripts

### `bin_label.sh` / `bin_label.py` — Storage Bin Labels

Generate 4×6" portrait labels for storage bins with a category, subcategory, item list, and blank handwriting lines.

```bash
# With CLI args
./bin_label.sh --category "Electronics" --subcategory "Cables" --item "USB-C" --item "HDMI" --item "Lightning"

# Interactive (prompts for each field)
./bin_label.sh

# Auto-print after generating
./bin_label.sh --category "Hardware" --subcategory "Screws" --item "M3" --item "M4" --print
```

**Output:** `<category>-<subcategory>.zpl` + `<category>-<subcategory>-preview.png`

**Manual print:**

```bash
lp -d ZebraGX420d -o raw electronics-cables.zpl
```

### `generate_label.py` — Decorative Name Sticker

Generate a shojo-themed decorative name label with scattered motifs and quotes.

```bash
.venv/bin/python3 generate_label.py
```

**Output:** `adrienne-label.zpl` + `adrienne-label-preview.png`
