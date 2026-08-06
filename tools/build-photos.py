#!/usr/bin/env python3
"""Resize source photos into the two sizes the page actually serves.

    python3 tools/build-photos.py <source-dir>

The originals are ~350 KB each, which is wasteful for an 86px card thumbnail
and more than the detail hero needs. This writes:

    photos/<slug>-thumb.jpg   240x240, centre-cropped, for list cards
    photos/<slug>.jpg         fits within 1200x800, for the detail hero

Only the outputs are committed. Every original is linked from its entry in
tools/photos.json, so this can be re-run against a fresh download.
"""

import json
import pathlib
import sys
from PIL import Image, ImageOps

ROOT = pathlib.Path(__file__).resolve().parent.parent
OUT = ROOT / "photos"
THUMB = 240
WIDE = (1200, 800)   # the hero is ~760x250; this is generous even at 2x


def main():
    if len(sys.argv) < 2:
        raise SystemExit(__doc__)
    src_dir = pathlib.Path(sys.argv[1])
    credits = {k: v for k, v in json.loads((ROOT / "tools/photos.json").read_text()).items()
               if not k.startswith("_")}
    OUT.mkdir(exist_ok=True)

    total_in = total_out = 0
    for slug, meta in sorted(credits.items()):
        src = src_dir / meta["file"]
        if not src.exists():
            print(f"  missing: {src}")
            continue
        total_in += src.stat().st_size
        img = ImageOps.exif_transpose(Image.open(src)).convert("RGB")

        thumb = ImageOps.fit(img, (THUMB, THUMB), Image.LANCZOS, centering=(0.5, 0.42))
        thumb.save(OUT / f"{slug}-thumb.jpg", quality=76, optimize=True, progressive=True)

        # Bound both dimensions: capping width alone left the portrait shots
        # nearly 1600px tall for a 250px hero.
        wide = img.copy()
        wide.thumbnail(WIDE, Image.LANCZOS)
        wide.save(OUT / f"{slug}.jpg", quality=78, optimize=True, progressive=True)

        out = (OUT / f"{slug}-thumb.jpg").stat().st_size + (OUT / f"{slug}.jpg").stat().st_size
        total_out += out
        print(f"  {slug:28} {img.width}x{img.height} -> {out/1024:6.0f} KB")

    print(f"\n{total_in/1024/1024:.1f} MB in -> {total_out/1024/1024:.1f} MB out")


if __name__ == "__main__":
    main()
