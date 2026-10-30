"""The profile cover: the name, set as on ellensyuu.github.io, beside one plate —
the Yasaka pagoda (Hōkan-ji, Kyōto) drawn as an exploded isometric, pulled apart along its
free-hanging core post. Static; the only motion is two wind-bells at the eaves.

    python scripts/cover.py            # -> assets/cover.svg
"""
from __future__ import annotations

import random
import sys
from pathlib import Path

from draft import (
    AMBER, FACE, FAINT, GRAPH, INK, LIGHT, ORANGE, PAPER, RUST, SLATE,
    P, compass, dim_v, f, fill, hatch, inked, iso, leader, line, scale_bar, text, title_block,
)
from sketch import ALL_FACES, BASE_CSS, PENCIL_DEFS, font_css, text_width

W, H = 1280, 600
S = 6.85  # drawing scale, px per metre-ish unit
CSS = """
.bell{transform-box:fill-box;transform-origin:50% 0;animation:bell 3.6s ease-in-out infinite alternate}
@keyframes bell{from{transform:rotate(-7deg)}to{transform:rotate(7deg)}}
@media (prefers-reduced-motion:reduce){.bell{animation:none}}
"""


def _box(pts):
    xs, ys = [x for x, _ in pts], [y for _, y in pts]
    return min(xs), min(ys), max(xs), max(ys)


