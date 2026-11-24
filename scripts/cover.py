"""The cover, set like a magazine: an issue bar, the name as a masthead, and one painting —
Montréal from the river at dusk — running the full width beneath it.
The same drawing as the website's cover (src/utils/cover-scene.js there), exported from it.

    python scripts/cover.py [assets/cover.svg]
"""
from __future__ import annotations

import base64
import sys
from pathlib import Path

from sketch import FONTS, font_css

W, H = 1440, 800
DY = -100  # the scene is drawn for y in 280..900

CREAM, NAVY, VERMILION, GOLD = "#f6f0e4", "#14213a", "#c8431f", "#e0ad4a"


def _face(file: str, family: str, weight: int) -> str:
    data = base64.b64encode((FONTS / file).read_bytes()).decode()
    return (f"@font-face{{font-family:'{family}';font-weight:{weight};"
            f"src:url(data:font/woff2;base64,{data}) format('woff2');}}")


def scene() -> str:
    """The drawing itself, exported from the website's src/utils/cover-scene.js."""
    return (Path(__file__).parent / "cover-scene.svgfrag").read_text(encoding="utf-8")


def build() -> str:
    css = (
        _face("bodoni-600.woff2", "Bodoni Moda", 600) + _face("bodoni-500.woff2", "Bodoni Moda", 500)
        + font_css("sans", "sans-m")
        + ".d{font-family:'Bodoni Moda',Didot,'Bodoni MT',serif}"
        ".cap{font-family:Inter,system-ui,sans-serif;font-weight:500;font-size:11px;letter-spacing:.22em}"
        ".s{font-family:Inter,system-ui,sans-serif;font-weight:400;font-size:14px}"
    )
    lx, rx = 80, W - 80
    o = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" aria-labelledby="t d">',
        '<title id="t">Ziyi (Ellen) Zhou — statistician and data engineer, Montréal</title>',
        '<desc id="d">A magazine cover: the name Ziyi Zhou as a masthead above a painting of Montréal from the river at '
        'dusk — Mont Royal and its cross, the towers of the centre, the Old Port and the Jacques-Cartier bridge in gold.</desc>',
        f"<style>{css}</style>",
        f'<rect width="{W}" height="{H}" fill="{CREAM}"/>',
        f'<g transform="translate(0 {DY})">{scene()}</g>',
        # issue bar
        f'<path d="M{lx} 44H{rx}M{lx} 80H{rx}" stroke="{NAVY}" stroke-width="1"/>',
        f'<text class="cap" x="{lx}" y="66" fill="{NAVY}">N° 01</text>',
        f'<text class="cap" x="{W / 2}" y="66" fill="{NAVY}" text-anchor="middle">STATISTICIAN · DATA ENGINEER</text>',
        f'<text class="cap" x="{rx}" y="66" fill="{NAVY}" text-anchor="end">MONTRÉAL · HIVER 2026</text>',
        # masthead
        f'<text class="d" x="{lx - 6}" y="286" font-size="244" font-weight="600" letter-spacing="-2.4" fill="{NAVY}">ZIYI ZHOU</text>',
    ]
    x = lx
    for dt, dd, step in (("NOW", "UNESCO Institute for Statistics", 266), ("M.SC.", "Statistics, McGill", 174),
                         ("B.SC.", "Statistics, HKU", 0)):
        o.append(f'<text class="cap" x="{x}" y="744" fill="{CREAM}" opacity=".72" font-size="10.5">{dt}</text>'
                 f'<text class="s" x="{x}" y="770" fill="{CREAM}">{dd}</text>')
        x += step
    o.append(f'<text class="cap" x="{rx}" y="770" fill="{CREAM}" text-anchor="end">ELLENSYUU.GITHUB.IO</text>')
    o.append("</svg>")
    return "".join(o)


if __name__ == "__main__":
    dest = Path(sys.argv[1] if len(sys.argv) > 1 else "assets/cover.svg")
    dest.write_text(build(), encoding="utf-8")
    print(f"wrote {dest} ({dest.stat().st_size / 1024:.0f} KB)")
