#!/usr/bin/env python3

"""
Generate a 480x16 PNG with centered white text on black background.
- Text can come from CLI arg or a file.
- Auto downscales font size to fit width.
"""

import argparse
import sys
from pathlib import Path
from typing import Optional
from PIL import Image, ImageDraw, ImageFont

CANVAS_W, CANVAS_H = 480, 16
DEFAULT_FONT_SIZE = 14
MIN_FONT_SIZE = 8
TEXT_COLOR = (255, 255, 255, 255)
BG_COLOR = (0, 0, 0, 255)


def measure_text(draw: ImageDraw.ImageDraw, text: str, font: ImageFont.FreeTypeFont) -> tuple[int, int]:
    """Return (width, height) using textbbox for Pillow compatibility."""
    bbox = draw.textbbox((0, 0), text, font=font)
    return bbox[2] - bbox[0], bbox[3] - bbox[1]


def load_font(font_path: Optional[Path], size: int) -> ImageFont.FreeTypeFont:
    if font_path:
        return ImageFont.truetype(str(font_path), size=size)
    return ImageFont.load_default()


def fit_font(text: str, font_path: Optional[Path], explicit_size: Optional[int] = None) -> ImageFont.FreeTypeFont:
    if explicit_size is not None:
        return load_font(font_path, explicit_size)
    dummy = Image.new("RGBA", (1, 1))
    draw = ImageDraw.Draw(dummy)
    size = DEFAULT_FONT_SIZE
    while size >= MIN_FONT_SIZE:
        font = load_font(font_path, size)
        w, h = measure_text(draw, text, font)
        if w <= CANVAS_W and h <= CANVAS_H:
            return font
        size -= 1
    return load_font(font_path, MIN_FONT_SIZE)


def render_text(text: str, font_path: Optional[Path], font_size: Optional[int] = None, verbose: bool = False, clip: bool = False) -> Image:
    font = fit_font(text, font_path, explicit_size=font_size)
    im = Image.new("RGBA", (CANVAS_W, CANVAS_H), BG_COLOR)
    draw = ImageDraw.Draw(im)
    w, h = measure_text(draw, text, font)
    if verbose:
        print(f"[info] text='{text}' width={w} height={h} canvas={CANVAS_W}x{CANVAS_H}")
    
    if clip and w > CANVAS_W:
        if verbose:
            print(f"[warn] text overflow by {w - CANVAS_W}px, clipping to canvas")
        x = 0
    else:
        x = (CANVAS_W - w) // 2
    
    y = -2  # align to top
    draw.text((x, y), text, font=font, fill=TEXT_COLOR)
    return im


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate centered 480x16 black PNG with white text")
    parser.add_argument("text", nargs="?", help="Text content (if omitted, use --text-file)")
    parser.add_argument("-o", "--output", required=True, help="Output PNG path")
    parser.add_argument("--text-file", help="Read text from file (first line)")
    parser.add_argument("--font", help="Path to TTF/OTF font")
    parser.add_argument("--font-size", type=int, help="Font size (default: auto-fit from 18 down to 8)")
    parser.add_argument("-v", "--verbose", action="store_true", help="Verbose debug info")
    parser.add_argument("--clip", action="store_true", help="Clip text to left if overflow (default: center)")
    args = parser.parse_args()

    if not args.text and not args.text_file:
        print("Error: provide text or --text-file", file=sys.stderr)
        return 1

    text = args.text
    if args.text_file:
        path = Path(args.text_file)
        if not path.exists():
            print(f"Error: text file not found: {path}", file=sys.stderr)
            return 1
        text = path.read_text(encoding="utf-8").splitlines()[0] if text is None else text
    if text is None:
        print("Error: empty text", file=sys.stderr)
        return 1

    font_path = Path(args.font) if args.font else None
    try:
        im = render_text(text, font_path, font_size=args.font_size, verbose=args.verbose, clip=args.clip)
        out_path = Path(args.output)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        im.save(out_path)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