def pagoda(rng: random.Random, cx: float, gy: float, s: float) -> tuple[str, dict]:
    p = iso(cx, gy, s)
    o, at = [], {}

    def pts(q3):
        return [p(*q) for q in q3]

    def face(q3):
        return P(pts(q3))

    # podium (kidan)
    kb, kh = 5.0, 1.4
    top = [(-kb, -kb, kh), (kb, -kb, kh), (kb, kb, kh), (-kb, kb, kh)]
    lf = [(-kb, kb, 0), (kb, kb, 0), (kb, kb, kh), (-kb, kb, kh)]
    rf = [(kb, -kb, 0), (kb, kb, 0), (kb, kb, kh), (kb, -kb, kh)]
    for q3, tone in ((top, LIGHT), (lf, PAPER), (rf, FACE)):
        o.append(fill(face(q3), tone))
    o.append(hatch(rng, face(rf), _box(pts(rf)), 3.0, 62, .5, GRAPH, .7))
    joints = [P([p(-kb, kb, kh * t), p(kb, kb, kh * t), p(kb, -kb, kh * t)], False) for t in (.33, .66)]
    joints += [P([p(xx, kb, 0), p(xx, kb, kh * .33)], False) for xx in (-2.5, 0, 2.5)]
    o.append(line(" ".join(joints), .45, GRAPH, .7))
    for i in range(3):
        z0, z1 = kh * i / 3, kh * (i + 1) / 3
        yy = kb + 1.2 - i * .4
        st = [(-1.4, yy, z1), (1.4, yy, z1), (1.4, yy - .4, z1), (-1.4, yy - .4, z1)]
        sf = [(-1.4, yy, z0), (1.4, yy, z0), (1.4, yy, z1), (-1.4, yy, z1)]
        o.append(fill(face(st), LIGHT) + fill(face(sf), PAPER) + inked(rng, pts(sf), .7, INK, True))
    for q3 in (top, lf, rf):
        o.append(inked(rng, pts(q3), .9, INK, True))
    at["kidan"] = p(kb, kb * .2, kh * .5)

    # the five storeys, exploded upward
    z, gap, tiers = kh, 2.7, []
    for i in range(5):
        b = 3.4 - .36 * i
        h = 3.9 - .2 * i
        band, rise = .7, 1.9
        r, q = b + 1.55, b * .5
        tiers.append((z, b, h, band, r, rise, q))
        z += h + band + rise + gap
    finial_z = tiers[-1][0] + tiers[-1][2] + tiers[-1][3] + tiers[-1][5]

    # the core post (shinbashira), behind everything, in orange
    cp = .32
    post_l = [(-cp, cp, kh), (cp, cp, kh), (cp, cp, finial_z), (-cp, cp, finial_z)]
    post_r = [(cp, -cp, kh), (cp, cp, kh), (cp, cp, finial_z), (cp, -cp, finial_z)]
    o.append(fill(face(post_l), "#f3d9c6") + fill(face(post_r), "#ebc2a6"))
    o.append(hatch(rng, face(post_r), _box(pts(post_r)), 2.2, 75, .5, ORANGE, .8))
    o.append(inked(rng, pts(post_l), .8, RUST, True) + inked(rng, pts(post_r), .8, RUST, True))

    # alignment guides between storeys
    guides = []
    for cur, nxt in zip(tiers, tiers[1:]):
        z0, b, h, band, r, rise, q = cur
        zt = z0 + h + band + rise
        nb = nxt[1]
        for sx, sy in ((-1, 1), (1, 1), (1, -1)):
            guides.append(P([p(sx * nb, sy * nb, zt - .2), p(sx * nb, sy * nb, nxt[0])], False))
    o.append(line(" ".join(guides), .55, GRAPH, .7, 'stroke-dasharray="3 3"'))

    def lift(u):
        return .85 * u ** 4

    for i, (z0, b, h, band, r, rise, q) in enumerate(tiers):
        z1 = z0 + h
        lf = [(-b, b, z0), (b, b, z0), (b, b, z1), (-b, b, z1)]
        rf = [(b, -b, z0), (b, b, z0), (b, b, z1), (b, -b, z1)]
        o.append(fill(face(lf), PAPER) + fill(face(rf), FACE))
        o.append(hatch(rng, face(rf), _box(pts(rf)), 2.6, 62, .5, GRAPH, .75))
        det = []
        for t in (-1 / 3, 1 / 3):
            det.append(P([p(t * 2 * b, b, z0), p(t * 2 * b, b, z1)], False))
            det.append(P([p(b, t * 2 * b, z0), p(b, t * 2 * b, z1)], False))
        for k in range(1, 6):
            xx = -b / 3 + 2 * b / 3 * k / 6
            det.append(P([p(xx, b, z0 + .15), p(xx, b, z1 - .35)], False))
        det.append(P([p(-b, b, z1 - .35), p(b, b, z1 - .35), p(b, -b, z1 - .35)], False))
        o.append(line(" ".join(det), .55, INK, .8))
        o.append(inked(rng, pts(lf), .9, INK, True) + inked(rng, pts(rf), .9, INK, True))

        # bracket sets (masugumi)
        zb0, zb1 = z1, z1 + band
        bb = b + .55
        bl = [(-bb, bb, zb0), (bb, bb, zb0), (bb, bb, zb1), (-bb, bb, zb1)]
        br = [(bb, -bb, zb0), (bb, bb, zb0), (bb, bb, zb1), (bb, -bb, zb1)]
        o.append(fill(face(bl), LIGHT) + fill(face(br), FACE))
        blocks = []
        for k in range(7):
            t = -bb + 2 * bb * (k + .5) / 7
            blocks.append(P([p(t - .18, bb, zb0 + .1), p(t + .18, bb, zb0 + .1), p(t + .18, bb, zb1 - .1), p(t - .18, bb, zb1 - .1)]))
            blocks.append(P([p(bb, t - .18, zb0 + .1), p(bb, t + .18, zb0 + .1), p(bb, t + .18, zb1 - .1), p(bb, t - .18, zb1 - .1)]))
        o.append(line(" ".join(blocks), .45, INK, .85))
        o.append(inked(rng, pts(bl), .7, INK, True) + inked(rng, pts(br), .7, INK, True))

        # roof (kawara): two visible slopes, the eaves lifting at the corners
        ze, n = zb1, 16
        eave_l = [(-r + 2 * r * k / n, r, ze + lift(abs(-1 + 2 * k / n))) for k in range(n + 1)]
        eave_r = [(r, r - 2 * r * k / n, ze + lift(abs(1 - 2 * k / n))) for k in range(n + 1)]
        sl = pts(eave_l) + [p(q, q, ze + rise), p(-q, q, ze + rise)]
        sr = pts(eave_r) + [p(q, -q, ze + rise), p(q, q, ze + rise)]
        o.append(fill(P(sl), LIGHT) + fill(P(sr), FACE))
        tl, tr = [], []
        for k in range(1, 22):
            u = k / 22
            tl.append(P([p(-r + 2 * r * u, r, ze + lift(abs(-1 + 2 * u))), p(-q + 2 * q * u, q, ze + rise)], False))
            tr.append(P([p(r, r - 2 * r * u, ze + lift(abs(1 - 2 * u))), p(q, q - 2 * q * u, ze + rise)], False))
        o.append(line(" ".join(tl), .45, GRAPH, .8) + line(" ".join(tr), .45, INK, .7))
        o.append(hatch(rng, P(sr), _box(sr), 3.4, 150, .45, GRAPH, .55))
        fas = [(x, y, zz - .28) for x, y, zz in eave_l] + [(x, y, zz - .28) for x, y, zz in eave_r[1:]]
        o.append(inked(rng, pts(eave_l) + pts(eave_r[1:]), 1.3, INK))
        o.append(line(P(pts(fas), False), .7, INK, .8))
        o.append(line(P([sl[0], sl[-1], sl[-2]], False) + " " + P([sr[-2], sr[0]], False), .7, INK, .8))
        o.append(inked(rng, [p(r, r, ze + lift(1)), p(q, q, ze + rise)], 1.0, INK))
        if i == 1:
            at["kawara"] = p(-r * .45, r * .85, ze + rise * .3)
        if i == 2:
            at["masugumi"] = p(-bb * .4, bb, (zb0 + zb1) / 2)
        if i == 0:
            at["bells"] = [p(r, r, ze + lift(1) - .3), p(-r, r, ze + lift(1) - .3), p(r, -r, ze + lift(1) - .3)]
        if i == 3:
            at["gap"] = p(cp, cp, z0 - gap * .5)
        at.setdefault("tier_z", []).append(z0)

    # finial (sōrin): base, nine rings, water-flame, jewel
    zf = finial_z
    base = [(-.8, .8, zf), (.8, .8, zf), (.8, .8, zf + .7), (-.8, .8, zf + .7)]
    o.append(fill(face(base), PAPER) + inked(rng, pts(base), .8, INK, True))
    o.append(inked(rng, [p(0, 0, zf + .7), p(0, 0, zf + 9.5)], 1.4, INK))
    for k in range(9):
        zz = zf + 1.4 + k * .62
        rr = .78 - k * .025
        a, bq, c = p(-rr, rr, zz), p(rr, -rr, zz), p(0, 0, zz)
        o.append(f'<ellipse cx="{f(c[0])}" cy="{f(c[1])}" rx="{f(abs(bq[0] - a[0]) / 2 + 2)}" ry="1.6" '
                 f'fill="{LIGHT}" stroke="{INK}" stroke-width=".7"/>')
    tip = p(0, 0, zf + 7.6)
    o.append(line(f"M{f(tip[0] - 7)},{f(tip[1] + 2)} q-6,-8 2,-12 q-2,6 5,4 q2,-6 7,-2 q4,6 -2,10", .7, INK, .9))
    jw = p(0, 0, zf + 9.9)
    o.append(f'<circle cx="{f(jw[0])}" cy="{f(jw[1])}" r="3.2" fill="{AMBER}" fill-opacity=".85" stroke="{INK}" stroke-width=".8"/>')
    at.update(sorin=p(0, 0, zf + 4), hoju=jw, top=jw, ground=p(0, 0, 0))
    return "".join(o), at


