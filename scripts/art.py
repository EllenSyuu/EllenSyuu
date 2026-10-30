"""Atelier kit for the illustrated plates: graphite hatching, watercolour washes, sketchbook margins.

The look aims at a fine-art sketchbook: a hard pencil for construction lines, a soft one for
contours drawn twice, hatching in short broken strokes, and transparent washes that pool at
their edges and granulate on the paper. Only SVG + CSS, so GitHub can show it as an image.
"""
from __future__ import annotations

import math
import random
import re
import zlib

from sketch import f1, smooth

INK = "#1f2a3d"
GRAPHITE = "#4a5363"

# Pigments, named as on a palette. Each plate picks its own few.
PIG = {
    # keys are roles in the drawings; values are the pencils actually used
    "prussian": "#1f9a6b",   # emerald
    "indigo": "#2f7d55",     # forest green
    "cerulean": "#3fbf9b",   # jade
    "rose": "#f7c948",       # Naples yellow
    "madder": "#d9536f",
    "vermilion": "#ea4f2f",
    "sienna": "#d48a2c",     # raw sienna
    "sepia": "#8a6a3f",
    "sakura": "#f39cb6",
    "sap": "#8cc63f",        # spring green
    "viridian": "#15946c",
    "teal": "#2fb29a",
    "coral": "#f7a23b",      # apricot
    "lavender": "#b8d44a",   # chartreuse
    "slate": "#7fb87a",      # sage
    "amber": "#f6b726",
    "sand": "#f0cf6a",
    "snow": "#ffffff",
}


def defs() -> str:
    """Filters shared by all plates: five watercolour variants, a bloom and a graphite tooth."""
    wc = []
    for k, (freq, scale, seed) in enumerate([(0.016, 26, 2), (0.022, 20, 7), (0.03, 16, 13), (0.012, 34, 21), (0.045, 10, 29)]):
        wc.append(f"""
<filter id="wc{k}" x="-15%" y="-15%" width="130%" height="130%" color-interpolation-filters="sRGB">
  <feTurbulence type="fractalNoise" baseFrequency="{freq}" numOctaves="4" seed="{seed}" result="t"/>
  <feDisplacementMap in="SourceGraphic" in2="t" scale="{scale}" xChannelSelector="R" yChannelSelector="G" result="d"/>
  <feGaussianBlur in="d" stdDeviation="1.1" result="b"/>
  <feGaussianBlur in="d" stdDeviation="6" result="bb"/>
  <feComposite in="b" in2="bb" operator="arithmetic" k1="0" k2="1.55" k3="-0.62" k4="0" result="edge"/>
  <feTurbulence type="fractalNoise" baseFrequency="0.55" numOctaves="2" seed="{seed + 3}" result="g"/>
  <feColorMatrix in="g" type="matrix" values="0 0 0 0 0  0 0 0 0 0  0 0 0 0 0  0 0 0 -0.6 1.22" result="gm"/>
  <feComposite in="edge" in2="gm" operator="in"/>
</filter>""")
    return "".join(wc) + """
<filter id="patchf" x="0" y="0" width="100%" height="100%">
  <feTurbulence type="fractalNoise" baseFrequency="0.009 0.016" numOctaves="3" seed="31" result="n"/>
  <feColorMatrix in="n" type="matrix" values="0 0 0 0 1  0 0 0 0 1  0 0 0 0 1  2.0 0 0 0 0.12"/>
</filter>
<linearGradient id="skyfade" x1="0" y1="0" x2="0" y2="260" gradientUnits="userSpaceOnUse">
  <stop offset="0" stop-color="#000"/><stop offset=".25" stop-color="#000"/><stop offset="1" stop-color="#fff"/></linearGradient>
<mask id="vfade" maskUnits="userSpaceOnUse" x="-100" y="-100" width="900" height="820">
  <rect x="-100" y="-100" width="900" height="820" fill="url(#skyfade)"/></mask>
<mask id="patchy" maskUnits="userSpaceOnUse" x="-100" y="-100" width="900" height="820">
  <g mask="url(#vfade)"><rect x="-100" y="-100" width="900" height="820" fill="#fff" filter="url(#patchf)"/></g></mask>
<filter id="bloom" x="-60%" y="-60%" width="220%" height="220%"><feGaussianBlur stdDeviation="9"/></filter>
<filter id="soft" x="-30%" y="-30%" width="160%" height="160%"><feGaussianBlur stdDeviation="3"/></filter>
<filter id="tooth" x="0" y="0" width="100%" height="100%">
  <feTurbulence type="fractalNoise" baseFrequency="1.4" numOctaves="1" seed="4" result="n"/>
  <feColorMatrix in="n" type="matrix" values="0 0 0 0 0  0 0 0 0 0  0 0 0 0 0  0 0 0 -2.2 1.6" result="m"/>
  <feComposite in="SourceGraphic" in2="m" operator="in"/>
</filter>
<filter id="rough" x="-3%" y="-3%" width="106%" height="106%">
  <feTurbulence type="fractalNoise" baseFrequency="0.7" numOctaves="2" seed="9" result="n"/>
  <feDisplacementMap in="SourceGraphic" in2="n" scale="1.4" xChannelSelector="R" yChannelSelector="G"/>
</filter>
<filter id="edgefade" x="-10%" y="-10%" width="120%" height="120%">
  <feTurbulence type="fractalNoise" baseFrequency="0.011" numOctaves="4" seed="17" result="t"/>
  <feDisplacementMap in="SourceGraphic" in2="t" scale="70" xChannelSelector="R" yChannelSelector="G" result="d"/>
  <feGaussianBlur in="d" stdDeviation="7"/>
</filter>
"""


