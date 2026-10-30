"""The work cards and section headings, set and drawn like the case studies on ellensyuu.github.io.

Each card: kicker in small caps (orange) and the plate number in italic; the title in Cormorant
600; the package in the hand; the question in italic with orange quotes; then a mounted plate —
an engineering drawing of the idea — and one result line. Static.

    python scripts/cards.py        # -> assets/works/*.svg, assets/heading-*.svg
"""
from __future__ import annotations

import math
import random
from pathlib import Path

import art
from draft import (
    AMBER, FACE, FAINT, GRAPH, INK, LIGHT, ORANGE, PAPER, RUST, SAGE, SLATE,
    P, compass, dim_h, f, fill, hatch, inked, iso, leader, line, scale_bar, text,
)
from sketch import ALL_FACES, BASE_CSS, PENCIL_DEFS, font_css, smooth, text_width, wrap

W, H = 640, 580
LIGHT_SLATE = "#34425a"
DARK_SLATE = "#626d7d"


def doc(w, h, title, desc, body: str) -> str:
    from xml.sax.saxutils import escape
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}" role="img" aria-labelledby="t d">'
            f'<title id="t">{escape(title)}</title><desc id="d">{escape(desc)}</desc>'
            f"<style>{font_css(*ALL_FACES)}{BASE_CSS}</style>"
            f"<defs>{PENCIL_DEFS}{art.defs()}"
            '<linearGradient id="plateg" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#fbf8f1"/><stop offset="1" stop-color="#fbf3e6"/></linearGradient>'
            '<filter id="plateshadow" x="-10%" y="-10%" width="120%" height="130%"><feDropShadow dx="0" dy="14" stdDeviation="12" flood-color="#22314a" flood-opacity=".13"/></filter>'
            "</defs>"
            f'<rect width="{w}" height="{h}" fill="{PAPER}"/>{body}'
            f'<rect width="{w}" height="{h}" filter="url(#grain)" opacity=".5" pointer-events="none"/></svg>')


def wash(d, c=ORANGE, op=.45, k=1):
    return f'<path d="{d}" fill="{c}" fill-opacity="{op}" filter="url(#wc{k})"/>'


def cloud(rng, cx, cy, w):
    """The website's cloud: a row of pen bumps climbing to the middle, a flat underside, washed warm."""
    n = 5
    pts = [(cx - w / 2, cy)]
    for i in range(n):
        t0, t1 = i / n, (i + 1) / n
        x0, x1 = cx - w / 2 + w * t0, cx - w / 2 + w * t1
        hgt = w * (.22 + .16 * math.sin(math.pi * (t0 + t1) / 2))
        pts.append(((x0 + x1) / 2, cy - hgt))
        pts.append((x1, cy - w * .05))
    d = f"M{f(cx - w / 2)},{f(cy)} " + " ".join(f"Q{f(a[0])},{f(a[1])} {f(b[0])},{f(b[1])}" for a, b in zip(pts[1::2], pts[2::2])) + " Z"
    return wash(d, ORANGE, .4, 2) + line(d, .9, INK, .85) + line(f"M{f(cx - w * .42)},{f(cy - 3)} h{f(w * .3)}", .5, INK, .5)


def mini_title(x, y, num, name, sign=True, w=560):
    return (text(x, y, num, "ital", 16, INK) + text(x + 14 + len(num) * 6.4, y, name.upper(), "caps", 8, GRAPH)
            + line(f"M{x},{y + 6} h{w * .62}", .45, INK) + line(f"M{x},{y + 8.5} h{w * .62}", .2, INK)
            + (text(x + w, y, "Z. Zhou, MMXXVI", "hand", 12, GRAPH, "end") if sign else ""))


# ======================================================================= the eight drawings
# Each gets the inner frame (x, y, w, h) and draws inside it.