def detail_b(rng, cx, cy, R, fx, fy) -> str:
    """Détail B: one bracket set (masugumi), front elevation at 1:20, in a circle."""
    cid = "detb"
    o = [f'<clipPath id="{cid}"><circle cx="{cx}" cy="{cy}" r="{R}"/></clipPath>',
         f'<circle cx="{cx}" cy="{cy}" r="{R}" fill="{LIGHT}"/>']
    g = [f'<g clip-path="url(#{cid})">']
    u = 7.0
    base = cy + 22

    def blk(x0, y0, w, h, cut=False):
        d = P([(x0, y0), (x0 + w, y0), (x0 + w, y0 + h), (x0, y0 + h)])
        r = fill(d, FACE if cut else PAPER)
        if cut:
            r += hatch(rng, d, (x0, y0, x0 + w, y0 + h), 2.2, 45, .45, GRAPH, .8)
        return r + inked(rng, [(x0, y0), (x0 + w, y0), (x0 + w, y0 + h), (x0, y0 + h)], .8, INK, True)

    # post below, the big bearing block (daito), arm, small blocks, arm, small blocks, beam
    g.append(blk(cx - 1.3 * u, base, 2.6 * u, 4 * u, True))
    g.append(fill(P([(cx - 2.2 * u, base), (cx + 2.2 * u, base), (cx + 1.6 * u, base - 1.4 * u), (cx - 1.6 * u, base - 1.4 * u)]), PAPER))
    g.append(inked(rng, [(cx - 1.3 * u, base), (cx - 2.2 * u, base - .2 * u), (cx - 2.2 * u, base - 1.4 * u), (cx + 2.2 * u, base - 1.4 * u),
                         (cx + 2.2 * u, base - .2 * u), (cx + 1.3 * u, base)], .9, INK))
    y = base - 1.4 * u
    for lvl, span in enumerate((4.4, 6.6)):
        arm = [(cx - span * u, y - .8 * u), (cx + span * u, y - .8 * u), (cx + span * u - .4 * u, y), (cx - span * u + .4 * u, y)]
        g.append(fill(P(arm), PAPER) + inked(rng, arm, .8, INK, True))
        y -= .8 * u
        for k in (-1, 0, 1):
            bx = cx + k * (span - .9) * u
            g.append(blk(bx - .7 * u, y - .9 * u, 1.4 * u, .9 * u))
        y -= .9 * u
    beam = [(cx - 9 * u, y - 1.1 * u), (cx + 9 * u, y - 1.1 * u), (cx + 9 * u, y), (cx - 9 * u, y)]
    g.append(fill(P(beam), FACE) + hatch(rng, P(beam), (cx - 9 * u, y - 1.1 * u, cx + 9 * u, y), 2.4, 135, .45, GRAPH, .7)
             + inked(rng, beam, .9, INK, True))
    g.append(line(f"M{cx - R},{base} H{cx + R}", .5, GRAPH, .6, 'stroke-dasharray="6 3 1.5 3"'))
    g.append("</g>")
    o += g
    o.append(f'<circle cx="{cx}" cy="{cy}" r="{R}" fill="none" stroke="{INK}" stroke-width="1"/>')
    o.append(f'<circle cx="{cx}" cy="{cy}" r="{R + 3}" fill="none" stroke="{INK}" stroke-width=".35"/>')
    # callout leader from the circle to the bracket set on the pagoda
    o.append(line(f"M{cx + R * .71},{cy - R * .71} Q{(cx + fx) / 2},{min(cy - R, fy) - 18} {f(fx - 8)},{f(fy - 4)}", .55, GRAPH, .8, 'stroke-dasharray="3 3"'))
    o.append(text(cx, cy + R + 20, "DÉTAIL B · 1:20", "caps", 9.5, GRAPH, "middle"))
    o.append(text(cx, cy + R + 37, "masugumi · a bracket set", "hand", 13.5, INK, "middle"))
    return "".join(o)