# ------------------------------------------------------------------ washes

def _bbox(d: str):
    xs, ys = [], []
    for cmd, args in re.findall(r"([A-Za-z])([^A-Za-z]*)", d):
        if not cmd.isupper() or cmd in "ZA":
            continue
        nums = [float(v) for v in re.findall(r"-?\d+(?:\.\d+)?", args)]
        if cmd == "H":
            xs += nums
        elif cmd == "V":
            ys += nums
        else:
            xs += nums[0::2]
            ys += nums[1::2]
    if not xs or not ys:
        return None
    return min(xs), min(ys), max(xs), max(ys)


def _light(color: str) -> bool:
    r, g, b = (int(color[i:i + 2], 16) for i in (1, 3, 5))
    return 0.299 * r + 0.587 * g + 0.114 * b > 225


_ids = [0]
PENCIL_AREA = 5200  # px²: larger than this, colour goes on as pencil, not as a flat wash


def wash(d: str, color: str, op: float = 0.4, f: int = 0, extra: str = "") -> str:
    """Colour, laid in with a coloured pencil only — no watercolour anywhere.

    Large areas get sparse, shallow strokes that break into patches and leave paper showing;
    small shapes (a torii, a lantern, a petal) get tight hatching, crossed when the colour
    should read strong. Near-white shapes (snow, foam, clouds) are paper held back.
    """
    if _light(color):
        return f'<path d="{d}" fill="{color}" fill-opacity="{op:.2f}" {extra}/>'
    box = _bbox(d)
    if box is None:
        return ""
    _ids[0] += 1
    cid = f"cp{_ids[0]}"
    rng = random.Random(zlib.crc32(d.encode()))
    x0, y0, x1, y1 = box
    area = (x1 - x0) * (y1 - y0)
    k = min(1.0, op * 2.1)
    if area > PENCIL_AREA:
        ang = 26 + rng.uniform(-8, 8)
        body = hatch(rng, x0, y0, x1, y1, spacing=4.0 - 2.0 * k, angle=ang, lmin=8, lmax=28, gap=.3,
                     ops=(.28 * k + .1, .46 * k + .12, .64 * k + .14), sw=.8, color=color, jitter=4)
        if k > .35:
            body += hatch(rng, x0, y0, x1, y1, spacing=7 - 3 * k, angle=ang + 64, lmin=6, lmax=18, gap=.5,
                          ops=(.1 * k + .05, .18 * k + .06, .26 * k + .07), sw=.6, color=color, jitter=5)
        return (f'<g {extra}><clipPath id="{cid}"><path d="{d}"/></clipPath>'
                f'<g clip-path="url(#{cid})" mask="url(#patchy)">{body}</g></g>')
    ang = 40 + rng.uniform(-15, 15)
    body = hatch(rng, x0 - 2, y0 - 2, x1 + 2, y1 + 2, spacing=1.9 - .7 * k, angle=ang, lmin=3, lmax=11, gap=.1,
                 ops=(.4 * k + .22, .6 * k + .22, .78 * k + .2), sw=.8, color=color, jitter=6)
    if k > .55:
        body += hatch(rng, x0 - 2, y0 - 2, x1 + 2, y1 + 2, spacing=3.2 - k, angle=ang + 75, lmin=3, lmax=9, gap=.25,
                      ops=(.25 * k + .1, .4 * k + .1, .55 * k + .1), sw=.55, color=color, jitter=6)
    return f'<g {extra}><clipPath id="{cid}"><path d="{d}"/></clipPath><g clip-path="url(#{cid})">{body}</g></g>'


def blob(rng, cx, cy, rx, ry, n=10, wob=0.22) -> str:
    pts = []
    for i in range(n):
        t = 2 * math.pi * i / n
        r = 1 + rng.uniform(-wob, wob)
        pts.append((cx + rx * r * math.cos(t), cy + ry * r * math.sin(t)))
    return smooth(pts, closed=True)


def poly(pts) -> str:
    return "M" + " L".join(f"{f1(x)},{f1(y)}" for x, y in pts) + " Z"


# ------------------------------------------------------------------ graphite

