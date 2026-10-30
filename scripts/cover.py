"""Planche II — Mont-Tremblant in winter, seen from the river: the profile's cover plate.

Same hand as Planche I on ellensyuu.github.io (Montréal, from the river): ink ridges drawn in,
graphite hatching on the shadow side, hand-lettered names, a statistical inset in the sky.
Winter replaces autumn: snow caps, falling snow, and one lit café window carry the warmth.
"""
from __future__ import annotations

import math
import random

from sketch import (
    AMBER, FAINT, FROST, GRAPHITE, INK, PAPER, PAPER_DARK, PAPER_LIGHT, RUST, SLATE,
    f1, hatch_lines, paper_finish, path, smooth, svg_open, text, text_width, wobble_line,
)

W, H = 1280, 600
PX0 = 742  # where the drawing plate begins

CSS = f"""
.snow{{fill:{FAINT};opacity:.85;animation:fall linear infinite}}
@keyframes fall{{from{{transform:translate(0,-40px)}}to{{transform:translate(var(--dx),640px)}}}}
.steam{{animation:steam 6s ease-in-out infinite;opacity:0}}
@keyframes steam{{0%{{opacity:0;transform:translate(0,6px)}}30%{{opacity:.75}}100%{{opacity:0;transform:translate(6px,-34px)}}}}
.glow{{animation:glow 5s ease-in-out infinite alternate}}
@keyframes glow{{from{{opacity:.7}}to{{opacity:1}}}}
.shimmer{{stroke-dasharray:14 22;animation:shim 9s linear infinite}}
@keyframes shim{{to{{stroke-dashoffset:-180}}}}
.gull{{animation:gull 26s linear infinite;animation-delay:6s;opacity:0}}
@keyframes gull{{0%{{transform:translate(0,0);opacity:0}}3%{{opacity:1}}38%{{opacity:1}}42%,100%{{transform:translate(-620px,-70px);opacity:0}}}}
.flap{{animation:flap .55s ease-in-out infinite alternate;transform-origin:center;transform-box:fill-box}}
@keyframes flap{{to{{transform:scaleY(.45)}}}}
"""


def ridge(rng, x0, x1, base, peaks, step=6.0, rough=2.2):
    pts = []
    x = x0
    while x <= x1 + 0.1:
        y = base
        for px, py, w in peaks:
            t = max(0.0, 1 - abs(x - px) / w)
            t = t * t * (3 - 2 * t)  # smoothstep: rounded summits, long feet
            y = min(y, base - (base - py) * t ** 0.85)
        y += rng.uniform(-rough, rough) * (1 if y < base - 4 else 0.3)
        pts.append((x, y))
        x += step
    return pts


def ridge_y(pts, x):
    for (ax, ay), (bx, by) in zip(pts, pts[1:]):
        if ax <= x <= bx:
            return ay + (by - ay) * (x - ax) / (bx - ax)
    return pts[-1][1]


