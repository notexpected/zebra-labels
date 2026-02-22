#!/usr/bin/env bash
# Setup script for Zebra GX420d label printer tools
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR"

echo "=== Zebra Label Printer Setup ==="

# Check for required fonts
missing_fonts=0
for font in "/usr/share/fonts/OTF/SpaceGrotesk-Bold.otf" "/usr/share/fonts/liberation/LiberationSerif-Italic.ttf"; do
    if [ ! -f "$font" ]; then
        echo "MISSING FONT: $font"
        missing_fonts=1
    fi
done
if [ "$missing_fonts" -eq 1 ]; then
    echo "Install missing fonts before continuing."
    exit 1
fi
echo "Fonts: OK"

# Create venv and install dependencies
if [ ! -d ".venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv .venv
else
    echo "Virtual environment already exists."
fi

echo "Installing dependencies..."
.venv/bin/pip install --quiet Pillow
echo "Dependencies: OK"

# Make scripts executable
chmod +x bin_label.sh
echo "Scripts: OK"

# Check for printer (optional)
if command -v lpstat &>/dev/null && lpstat -p ZebraGX420d &>/dev/null 2>&1; then
    echo "Printer: ZebraGX420d found"
else
    echo "Printer: ZebraGX420d not found (configure via CUPS to print)"
fi

echo ""
echo "Setup complete! Try:"
echo "  ./bin_label.sh --category \"Test\" --subcategory \"Demo\" --item \"Hello\""