def d_quebec(rng, x, y, w, h):
    """Planche II: the St. Lawrence lowlands as a cut terrain block, arcs of co-occurrence, washed clouds."""
    o = []
    p = iso(x + w * .37, y + h * .33, 23)
    L, D, T = 9.0, 4.6, 1.1

    def surf(u, v):
        return T + .35 * math.sin(u * .9) * math.cos(v * 1.3) + .5 * math.exp(-((v - 4.3) / .8) ** 2) * (u < 7)

    top = [p(u, 0, surf(u, 0)) for u in [i * L / 30 for i in range(31)]]
    top += [p(L, v, surf(L, v)) for v in [i * D / 16 for i in range(17)]]
    top += [p(u, D, surf(u, D)) for u in [L - i * L / 30 for i in range(31)]]
    top += [p(0, v, surf(0, v)) for v in [D - i * D / 16 for i in range(17)]]
    front = [p(u, D, surf(u, D)) for u in [i * L / 30 for i in range(31)]] + [p(L, D, 0), p(0, D, 0)]
    right = [p(L, v, surf(L, v)) for v in [i * D / 16 for i in range(17)]] + [p(L, D, 0), p(L, 0, 0)]
    o.append(fill(P(top), LIGHT) + fill(P(front), PAPER) + fill(P(right), FACE))
    o.append(hatch(rng, P(right), (x, y, x + w, y + h), 2.4, 62, .45, GRAPH, .75))
    # strata on the cut faces
    st = []
    for k in (1, 2, 3):
        z = surf(0, D) * k / 4
        st.append(P([p(u, D, z * surf(u, D) / surf(0, D)) for u in [i * L / 20 for i in range(21)]], False))
        st.append(P([p(L, v, z * surf(L, v) / surf(L, D)) for v in [i * D / 10 for i in range(11)]], False))
    o.append(line(" ".join(st), .45, GRAPH, .75))
    # contours across the surface; the river as a double line
    ct = []
    for v in [i * D / 9 for i in range(1, 9)]:
        ct.append(P([p(u, v, surf(u, v)) for u in [i * L / 30 for i in range(31)]], False))
    o.append(line(" ".join(ct), .4, GRAPH, .6))
    river = [p(u, 2.1 + .35 * math.sin(u * .7), surf(u, 2.1) + .02) for u in [i * L / 30 for i in range(31)]]
    o.append(line(P(river, False), 2.2, "#c9d0da", .9) + line(P(river, False), .6, INK, .7))
    o.append(inked(rng, top, 1.1, INK, True) + inked(rng, front, .9, INK, True) + inked(rng, right, .9, INK, True))
    # six stations and the arcs between them
    names = [("L'Assomption", 1.6, 3.1), ("Les Cèdres", 1.0, 1.3), ("St-Charles", 3.2, .9),
             ("Nicolet", 6.4, 1.2), ("Drummondville", 7.4, 3.0), ("Lennoxville", 8.3, 4.0)]
    pts = {n: p(u, v, surf(u, v) + .05) for n, u, v in names}
    pairs = [("L'Assomption", "Nicolet", 2.4, True), ("Les Cèdres", "St-Charles", 1.4, False), ("St-Charles", "Nicolet", 1.6, False),
             ("Nicolet", "Drummondville", 1.8, False), ("Drummondville", "Lennoxville", 1.2, False), ("L'Assomption", "St-Charles", 1.0, False)]
    for a, b, wgt, hot in pairs:
        (ax, ay), (bx, by) = pts[a], pts[b]
        mx, my = (ax + bx) / 2, min(ay, by) - 18 - wgt * 9
        o.append(line(f"M{f(ax)},{f(ay)} Q{f(mx)},{f(my)} {f(bx)},{f(by)}", .6 + wgt * .55, ORANGE if hot else INK, .9 if hot else .7))
    side = {"L'Assomption": -1, "Les Cèdres": -1, "St-Charles": 1, "Nicolet": 1, "Drummondville": 1, "Lennoxville": 1}
    lift_ = {"L'Assomption": 0, "Les Cèdres": 0, "St-Charles": -4, "Nicolet": -8, "Drummondville": 6, "Lennoxville": 10}
    for n, (px_, py_) in pts.items():
        o.append(line(f"M{f(px_)},{f(py_)} v-9", .8, INK) + f'<circle cx="{f(px_)}" cy="{f(py_ - 10)}" r="2.6" fill="{RUST}" stroke="{INK}" stroke-width=".6"/>')
        o.append(text(px_ + 6 * side[n], py_ - 14 + lift_[n], n, "hand", 11.5, INK, "start" if side[n] > 0 else "end"))
    # the block's dimensions and the season's clouds
    a, b = p(0, D, 0), p(L, D, 0)
    o.append(line(f"M{f(a[0])},{f(a[1] + 10)} L{f(b[0])},{f(b[1] + 10)}", .6, INK, .8)
             + text((a[0] + b[0]) / 2 - 18, (a[1] + b[1]) / 2 + 26, "≈ 210 km", "hand", 13, INK))
    for cx, cy, cw in ((x + w * .66, y + 40, 96), (x + w * .86, y + 58, 70)):
        o.append(cloud(rng, cx, cy, cw))
        o.append(line(" ".join(f"M{f(cx - cw * .35 + k * cw / 9)},{f(cy + 6)} l-4,{f(12 + 6 * (k % 2))}" for k in range(7)), .6, GRAPH, .75))
    o.append(text(x + 14, y + 22, "LAURENTIDES", "caps", 7.5, GRAPH) + text(x + w * .74, y + h - 8, "APPALACHES", "caps", 7.5, GRAPH))
    o.append(compass(x + w - 26, y + h - 52, 13))
    return "".join(o)


def d_tail(rng, x, y, w, h):
    """Planche IV: heavy-tailed densities as ridges; magnitudes (warm) and ranks (ink) take separate paths."""
    o = []
    rx0, rx1 = x + 22, x + w * .52
    for k, xi in enumerate((.1, .2, .3, .4, .5)):
        by = y + 56 + k * 30
        pts = []
        for i in range(61):
            t = i / 60
            z = t * 7
            dens = (1 + xi * z) ** (-1 / xi - 1)
            pts.append((rx0 + t * (rx1 - rx0), by - 46 * dens * (1 - math.exp(-z * 6))))
        d = P(pts + [(rx1, by), (rx0, by)])
        o.append(fill(d, PAPER))
        tail = [q for q in pts if q[0] > rx0 + (rx1 - rx0) * .45]
        td = P(tail + [(rx1, by), (tail[0][0], by)])
        o.append(hatch(rng, td, (tail[0][0], by - 30, rx1, by), 2.1, 62, .5, ORANGE, .85))
        o.append(inked(rng, pts, 1.0, INK) + line(f"M{rx0},{by} H{rx1}", .5, GRAPH, .7))
        o.append(text(rx1 + 6, by - 2, f"ξ = {xi:.1f}", "ital", 12, INK))
    o.append(line(f"M{f(rx0 + (rx1 - rx0) * .45)},{y + 18} V{y + 56 + 4 * 30 + 4}", .5, GRAPH, .8, 'stroke-dasharray="3 3"'))
    o.append(text(rx0 + (rx1 - rx0) * .45 + 4, y + 22, "threshold u", "hand", 11.5, GRAPH))
    # two pathways into a DeepSets network
    nx = x + w * .7
    boxes = [("φ magnitudes", y + 52, ORANGE), ("φ ranks", y + 132, INK)]
    for lab, by, col in boxes:
        o.append(fill(P([(nx - 34, by - 16), (nx + 34, by - 16), (nx + 34, by + 16), (nx - 34, by + 16)]), LIGHT)
                 + inked(rng, [(nx - 34, by - 16), (nx + 34, by - 16), (nx + 34, by + 16), (nx - 34, by + 16)], .9, col, True)
                 + text(nx, by + 5, lab, "ital", 12.5, col, "middle"))
        o.append(line(f"M{f(rx1 + 50)},{f(by)} H{f(nx - 38)} M{f(nx - 44)},{f(by - 3)} L{f(nx - 38)},{f(by)} L{f(nx - 44)},{f(by + 3)}", .8, col, .85))
    sx, sy = nx + 74, y + 92
    o.append(f'<circle cx="{f(sx)}" cy="{f(sy)}" r="13" fill="{LIGHT}" stroke="{INK}" stroke-width=".9"/>' + text(sx, sy + 6, "Σ", "serif", 16, INK, "middle"))
    for _, by, col in boxes:
        o.append(line(f"M{f(nx + 36)},{f(by)} Q{f(sx - 10)},{f(by)} {f(sx - 10)},{f(sy + (by - sy) * .3)}", .8, col, .85))
    o.append(line(f"M{f(sx + 14)},{f(sy)} H{f(sx + 36)}", .8, INK))
    for k, (lab, dy) in enumerate((("ξ̂", -18), ("λ̂", 18))):
        o.append(text(sx + 46, sy + dy + 5, lab, "ital", 16, ORANGE if k == 0 else INK))
        o.append(line(f"M{f(sx + 36)},{f(sy)} L{f(sx + 42)},{f(sy + dy)}", .6, INK))
    # a scatter of the data, tiny, under the network
    for _ in range(46):
        u = rng.random()
        o.append(f'<circle cx="{f(nx - 30 + rng.random() * 110)}" cy="{f(y + h - 50 - 30 * (-math.log(1 - u * .97)) / 3.5)}" r="1.2" fill="{INK}" opacity=".6"/>')
    o.append(text(nx - 30, y + h - 34, "64 simulated worlds per family", "hand", 11.5, GRAPH))
    return "".join(o)


