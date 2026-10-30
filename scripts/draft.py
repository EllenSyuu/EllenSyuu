"""Drafting kit for the profile's plates, in the hand of ellensyuu.github.io.

Ink is blue-black, construction is graphite, colour is orange and used sparingly. Tone is
ruled hatching (parallel lines, slightly irregular), never fill. Lines are inked twice.
Everything is plain SVG so GitHub shows it as an image without scripts.
"""
from __future__ import annotations

import math
import random
from xml.sax.saxutils import escape

INK = "#22314a"
SLATE = "#46526a"
GRAPH = "#6f7b8c"
FAINT = "#b4bcc7"
PAPER = "#f6f1e6"
FACE = "#eee6d6"
LIGHT = "#fbf8f1"
ORANGE = "#cf602b"
AMBER = "#e0a046"
RUST = "#a3432a"
SAGE = "#7c8a5c"

_n = [0]


def uid(prefix: str = "c") -> str:
    _n[0] += 1
    return f"{prefix}{_n[0]}"


def f(v: float) -> str:
    return f"{v:.1f}"


def P(pts, close=True) -> str:
    return "M" + " L".join(f"{f(x)},{f(y)}" for x, y in pts) + (" Z" if close else "")


def line(d: str, w=1.0, c=INK, op=1.0, extra="") -> str:
    return (f'<path d="{d}" fill="none" stroke="{c}" stroke-width="{w}" stroke-linecap="round" '
            f'stroke-linejoin="round" opacity="{op}" {extra}/>')


def inked(rng: random.Random, pts, w=1.1, c=INK, close=False, op=1.0) -> str:
    """A ruled line inked twice: a firm pass and a hairline a fraction off it."""
    d1 = P(pts, close)
    off = [(x + rng.uniform(-.55, .55), y + rng.uniform(-.55, .55)) for x, y in pts]
    return line(d1, w, c, op) + line(P(off, close), w * .4, c, op * .5)


def fill(d: str, c=PAPER, op=1.0) -> str:
    return f'<path d="{d}" fill="{c}" fill-opacity="{op}"/>'


def hatch(rng, d: str, box, spacing=3.2, angle=60, w=.5, c=GRAPH, op=.75, cross=False) -> str:
    """Ruled hatching clipped to shape d: long parallel lines with a little irregularity."""
    cid = uid("h")
    x0, y0, x1, y1 = box
    out = [f'<clipPath id="{cid}"><path d="{d}"/></clipPath><g clip-path="url(#{cid})">']
    for ang in ([angle, angle + 90] if cross else [angle]):
        a = math.radians(ang)
        dx, dy = math.cos(a), math.sin(a)
        nx, ny = -dy, dx
        cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
        R = math.hypot(x1 - x0, y1 - y0) / 2 + 4
        segs = []
        k = -R
        while k <= R:
            j = rng.uniform(-.35, .35)
            px, py = cx + nx * (k + j), cy + ny * (k + j)
            t0, t1 = -R + rng.uniform(0, 3), R - rng.uniform(0, 3)
            segs.append(f"M{f(px + dx * t0)},{f(py + dy * t0)} L{f(px + dx * t1)},{f(py + dy * t1)}")
            k += spacing * rng.uniform(.9, 1.1)
        out.append(line(" ".join(segs), w, c, op if ang == angle else op * .6))
    out.append("</g>")
    return "".join(out)


def text(x, y, s, cls="serif", size=14, c=INK, anchor="start", extra="") -> str:
    return (f'<text x="{f(x)}" y="{f(y)}" class="{cls}" font-size="{size}" fill="{c}" '
            f'text-anchor="{anchor}" {extra}>{escape(s)}</text>')


def leader(rng, px, py, tx, ty, label, cls="hand", size=14, c=INK, anchor=None) -> str:
    """A labelled leader: a small target cross at the point, a curved lead, the label."""
    anchor = anchor or ("start" if tx >= px else "end")
    gap = 4 if anchor == "start" else -4
    mx = px + (tx - px) * .35
    return (line(f"M{f(px - 3)},{f(py)} h6 M{f(px)},{f(py - 3)} v6", .7, INK, .9)
            + line(f"M{f(px)},{f(py)} Q{f(mx)},{f(ty)} {f(tx - gap)},{f(ty)}", .55, GRAPH, .85)
            + text(tx, ty + size * .32, label, cls, size, c, anchor))


