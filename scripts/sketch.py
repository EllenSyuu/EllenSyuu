"""Shared drawing kit: the ink-and-pencil vocabulary of ellensyuu.github.io, as SVG strings.

Every plate on the profile page is drawn from these pieces so they read as one sketchbook:
warm paper, blue-black ink, graphite, a rust accent, and three typefaces embedded as
subsets so the drawings look the same wherever GitHub shows them.
"""
from __future__ import annotations

import base64
import os
import math
import random
from functools import lru_cache
from pathlib import Path
from xml.sax.saxutils import escape

FONTS = Path(__file__).parent / "fonts"

PAPER = os.environ.get("PAPER", "#f4f4f1")  # museum white: neutral, a breath cool
PAPER_LIGHT = "#fbfbf9"
PAPER_DARK = "#e7e7e2"
INK = "#22314a"
SLATE = "#46526a"
GRAPHITE = "#6f7b8c"
FAINT = "#b4bcc7"
RUST = "#a84a26"
MAPLE = "#cf602b"
AMBER = "#e0a046"
FROST = "#c9d4df"

FACES = {
    "serif": ("cormorant-500.woff2", "Cormorant Garamond", "normal"),
    "serif-i": ("cormorant-500i.woff2", "Cormorant Garamond", "italic"),
    "hand": ("belle-aurore.woff2", "La Belle Aurore", "normal"),
    "sans": ("inter-400.woff2", "Inter", "normal"),
}


def font_css(*keys: str) -> str:
    out = []
    for k in keys:
        file, family, style = FACES[k]
        data = base64.b64encode((FONTS / file).read_bytes()).decode()
        out.append(
            f"@font-face{{font-family:'{family}';font-style:{style};font-weight:500;"
            f"src:url(data:font/woff2;base64,{data}) format('woff2');}}"
        )
    return "".join(out)


BASE_CSS = f"""
.serif{{font-family:'Cormorant Garamond',Garamond,'Times New Roman',serif;font-weight:500}}
.ital{{font-family:'Cormorant Garamond',Garamond,serif;font-style:italic;font-weight:500}}
.hand{{font-family:'La Belle Aurore','Segoe Script',cursive}}
.sans{{font-family:Inter,-apple-system,'Segoe UI',Helvetica,Arial,sans-serif}}
.caps{{font-family:'Cormorant Garamond',Garamond,serif;font-weight:500;letter-spacing:.2em}}
.ink{{fill:none;stroke:{INK};stroke-linecap:round;stroke-linejoin:round}}
.pen{{fill:none;stroke:{GRAPHITE};stroke-linecap:round;stroke-linejoin:round}}
.draw{{stroke-dasharray:1;stroke-dashoffset:1;animation:draw 2.2s cubic-bezier(.55,.05,.25,1) forwards}}
.fade{{animation:fade 1.4s ease both}}
.write{{animation:write 1.6s steps(28,end) both}}
@keyframes draw{{to{{stroke-dashoffset:0}}}}
@keyframes fade{{from{{opacity:0}}}}
@keyframes write{{from{{clip-path:inset(0 100% 0 0)}}to{{clip-path:inset(0 0 0 0)}}}}
@media (prefers-reduced-motion:reduce){{
  *{{animation:none!important}} .draw{{stroke-dashoffset:0}}
}}
"""

PENCIL_DEFS = """
<filter id="pencil" x="-5%" y="-5%" width="110%" height="110%">
  <feTurbulence type="fractalNoise" baseFrequency="0.9" numOctaves="1" seed="3" result="n"/>
  <feDisplacementMap in="SourceGraphic" in2="n" scale="1.6" xChannelSelector="R" yChannelSelector="G"/>
</filter>
<filter id="wash" x="-20%" y="-20%" width="140%" height="140%">
  <feTurbulence type="fractalNoise" baseFrequency="0.035" numOctaves="3" seed="8" result="n"/>
  <feDisplacementMap in="SourceGraphic" in2="n" scale="14" xChannelSelector="R" yChannelSelector="G" result="d"/>
  <feGaussianBlur in="d" stdDeviation="2.2"/>
</filter>
<filter id="grain" x="0" y="0" width="100%" height="100%">
  <feTurbulence type="fractalNoise" baseFrequency="0.85" numOctaves="2" seed="11" result="n"/>
  <feColorMatrix in="n" type="matrix" values="0 0 0 0 0.13  0 0 0 0 0.19  0 0 0 0 0.29  0 0 0 0.09 0"/>
</filter>
"""


def svg_open(w: int, h: int, title: str, desc: str, fonts=("serif", "serif-i", "hand", "sans"), css="") -> str:
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}" '
        f'role="img" aria-labelledby="t d">'
        f"<title id=\"t\">{escape(title)}</title><desc id=\"d\">{escape(desc)}</desc>"
        f"<style>{font_css(*fonts)}{BASE_CSS}{css}</style><defs>{PENCIL_DEFS}</defs>"
        f'<rect width="{w}" height="{h}" fill="{PAPER}"/>'
    )


def paper_finish(w: int, h: int) -> str:
    return f'<rect width="{w}" height="{h}" filter="url(#grain)" opacity=".9" pointer-events="none"/></svg>'


# ---------------------------------------------------------------- text metrics

@lru_cache(maxsize=None)
def _font(key: str):
    from fontTools.ttLib import TTFont

    f = TTFont(FONTS / FACES[key][0])
    return f, f.getBestCmap(), f["hmtx"], f["head"].unitsPerEm


