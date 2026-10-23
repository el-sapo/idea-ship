#!/usr/bin/env python3
"""Render the plugin icon from its SVG source.

Writes plugins/idea-ship/.claude-plugin/icon.png at 1024 px from
plugins/idea-ship/assets/mark.svg, and a 48 px check render outside the
repository, to look at before committing. The output is deterministic: a
run on an unchanged mark leaves the committed PNG byte for byte the same.

Needs Python 3.9+ and one rasteriser, pinned:

  pip install resvg-py==0.2.0
  python3 scripts/render-icon.py
  python3 scripts/render-icon.py --check /path/outside/the/repo/icon-48.png
"""

import argparse
import re
import struct
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SOURCE = ROOT / "plugins" / "idea-ship" / "assets" / "mark.svg"
ICON = ROOT / "plugins" / "idea-ship" / ".claude-plugin" / "icon.png"
ICON_SIZE = 1024
CHECK_SIZE = 48
ROOT_TAG = re.compile(r"<svg\b[^>]*>")
SIZE_ATTRIBUTE = re.compile(r"""\s(?:width|height)\s*=\s*(?:"[^"]*"|'[^']*')""")


def sized(svg, size):
    """The SVG text with width and height set on its root element.

    resvg-py 0.2.0 ignores its own width and height arguments and renders
    at the size the root element states, so the size goes into a copy of
    the text. The file on disk is never changed.
    """
    match = ROOT_TAG.search(svg)
    if match is None:
        raise ValueError("no <svg> root element")
    tag = SIZE_ATTRIBUTE.sub("", match.group(0))
    tag = tag[:4] + f' width="{size}" height="{size}"' + tag[4:]
    return svg[:match.start()] + tag + svg[match.end():]


def png_size(data):
    """Width and height from a PNG's header."""
    if not data.startswith(b"\x89PNG\r\n\x1a\n") or data[12:16] != b"IHDR":
        raise ValueError("not a PNG")
    return struct.unpack(">II", data[16:24])


def render(resvg_py, svg, size):
    data = bytes(resvg_py.svg_to_bytes(svg_string=sized(svg, size)))
    if png_size(data) != (size, size):
        raise ValueError(f"rendered {png_size(data)}, expected ({size}, {size})")
    return data


def main():
    parser = argparse.ArgumentParser(description="Render the plugin icon from its SVG source.")
    parser.add_argument(
        "--check",
        type=Path,
        default=Path(tempfile.gettempdir()) / "idea-ship-icon-48.png",
        help="where to write the 48 px check render (default: the system temp folder)",
    )
    args = parser.parse_args()

    try:
        import resvg_py
    except ImportError:
        print("needs the rasteriser: pip install resvg-py==0.2.0", file=sys.stderr)
        return 1

    svg = SOURCE.read_text(encoding="utf-8")
    try:
        icon = render(resvg_py, svg, ICON_SIZE)
        check = render(resvg_py, svg, CHECK_SIZE)
    except ValueError as error:
        print(f"{SOURCE.relative_to(ROOT)}: {error}", file=sys.stderr)
        return 1

    ICON.write_bytes(icon)
    args.check.parent.mkdir(parents=True, exist_ok=True)
    args.check.write_bytes(check)
    print(f"{ICON.relative_to(ROOT)}: {ICON_SIZE} px, {len(icon)} bytes")
    print(f"{args.check}: {CHECK_SIZE} px check render")
    return 0


if __name__ == "__main__":
    sys.exit(main())