def build() -> str:
    rng = random.Random(1874)
    out = [svg_open(
        W, H,
        "Ziyi (Ellen) Zhou — statistician and data engineer, Montréal",
        "Hand-drawn plate: Mont-Tremblant in winter seen across a river, with a lit café on the near bank, "
        "falling snow and a small return-level curve sketched in the sky. On the left: Ziyi (Ellen) Zhou, "
        "statistician and data engineer in Montréal, modelling rare, high-impact events.",
        css=CSS,
    )]

    # ---- light: a pale winter sun and a cool wash behind the range
    out.append(
        '<defs>'
        '<radialGradient id="sun" cx="0.5" cy="0.5" r="0.5">'
        f'<stop offset="0" stop-color="{AMBER}" stop-opacity=".38"/><stop offset="1" stop-color="{AMBER}" stop-opacity="0"/></radialGradient>'
        '<radialGradient id="cold" cx="0.5" cy="0.5" r="0.5">'
        f'<stop offset="0" stop-color="{FROST}" stop-opacity=".55"/><stop offset="1" stop-color="{FROST}" stop-opacity="0"/></radialGradient>'
        '<linearGradient id="fadeL" x1="0" x2="1">'
        '<stop offset="0" stop-color="#fff" stop-opacity="0"/><stop offset=".16" stop-color="#fff" stop-opacity="1"/></linearGradient>'
        f'<mask id="plate"><rect x="{PX0 - 30}" y="0" width="{W - PX0 + 30}" height="{H}" fill="url(#fadeL)"/></mask>'
        f'<clipPath id="plateClip"><rect x="{PX0 - 30}" y="0" width="{W - PX0 + 30}" height="{H}"/></clipPath>'
        '</defs>'
    )
    out.append(f'<ellipse cx="1150" cy="150" rx="170" ry="150" fill="url(#sun)" class="fade"/>')
    out.append(f'<ellipse cx="1010" cy="300" rx="300" ry="170" fill="url(#cold)" class="fade"/>')

    plate = ['<g mask="url(#plate)"><g filter="url(#pencil)">']

    # ---- far range: lighter, flatter, drawn first
    base = 432
    far = ridge(rng, PX0 - 30, W + 10, base, [(930, 250, 190), (1112, 214, 200), (1262, 236, 150)], rough=0.9)
    far_d = smooth(far)
    plate.append(f'<path d="{far_d} L{W + 10},{base} L{PX0 - 30},{base} Z" fill="{PAPER_DARK}" opacity=".7"/>')
    plate.append(path(far_d, "pen", 0.9, draw=True, delay=0.2, dur=2.6, extra='opacity=".7"'))

    # ---- main range
    peaks = [(1012, 176, 270), (1196, 246, 170), (868, 300, 160)]
    main = ridge(rng, PX0 - 30, W + 10, base, peaks, rough=1.1)
    main_d = smooth(main)
    plate.append(f'<clipPath id="mtn"><path d="{main_d} L{W + 10},{base} L{PX0 - 30},{base} Z"/></clipPath>')
    plate.append(f'<path d="{main_d} L{W + 10},{base} L{PX0 - 30},{base} Z" fill="{PAPER}"/>')

    # shadow flanks: hatch everything right of a steep line dropped from each summit
    for i, (px, py, w) in enumerate(peaks):
        foot = px + 0.2 * (base - py)
        right = [(x, y) for x, y in main if px <= x <= px + w]
        poly = [(px, ridge_y(main, px))] + right + [(right[-1][0], base), (foot, base)]
        pd = "M" + " L".join(f"{f1(x)},{f1(y)}" for x, y in poly) + " Z"
        plate.append(f'<clipPath id="sh{i}"><path d="{pd}"/></clipPath>')
        plate.append(
            f'<g clip-path="url(#mtn)"><g clip-path="url(#sh{i})" class="fade" style="animation-delay:{1.6 + .3 * i:.1f}s">'
            + path(hatch_lines(px - 20, py - 10, px + w, base, 5.4, 62), "pen", 0.55, extra='opacity=".45"')
            + "</g></g>"
        )

    # snow caps: the ridge near each summit, closed by a ragged snowline
    for i, (px, py, w) in enumerate(peaks):
        depth = 44 if i == 0 else 30
        cap = [(x, y) for x, y in main if y < py + depth and abs(x - px) < w * 0.5]
        if len(cap) < 3:
            continue
        lower = []
        xs = [x for x, _ in cap]
        x = xs[-1]
        while x >= xs[0]:
            lower.append((x, ridge_y(main, x) + rng.uniform(10, 26) * (1 - (abs(x - px) / (w * 0.5)) ** 2) + 3))
            x -= rng.uniform(6, 13)
        lower.append((xs[0], cap[0][1]))
        d = smooth(cap) + " L" + smooth(lower)[1:] + " Z"
        plate.append(f'<path d="{d}" fill="{PAPER_LIGHT}" stroke="{GRAPHITE}" stroke-width=".7" class="fade" '
                     f'style="animation-delay:{1.1 + .2 * i:.1f}s" filter="url(#pencil)"/>')

    plate.append(path(main_d, "ink", 1.5, draw=True, delay=0.5, dur=2.8))

    # Tremblant's ski runs, pale ribbons down the sunlit face
    runs = []
    for k, off in enumerate((-70, -46, -24, -100)):
        x0 = peaks[0][0] + off * .35
        y0 = ridge_y(main, x0) + 10
        pts = [(x0, y0)]
        for j in range(1, 7):
            y = y0 + (base - y0) * j / 6
            pts.append((x0 + off * j / 6 + rng.uniform(-4, 4), y))
        runs.append(smooth(pts))
    plate.append(f'<g class="fade" style="animation-delay:2.4s">'
                 + path(" ".join(runs), "pen", 5.5, stroke=PAPER_LIGHT, extra='opacity=".95"')
                 + path(" ".join(runs), "pen", .5, extra='stroke-dasharray="2 5" opacity=".7"') + "</g>")

    # summit marker, like Planche I's "+ Mont Royal"
    mx, my = peaks[0][0], ridge_y(main, peaks[0][0])
    plate.append(path(f"M{mx},{my - 30} L{mx},{my - 8} M{mx - 7},{my - 22} L{mx + 7},{my - 22}", "ink", 1.1, draw=True, delay=2.6, dur=.6))
    plate.append(text(mx + 12, my - 22, "Mont Tremblant", "hand fade", 21, INK, extra='style="animation-delay:2.8s"'))
    # elevation dimension on the left flank
    plate.append(path(f"M{PX0 + 10},{my} L{PX0 + 10},{base} M{PX0 + 4},{my} L{PX0 + 16},{my} M{PX0 + 4},{base} L{PX0 + 16},{base}",
                      "pen", .8, extra='stroke-dasharray="3 3"'))
    plate.append(path(f"M{PX0 + 16},{my} L{mx - 14},{my}", "pen", .5, extra='stroke-dasharray="2 4" opacity=".7"'))
    plate.append(text(PX0 + 20, (my + base) / 2 - 10, "+ 875 m", "hand fade", 17, SLATE, extra='style="animation-delay:3s"'))

    # ---- treeline along the foot of the range
    trees = []
    x = PX0 - 20
    while x < W:
        if rng.random() < 0.12:
            x += rng.uniform(14, 34)  # a clearing
            continue
        for _ in range(rng.choice([1, 2, 2, 3])):
            trees.append((x + rng.uniform(-3, 3), base + rng.uniform(5, 15), rng.uniform(11, 27)))
        x += rng.uniform(9, 18)
    trees.sort(key=lambda t: t[1])
    plate.append(f'<path d="M{PX0 - 30},{base} L{W + 10},{base} L{W + 10},{base + 18} L{PX0 - 30},{base + 18} Z" fill="{PAPER}"/>')
    tl = []
    for x, yb, h in trees:
        w2 = h * rng.uniform(.22, .3)
        d = (f"M{f1(x)},{f1(yb - h)} L{f1(x - w2 * .7)},{f1(yb - h * .45)} L{f1(x - w2 * .35)},{f1(yb - h * .48)} "
             f"L{f1(x - w2)},{f1(yb)} L{f1(x + w2)},{f1(yb)} L{f1(x + w2 * .35)},{f1(yb - h * .48)} L{f1(x + w2 * .7)},{f1(yb - h * .45)} Z")
        tl.append(f'<path d="{d}" fill="{PAPER}" stroke="{INK}" stroke-width=".75" stroke-linejoin="round"/>')
    plate.append(f'<g class="fade" style="animation-delay:2.1s">{"".join(tl)}</g>')

    # ---- river
    r0, r1 = 452, 512
    bank = [(x, r0 + rng.uniform(-1.5, 1.5)) for x in range(PX0 - 30, W + 12, 24)]
    plate.append(f'<path d="M{PX0 - 30},{r0} L{W + 10},{r0} L{W + 10},{r1} L{PX0 - 30},{r1} Z" fill="{PAPER_LIGHT}"/>')
    plate.append(path(smooth(bank), "ink", 1.0, draw=True, delay=1.0, dur=2.0))
    # reflection: the main ridge, flipped and broken
    refl = [(x, r0 + (base - y) * 0.22 + 2) for x, y in main[::2]]
    plate.append(path(smooth(refl), "pen", .7, extra='stroke-dasharray="10 7" opacity=".6"'))
    ripples = []
    for _ in range(70):
        y = rng.uniform(r0 + 6, r1 - 4)
        x = rng.uniform(PX0 - 10, W)
        L = rng.uniform(12, 46) * (0.6 + (y - r0) / (r1 - r0))
        ripples.append(f"M{f1(x)},{f1(y)} L{f1(x + L)},{f1(y + rng.uniform(-.6, .6))}")
    plate.append(path(" ".join(ripples), "pen shimmer", .7, extra='opacity=".75"'))
    plate.append(text(1044, 494, "Rivière du Diable", "hand fade", 19, INK, extra='style="animation-delay:3.2s"'))

    # ---- near bank: snow field
    near = [(x, r1 + rng.uniform(-1.8, 1.8)) for x in range(PX0 - 30, W + 12, 20)]
    plate.append(f'<path d="{smooth(near)} L{W + 10},{H} L{PX0 - 30},{H} Z" fill="{PAPER}"/>')
    plate.append(path(smooth(near), "ink", 1.1, draw=True, delay=1.2, dur=2))
    tufts = []
    for _ in range(46):
        x, y = rng.uniform(PX0, W - 10), rng.uniform(r1 + 18, H - 30)
        tufts.append(f"M{f1(x)},{f1(y)} l{f1(rng.uniform(-2, 2))},{f1(-rng.uniform(5, 11))}")
    plate.append(path(" ".join(tufts), "pen", .6, extra='opacity=".6"'))

    # ---- the café on the near bank, with its little quay
    cx, cy = 820, 548  # front-left foot of the building
    cw, ch = 112, 50
    roof_peak = (cx + cw / 2, cy - ch - 44)
    house = (
        f"M{cx},{cy} L{cx},{cy - ch} L{cx + cw},{cy - ch} L{cx + cw},{cy} "
        f"M{cx - 10},{cy - ch + 2} L{roof_peak[0]},{roof_peak[1]} L{cx + cw + 10},{cy - ch + 2} "
        f"M{cx + 78},{cy - ch - 26} L{cx + 78},{cy - ch - 50} L{cx + 92},{cy - ch - 50} L{cx + 92},{cy - ch - 14}"
    )
    plate.append(f'<path d="M{cx},{cy} L{cx},{cy - ch} L{cx - 10},{cy - ch + 2} L{roof_peak[0]},{roof_peak[1]} '
                 f'L{cx + cw + 10},{cy - ch + 2} L{cx + cw},{cy - ch} L{cx + cw},{cy} Z" fill="{PAPER}"/>')
    # snow on the roof
    plate.append(f'<path d="M{cx - 13},{cy - ch + 1} L{roof_peak[0]},{roof_peak[1] - 4} L{cx + cw + 13},{cy - ch + 1} '
                 f'Q{cx + cw - 10},{cy - ch - 6} {cx + cw - 30},{cy - ch - 14} Q{roof_peak[0]},{roof_peak[1] + 12} {cx + 22},{cy - ch - 10} Z" '
                 f'fill="{PAPER_LIGHT}" stroke="{GRAPHITE}" stroke-width=".7"/>')
    # the lit window, an amber wash with a warm halo
    wx, wy, ww, wh = cx + 14, cy - ch + 12, 40, 24
    plate.append(f'<ellipse cx="{wx + ww / 2}" cy="{wy + wh / 2}" rx="34" ry="22" fill="{AMBER}" fill-opacity=".2" filter="url(#wash)" class="glow"/>')
    plate.append(f'<rect x="{wx}" y="{wy}" width="{ww}" height="{wh}" fill="{AMBER}" fill-opacity=".55" class="glow"/>')
    win = f"M{wx},{wy} h{ww} v{wh} h-{ww} Z M{wx + ww / 2},{wy} v{wh} M{wx},{wy + wh / 2} h{ww}"
    door = f"M{cx + 72},{cy} v-32 h20 v32"
    siding = " ".join(f"M{cx + 2},{cy - ch + k} L{cx + cw - 2},{cy - ch + k}" for k in range(8, ch, 7) if not (wy - (cy - ch) - 2 < k < wy - (cy - ch) + wh + 2))
    plate.append(path(siding, "pen", .5, extra='opacity=".6"'))
    plate.append(path(house + " " + win + " " + door, "ink", 1.2, draw=True, delay=1.8, dur=2.2))
    plate.append(f'<circle cx="{cx + 88}" cy="{cy - 15}" r="1.6" fill="{INK}"/>')
    # hanging sign
    plate.append(path(f"M{cx + cw},{cy - ch + 8} h22 M{cx + cw + 8},{cy - ch + 8} v6 M{cx + cw + 20},{cy - ch + 8} v6", "ink", .9))
    plate.append(f'<rect x="{cx + cw + 3}" y="{cy - ch + 14}" width="24" height="13" fill="{PAPER_LIGHT}" stroke="{INK}" stroke-width=".9"/>')
    plate.append(text(cx + cw + 15, cy - ch + 24, "café", "hand", 9.5, RUST, "middle"))
    # steam from the chimney
    for k in range(3):
        sx = cx + 85 + k * 3
        plate.append(path(f"M{sx},{cy - ch - 54} q-6,-8 0,-14 q6,-7 0,-14", "pen steam", .9,
                          extra=f'style="animation-delay:{k * 2:.0f}s"'))
    # the quay, on short piles into the river
    q = f"M{cx + cw + 30},{r1 - 2} L{cx + cw + 150},{r1 - 9} L{cx + cw + 150},{r1 - 4} L{cx + cw + 30},{r1 + 3} Z"
    piles = " ".join(f"M{f1(cx + cw + 40 + k * 26)},{f1(r1 - 2 - k * 1.5)} v12" for k in range(5))
    plate.append(path(q + " " + piles, "ink", 1.0, draw=True, delay=2.3, dur=1.4))
    plate.append(text(cx + cw + 30, r1 + 30, "Café du Quai", "hand fade", 19, INK, extra='style="animation-delay:3.4s"'))

    # pines beside the café, snow-laden
    for (tx, ty, th) in [(780, 556, 58), (762, 562, 40), (1218, 560, 54), (1240, 566, 36)]:
        tiers = []
        for k in range(4):
            yy = ty - th * (k / 4)
            ww = th * 0.34 * (1 - k / 5)
            tiers.append(f"M{f1(tx - ww)},{f1(yy)} L{tx},{f1(yy - th * .32)} L{f1(tx + ww)},{f1(yy)}")
        plate.append(path(" ".join(tiers) + f" M{tx},{ty} v8", "ink", 1.0, draw=True, delay=2.0, dur=1.6))
        snowy = " ".join(
            f"M{f1(tx - th * .3 * (1 - k / 5) + 3)},{f1(ty - th * (k / 4) - 3)} "
            f"Q{tx},{f1(ty - th * (k / 4) - th * .22)} {f1(tx + th * .2 * (1 - k / 5))},{f1(ty - th * (k / 4) - 5)}"
            for k in range(4)
        )
        plate.append(path(snowy, "pen", 2.2, stroke=PAPER_LIGHT, extra='opacity=".95"'))

    plate.append("</g></g>")  # end masked plate
    out += plate

    # ---- the statistical inset in the sky: a GEV return-level curve for snow depth
    ix, iy, iw, ih = 792, 44, 178, 116
    out.append(f'<rect x="{ix}" y="{iy}" width="{iw}" height="{ih}" fill="{PAPER_LIGHT}" opacity=".9"/>')
    out.append(path(f"M{ix},{iy} h{iw} v{ih} h-{iw} Z", "pen", .8, draw=True, delay=.4, dur=1.4))
    # axes: log return period × return level
    out.append(path(f"M{ix + 20},{iy + ih - 18} H{ix + iw - 10} M{ix + 20},{iy + ih - 18} V{iy + 12}", "pen", .7))
    for t in (2, 10, 50, 200):
        tx = ix + 20 + (math.log(t) / math.log(400)) * (iw - 40)
        out.append(path(f"M{f1(tx)},{iy + ih - 18} v3", "pen", .6))
        out.append(text(tx, iy + ih - 5, str(t), "serif", 9, GRAPHITE, "middle"))
    mu, sig, xi = 1.0, 0.32, 0.12

    def rl(T):
        y = -math.log(1 - 1 / T)
        return mu + sig / xi * (y ** -xi - 1)

    zlo, zhi = rl(1.15) * 0.8, rl(400) * 1.18 * 1.15

    def to_xy(T, z):
        return ix + 20 + (math.log(T) / math.log(400)) * (iw - 40), iy + ih - 18 - (z - zlo) / (zhi - zlo) * (ih - 34)

    curve = [to_xy(T, rl(T)) for T in [1.15 * 1.18 ** k for k in range(36) if 1.15 * 1.18 ** k < 400]]
    up = [to_xy(T, rl(T) * (1 + .03 * math.log(T))) for T in [1.15 * 1.18 ** k for k in range(36) if 1.15 * 1.18 ** k < 400]]
    lo = [to_xy(T, rl(T) * (1 - .025 * math.log(T))) for T in [1.15 * 1.18 ** k for k in range(36) if 1.15 * 1.18 ** k < 400]]
    out.append(f'<path d="{smooth(up)} L{" L".join(f"{f1(a)},{f1(b)}" for a, b in lo[::-1])} Z" fill="{RUST}" opacity=".10" class="fade" style="animation-delay:1.8s"/>')
    out.append(path(smooth(up) + " " + smooth(lo), "pen", .6, stroke=RUST, extra='stroke-dasharray="3 3" opacity=".7"'))
    out.append(path(smooth(curve), "ink", 1.6, stroke=RUST, draw=True, delay=1.2, dur=1.8))
    prng = random.Random(7)
    n = 48
    dots = []
    for k in range(1, n + 1):
        T = (n + 1) / (n + 1 - k)
        z = rl(T) + prng.gauss(0, 0.05 + 0.02 * math.log(T))
        x, y = to_xy(T, z)
        dots.append(f'<circle cx="{f1(x)}" cy="{f1(y)}" r="1.6" fill="{INK}" opacity=".75"/>')
    out.append(f'<g class="fade" style="animation-delay:.9s">{"".join(dots)}</g>')
    # the hand note beside it
    note = [("deep, in the snow —", RUST), ("how deep the deepest", INK), ("snowfall gets, once", INK), ("every T winters: a GEV", INK), ("return-level curve", INK)]
    for k, (s, col) in enumerate(note):
        out.append(text(ix - 10, iy + 16 + k * 18, s, "hand fade", 14.5, col, "end", extra=f'style="animation-delay:{2.0 + .15 * k:.2f}s"'))
    out.append(text(ix + iw + 2, iy + 10, "T", "ital", 11, GRAPHITE))

    # ---- a gull, now and then
    out.append(f'<g class="gull"><g transform="translate(1270,96)">'
               f'<path class="flap" d="M-11,0 Q-5,-6 0,0 Q5,-6 11,0" fill="none" stroke="{INK}" stroke-width="1.3" stroke-linecap="round"/></g></g>')

    # ---- falling snow over the plate only
    flakes = ['<g clip-path="url(#plateClip)">']
    srng = random.Random(42)
    for _ in range(64):
        x = srng.uniform(PX0 - 20, W)
        r = srng.choice([1.1, 1.4, 1.8, 2.3])
        dur = srng.uniform(9, 18) * (2.6 / r) ** .4
        flakes.append(
            f'<circle class="snow" cx="{f1(x)}" cy="0" r="{r}" '
            f'style="--dx:{srng.uniform(-40, 20):.0f}px;animation-duration:{dur:.1f}s;animation-delay:-{srng.uniform(0, dur):.1f}s"/>'
        )
    flakes.append("</g>")
    out += flakes

    # ---- the left column: who
    lx = 70
    out.append(path(f"M{lx},{204} h38", "ink", 1, draw=True, delay=.2, dur=.8))
    out.append(text(lx + 52, 209, "STATISTICIAN & DATA ENGINEER · MONTRÉAL", "caps", 14, SLATE))
    size = 84
    parts = [("Ziyi ", "serif", INK), ("(Ellen)", "serif-i", RUST), (" Zhou.", "serif", INK)]
    x = lx - 4
    spans = []
    for s, key, col in parts:
        cls = "ital" if key == "serif-i" else "serif"
        spans.append(f'<tspan x="{f1(x)}" class="{cls}" fill="{col}">{s.replace(" ", "&#160;")}</tspan>')
        x += text_width(s, key, size)
    out.append(f'<text y="300" font-size="{size}" class="serif fade" style="animation-delay:.1s">{"".join(spans)}</text>')
    body = [
        ("I model ", "rare, high-impact events", " — floods, financial tail risk,"),
        ("gaps in education data — and build the software that makes", "", ""),
        ("those models trustworthy.", "", ""),
    ]
    for k, (a, em, b) in enumerate(body):
        y = 362 + k * 30
        if em:
            x = lx
            sp = [f'<tspan x="{lx}">{a.replace(" ", "&#160;")}</tspan>']
            x += text_width(a, "sans", 19)
            sp.append(f'<tspan x="{f1(x)}" class="ital" font-size="22">{em}</tspan>')
            x += text_width(em, "serif-i", 22)
            sp.append(f'<tspan x="{f1(x)}">{b.replace(" ", "&#160;")}</tspan>')
            out.append(f'<text y="{y}" class="sans fade" font-size="19" fill="{SLATE}" style="animation-delay:.5s">{"".join(sp)}</text>')
        else:
            out.append(text(lx, y, a, "sans fade", 19, SLATE, extra='style="animation-delay:.5s"'))
    out.append(text(lx, 470, "UNESCO INSTITUTE FOR STATISTICS  ·  M.SC. MCGILL  ·  B.SC. HKU", "caps", 12, GRAPHITE))

    # caption, like a plate in a folio
    out.append(text(1176, 588, "Mont-Tremblant, vue de la rivière", "ital", 15, SLATE, "end"))
    out.append(text(1188, 588, "PLANCHE II", "caps", 11, GRAPHITE))

    out.append(paper_finish(W, H))
    return "".join(out)


if __name__ == "__main__":
    import sys
    from pathlib import Path

    dest = Path(sys.argv[1] if len(sys.argv) > 1 else "assets/cover.svg")
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(build(), encoding="utf-8")
    print(f"wrote {dest} ({dest.stat().st_size / 1024:.0f} KB)")