def d_immunity(rng, x, y, w, h):
    """Planche III: 2022's two Omicron waves as a ridge; person-days settle into a ledger of sufficient statistics."""
    o = []
    gx0, gx1, gy = x + 20, x + w - 20, y + 118
    pts = []
    for i in range(121):
        t = i / 120
        v = 70 * math.exp(-((t - .2) / .07) ** 2) + 44 * math.exp(-((t - .62) / .09) ** 2) + 6
        pts.append((gx0 + t * (gx1 - gx0), gy - v))
    d = P(pts + [(gx1, gy), (gx0, gy)])
    o.append(fill(d, LIGHT) + hatch(rng, d, (gx0, gy - 80, gx1, gy), 2.6, 60, .45, GRAPH, .7))
    o.append(inked(rng, pts, 1.2, INK) + line(f"M{gx0},{gy} H{gx1}", .7, INK))
    for t, lab in ((.2, "BA.1 / BA.2"), (.62, "BA.5")):
        px_ = gx0 + t * (gx1 - gx0)
        o.append(leader(rng, px_, min(q[1] for q in pts if abs(q[0] - px_) < 4) + 2, px_ + 34, y + 18, lab, "hand", 12))
    for k, m in enumerate(("JAN", "APR", "JUL", "OCT", "DEC")):
        tx = gx0 + k / 4 * (gx1 - gx0)
        o.append(line(f"M{f(tx)},{gy} v4", .5, INK) + text(tx, gy + 14, m, "caps", 7.5, GRAPH, "middle"))
    o.append(text(gx1, y + 16, "MMXXII", "caps", 7.5, GRAPH, "end"))
    # three people's histories as threads, then the ledger they collapse into
    hy = gy + 30
    for k, ev in enumerate(((.05, "V"), (.3, "V"), (.66, "I"))):
        pass
    for r, seq in enumerate(((.08, "V", .34, "V", .7, "I"), (.12, "V", .22, "I", None, None), (.04, "V", .5, "V", .82, "V"))):
        yy = hy + r * 12
        o.append(line(f"M{gx0},{yy} H{gx0 + (gx1 - gx0) * .55}", .45, GRAPH, .6, 'stroke-dasharray="1 3"'))
        for j in range(0, 6, 2):
            if seq[j] is None:
                continue
            tx = gx0 + seq[j] * (gx1 - gx0) * .55
            col = ORANGE if seq[j + 1] == "I" else INK
            o.append(text(tx, yy + 4, seq[j + 1], "ital", 11, col, "middle"))
    lx0, ly0 = gx0 + (gx1 - gx0) * .6, hy - 8
    cols, rows, cw, ch = 8, 4, 22, 11
    o.append(line(f"M{f(gx0 + (gx1 - gx0) * .56)},{f(hy + 12)} H{f(lx0 - 4)} M{f(lx0 - 9)},{f(hy + 9)} L{f(lx0 - 4)},{f(hy + 12)} L{f(lx0 - 9)},{f(hy + 15)}", .7, INK))
    for i in range(rows + 1):
        o.append(line(f"M{f(lx0)},{f(ly0 + i * ch)} h{cols * cw}", .45, GRAPH, .8))
    for j in range(cols + 1):
        o.append(line(f"M{f(lx0 + j * cw)},{f(ly0)} v{rows * ch}", .45, GRAPH, .8))
    for i in range(rows):
        for j in range(cols):
            n = int(abs(math.sin(i * 3.1 + j * 1.7)) * 90) + 3
            o.append(text(lx0 + j * cw + cw / 2, ly0 + i * ch + 8.5, str(n), "serif", 7.5, ORANGE if (i, j) == (1, 5) else INK, "middle"))
    o.append(text(lx0, ly0 + rows * ch + 16, "5×10⁸ person-days → 17,520 cells", "hand", 12, INK))
    return "".join(o)


