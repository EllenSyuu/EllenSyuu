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
from sketch import font_css
from scenes import PH, PW, SCENES

OUT = Path("assets/plates")
LIVE = re.compile(r'<(?:circle|ellipse) class="(?:flake|petal)"[^>]*/>')


def split(k: int) -> tuple[str, str]:
    """(still drawing, live overlay) for plate k."""
    drawing = SCENES[k][2]()
    live = "".join(LIVE.findall(drawing))
    return LIVE.sub("", drawing), live


def plate_svg(drawing: str) -> str:
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {PW} {PH}" width="{PW}" height="{PH}">'
        f"<style>{font_css('hand')}.hand{{font-family:'La Belle Aurore',cursive}}</style><defs>{art.defs()}"
        '<linearGradient id="fadeL" x1="0" x2="1"><stop offset="0" stop-color="#fff" stop-opacity="0"/>'
        '<stop offset=".11" stop-color="#fff"/></linearGradient>'
        f'<mask id="folio" maskUnits="userSpaceOnUse" x="-80" y="-40" width="{PW + 120}" height="{PH + 80}">'
        f'<g filter="url(#edgefade)"><rect x="14" y="18" width="{PW - 30}" height="{PH - 40}" fill="url(#fadeL)"/></g></mask></defs>'
        f'<g mask="url(#folio)">{drawing}</g></svg>'
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
            await pg.set_content(f'<html><body style="margin:0;background:#f6f1e6">{plate_svg(drawing)}</body></html>')
            await pg.wait_for_timeout(400)
            png = await pg.screenshot(clip={"x": 0, "y": 0, "width": PW, "height": PH})
            im = Image.open(io.BytesIO(png)).convert("RGB")
            dest = OUT / f"plate-{k + 2}.webp"
            im.save(dest, "WEBP", quality=82, method=6)
            print(f"wrote {dest} ({dest.stat().st_size / 1024:.0f} KB)")
        await b.close()


if __name__ == "__main__":
    asyncio.run(render_all())