def hatch(rng, x0, y0, x1, y1, spacing=4.0, angle=55.0, lmin=8, lmax=30, gap=0.35,
          ops=(0.22, 0.42, 0.65), sw=0.55, color=GRAPHITE, jitter=4.0) -> str:
    """Short broken strokes in one direction — how a soft pencil lays down a tone.

    Strokes are bucketed into three opacities so a whole tone is only three <path>s.
    """
    a = math.radians(angle + rng.uniform(-1.5, 1.5))
    dx, dy = math.cos(a), math.sin(a)
    nx, ny = -dy, dx
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
    R = math.hypot(x1 - x0, y1 - y0) / 2 + 6
    buckets = [[], [], []]
    k = -R
    while k <= R:
        t = -R + rng.uniform(0, lmin)
        while t < R:
            L = rng.uniform(lmin, lmax)
            if rng.random() > gap:
                aj = math.radians(rng.uniform(-jitter, jitter))
                ex, ey = dx * math.cos(aj) - dy * math.sin(aj), dy * math.cos(aj) + dx * math.sin(aj)
                sx, sy = cx + nx * (k + rng.uniform(-.6, .6)) + dx * t, cy + ny * (k + rng.uniform(-.6, .6)) + dy * t
                buckets[rng.randrange(3)].append(f"M{sx:.0f} {sy:.0f}l{ex * L:.0f} {ey * L:.0f}")
            t += L + rng.uniform(1, 5)
        k += spacing * rng.uniform(.8, 1.2)
    return "".join(
        f'<path d="{" ".join(b)}" fill="none" stroke="{color}" stroke-width="{sw}" stroke-linecap="round" opacity="{ops[i]}"/>'
        for i, b in enumerate(buckets) if b
    )


def tone(rng, clip_id, d, box, layers=((4.2, 52),), **kw) -> str:
    """A hatched tone clipped to a shape; several layers make cross-hatching."""
    out = [f'<clipPath id="{clip_id}"><path d="{d}"/></clipPath><g clip-path="url(#{clip_id})">']
    for spacing, ang in layers:
        out.append(hatch(rng, *box, spacing=spacing, angle=ang, **kw))
    out.append("</g>")
    return "".join(out)


def contour(rng, pts, sw=1.3, color=INK, closed=False, ghost=True, op=0.9) -> str:
    """A line drawn with a soft pencil: a firm pass and a lighter, slightly offset second pass."""
    d = smooth(pts, closed=closed)
    out = f'<path d="{d}" fill="none" stroke="{color}" stroke-width="{sw}" stroke-linecap="round" stroke-linejoin="round" opacity="{op}"/>'
    if ghost:  # the line traced over again, twice, never quite on top of itself
        for amp, w, a in ((1.3, .45, .45), (2.2, .3, .28)):
            off = [(x + rng.uniform(-amp, amp), y + rng.uniform(-amp, amp)) for x, y in pts]
            out += f'<path d="{smooth(off, closed=closed)}" fill="none" stroke="{color}" stroke-width="{sw * w:.2f}" stroke-linecap="round" opacity="{op * a:.2f}"/>'
    return out


def stroke(d, sw=1.0, color=INK, op=0.9, extra="") -> str:
    return f'<path d="{d}" fill="none" stroke="{color}" stroke-width="{sw}" stroke-linecap="round" stroke-linejoin="round" opacity="{op}" {extra}/>'


def construction(lines, op=0.16) -> str:
    """Hard-pencil guide lines that a finished drawing leaves visible."""
    d = " ".join(f"M{f1(a)},{f1(b)} L{f1(c)},{f1(e)}" for a, b, c, e in lines)
    return f'<path d="{d}" fill="none" stroke="{GRAPHITE}" stroke-width=".5" opacity="{op}"/>'


def swatches(x, y, items, hand_cls="hand") -> str:
    """Pigment notes in the margin: a dab of each colour and its name in pencil."""
    rng = random.Random(int(x * 7 + y))
    out = []
    for i, (name, col) in enumerate(items):
        cx = x + i * 92
        out.append(wash(blob(rng, cx, y, 9, 6.5, n=8, wob=.25), col, .75, f=4))
        out.append(f'<text x="{f1(cx + 14)}" y="{f1(y + 4)}" class="{hand_cls}" font-size="12" fill="{GRAPHITE}">{name}</text>')
    return "".join(out)


def ribbon(pts, w0, w1) -> str:
    """A tapered brush stroke along pts, w0 wide at the start and w1 at the end."""
    n = len(pts)
    left, right = [], []
    for i, (x, y) in enumerate(pts):
        a = pts[max(i - 1, 0)]
        b = pts[min(i + 1, n - 1)]
        dx, dy = b[0] - a[0], b[1] - a[1]
        L = math.hypot(dx, dy) or 1
        nx, ny = -dy / L, dx / L
        w = (w0 + (w1 - w0) * i / max(n - 1, 1)) / 2
        left.append((x + nx * w, y + ny * w))
        right.append((x - nx * w, y - ny * w))
    return smooth(left) + " L" + smooth(right[::-1])[1:] + " Z"
