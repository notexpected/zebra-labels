# Zebra GX420d Label Printer

## Project Overview
Python scripts that generate ZPL label files for a Zebra GX420d direct thermal printer (203dpi, 4×6" labels). Labels are rendered as bitmaps using Pillow, then converted to ZPL `^GF` (graphic field) commands.

## Architecture
- All labels follow the same pipeline: **Pillow image → 1-bit mono (hard threshold) → ZPL `^GF` hex bitmap**
- The `image_to_zpl_gf()` function is the core converter — duplicated in each script (no shared module)
- ZPL settings: `~SD25` (darkness), `^PR2,2,2` (print speed)
- Labels are 812×1218 pixels (4"×6" at 203dpi), portrait orientation

## Scripts
- `bin_label.py` / `bin_label.sh` — Storage bin labels (category, subcategory, item list + blank lines)
- `generate_label.py` — Decorative shojo-themed name sticker (one-off)

## Key Conventions
- Venv at `.venv/` with Pillow as the only dependency
- Fonts are system-installed: Space Grotesk Bold (`/usr/share/fonts/OTF/SpaceGrotesk-Bold.otf`), Liberation Serif Italic (`/usr/share/fonts/liberation/LiberationSerif-Italic.ttf`)
- Output files: `<name>.zpl` (printer data) + `<name>-preview.png` (visual check)
- Print command: `lp -d ZebraGX420d -o raw <file>.zpl`
- Shell wrappers use `exec` to call `.venv/bin/python3` relative to the script directory

## When Adding New Label Scripts
1. Create a new `<name>.py` following the same Pillow → mono → `image_to_zpl_gf()` pipeline
2. Add a `<name>.sh` wrapper if needed
3. Output naming: descriptive slug based on user input, e.g. `category-subcategory.zpl`
4. Use `--print` flag convention to auto-send to printer
5. Support both CLI args and interactive prompts for input