def text_width(s: str, key: str, size: float, tracking: float = 0.0) -> float:
    f, cmap, hmtx, upm = _font(key)
    total = 0
    for ch in s:
        g = cmap.get(ord(ch))
        total += hmtx[g][0] if g else upm * 0.5
    return total / upm * size + tracking * size * max(len(s) - 1, 0)


def wrap(s: str, key: str, size: float, width: float) -> list[str]:
    lines, cur = [], ""
    for word in s.split():
        trial = f"{cur} {word}".strip()
        if cur and text_width(trial, key, size) > width:
            lines.append(cur)
            cur = word
        else:
            cur = trial
    if cur:
        lines.append(cur)
    return lines


def text(x, y, s, cls="serif", size=16, fill=INK, anchor="start", extra="") -> str:
    return (
        f'<text x="{x:.1f}" y="{y:.1f}" class="{cls}" font-size="{size}" fill="{fill}" '
        f'text-anchor="{anchor}" {extra}>{escape(s)}</text>'
    )


# ---------------------------------------------------------------- strokes

def f1(v: float) -> str:
    return f"{v:.1f}"


def smooth(points, closed=False) -> str:
    """Catmull–Rom through points, as one cubic Bézier path."""
    pts = list(points)
    if len(pts) < 3:
        return "M" + " L".join(f"{f1(x)},{f1(y)}" for x, y in pts)
    if closed:
        pts = pts[-1:] + pts + pts[:2]
    else:
        pts = pts[:1] + pts + pts[-1:]
    d = f"M{f1(pts[1][0])},{f1(pts[1][1])}"
    for i in range(1, len(pts) - 2):
        p0, p1, p2, p3 = pts[i - 1], pts[i], pts[i + 1], pts[i + 2]
        c1 = (p1[0] + (p2[0] - p0[0]) / 6, p1[1] + (p2[1] - p0[1]) / 6)
        c2 = (p2[0] - (p3[0] - p1[0]) / 6, p2[1] - (p3[1] - p1[1]) / 6)
        d += f" C{f1(c1[0])},{f1(c1[1])} {f1(c2[0])},{f1(c2[1])} {f1(p2[0])},{f1(p2[1])}"
    return d + (" Z" if closed else "")


def wobble_line(rng: random.Random, x1, y1, x2, y2, amp=1.2, overshoot=2.0) -> str:
    """A hand-ruled line: slight bow, a little overshoot at both ends."""
    L = math.hypot(x2 - x1, y2 - y1) or 1
    ux, uy = (x2 - x1) / L, (y2 - y1) / L
    nx, ny = -uy, ux
    a = (x1 - ux * rng.uniform(0, overshoot), y1 - uy * rng.uniform(0, overshoot))
    b = (x2 + ux * rng.uniform(0, overshoot), y2 + uy * rng.uniform(0, overshoot))
    bow = rng.uniform(-amp, amp)
    m = ((a[0] + b[0]) / 2 + nx * bow, (a[1] + b[1]) / 2 + ny * bow)
    return f"M{f1(a[0])},{f1(a[1])} Q{f1(m[0])},{f1(m[1])} {f1(b[0])},{f1(b[1])}"


def sketch_rect(rng, x, y, w, h, amp=1.0, overshoot=3.0) -> str:
    return " ".join(
        wobble_line(rng, *seg, amp=amp, overshoot=overshoot)
        for seg in ((x, y, x + w, y), (x + w, y, x + w, y + h), (x + w, y + h, x, y + h), (x, y + h, x, y))
    )


def path(d, cls="ink", sw=1.2, extra="", stroke=None, delay=None, dur=None, draw=False) -> str:
    style = [f"stroke:{stroke}"] if stroke else []
    if delay is not None:
        style.append(f"animation-delay:{delay:.2f}s")
    if dur is not None:
        style.append(f"animation-duration:{dur:.2f}s")
    s = f' style="{";".join(style)}"' if style else ""
    st = ""
    pl = ' pathLength="1"' if draw else ""
    c = cls + (" draw" if draw else "")
    return f'<path d="{d}" class="{c}" stroke-width="{sw}"{st}{pl}{s} {extra}/>'


def hatch_lines(x0, y0, x1, y1, spacing=5.0, angle=60.0) -> str:
    """Parallel strokes covering a box; clip them to a shape to shade it."""
    a = math.radians(angle)
    dx, dy = math.cos(a), math.sin(a)
    nx, ny = -dy, dx
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
    R = math.hypot(x1 - x0, y1 - y0) / 2 + 4
    d = []
    k = -R
    while k <= R:
        px, py = cx + nx * k, cy + ny * k
        d.append(f"M{f1(px - dx * R)},{f1(py - dy * R)} L{f1(px + dx * R)},{f1(py + dy * R)}")
        k += spacing
    return " ".join(d)


def tick_path(cx, cy, s=1.0, rng: random.Random | None = None) -> str:
    """A quick hand check-mark, centred on (cx, cy)."""
    j = (lambda v: v + rng.uniform(-1.2, 1.2)) if rng else (lambda v: v)
    return (
        f"M{f1(cx - 11 * s)},{f1(j(cy - 1 * s))} "
        f"Q{f1(cx - 6 * s)},{f1(cy + 5 * s)} {f1(cx - 3 * s)},{f1(j(cy + 10 * s))} "
        f"Q{f1(cx + 3 * s)},{f1(cy - 6 * s)} {f1(cx + 14 * s)},{f1(j(cy - 15 * s))}"
    )
