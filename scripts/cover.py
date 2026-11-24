"""The cover, set like a magazine: an issue bar, the name as a masthead, and one painting —
Montréal from the river at dusk on the first frost — running the full width beneath it.
The same drawing as the website's cover (src/utils/cover-scene.js there), ported line for line.

    python scripts/cover.py [assets/cover.svg]
"""
from __future__ import annotations

import base64
import math
import sys
from pathlib import Path

from sketch import FONTS, font_css

W, H = 1440, 800
DY = -100  # the scene is drawn for y in 280..900

CREAM, NAVY, VERMILION, GOLD = "#f6f0e4", "#14213a", "#c8431f", "#e0ad4a"
BLUE, PALE, DUSK, ROSE = "#2c5d7c", "#bcd3df", "#f2c79c", "#eaa283"


class Lehmer:
    def __init__(self, seed: int):
        self.s = seed

    def __call__(self) -> float:
        self.s = (self.s * 16807) % 2147483647
        return self.s / 2147483647


def _face(file: str, family: str, weight: int) -> str:
    data = base64.b64encode((FONTS / file).read_bytes()).decode()
    return (f"@font-face{{font-family:'{family}';font-weight:{weight};"
            f"src:url(data:font/woff2;base64,{data}) format('woff2');}}")


def scene() -> str:
    R = Lehmer(11)
    f = lambda n: f"{n:.1f}"
    o = []
    o.append(f'<rect x="0" y="280" width="{W}" height="480" fill="url(#cvsky)"/>')
    o.append('<circle cx="1296" cy="392" r="30" fill="#fbf7ee"/>'
             '<circle cx="1296" cy="392" r="42" fill="none" stroke="#fbf7ee" stroke-width="1"/>')
    o.append('<path d="M0 700 C180 672 330 684 500 664 C660 646 780 612 900 588 C1000 568 1080 548 1160 548 '
             'C1260 548 1350 580 1440 596 V900 H0Z" fill="#46708a"/>')
    ridge = ("M560 742 C680 716 760 676 850 628 C900 602 940 570 990 556 C1030 545 1056 560 1090 540 "
             "C1124 520 1150 498 1190 496 C1232 494 1256 520 1290 530 C1330 542 1352 536 1380 556 "
             "C1404 573 1424 590 1440 600")
    o.append(f'<path d="{ridge} V900 H560Z" fill="#1c3550"/>')
    o.append('<path d="M1010 552 C1034 546 1056 560 1090 540 C1124 520 1150 498 1190 496 C1232 494 1256 520 1290 530 '
             'C1320 539 1340 538 1362 546 C1340 548 1330 556 1310 550 C1290 544 1282 556 1262 548 C1242 540 1234 552 '
             '1214 540 C1196 530 1186 534 1170 528 C1150 536 1138 552 1118 554 C1098 556 1090 568 1070 566 '
             'C1050 564 1036 558 1010 552Z" fill="#fbf7ee"/>')
    o.append(f'<path d="M1190 494V462M1180 473H1200" stroke="{GOLD}" stroke-width="2.6"/>')
    # skyline
    x = 40.0
    while x < 1400:
        t = x / 1440
        w = 16 + R() * 26
        h = 26 + R() ** 1.7 * (40 + 140 * math.exp(-(((t - 0.62) / 0.17) ** 2)))
        y0 = 742
        o.append(f'<rect x="{f(x)}" y="{f(y0 - h)}" width="{f(w)}" height="{f(h)}" fill="#0f1a30"/>')
        k = 0
        while k < h / 10 - 1:
            j = 0
            while j < w / 7 - 1:
                if R() < 0.4:
                    if R() < 0.12:
                        R()
                    o.append(f'<rect x="{f(x + 4 + j * 7)}" y="{f(y0 - h + 6 + k * 10)}" width="2.6" height="4" fill="{GOLD}"/>')
                j += 1
            k += 1
        if R() < 0.15:
            o.append(f'<path d="M{f(x + w / 2)} {f(y0 - h)}v-20" stroke="#0f1a30" stroke-width="1.6"/>')
        x += w + 3 + R() * 8
    # river
    o.append(f'<rect x="0" y="740" width="{W}" height="160" fill="{BLUE}"/>')
    for r in range(13):
        y = 754 + r * 11.5
        d = ""
        px = -20 + R() * 60
        while px < 1440:
            ln = 30 + R() * 150
            d += f"M{f(px)} {f(y)}h{f(ln)}"
            px += ln + 16 + R() * 70
        o.append(f'<path d="{d}" stroke="{CREAM if r % 3 == 1 else PALE}" stroke-width="1" opacity="{f(0.55 - r * 0.02)}" fill="none"/>')
    for _ in range(90):
        gx = 60 + R() * 1320
        gy = 748 + R() * 46
        gl = 3 + R() * 7
        o.append(f'<path d="M{f(gx)} {f(gy)}v{f(gl)}" stroke="{GOLD}" stroke-width="1.6" opacity="{f(0.35 + R() * 0.4)}"/>')
    o.append(f'<rect x="0" y="806" width="{W}" height="94" fill="{NAVY}" opacity=".55"/>')
    # bridge
    br = "M620 752H1440M620 736H1440"
    for bx in range(620, 1440, 16):
        br += f"M{bx} 752l8-16l8 16"
    br += "M900 736Q1020 640 1140 736"
    for bx in range(916, 1140, 16):
        t = (bx - 900) / 240
        br += f"M{bx} {f(736 - 4 * 48 * t * (1 - t))}V736"
    o.append(f'<path d="{br}" fill="none" stroke="{GOLD}" stroke-width="1.4"/>')
    for px in (760, 900, 1140, 1300):
        o.append(f'<path d="M{px} 752V800" stroke="{GOLD}" stroke-width="2.4"/>')

    def berry(x0, y0, ang, ln, cv):
        s, b = "", ""
        a = ang
        steps = round(ln / 11)
        for i in range(steps):
            nx, ny = x0 + math.cos(a) * 11, y0 + math.sin(a) * 11
            s += (f"M{f(x0)} {f(y0)}L" if i == 0 else "L") + f"{f(nx)} {f(ny)}"
            if i % 2 == 1:
                ca = a + (1 if i % 4 == 1 else -1) * 1.2
                for k in range(3):
                    cx = nx + math.cos(ca + k * 0.5 - 0.5) * (10 + k * 2.5)
                    cy = ny + math.sin(ca + k * 0.5 - 0.5) * (10 + k * 2.5)
                    b += (f'<circle cx="{f(cx)}" cy="{f(cy)}" r="5.2" fill="{VERMILION}"/>'
                          f'<circle cx="{f(cx - 1.5)}" cy="{f(cy - 1.7)}" r="1.3" fill="#f6c9a8"/>')
            x0, y0 = nx, ny
            a += cv
        return f'<path d="{s}" stroke="#3a2618" stroke-width="2" fill="none"/>{b}'

    o.append(berry(1440, 716, -2.55, 200, -0.03) + berry(1440, 668, -2.2, 150, 0.04))
    return "".join(o)


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
        'dusk on the first frost — Mont Royal and its cross, the lit skyline, the Jacques-Cartier bridge in gold and a '
        'winterberry branch. Rare events, honestly measured.</desc>',
        f"<style>{css}</style>",
        f'<defs><linearGradient id="cvsky" x1="0" x2="0" y1="0" y2="1"><stop offset="0" stop-color="{CREAM}" stop-opacity="0"/>'
        f'<stop offset=".5" stop-color="{DUSK}"/><stop offset="1" stop-color="{ROSE}"/></linearGradient></defs>',
        f'<rect width="{W}" height="{H}" fill="{CREAM}"/>',
        f'<g transform="translate(0 {DY})">{scene()}</g>',
        # issue bar
        f'<path d="M{lx} 44H{rx}M{lx} 80H{rx}" stroke="{NAVY}" stroke-width="1"/>',
        f'<text class="cap" x="{lx}" y="66" fill="{NAVY}">N° 01</text>',
        f'<text class="cap" x="{W / 2}" y="66" fill="{NAVY}" text-anchor="middle">STATISTICIAN · DATA ENGINEER</text>',
        f'<text class="cap" x="{rx}" y="66" fill="{NAVY}" text-anchor="end">MONTRÉAL · HIVER 2026</text>',
        # masthead
        f'<text class="d" x="{lx - 6}" y="286" font-size="244" font-weight="600" letter-spacing="-2.4" fill="{NAVY}">ZIYI ZHOU</text>',
        f'<text class="d" x="{lx}" y="350" font-size="31" font-weight="500" fill="{VERMILION}">Rare events, honestly measured.</text>',
    ]
    lines = ["I model rare, high-impact events — floods,", "financial tail risk, gaps in education data — and",
             "build the software that makes those models", "trustworthy."]
    for i, ln in enumerate(lines):
        o.append(f'<text class="d" x="{lx}" y="{394 + i * 29}" font-size="20" font-weight="500" fill="{NAVY}">{ln}</text>')
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