def plan_inset(rng, x, y, s=6.2) -> str:
    """Ground plan: three bays square, the core post at the centre, section A–A."""
    o = [text(x, y - 12, "PLAN · 1:200", "caps", 9.5, GRAPH)]
    b = 3.0 * s
    cx, cy = x + b + 6, y + b + 6
    sq = P([(cx - b, cy - b), (cx + b, cy - b), (cx + b, cy + b), (cx - b, cy + b)])
    o.append(fill(sq, LIGHT) + hatch(rng, sq, (cx - b, cy - b, cx + b, cy + b), 4.2, 45, .4, FAINT, .8))
    grid = [f"M{f(cx + t * 2 * b)},{f(cy - b)} V{f(cy + b)} M{f(cx - b)},{f(cy + t * 2 * b)} H{f(cx + b)}" for t in (-1 / 3, 1 / 3)]
    o.append(line(" ".join(grid), .5, GRAPH, .8))
    for i in (-1, -1 / 3, 1 / 3, 1):
        for j in (-1, -1 / 3, 1 / 3, 1):
            o.append(f'<rect x="{f(cx + i * b - 1.6)}" y="{f(cy + j * b - 1.6)}" width="3.2" height="3.2" fill="{INK}"/>')
    o.append(inked(rng, [(cx - b, cy - b), (cx + b, cy - b), (cx + b, cy + b), (cx - b, cy + b)], .9, INK, True))
    o.append(f'<circle cx="{f(cx)}" cy="{f(cy)}" r="3.6" fill="{ORANGE}" stroke="{RUST}" stroke-width=".7"/>')
    ay = cy + b * .15
    o.append(line(f"M{f(cx - b - 12)},{f(ay)} H{f(cx + b + 12)}", .6, INK, .8, 'stroke-dasharray="7 3 1.5 3"'))
    for sx in (-1, 1):
        ex = cx + sx * (b + 12)
        o.append(line(f"M{f(ex)},{f(ay)} v-8 M{f(ex - 3)},{f(ay - 5)} L{f(ex)},{f(ay - 8)} L{f(ex + 3)},{f(ay - 5)}", .7, INK))
        o.append(text(ex + sx * 6, ay + 4, "A", "ital", 12, INK, "middle"))
    o.append(text(cx, cy + b + 16, "6.4 m square", "hand", 12, GRAPH, "middle"))
    return "".join(o)