def d_vintage(rng, x, y, w, h):
    """Planche I: four releases of one indicator, stacked like file sheets; the latest revises the past."""
    o = []
    sx, sy, sw, sh = x + 40, y + 30, w * .6, h - 70
    years = ("2022", "2023", "2024", "2025")
    for k in range(4)[::-1]:
        ox, oy = k * 10, k * 7
        r = [(sx + ox, sy + oy), (sx + ox + sw, sy + oy), (sx + ox + sw, sy + oy + sh), (sx + ox, sy + oy + sh)]
        o.append(fill(P(r), LIGHT if k == 0 else "#f8f3e8") + inked(rng, r, .7, INK, True, .8))
        tx = sx + ox + 18 + k * 46
        tab = [(tx, sy + oy), (tx + 4, sy + oy - 13), (tx + 40, sy + oy - 13), (tx + 44, sy + oy)]
        o.append(fill(P(tab), ORANGE if k == 1 else LIGHT, .3 if k == 1 else 1) + inked(rng, tab, .7, INK))
        o.append(text(tx + 22, sy + oy - 3, years[k], "serif", 10, INK, "middle"))
    # the chart on the front sheet
    cx0, cy0, cx1, cy1 = sx + 28, sy + 26, sx + sw - 18, sy + sh - 24
    o.append(text(cx0, cy0 - 6, "COUNTRIES WITH A VALUE · INDICATOR 4.1.1", "caps", 7, INK))
    grid = [f"M{cx0},{f(cy0 + i * (cy1 - cy0) / 4)} H{cx1}" for i in range(5)]
    o.append(line(" ".join(grid), .35, FAINT, .9) + line(f"M{cx0},{cy0} V{cy1} H{cx1}", .6, INK))
    def series(shift, n=10, tail=0):
        return [(cx0 + i * (cx1 - cx0) / (n - 1), cy0 + 22 + 10 * math.sin(i * 1.3) + 4 * shift + (tail * (i - 6) * 6 if i > 6 else 0)) for i in range(n)]
    for k, sh_ in enumerate((3, 2, 1)):
        o.append(line(P(series(sh_, tail=1 - k * .4), False), .6, GRAPH, .5 + k * .1))
    latest = series(0, tail=-1.6)
    o.append(inked(rng, latest, 1.4, ORANGE))
    o.append(f'<circle cx="{f(latest[-1][0])}" cy="{f(latest[-1][1])}" r="2.6" fill="{RUST}"/>')
    o.append(line(f"M{f(latest[7][0])},{cy0 + 4} V{cy1}", .5, INK, .7, 'stroke-dasharray="3 3"'))
    o.append(text(latest[-1][0] - 4, latest[-1][1] - 8, "+16 since 2022", "hand", 11.5, ORANGE, "end"))
    o.append(text(latest[7][0] + 4, cy1 - 6, "2021, the year we follow", "hand", 11, RUST))
    # paper clip and a pencil
    o.append(line(f"M{sx + 20},{sy + 22} V{sy - 18} a5,5 0 0 1 10,0 V{sy + 28} a8,8 0 0 1 -16,0 V{sy - 8}", 1.4, GRAPH))
    o.append(f'<g transform="translate({f(sx + sw - 30)} {f(sy + sh + 34)}) rotate(-14)">'
             f'<rect x="0" y="-3.5" width="104" height="7" fill="{AMBER}" stroke="{INK}" stroke-width=".7"/>'
             f'<path d="M0,-3.5 L-14,0 L0,3.5 Z" fill="#e8d6b4" stroke="{INK}" stroke-width=".7"/><path d="M-14,0 L-9,-1.1 L-9,1.1 Z" fill="{INK}"/></g>')
    # the release card, as on the website
    kx, ky, kw, kh = x + w * .7, y + 34, w * .27, 120
    o.append(fill(P([(kx, ky), (kx + kw, ky), (kx + kw, ky + kh), (kx, ky + kh)]), "#faf7f0", .96)
             + line(P([(kx, ky), (kx + kw, ky), (kx + kw, ky + kh), (kx, ky + kh)]), .75, INK)
             + line(P([(kx + 5, ky + 5), (kx + kw - 5, ky + 5), (kx + kw - 5, ky + kh - 5), (kx + 5, ky + kh - 5)]), .6, INK, .35))
    o.append(text(kx + 12, ky + 20, "choose a release", "hand", 11, ORANGE))
    bw = (kw - 24) / 4
    for k, yr in enumerate(years):
        r = [(kx + 12 + k * bw, ky + 28), (kx + 12 + (k + 1) * bw, ky + 28), (kx + 12 + (k + 1) * bw, ky + 42), (kx + 12 + k * bw, ky + 42)]
        o.append(fill(P(r), ORANGE if k == 1 else "#faf7f0") + line(P(r), .6, INK)
                 + text(kx + 12 + (k + .5) * bw, ky + 38.5, yr, "serif", 8.5, "#fff" if k == 1 else INK, "middle"))
    o.append(text(kx + 12, ky + 76, "32", "serif", 30, INK) + text(kx + 48, ky + 76, "countries, 2023 release", "ital", 10.5, SLATE))
    o.append(text(kx + 12, ky + 100, "late data keep arriving", "ital", 10.5, SLATE) + text(kx + 12, ky + 112, "for years after a release", "ital", 10.5, SLATE))
    return "".join(o)