def dim_v(x, y0, y1, label, side=1, cls="hand", size=14) -> str:
    """Vertical dimension with arrowheads and extension ticks."""
    a = 5
    d = (f"M{f(x)},{f(y0)} V{f(y1)} M{f(x - 5)},{f(y0)} h10 M{f(x - 5)},{f(y1)} h10 "
         f"M{f(x - 2.5)},{f(y0 + a)} L{f(x)},{f(y0)} L{f(x + 2.5)},{f(y0 + a)} "
         f"M{f(x - 2.5)},{f(y1 - a)} L{f(x)},{f(y1)} L{f(x + 2.5)},{f(y1 - a)}")
    ty = (y0 + y1) / 2
    return (line(d, .6, INK, .85)
            + f'<rect x="{f(x - 9)}" y="{f(ty - 30)}" width="18" height="60" fill="{PAPER}"/>'
            + text(x + 4, ty, label, cls, size, INK, "middle", f'transform="rotate(-90 {f(x + 4)} {f(ty)})"'))


def dim_h(y, x0, x1, label, cls="hand", size=14) -> str:
    a = 5
    d = (f"M{f(x0)},{f(y)} H{f(x1)} M{f(x0)},{f(y - 5)} v10 M{f(x1)},{f(y - 5)} v10 "
         f"M{f(x0 + a)},{f(y - 2.5)} L{f(x0)},{f(y)} L{f(x0 + a)},{f(y + 2.5)} "
         f"M{f(x1 - a)},{f(y - 2.5)} L{f(x1)},{f(y)} L{f(x1 - a)},{f(y + 2.5)}")
    w = len(label) * size * .42 + 12
    mx = (x0 + x1) / 2
    return (line(d, .6, INK, .85) + f'<rect x="{f(mx - w / 2)}" y="{f(y - 9)}" width="{f(w)}" height="16" fill="{PAPER}"/>'
            + text(mx, y + 4, label, cls, size, INK, "middle"))


def compass(x, y, r=22) -> str:
    return (f'<g transform="translate({f(x)} {f(y)})">'
            + line(f"M0,{-r} L{r * .17:.1f},0 L0,{r} L{-r * .17:.1f},0 Z", .7, INK)
            + f'<path d="M0,{-r} L{r * .17:.1f},0 L{-r * .17:.1f},0 Z" fill="{INK}"/>'
            + f'<circle r="{r * .62:.1f}" fill="none" stroke="{INK}" stroke-width=".4" opacity=".6"/>'
            + text(0, -r - 5, "N", "ital", 13, INK, "middle") + "</g>")


def scale_bar(x, y, n=4, step=18, label="", unit="") -> str:
    o = []
    for i in range(n):
        if i % 2 == 0:
            o.append(f'<rect x="{f(x + i * step)}" y="{f(y - 2.5)}" width="{step}" height="5" fill="{INK}"/>')
    o.append(line(f"M{f(x)},{f(y - 2.5)} h{n * step} v5 h-{n * step} Z", .6, INK))
    o.append(text(x, y - 7, "0", "serif", 11, GRAPH, "middle"))
    o.append(text(x + n * step, y - 7, label, "serif", 11, GRAPH, "middle"))
    if unit:
        o.append(text(x + n * step + 8, y + 4, unit, "ital", 12, GRAPH))
    return "".join(o)


def title_block(x, y, num, name, note="", sign="Z. Zhou, MMXXVI", width=420, sign_x=None) -> str:
    """'Planche II.  EXTRÊMES DE PLUIE · QUÉBEC MÉRIDIONAL', double rule, hand note, signature."""
    o = [text(x, y, num, "ital", 22, INK),
         text(x + 26 + len(num) * 8.6, y, name.upper(), "caps", 10.5, GRAPH),
         line(f"M{x},{y + 10} h{width}", .5, INK), line(f"M{x},{y + 13} h{width}", .25, INK)]
    if sign:
        o.append(text(sign_x if sign_x is not None else x + width, y, sign, "hand", 15, GRAPH, "end"))
    if note:
        o.append(text(x, y + 34, note, "hand", 14.5, ORANGE))
    return "".join(o)


def iso(cx, cy, s):
    """Isometric projection at scale s with origin (cx, cy): returns P(x, y, z) -> (X, Y)."""
    c = math.cos(math.radians(30))

    def p(x, y, z):
        return (cx + (x - y) * c * s, cy + (x + y) * .5 * s - z * s)
    return p