def build() -> str:
    rng = random.Random(1440)
    o = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" aria-labelledby="t d">',
        '<title id="t">Ziyi (Ellen) Zhou — statistician and data engineer, Montréal</title>',
        '<desc id="d">An engineering plate: the Yasaka pagoda in Kyōto drawn as an exploded isometric, its five storeys '
        'pulled apart along the free-hanging core post that lets it sway through earthquakes, with a ground plan, '
        'dimensions and hand-lettered names of its parts. Beside it: Ziyi (Ellen) Zhou, statistician and data engineer in '
        'Montréal, who models rare, high-impact events.</desc>',
        f"<style>{font_css(*ALL_FACES)}{BASE_CSS}{CSS}</style>",
        f"<defs>{PENCIL_DEFS}"
        '<linearGradient id="plateg" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#fbf8f1"/><stop offset="1" stop-color="#fbf3e6"/></linearGradient>'
        '<filter id="plateshadow" x="-10%" y="-10%" width="120%" height="125%"><feDropShadow dx="0" dy="18" stdDeviation="16" flood-color="#22314a" flood-opacity=".13"/></filter>'
        "</defs>",
        f'<rect width="{W}" height="{H}" fill="{PAPER}"/>',
    ]

    # ---- left: set as the website's hero
    lx = 72
    o.append(line(f"M{lx},206 h40", 1, INK))
    o.append(text(lx + 54, 210.5, "STATISTICIAN & DATA ENGINEER · MONTRÉAL", "caps", 13, SLATE))
    size, x, spans = 76, lx - 3, []
    for s, key, col, cls in (("Ziyi ", "serif", INK, "serif"), ("(Ellen)", "serif-i", RUST, "ital"), (" Zhou.", "serif", INK, "serif")):
        spans.append(f'<tspan x="{f(x)}" class="{cls}" fill="{col}">{s.replace(" ", "&#160;")}</tspan>')
        x += text_width(s, key, size)
    o.append(f'<text y="296" font-size="{size}">{"".join(spans)}</text>')
    body = [[("I model ", "sans"), ("rare, high-impact events", "em"), (" — floods,", "sans")],
            [("financial tail risk, gaps in education data — and", "sans")],
            [("build the software that makes those models", "sans")],
            [("trustworthy.", "sans")]]
    for k, segs in enumerate(body):
        x, sp = lx, []
        for s, kind in segs:
            if kind == "em":
                sp.append(f'<tspan x="{f(x)}" class="title" font-style="italic" font-size="21" fill="{INK}">{s}</tspan>')
                x += text_width(s, "serif-i", 21) + 2
            else:
                sp.append(f'<tspan x="{f(x)}">{s.replace(" ", "&#160;")}</tspan>')
                x += text_width(s, "sans", 17.5)
        o.append(f'<text y="{350 + k * 28}" class="sans" font-size="17.5" fill="{SLATE}">{"".join(sp)}</text>')
    o.append(text(lx, 494, "UNESCO INSTITUTE FOR STATISTICS  ·  M.SC. MCGILL  ·  B.SC. HKU", "caps", 11.5, GRAPH))
    o.append(text(lx, 530, "a statistician’s sketchbook — the case studies are at ellensyuu.github.io", "hand", 15.5, GRAPH))

    # ---- right: the plate, mounted as on the website
    px0, py0, pw, ph = 620, 28, 624, 548
    o.append(f'<rect x="{px0}" y="{py0}" width="{pw}" height="{ph}" rx="2" fill="url(#plateg)" stroke="#ddd5c5" filter="url(#plateshadow)"/>')
    ix0, iy0, iw, ih = px0 + 16, py0 + 16, pw - 32, 452
    o.append(f'<rect x="{ix0}" y="{iy0}" width="{iw}" height="{ih}" rx="5" fill="{PAPER}" stroke="#5b4636" stroke-opacity=".1"/>')
    o.append(f'<clipPath id="inner"><rect x="{ix0}" y="{iy0}" width="{iw}" height="{ih}" rx="5"/></clipPath><g clip-path="url(#inner)">')
    grid = [f"M{gx},{iy0} V{iy0 + ih}" for gx in range(ix0 + 20, ix0 + iw, 40)]
    grid += [f"M{ix0},{gy} H{ix0 + iw}" for gy in range(iy0 + 20, iy0 + ih, 40)]
    o.append(line(" ".join(grid), .35, FAINT, .45))
    o.append(line(P([(ix0 + 12, iy0 + 12), (ix0 + iw - 12, iy0 + 12), (ix0 + iw - 12, iy0 + ih - 12), (ix0 + 12, iy0 + ih - 12)]), .6, GRAPH, .6))
    o.append(text(ix0 + 26, iy0 + 34, "ÉLÉVATION ISOMÉTRIQUE ÉCLATÉE", "caps", 9.5, GRAPH))
    o.append(text(ix0 + 26, iy0 + 52, "Hōkan-ji, Kyōto · rebuilt 1440", "ital", 14, SLATE))

    draw, at = pagoda(rng, 1010, iy0 + 410, S)
    o.append(f'<g filter="url(#pencil)">{draw}</g>')
    for bx, by in at["bells"]:
        o.append(f'<g class="bell"><path d="M{f(bx)},{f(by)} v5" stroke="{INK}" stroke-width=".6"/>'
                 f'<path d="M{f(bx - 2.6)},{f(by + 9)} q2.6,-5 5.2,0 Z" fill="{AMBER}" stroke="{INK}" stroke-width=".6"/>'
                 f'<path d="M{f(bx)},{f(by + 9)} v4" stroke="{INK}" stroke-width=".5"/></g>')

    for key, dy, s in (("hoju", -2, "hōju · the jewel"), ("sorin", 0, "sōrin · nine bronze rings")):
        x, y = at[key]
        o.append(leader(rng, x, y, 1066, y + dy, s, "hand", 14))

    def two_line(key, tx, dy, l1, l2, col=INK):
        x, y = at[key]
        o.append(leader(rng, x, y, tx, y + dy, l1, "hand", 14.5, col, "end"))
        o.append(text(tx, y + dy + 20, l2, "hand", 13, GRAPH if col == INK else col, "end"))

    two_line("gap", 930, -4, "shinbashira", "the core post, hung free", ORANGE)
    two_line("kawara", 930, 6, "kawara", "fired-clay tiles")
    two_line("kidan", 930, -10, "kidan", "stone podium")
    # detail callout B on a bracket set, drawn large at upper left
    x, y = at["masugumi"]
    o.append(f'<circle cx="{f(x)}" cy="{f(y)}" r="9" fill="none" stroke="{INK}" stroke-width=".7"/>')
    o.append(text(x - 12, y - 10, "B", "ital", 13, INK, "end"))
    o.append(detail_b(rng, 742, 232, 60, x, y))

    tx, ty = at["top"]
    gx, gy = at["ground"]
    o.append(dim_v(1206, ty, gy, "46 m"))
    o.append(line(f"M{f(tx + 6)},{f(ty)} H1202 M{f(gx + 44)},{f(gy)} H1202", .45, GRAPH, .7, 'stroke-dasharray="2 3"'))
    for k, z in enumerate(at["tier_z"]):
        yy = gy - z * S
        o.append(line(f"M1202,{f(yy)} h8", .5, INK, .8) + text(1188, yy + 4, f"{k + 1}F", "serif", 10, GRAPH, "end"))

    o.append(plan_inset(rng, ix0 + 34, iy0 + 338))
    o.append(scale_bar(ix0 + 130, iy0 + 376, 4, 14, "8", "m"))
    o.append(compass(ix0 + 160, iy0 + 418, 14))
    o.append("</g>")

    o.append(title_block(ix0 + 4, iy0 + ih + 30, "Planche 0.", "Anatomie d'une pagode · Kyōto",
                         "the core post hangs free: it sways so the tower does not — five centuries of earthquakes",
                         width=iw - 8))
    o.append(f'<rect width="{W}" height="{H}" filter="url(#grain)" opacity=".55" pointer-events="none"/></svg>')
    return "".join(o)


if __name__ == "__main__":
    dest = Path(sys.argv[1] if len(sys.argv) > 1 else "assets/cover.svg")
    dest.write_text(build(), encoding="utf-8")
    print(f"wrote {dest} ({dest.stat().st_size / 1024:.0f} KB)")