def d_cohort(rng, x, y, w, h):
    """Planche V: a Lexis diagram — age against year, cohorts as diagonals, school ages banded."""
    o = []
    gx0, gy0, gx1, gy1 = x + 52, y + 24, x + w * .66, y + h - 40
    ages, years = 12, 14
    cw, ch = (gx1 - gx0) / years, (gy1 - gy0) / ages

    def X(yr):
        return gx0 + yr * cw

    def Y(a):
        return gy1 - a * ch

    bands = [(6, 12, "PRIMARY"), (0, 6, "")]
    for a0, a1, lab in bands[:1]:
        d = P([(gx0, Y(a1)), (gx1, Y(a1)), (gx1, Y(a0)), (gx0, Y(a0))])
        o.append(fill(d, LIGHT) + hatch(rng, d, (gx0, Y(a1), gx1, Y(a0)), 4, 0, .35, FAINT, .9))
    grid = [f"M{f(X(i))},{f(gy0)} V{f(gy1)}" for i in range(years + 1)] + [f"M{f(gx0)},{f(Y(a))} H{f(gx1)}" for a in range(ages + 1)]
    o.append(line(" ".join(grid), .35, GRAPH, .55))
    diag = []
    for c in range(-ages, years):
        a0 = max(0, -c)
        a1 = min(ages, years - c)
        if a1 > a0:
            diag.append(f"M{f(X(c + a0))},{f(Y(a0))} L{f(X(c + a1))},{f(Y(a1))}")
    o.append(line(" ".join(diag), .45, INK, .55))
    # one cohort followed, out-of-school share as hatched gaps along it
    c = 1
    path_ = [(X(c + a), Y(a)) for a in range(0, ages + 1) if c + a <= years]
    o.append(inked(rng, path_, 1.8, ORANGE))
    for a in (7, 9, 10):
        if c + a + 1 <= years:
            cell = [(X(c + a), Y(a)), (X(c + a + 1), Y(a)), (X(c + a + 1), Y(a + 1)), (X(c + a), Y(a + 1))]
            o.append(hatch(rng, P(cell), (cell[0][0], cell[2][1], cell[1][0], cell[0][1]), 2, 45, .55, ORANGE, .9, True))
    o.append(inked(rng, [(gx0, gy0), (gx1, gy0), (gx1, gy1), (gx0, gy1)], .8, INK, True))
    for a in (0, 6, 12):
        o.append(text(gx0 - 6, Y(a) + 3, str(a), "serif", 9, GRAPH, "end"))
    for i, yr in ((0, "2010"), (7, "2017"), (14, "2024")):
        o.append(text(X(i), gy1 + 12, yr, "serif", 9, GRAPH, "middle"))
    o.append(text(gx0 - 30, (gy0 + gy1) / 2, "age", "hand", 12, GRAPH, "middle", f'transform="rotate(-90 {f(gx0 - 30)} {f((gy0 + gy1) / 2)})"'))
    o.append(text(gx0 + 6, Y(12) - 4 + 12, "PRIMARY-SCHOOL AGES", "caps", 7, GRAPH))
    o.append(leader(rng, X(c + 9), Y(9), gx1 + 34, Y(10), "the 2009 cohort", "hand", 12.5, ORANGE))
    o.append(text(gx1 + 34, Y(10) + 18, "hatched: years out of school", "hand", 11, GRAPH))
    # posterior, as a small density in the margin
    bx, by = gx1 + 40, gy1 - 6
    pts = [(bx + i * 1.6, by - 46 * math.exp(-((i - 30) / 11) ** 2)) for i in range(61)]
    o.append(fill(P(pts + [(bx + 96, by), (bx, by)]), LIGHT) + hatch(rng, P(pts + [(bx + 96, by), (bx, by)]), (bx, by - 46, bx + 96, by), 2.2, 60, .45, GRAPH, .7))
    o.append(inked(rng, pts, 1, INK) + line(f"M{bx},{by} h98", .5, INK))
    o.append(text(bx + 48, by + 13, "posterior, out-of-school rate", "hand", 10.5, GRAPH, "middle"))
    return "".join(o)


def d_routes(rng, x, y, w, h):
    """Planche VI: pathways drawn as a route map — federal, Québec and provincial lines converging on PR."""
    o = []
    ex, ey = x + w - 70, y + 112
    lines_ = [
        ("FÉDÉRAL", INK, [(x + 30, y + 40), (x + 190, y + 40), (x + 250, y + 78), (ex - 30, y + 78)], ["Express Entry", "CEC", "FSW"]),
        ("QUÉBEC", ORANGE, [(x + 30, y + 112), (x + 210, y + 112), (ex - 30, y + 112)], ["Arrima", "PEQ", "PSTQ"]),
        ("PROVINCES", SAGE, [(x + 30, y + 182), (x + 190, y + 182), (x + 250, y + 146), (ex - 30, y + 146)], ["OINP", "BC PNP", "AAIP"]),
    ]
    for name, col, pts, stops in lines_:
        pts = pts + [(ex - 18, ey)]
        o.append(line(P(pts, False), 5.5, col, .25) + inked(rng, pts, 1.8, col))
        o.append(text(pts[0][0], pts[0][1] - 10, name, "caps", 8, col if col != SAGE else "#5d6b49"))
        for k, lab in enumerate(stops):
            t = (k + .6) / (len(stops) + .4)
            sx_ = pts[0][0] + t * (pts[1][0] - pts[0][0] + 120)
            sy_ = pts[0][1] if sx_ <= pts[1][0] else pts[1][1] + (pts[2][1] - pts[1][1]) * min(1, (sx_ - pts[1][0]) / max(1, pts[2][0] - pts[1][0]))
            o.append(f'<circle cx="{f(sx_)}" cy="{f(sy_)}" r="4.2" fill="{LIGHT}" stroke="{INK}" stroke-width="1"/>')
            o.append(text(sx_, sy_ + 17, lab, "hand", 11.5, INK, "middle"))
    o.append(f'<circle cx="{f(ex)}" cy="{f(ey)}" r="17" fill="{LIGHT}" stroke="{INK}" stroke-width="1.4"/>'
             f'<circle cx="{f(ex)}" cy="{f(ey)}" r="12" fill="none" stroke="{INK}" stroke-width=".6"/>' + text(ex, ey + 5, "PR", "serif", 14, INK, "middle"))
    o.append(text(ex, ey + 36, "permanent", "hand", 11.5, GRAPH, "middle") + text(ex, ey + 50, "residence", "hand", 11.5, GRAPH, "middle"))
    # the profile that enters on the left, as a small form
    o.append(text(x + 30, y + h - 4, "your profile in → the lines that fit light up · refreshed daily", "hand", 12, ORANGE))
    return "".join(o)


