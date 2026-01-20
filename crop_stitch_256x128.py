#!/usr/bin/env python3
"""
Docstring for crop_stitch_256x128
14X14 Font
480 Width
"""


import argparse
import sys
from pathlib import Path
from typing import Iterable
from PIL import Image


SOURCE_W, SOURCE_H = 256, 128
BLOCK_H = 54  # height of each stripe to keep
OUTPUT_W, OUTPUT_H = 512, BLOCK_H * 2  # stitched width/height (108)
FINAL_W, FINAL_H = 480, 54  # final crop after stitching (forward mode)


def iter_inputs(path: Path) -> Iterable[Path]:
    if path.is_dir():
        # process common image extensions
        exts = {'.png', '.bmp', '.jpg', '.jpeg', '.gif', '.tga'}
        for p in sorted(path.rglob('*')):
            if p.suffix.lower() in exts and p.is_file():
                yield p
    elif path.is_file():
        yield path
    else:
        return


def process_image(src: Path, dst: Path, *, mode: str, force: bool = False, verbose: bool = False) -> bool:
    try:
        with Image.open(src) as im:
            target_mode = im.mode if im.mode != 'P' else 'RGBA'
            if mode == 'forward':
                if im.size != (SOURCE_W, SOURCE_H):
                    if not force:
                        raise ValueError(f"expected {SOURCE_W}x{SOURCE_H}, got {im.size}")
                    if verbose:
                        print(f"[warn] {src.name}: size {im.size}, processing anyway")

                # pick upper two stripes then stitch horizontally
                upper1 = im.crop((0, 0, SOURCE_W, BLOCK_H))
                upper2 = im.crop((0, BLOCK_H, SOURCE_W, BLOCK_H * 2))

                canvas = Image.new(target_mode, (OUTPUT_W, OUTPUT_H))
                canvas.paste(upper1.convert(target_mode), (0, 0))
                canvas.paste(upper2.convert(target_mode), (SOURCE_W, 0))
                # final crop to left 480px and top 14px
                canvas = canvas.crop((0, 0, FINAL_W, FINAL_H))
            else:  # reverse: take 512x108 stitched image, split back to 256x128 top stripes
                # allow directly using the 480x14 cropped output: pad it back to 512x108 then split
                if im.size == (FINAL_W, FINAL_H):
                    if verbose:
                        print(f"[info] {src.name}: got {FINAL_W}x{FINAL_H}, padding to {OUTPUT_W}x{OUTPUT_H} before split")
                    padded = Image.new(target_mode, (OUTPUT_W, OUTPUT_H))
                    padded.paste(im.convert(target_mode), (0, 0))
                    im = padded
                elif im.size != (OUTPUT_W, OUTPUT_H):
                    if not force:
                        raise ValueError(f"expected {OUTPUT_W}x{OUTPUT_H}, got {im.size}")
                    if verbose:
                        print(f"[warn] {src.name}: size {im.size}, processing anyway")

                left = im.crop((0, 0, SOURCE_W, BLOCK_H))
                right = im.crop((SOURCE_W, 0, OUTPUT_W, BLOCK_H))

                # Create black background and composite images onto it
                canvas = Image.new('RGBA', (SOURCE_W, SOURCE_H), (0, 0, 0, 255))
                canvas.paste(left.convert('RGBA'), (0, 0), left.convert('RGBA') if left.mode == 'RGBA' else None)
                canvas.paste(right.convert('RGBA'), (0, BLOCK_H), right.convert('RGBA') if right.mode == 'RGBA' else None)
                # Convert to target mode (removes alpha if needed)
                canvas = canvas.convert(target_mode)
                
            dst.parent.mkdir(parents=True, exist_ok=True)
            canvas.save(dst)
        if verbose:
            print(f"[ok] {src} -> {dst}")
        return True
    except Exception as e:
        print(f"[err] {src}: {e}", file=sys.stderr)
        return False


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Forward: crop top two 256x54 regions of a 256x128 image, stitch to 512x108, then final-crop to 480x14. Reverse: accept 480x14 (or 512x108), pad if needed, then split back to 256x128 (rest blank).",
    )
    parser.add_argument('input', help='Input file or directory')
    parser.add_argument('output', help='Output file or directory')
    parser.add_argument('-m', '--mode', choices=['forward', 'reverse'], default='forward', help='forward (256x128 -> 512x108) or reverse (512x108 -> 256x128)')
    parser.add_argument('--force', action='store_true', help='Ignore size check (still crops fixed regions)')
    parser.add_argument('-v', '--verbose', action='store_true', help='Verbose logs')
    args = parser.parse_args()

    in_path = Path(args.input)
    out_path = Path(args.output)

    inputs = list(iter_inputs(in_path))
    if not inputs:
        print(f"No input files found: {in_path}", file=sys.stderr)
        return 1

    multi = len(inputs) > 1 or in_path.is_dir()

    ok = 0
    for src in inputs:
        if multi:
            rel = src.relative_to(in_path) if in_path.is_dir() else src.name
            dst = out_path / (rel if isinstance(rel, Path) else Path(rel))
            dst = dst.with_suffix('.png')
        else:
            dst = out_path
            if dst.is_dir():
                dst = dst / src.with_suffix('.png').name

        if process_image(src, dst, mode=args.mode, force=args.force, verbose=args.verbose):
            ok += 1

    total = len(inputs)
    if args.verbose or multi:
        print(f"Done: {ok}/{total} succeeded")
    return 0 if ok == total else 1


if __name__ == '__main__':
    sys.exit(main())
