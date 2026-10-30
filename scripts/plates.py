"""Render each watercolour plate once, at 2×, to assets/plates/*.webp.

The plates are drawn as vectors (scenes.py) but carry ~1,000 watercolour filters; animating
them live inside an <img> would repaint every filter each frame. So they are baked here with a
headless browser, and cover.py embeds the WebPs with only the snow and petals left live.

    pip install playwright pillow && playwright install chromium
    python scripts/plates.py
"""
from __future__ import annotations

import asyncio
import io
import re
from pathlib import Path

import art
from sketch import PAPER, font_css
from scenes import PH, PW, SCENES

OUT = Path("assets/plates")
LIVE = re.compile(r'<(?:circle|ellipse) class="(?:flake|petal)"[^>]*/>')


def split(k: int) -> tuple[str, str]:
    """(still drawing, live overlay) for plate k."""
    drawing = SCENES[k][2]()
    drawing = re.sub(r'<(?:ellipse|circle|path)[^>]*filter="url\(#(?:bloom|soft)\)"[^>]*/>', "", drawing)
    live = "".join(LIVE.findall(drawing))
    return LIVE.sub("", drawing), live


# The drawing's own ruled frame (scenes.sheet) is cropped and set on a sheet of paper,
# the way the website presents its plates: a second sheet underneath, a paper clip, a
# pencil left on the table, and the title block with a hand note and the signature.
CROP = (26, 24, 658, 570)
SCALE = 0.93
SX, SY = 46, 18                      # where the crop's top-left lands
TX, TY = SX - CROP[0] * SCALE, SY - CROP[1] * SCALE
SHEET = (SX - 8, SY - 8, (CROP[2] - CROP[0]) * SCALE + 16, (CROP[3] - CROP[1]) * SCALE + 16)

NOTES = [
    "first light on the lake, seen from the shore",
    "snow on the eaves · the lamps lit at five",
    "the blossom comes all the way down to the river",
    "the long swell, late in the afternoon",
]

INK, GRAPH, ORANGE, AMBER = "#22314a", "#6f7b8c", "#cf602b", "#e0a046"


def furniture(k: int) -> tuple[str, str]:
    """(under the sheet, over the sheet)."""
    x, y, w, h = SHEET
    cx, cy = x + w / 2, y + h / 2
    under = (
        f'<g transform="rotate(-1.6 {cx:.0f} {cy:.0f}) translate(9 7)">'
        f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="#f9f5ec" stroke="{INK}" stroke-opacity=".25" stroke-width=".75" filter="url(#sheetshadow)"/></g>'
        f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="#fbf8f1" stroke="{INK}" stroke-opacity=".28" stroke-width=".75" filter="url(#sheetshadow)"/>'
    )
    cap, num, _ = SCENES[k]
    ty = y + h + 26
    clip_x = x + 30
    over = (
        # paper clip over the top edge
        f'<path d="M{clip_x},{y + 26} V{y - 10} a6,6 0 0 1 12,0 V{y + 32} a9,9 0 0 1 -18,0 V{y - 2}" fill="none" '
        f'stroke="{GRAPH}" stroke-width="1.6" stroke-linecap="round"/>'
        f'<path d="M{clip_x},{y + 26} V{y - 10} a6,6 0 0 1 12,0 V{y + 32} a9,9 0 0 1 -18,0 V{y - 2}" fill="none" '
        f'stroke="#fff" stroke-opacity=".6" stroke-width=".5" stroke-linecap="round" transform="translate(-.6 -.4)"/>'
        # a pencil left lying across the corner
        f'<g transform="translate({x + w - 150} {y + h + 4}) rotate(-13)">'
        f'<rect x="0" y="-4" width="118" height="8" fill="{AMBER}" stroke="{INK}" stroke-width=".7"/>'
        f'<path d="M0,-4 L-16,0 L0,4 Z" fill="#e8d6b4" stroke="{INK}" stroke-width=".7"/>'
        f'<path d="M-16,0 L-11,-1.3 L-11,1.3 Z" fill="{INK}"/>'
        f'<rect x="118" y="-4" width="12" height="8" fill="#c9cdd3" stroke="{INK}" stroke-width=".7"/>'
        f'<path d="M4,-1.4 H112" stroke="{INK}" stroke-opacity=".25" stroke-width=".6"/></g>'
        # title block
        f'<text x="{x + 6}" y="{ty}" class="ital" font-size="22" fill="{INK}">{num}</text>'
        f'<text x="{x + 112}" y="{ty}" class="caps" font-size="10.5" fill="{GRAPH}" font-weight="600">{cap.upper()}</text>'
        f'<path d="M{x + 6},{ty + 9} H{x + 400} M{x + 6},{ty + 12} H{x + 400}" stroke="{INK}" stroke-width=".5" stroke-opacity=".9"/>'
        f'<path d="M{x + 6},{ty + 12} H{x + 400}" stroke="{INK}" stroke-width=".25"/>'
        f'<text x="{x + 6}" y="{ty + 31}" class="hand" font-size="14.5" fill="{ORANGE}">{NOTES[k]}</text>'
        f'<text x="{x + w - 4}" y="{ty + 4}" class="hand" font-size="15" fill="{GRAPH}" text-anchor="end">Z. Zhou, MMXXVI</text>'
    )
    return under, over


def plate_svg(drawing: str, k: int = 0) -> str:
    under, over = furniture(k)
    x0, y0, x1, y1 = CROP
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {PW} {PH}" width="{PW}" height="{PH}">'
        f"<style>{font_css('hand', 'serif', 'serif-i')}.hand{{font-family:'La Belle Aurore',cursive}}"
        ".caps{font-family:'Cormorant Garamond',serif;letter-spacing:.24em}"
        ".ital{font-family:'Cormorant Garamond',serif;font-style:italic;font-weight:500}</style>"
        f"<defs>{art.defs()}"
        '<filter id="sheetshadow" x="-10%" y="-10%" width="120%" height="130%">'
        '<feDropShadow dx="0" dy="16" stdDeviation="14" flood-color="#22314a" flood-opacity=".16"/></filter>'
        f'<clipPath id="crop"><rect x="{x0}" y="{y0}" width="{x1 - x0}" height="{y1 - y0}"/></clipPath></defs>'
        f"{under}"
        f'<g transform="translate({TX:.2f} {TY:.2f}) scale({SCALE})"><g clip-path="url(#crop)">{drawing}</g></g>'
        f"{over}</svg>"
    )


async def render_all() -> None:
    from PIL import Image
    from playwright.async_api import async_playwright

    OUT.mkdir(parents=True, exist_ok=True)
    async with async_playwright() as p:
        b = await p.chromium.launch()
        pg = await b.new_page(viewport={"width": PW, "height": PH}, device_scale_factor=2)
        for k in range(len(SCENES)):
            drawing, _ = split(k)
            await pg.set_content(f'<html><body style="margin:0;background:{PAPER}">{plate_svg(drawing, k)}</body></html>')
            await pg.wait_for_timeout(400)
            png = await pg.screenshot(clip={"x": 0, "y": 0, "width": PW, "height": PH})
            im = Image.open(io.BytesIO(png)).convert("RGB")
            dest = OUT / f"plate-{k + 2}.webp"
            im.save(dest, "WEBP", quality=82, method=6)
            print(f"wrote {dest} ({dest.stat().st_size / 1024:.0f} KB)")
        await b.close()


if __name__ == "__main__":
    asyncio.run(render_all())