def d_atlas(rng, x, y, w, h):
    """Planche VII: a field of research as an old painted map — islands of topics, sea routes of citations."""
    o = []
    grid = [f"M{x + i * w / 8},{y} V{y + h}" for i in range(1, 8)] + [f"M{x},{y + j * h / 5} H{x + w}" for j in range(1, 5)]
    o.append(line(" ".join(grid), .35, GRAPH, .45, 'stroke-dasharray="2 4"'))
    isles = [(x + w * .2, y + h * .38, 62, 34, "Extremes"), (x + w * .52, y + h * .3, 48, 28, "Copulas"),
             (x + w * .44, y + h * .7, 70, 30, "Deep learning"), (x + w * .78, y + h * .58, 44, 30, "Climate")]
    shapes = []
    for cx, cy, rx, ry, name in isles:
        pts = [(cx + rx * (1 + rng.uniform(-.22, .18)) * math.cos(t), cy + ry * (1 + rng.uniform(-.22, .18)) * math.sin(t))
               for t in [i * math.pi / 9 for i in range(18)]]
        d = smooth(pts, closed=True)
        shapes.append((d, cx, cy, rx, ry, name))
        # coastal ripple lines, then land
        for k, sc in enumerate((1.22, 1.12)):
            rp = smooth([(cx + (px - cx) * sc, cy + (py - cy) * sc) for px, py in pts], closed=True)
            o.append(line(rp, .45, GRAPH, .45 - k * .1))
        o.append(fill(d, FACE) + hatch(rng, d, (cx - rx * 1.3, cy - ry * 1.3, cx + rx * 1.3, cy + ry * 1.3), 3, 70, .4, GRAPH, .6))
        o.append(line(d, 1.0, INK, .9))
        o.append(text(cx, cy + 4, name, "hand", 13, INK, "middle"))
    routes = [(0, 1, True), (0, 2, False), (1, 3, False), (2, 3, False), (1, 2, False)]
    for a, b, hot in routes:
        _, ax, ay, *_ = shapes[a]
        _, bx, by, *_ = shapes[b]
        mx, my = (ax + bx) / 2 + 16, (ay + by) / 2 - 22
        o.append(line(f"M{f(ax)},{f(ay)} Q{f(mx)},{f(my)} {f(bx)},{f(by)}", 1.1 if hot else .8, ORANGE if hot else INK, .85, 'stroke-dasharray="4 3"'))
    # a little ship and a cartouche
    sx, sy = x + w * .67, y + h * .2
    o.append(line(f"M{f(sx - 10)},{f(sy)} q10,6 20,0 M{f(sx)},{f(sy)} v-14 M{f(sx)},{f(sy - 14)} l8,8 h-8", .8, INK))
    cxx, cyy = x + 26, y + h - 46
    o.append(fill(P([(cxx, cyy), (cxx + 128, cyy), (cxx + 128, cyy + 30), (cxx, cyy + 30)]), LIGHT)
             + line(P([(cxx, cyy), (cxx + 128, cyy), (cxx + 128, cyy + 30), (cxx, cyy + 30)]), .8, INK)
             + line(P([(cxx + 3, cyy + 3), (cxx + 125, cyy + 3), (cxx + 125, cyy + 27), (cxx + 3, cyy + 27)]), .4, INK)
             + text(cxx + 64, cyy + 13, "CARTE DES CITATIONS", "caps", 6.5, INK, "middle") + text(cxx + 64, cyy + 24, "a field, read as a sea", "hand", 10, GRAPH, "middle"))
    o.append(compass(x + w - 30, y + 34, 15))
    return "".join(o)


def d_montreal(rng, x, y, w, h):
    """Planche VIII: Montréal from the river — Mont Royal, the towers, the Jacques-Cartier bridge."""
    o = []
    base = y + h * .66
    hill = [(x + w * t, base - 92 * math.sin(math.pi * min(1, max(0, (t - .08) / .84))) ** 1.4) for t in [i / 60 for i in range(61)]]
    hd = P(hill + [(x + w, base), (x, base)])
    o.append(fill(hd, LIGHT) + hatch(rng, hd, (x, base - 92, x + w, base), 3.2, 120, .45, GRAPH, .6))
    o.append(inked(rng, hill, 1.1, INK))
    towers = [(.32, 52, 18), (.4, 70, 16), (.47, 96, 20), (.55, 82, 18), (.62, 60, 14), (.68, 74, 16), (.76, 48, 18)]
    for t, ht, tw in towers:
        tx = x + w * t
        r = [(tx, base), (tx, base - ht), (tx + tw, base - ht), (tx + tw, base)]
        o.append(fill(P(r), PAPER) + hatch(rng, P([(tx + tw * .55, base), (tx + tw * .55, base - ht), (tx + tw, base - ht), (tx + tw, base)]),
                                         (tx, base - ht, tx + tw, base), 2.4, 62, .45, GRAPH, .75))
        o.append(line(" ".join(f"M{f(tx + 2)},{f(base - ht + k * 6)} h{f(tw - 4)}" for k in range(1, int(ht / 6))), .3, GRAPH, .6))
        o.append(inked(rng, r, .9, INK))
    cx = x + w * .5
    o.append(line(f"M{f(cx)},{f(base - 92 - 18)} V{f(base - 92 + 2)} M{f(cx - 6)},{f(base - 104)} h12", 1, INK))
    o.append(text(cx + 10, base - 104, "Mont Royal", "hand", 13, INK))
    # the bridge truss over the river
    by = base + 14
    o.append(line(f"M{x},{f(by)} H{x + w}", 1.1, INK) + line(f"M{x},{f(by + 6)} H{x + w}", .6, INK))
    truss = []
    for k in range(int(w / 16)):
        bx = x + k * 16
        truss.append(f"M{f(bx)},{f(by)} L{f(bx + 8)},{f(by - 10)} L{f(bx + 16)},{f(by)}")
    o.append(line(" ".join(truss), .6, INK, .85) + line(f"M{x},{f(by - 10)} H{x + w}", .7, INK))
    arch = f"M{f(x + w * .35)},{f(by)} Q{f(x + w * .5)},{f(by - 46)} {f(x + w * .65)},{f(by)}"
    o.append(line(arch, 1.1, INK))
    o.append(text(x + 14, by + 22, "Pont Jacques-Cartier", "hand", 12.5, INK))
    river = " ".join(f"M{f(x + rng.uniform(0, w - 40))},{f(by + 30 + rng.uniform(0, h * .2))} h{f(rng.uniform(16, 60))}" for _ in range(26))
    o.append(line(river, .5, GRAPH, .6) + text(x + w * .62, by + 40, "Fleuve Saint-Laurent", "hand", 12.5, INK))
    for tx in (.12, .18, .86, .92):
        px_ = x + w * tx
        o.append(wash(f"M{f(px_ - 10)},{f(base - 6)} a10,9 0 1 1 20,0 a10,9 0 1 1 -20,0 Z", ORANGE, .45, 3)
                 + line(f"M{f(px_)},{f(base + 6)} V{f(base - 6)}", .8, INK))
    return "".join(o)


