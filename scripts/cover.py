"""Planche II — Fuji in winter across Lake Ashi, Hakone: the profile's cover plate.

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
.sway{{animation:sway 4s ease-in-out infinite alternate}}
@keyframes sway{{from{{transform:rotate(-4deg)}}to{{transform:rotate(4deg)}}}}
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
        "Hand-drawn plate: Mount Fuji in winter seen across Lake Ashi in Hakone, with the torii standing in the water and a lit kissaten on the shore, "
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

    # ---- Fuji: one cone, concave flanks, a flat crater rim
    px, top, base, half = 1046, 150, 404, 330
    fuji = []
    x = PX0 - 30
    while x <= W + 10:
        d = abs(x - px)
        if d < 20:
            y = top + rng.uniform(-1.2, 1.6) + (2.5 if 4 < d < 10 else 0)
        else:
            t = min(1.0, (d - 20) / (half - 20))
            y = top + (base - top) * (1 - (1 - t) ** 2.3) + rng.uniform(-.8, .8)
        fuji.append((x, y))
        x += 5
    fuji_d = smooth(fuji)
    plate.append(f'<clipPath id="mtn"><path d="{fuji_d} L{W + 10},{base} L{PX0 - 30},{base} Z"/></clipPath>')
    plate.append(f'<path d="{fuji_d} L{W + 10},{base} L{PX0 - 30},{base} Z" fill="#e8dfcd"/>')
    plate.append(f'<g clip-path="url(#mtn)" class="fade" style="animation-delay:1.4s">'
                 + path(hatch_lines(PX0, top, W, base, 6.5, 100), "pen", .45, extra='opacity=".28"') + "</g>")
    # the shadowed east flank
    plate.append(f'<clipPath id="sh0"><path d="M{px + 6},{top} L{px + 150},{base} L{W + 10},{base} L{W + 10},{top} Z"/></clipPath>')
    plate.append(f'<g clip-path="url(#mtn)"><g clip-path="url(#sh0)" class="fade" style="animation-delay:1.6s">'
                 + path(hatch_lines(px - 20, top - 10, W + 10, base, 5.2, 64), "pen", .55, extra='opacity=".45"') + "</g></g>")
    # gullies running down from the rim
    gul = []
    for off in (-150, -96, -52, -18, 22, 60, 110, 170):
        x0 = px + off * .12
        y0 = ridge_y(fuji, x0) + 6
        pts = [(x0 + off * j / 5 + rng.uniform(-2, 2), y0 + (base - y0) * j / 5 * (0.75 + .2 * rng.random())) for j in range(6)]
        gul.append(smooth(pts))
    plate.append(f'<g clip-path="url(#mtn)">{path(" ".join(gul), "pen", .6, extra=chr(111) + "pacity=" + chr(34) + ".5" + chr(34))}</g>')
    # the snow cap, ending in long fingers down the gullies
    cap = [(x, y) for x, y in fuji if abs(x - px) < 128]
    lower = []
    for x, _ in cap[::-1][::2]:
        u = (x - px) / 128
        finger = abs(math.sin((x - px) / 11.0)) ** 4 * 42 * (1 - abs(u))
        lower.append((x, ridge_y(fuji, x) + 3 + (30 + finger) * (1 - u * u) ** 1.1))
    capd = smooth(cap) + " L" + smooth(lower)[1:] + " Z"
    plate.append(f'<path d="{capd}" fill="{PAPER_LIGHT}" stroke="{GRAPHITE}" stroke-width=".7" class="fade" style="animation-delay:1.1s"/>')
    plate.append(path(fuji_d, "ink", 1.6, draw=True, delay=0.4, dur=3.0))

    my = ridge_y(fuji, px)
    plate.append(path(f"M{px},{my - 30} L{px},{my - 8} M{px - 7},{my - 22} L{px + 7},{my - 22}", "ink", 1.1, draw=True, delay=2.6, dur=.6))
    plate.append(text(px + 12, my - 22, "Fuji-san", "hand fade", 22, INK, extra='style="animation-delay:2.8s"'))
    plate.append(text(px + 104, my - 22, "富士山", "serif fade", 13, GRAPHITE, extra='style="animation-delay:2.9s"'))

    # ---- the Hakone hills in front, darker and nearer
    hills = []
    x = PX0 - 30
    while x <= W + 10:
        y = 412 - 60 * math.exp(-((x - 800) / 80) ** 2) - 26 * math.exp(-((x - 920) / 50) ** 2) \
            - 44 * math.exp(-((x - 1260) / 70) ** 2) + 5 * math.sin(x / 23) + rng.uniform(-.8, .8)
        hills.append((x, y))
        x += 6
    hb = 456
    hd = smooth(hills)
    plate.append(f'<clipPath id="hill"><path d="{hd} L{W + 10},{hb} L{PX0 - 30},{hb} Z"/></clipPath>')
    plate.append(f'<path d="{hd} L{W + 10},{hb} L{PX0 - 30},{hb} Z" fill="{PAPER_DARK}"/>')
    plate.append(f'<g clip-path="url(#hill)" class="fade" style="animation-delay:1.9s">'
                 + path(hatch_lines(PX0 - 30, 330, W + 10, hb, 4.2, 118), "pen", .5, extra='opacity=".4"')
                 + path(hatch_lines(PX0 - 30, 330, W + 10, hb, 7, 40), "pen", .45, extra='opacity=".25"') + "</g>")
    # cedar tufts along the crest
    tufts = []
    for x, y in hills[::2]:
        if rng.random() < .8:
            h = rng.uniform(3.5, 7)
            tufts.append(f"M{f1(x - h * .5)},{f1(y + 2)} Q{f1(x)},{f1(y - h * 1.6)} {f1(x + h * .5)},{f1(y + 2)}")
    plate.append(path(" ".join(tufts), "ink", .7, extra='opacity=".85"'))
    plate.append(path(hd, "ink", 1.2, draw=True, delay=1.0, dur=2.4))
    # elevation dimension
    plate.append(path(f"M{PX0 + 10},{my} L{PX0 + 10},{base - 40} M{PX0 + 4},{my} L{PX0 + 16},{my}", "pen", .8, extra='stroke-dasharray="3 3"'))
    plate.append(path(f"M{PX0 + 16},{my} L{px - 14},{my}", "pen", .5, extra='stroke-dasharray="2 4" opacity=".7"'))
    plate.append(text(PX0 + 20, my + 40, "+ 3 776 m", "hand fade", 17, SLATE, extra='style="animation-delay:3s"'))

    # ---- Lake Ashi, with the upside-down Fuji in it
    r0, r1 = 456, 520
    plate.append(f'<path d="M{PX0 - 30},{r0} L{W + 10},{r0} L{W + 10},{r1} L{PX0 - 30},{r1} Z" fill="{PAPER_LIGHT}"/>')
    plate.append(path(smooth([(x, r0 + rng.uniform(-1.2, 1.2)) for x in range(PX0 - 30, W + 12, 24)]), "ink", 1.0, draw=True, delay=1.0, dur=2.0))
    refl = [(x, r0 + 2 + (base - y) * 0.2) for x, y in fuji[::3] if abs(x - px) < half]
    plate.append(path(smooth(refl), "pen", .8, extra='stroke-dasharray="9 6" opacity=".55"'))
    ripples = []
    for _ in range(70):
        y = rng.uniform(r0 + 6, r1 - 4)
        x = rng.uniform(PX0 - 10, W)
        L = rng.uniform(12, 46) * (0.6 + (y - r0) / (r1 - r0))
        ripples.append(f"M{f1(x)},{f1(y)} L{f1(x + L)},{f1(y + rng.uniform(-.6, .6))}")
    plate.append(path(" ".join(ripples), "pen shimmer", .7, extra='opacity=".7"'))
    plate.append(text(1000, 500, "Ashi-no-ko", "hand fade", 19, INK, extra='style="animation-delay:3.2s"'))

    # the Heiwa torii, standing in the water
    tx, tb, th = 1186, 506, 66
    pil = f"M{tx - 22},{tb} L{tx - 19},{tb - th} M{tx + 22},{tb} L{tx + 19},{tb - th}"
    kasagi = (f"M{tx - 40},{tb - th - 4} Q{tx},{tb - th - 1} {tx + 40},{tb - th - 4} "
              f"L{tx + 36},{tb - th - 10} Q{tx},{tb - th - 7} {tx - 36},{tb - th - 10} Z")
    nuki = f"M{tx - 30},{tb - th + 12} h60 M{tx},{tb - th - 3} v15"
    plate.append(f'<path d="{kasagi}" fill="{RUST}" fill-opacity=".75" stroke="{RUST}" stroke-width="1"/>')
    plate.append(path(pil, "ink", 4.2, stroke=RUST, extra='opacity=".8"'))
    plate.append(path(nuki, "ink", 2.4, stroke=RUST, extra='opacity=".85"'))
    plate.append(path(f"M{tx - 20},{tb + 3} L{tx - 18},{tb + 30} M{tx + 20},{tb + 3} L{tx + 18},{tb + 30} M{tx - 34},{tb + 32} h68",
                      "pen", 1.6, stroke=RUST, extra='stroke-dasharray="4 4" opacity=".4"'))
    plate.append(path(f"M{tx - 34},{tb} q8,-3 16,0 M{tx + 12},{tb} q8,-3 16,0", "pen", .8))

    # ---- the near shore, under snow
    near = [(x, r1 + rng.uniform(-1.8, 1.8)) for x in range(PX0 - 30, W + 12, 20)]
    plate.append(f'<path d="{smooth(near)} L{W + 10},{H} L{PX0 - 30},{H} Z" fill="{PAPER}"/>')
    plate.append(path(smooth(near), "ink", 1.1, draw=True, delay=1.2, dur=2))
    grass = []
    for _ in range(40):
        gx, gy = rng.uniform(PX0, W - 10), rng.uniform(r1 + 18, H - 30)
        grass.append(f"M{f1(gx)},{f1(gy)} l{f1(rng.uniform(-2, 2))},{f1(-rng.uniform(5, 11))}")
    plate.append(path(" ".join(grass), "pen", .6, extra='opacity=".6"'))

    # ---- a kissaten on the shore: tiled roof, noren, a red lantern
    cx, cy, cw, ch = 806, 552, 118, 46
    eave = cy - ch
    roof = (f"M{cx - 20},{eave + 4} Q{cx - 8},{eave - 2} {cx + 6},{eave - 4} L{cx + 24},{eave - 30} "
            f"L{cx + cw - 24},{eave - 30} L{cx + cw - 6},{eave - 4} Q{cx + cw + 8},{eave - 2} {cx + cw + 20},{eave + 4} Z")
    plate.append(f'<path d="M{cx},{cy} V{eave} H{cx + cw} V{cy} Z" fill="{PAPER}"/>')
    plate.append(f'<path d="{roof}" fill="{PAPER}"/>')
    tiles = " ".join(f"M{f1(cx + 10 + k * 9)},{eave - 3} L{f1(cx + 26 + k * 7.1)},{eave - 28}" for k in range(12))
    plate.append(f'<clipPath id="rf"><path d="{roof}"/></clipPath><g clip-path="url(#rf)">{path(tiles, "pen", .6, extra=chr(111) + "pacity=" + chr(34) + ".7" + chr(34))}</g>')
    # snow along the ridge and eaves
    plate.append(f'<path d="M{cx + 20},{eave - 29} Q{cx + cw / 2},{eave - 40} {cx + cw - 20},{eave - 29} '
                 f'Q{cx + cw / 2},{eave - 24} {cx + 20},{eave - 29} Z" fill="{PAPER_LIGHT}" stroke="{GRAPHITE}" stroke-width=".7"/>')
    plate.append(path(f"M{cx - 16},{eave + 1} Q{cx},{eave - 6} {cx + 8},{eave - 7} M{cx + cw - 8},{eave - 7} Q{cx + cw},{eave - 6} {cx + cw + 16},{eave + 1}",
                      "pen", 2.4, stroke=PAPER_LIGHT))
    # lit shōji window: an amber wash behind a lattice
    wx, wy, ww, wh = cx + 10, eave + 10, 48, 24
    plate.append(f'<ellipse cx="{wx + ww / 2}" cy="{wy + wh / 2}" rx="38" ry="24" fill="{AMBER}" fill-opacity=".2" filter="url(#wash)" class="glow"/>')
    plate.append(f'<rect x="{wx}" y="{wy}" width="{ww}" height="{wh}" fill="{AMBER}" fill-opacity=".5" class="glow"/>')
    lattice = f"M{wx},{wy} h{ww} v{wh} h-{ww} Z " + " ".join(f"M{wx + k * 12},{wy} v{wh}" for k in range(1, 4)) + f" M{wx},{wy + wh / 2} h{ww}"
    # doorway with a noren curtain in three panels
    dx = cx + 74
    door = f"M{dx},{cy} V{eave + 6} H{dx + 30} V{cy}"
    plate.append(f'<path d="M{dx + 1},{eave + 7} h28 v15 h-28 Z" fill="{INK}" fill-opacity=".78"/>')
    plate.append(path(f"M{dx + 10.5},{eave + 7} v15 M{dx + 19.5},{eave + 7} v15", "pen", .9, stroke=PAPER_LIGHT))
    plate.append(f'<circle cx="{dx + 15}" cy="{eave + 14}" r="3" fill="none" stroke="{PAPER_LIGHT}" stroke-width=".9"/>')
    plate.append(path(f"M{cx},{cy} V{eave} H{cx + cw} V{cy} {lattice} {door} {roof}", "ink", 1.1, draw=True, delay=1.8, dur=2.2))
    # vertical sign board
    plate.append(f'<rect x="{cx - 14}" y="{eave + 6}" width="11" height="34" fill="{PAPER_LIGHT}" stroke="{INK}" stroke-width=".9"/>')
    plate.append(text(cx - 8.5, eave + 19, "喫", "serif", 9, INK, "middle"))
    plate.append(text(cx - 8.5, eave + 32, "茶", "serif", 9, INK, "middle"))
    # the red paper lantern, swinging gently, with a warm glow
    lx0, ly0 = cx + cw - 6, eave + 2
    plate.append(f'<g class="sway" style="transform-origin:{lx0}px {ly0}px">'
                 f'<path d="M{lx0},{ly0} v6" stroke="{INK}" stroke-width=".9"/>'
                 f'<ellipse cx="{lx0}" cy="{ly0 + 16}" rx="13" ry="12" fill="{AMBER}" fill-opacity=".25" filter="url(#wash)" class="glow"/>'
                 f'<ellipse cx="{lx0}" cy="{ly0 + 16}" rx="7" ry="10" fill="{RUST}" fill-opacity=".85" stroke="{INK}" stroke-width=".8"/>'
                 f'<path d="M{lx0 - 6},{ly0 + 12} h12 M{lx0 - 7},{ly0 + 16} h14 M{lx0 - 6},{ly0 + 20} h12" stroke="{INK}" stroke-width=".4" opacity=".6"/>'
                 f'<path d="M{lx0 - 3},{ly0 + 6} h6 M{lx0 - 3},{ly0 + 26} h6" stroke="{INK}" stroke-width="1.6"/></g>')
    # a cup of coffee steaming on the bench outside
    plate.append(path(f"M{cx + 40},{cy - 6} h26 M{cx + 43},{cy - 6} v6 M{cx + 63},{cy - 6} v6", "ink", .9))
    plate.append(path(f"M{cx + 49},{cy - 7} v-6 h8 v6 M{cx + 57},{cy - 11} q4,0 0,3", "ink", .8))
    for k in range(2):
        plate.append(path(f"M{cx + 51 + k * 3},{cy - 15} q-4,-5 0,-9 q4,-5 0,-9", "pen steam", .8,
                          extra=f'style="animation-delay:{k * 3:.0f}s"'))
    plate.append(text(cx + cw + 22, cy + 6, "Kissa Kosui", "hand fade", 19, INK, extra='style="animation-delay:3.4s"'))
    plate.append(text(cx + cw + 128, cy + 6, "喫茶 湖水", "serif fade", 12, GRAPHITE, extra='style="animation-delay:3.5s"'))

    # black pines, flat cloud-pads of needles holding snow
    def kuromatsu(bx, by, s, lean):
        trunk = f"M{bx},{by} C{bx + lean * .4 * s},{by - 30 * s} {bx - lean * .3 * s},{by - 52 * s} {bx + lean * s},{by - 72 * s}"
        pads, snow, br = [], [], []
        for (ox, oy, r) in ((lean * .9, -74, 27), (-16, -52, 21), (18 + lean * .3, -40, 23), (-8, -26, 16)):
            px2, py2, rr = bx + ox * s, by + oy * s, r * s
            br.append(f"M{f1(bx + ox * s * .3)},{f1(py2 + 8 * s)} Q{f1(px2 - ox * s * .2)},{f1(py2 + 6 * s)} {f1(px2)},{f1(py2 + 2 * s)}")
            pads.append(f"M{f1(px2 - rr)},{f1(py2 + 5 * s)} q{f1(-rr * .1)},{f1(-8 * s)} {f1(rr * .3)},{f1(-9 * s)} "
                        f"q{f1(rr * .2)},{f1(-9 * s)} {f1(rr * .6)},{f1(-4 * s)} q{f1(rr * .4)},{f1(-9 * s)} {f1(rr * .7)},{f1(1 * s)} "
                        f"q{f1(rr * .45)},{f1(-2 * s)} {f1(rr * .4)},{f1(12 * s)} Z")
            snow.append(f"M{f1(px2 - rr * .75)},{f1(py2 - 4 * s)} Q{f1(px2)},{f1(py2 - 15 * s)} {f1(px2 + rr * .75)},{f1(py2 - 4 * s)}")
        g = path(trunk, "ink", 2.2 * s) + path(" ".join(br), "ink", 1.1 * s)
        g += f'<path d="{" ".join(pads)}" fill="{PAPER_DARK}" stroke="{INK}" stroke-width="{.9 * s:.2f}" stroke-linejoin="round"/>'
        g += path(" ".join(snow), "pen", 2.6 * s, stroke=PAPER_LIGHT)
        return f'<g class="fade" style="animation-delay:2.2s">{g}</g>'

    plate.append(kuromatsu(748, 586, 1.4, 16))
    plate.append(kuromatsu(1262, 560, 1.15, -22))

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
    out.append(text(1176, 588, "Hakone, vue du lac Ashi", "ital", 15, SLATE, "end"))
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