WORKS = [
    dict(slug="03-covarchimax", over="M.Sc. thesis · McGill 2026", num="Planche II", title="Covariate-dependent Archimax copulas",
         pkg="covarchimax · R package", q="Does heavy rain hit several places at the same time — and is that changing?",
         value="3.90 vs 5.73", label="six-station extremal coefficient, autumn vs early summer", go="open the repository",
         draw=d_quebec, plate="Extrêmes de pluie · Québec méridional"),
    dict(slug="04-tailfm", over="Deep learning for extremes", num="Planche IV", title="TailFM",
         pkg="PyTorch · amortized inference", q="Can a neural network learn how heavy a tail is — and how often extremes arrive together?",
         value="9 of 9", label="seed × family checks where Hill still wins — reported, not tuned away", go="read the case study",
         draw=d_tail, plate="Queues lourdes · deux chemins"),
    dict(slug="05-vvi", over="Biostatistics · public health", num="Planche III", title="Hybrid immunity in calendar time",
         pkg="VVI · Python package", q="Does a booster before your first Omicron infection protect you — or imprint you?",
         value="1M people · 13 s", label="a million-person synthetic cohort, fitted on a laptop", go="read the case study",
         draw=d_immunity, plate="Immunité hybride · MMXXII"),
    dict(slug="06-sdg", over="Official statistics", num="Planche I", title="SDG 4 Data Revision Tracker",
         pkg="Python · Polars", q="How much do education statistics change from one data release to the next?",
         value="16 → 44", label="countries with a 2021 value as releases backfill it (synthetic data)", go="open the repository",
         draw=d_vintage, plate="Révisions de données · ODD 4"),
    dict(slug="07-bcm", over="Bayesian modelling · in progress", num="Planche V", title="Bayesian Cohort Model",
         pkg="R / Stan · SDG 4.1.4", q="How many children are out of school — when the surveys disagree and the gaps are wide?",
         value="Reproduction", label="an independent rebuild of a published model, with a synthetic demo and tests", go="open the repository",
         draw=d_cohort, plate="Diagramme de Lexis · cohortes"),
    dict(slug="08-immca", over="Civic tool · live", num="Planche VI", title="IMMCA",
         pkg="Canadian immigration pathways", q="Given who you are, which federal, Québec and provincial routes could fit?",
         value="3 languages", label="English · Français · 中文, refreshed every day, runs in the browser", go="open the live site",
         draw=d_routes, plate="Les chemins · Canada"),
    dict(slug="09-hosicite", over="Interactive · live", num="Planche VII", title="HosiCite",
         pkg="a citation atlas", q="What if exploring a research field felt like reading an old painted map?",
         value="Map + timeline", label="who cites whom, drawn as islands and sea routes", go="open the live site",
         draw=d_atlas, plate="Carte des citations"),
    dict(slug="10-site", over="This sketchbook", num="Planche VIII", title="ellensyuu.github.io",
         pkg="the full portfolio", q="Case studies, experience and public-interest work, drawn in ink on warm paper.",
         value="Planches I–IV", label="the interactive versions of these plates live on the site", go="visit the site",
         draw=d_montreal, plate="Montréal, vue du fleuve"),
]


def card(k: int, w: dict) -> str:
    rng = random.Random(300 + k)
    o = []
    lx, rx = 30, W - 30
    # case head: kicker in orange small caps, plate number in italic
    o.append(text(lx, 44, w["over"].upper(), "caps", 11.5, "#a84a26"))
    o.append(text(rx, 45, w["num"], "ital", 16, DARK_SLATE, "end"))
    # title
    size = 38
    while text_width(w["title"], "title", size) > rx - lx and size > 26:
        size -= 1
    o.append(text(lx - 1, 90, w["title"], "title", size, LIGHT_SLATE))
    o.append(text(lx, 116, w["pkg"], "hand", 15.5, DARK_SLATE))
    # question in italic with orange quotes
    lines_ = wrap(w["q"], "serif-i", 20, rx - lx - 14)[:2]
    for j, ln in enumerate(lines_):
        t = (("“" if j == 0 else "") + ln + ("”" if j == len(lines_) - 1 else ""))
        s = t.replace("“", '<tspan fill="#a84a26">“</tspan>').replace("”", '<tspan fill="#a84a26">”</tspan>')
        o.append(f'<text x="{lx}" y="{150 + j * 26}" class="ital" font-size="20" fill="{LIGHT_SLATE}">{s}</text>')
    # the mounted plate
    py0 = 150 + 2 * 26 + 6
    px0, pw, ph = lx, rx - lx, 300
    o.append(f'<rect x="{px0}" y="{py0}" width="{pw}" height="{ph}" rx="2" fill="url(#plateg)" stroke="#ddd5c5" filter="url(#plateshadow)"/>')
    ix, iy, iw, ih = px0 + 12, py0 + 12, pw - 24, ph - 24
    o.append(f'<rect x="{ix}" y="{iy}" width="{iw}" height="{ih}" rx="5" fill="{PAPER}" stroke="#5b4636" stroke-opacity=".1"/>')
    cid = f"pl{k}"
    o.append(f'<clipPath id="{cid}"><rect x="{ix}" y="{iy}" width="{iw}" height="{ih}" rx="5"/></clipPath><g clip-path="url(#{cid})">')
    o.append(f'<g filter="url(#pencil)">{w["draw"](rng, ix, iy, iw, ih - 34)}</g>')
    o.append(mini_title(ix + 14, iy + ih - 14, w["num"] + ".", w["plate"], True, iw - 28))
    o.append("</g>")
    # result line and the way in
    ry = py0 + ph + 34
    o.append(text(lx, ry, w["value"], "title", 24, "#a84a26"))
    vw = text_width(w["value"], "title", 24)
    for j, ln in enumerate(wrap(w["label"], "sans", 12.5, rx - lx - vw - 24)[:2]):
        o.append(text(lx + vw + 20, ry - 6 + j * 16, ln, "sans", 12.5, SLATE))
    gy = ry + 30
    o.append(text(rx, gy, w["go"], "hand", 16, "#a84a26", "end"))
    gw = text_width(w["go"], "hand", 16)
    o.append(line(f"M{f(rx - gw)},{gy + 6} q{f(gw / 2)},4 {f(gw + 2)},-1 l-6,-3.5 m6,3.5 l-5,4.5", 1, "#a84a26"))
    return doc(W, H, f"{w['title']} — {w['pkg']}", f"{w['q']} {w['value']}: {w['label']}.", "".join(o))


def heading(n: str, title: str, lede: str, dest: Path, w=1280, h=120) -> None:
    """A section heading as on the website: italic orange number, Cormorant 600, a fading hairline."""
    o = [text(72, 70, n, "ital", 26, "#a84a26")]
    tx = 72 + text_width(n, "serif-i", 26) + 14
    o.append(text(tx, 72, title, "title", 44, LIGHT_SLATE))
    ex = tx + text_width(title, "title", 44) + 22
    o.append('<linearGradient id="hair" x1="0" x2="1"><stop offset="0" stop-color="#22314a"/><stop offset=".7" stop-color="#22314a" stop-opacity=".25"/><stop offset="1" stop-color="#22314a" stop-opacity="0"/></linearGradient>')
    o.append(f'<rect x="{f(ex)}" y="58" width="300" height=".9" fill="url(#hair)"/>')
    o.append(text(72, 104, lede, "sans", 15, SLATE))
    dest.write_text(doc(w, h, title, lede, "".join(o)), encoding="utf-8")


MORE = [
    ("2023 — 26", "Hybrid immunity in calendar time", "VVI · PYTHON PACKAGE · FROM MY HKU FINAL-YEAR PROJECT",
     "Booster timing and Omicron infection; a million-person cohort fits in 13 s.", "read the case study"),
    ("2026 —", "Bayesian Cohort Model", "R / STAN · SDG 4.1.4 · WORK IN PROGRESS",
     "An independent reproduction of a published model of out-of-school rates.", "open the repository"),
    ("2026 —", "HosiCite", "A CITATION ATLAS · LIVE",
     "Who cites whom in a research field, drawn as an old painted map with a timeline.", "open the live site"),
    ("2026 —", "ellensyuu.github.io", "THIS SKETCHBOOK",
     "The interactive versions of these plates, plus experience and public-interest work.", "visit the site"),
]


def more_row(k: int, row) -> str:
    """One row in the style of the website's 'Leadership & community' list."""
    when, title, sub, desc, go = row
    w, h = 1280, 92
    o = [line(f"M72,{h - 1} H1208", .75, INK, .25)]
    o.append(text(72, 40, when, "ital", 15, DARK_SLATE))
    o.append(text(230, 40, title, "title", 21, LIGHT_SLATE))
    o.append(text(230, 62, sub, "caps", 9.5, GRAPH))
    o.append(text(700, 46, desc, "sans", 14, SLATE))
    o.append(text(1208, 72, go, "hand", 14, "#a84a26", "end"))
    return doc(w, h, title, f"{sub.title()}. {desc}", "".join(o))


def main() -> None:
    out = Path("assets/works")
    out.mkdir(parents=True, exist_ok=True)
    for old in out.glob("*.svg"):
        old.unlink()
    for k, w in enumerate(WORKS):
        if w["slug"] in FEATURED:
            (out / f"{w['slug']}.svg").write_text(card(k, w), encoding="utf-8")
    for k, row in enumerate(MORE):
        (out / f"more-{k + 1}.svg").write_text(more_row(k, row), encoding="utf-8")
    heading("02.", "Selected work", "Four case studies, each a different side of the same work: method, data system, model, product.",
            Path("assets/heading-work.svg"))
    heading("03.", "More work", "Smaller and in-progress pieces.", Path("assets/heading-more.svg"))
    print(f"wrote {len(FEATURED)} cards, {len(MORE)} rows and two headings")


FEATURED = {"03-covarchimax", "06-sdg", "04-tailfm", "08-immca"}


if __name__ == "__main__":
    main()
