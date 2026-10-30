"""Four Japanese plates for the cover, each in its own palette. Local coordinates: 680 × 600."""
from __future__ import annotations

import math
import random

from art import (
    GRAPHITE, INK, PIG, blob, construction, contour, hatch, poly, ribbon, stroke, swatches, tone, wash,
)
from sketch import f1, smooth

PW, PH = 680, 600


def _snow(rng, n, x0=0, x1=PW, cls="flake"):
    out = []
    for _ in range(n):
        r = rng.choice([1.0, 1.3, 1.7, 2.2])
        dur = rng.uniform(9, 17)
        out.append(f'<circle class="{cls}" cx="{f1(rng.uniform(x0, x1))}" cy="0" r="{r}" '
                   f'style="--dx:{rng.uniform(-40, 20):.0f}px;animation-duration:{dur:.1f}s;animation-delay:-{rng.uniform(0, dur):.1f}s"/>')
    return "".join(out)


# ======================================================================= I · Hakone, dawn

def fuji_dawn() -> str:
    rng = random.Random(11)
    o = []
    # sky: rose dawn low, cool blue high
    o.append(wash(f"M-20,-20 H{PW + 20} V210 Q{PW / 2},240 -20,215 Z", PIG["cerulean"], .22, f=3))
    o.append(wash(f"M-20,150 Q{PW / 2},120 {PW + 20},160 V330 H-20 Z", PIG["rose"], .38, f=0))
    o.append(wash(blob(rng, 520, 205, 120, 46), PIG["coral"], .3, f=1))
    o.append(f'<circle cx="548" cy="210" r="14" fill="{PIG["snow"]}" opacity=".9" filter="url(#soft)"/>')
    # a few long cloud streaks in graphite
    o.append(stroke("M60,96 q120,-10 240,-2 M330,120 q90,-6 170,0 M90,150 q70,-4 130,2", .6, GRAPHITE, .35))

    # Fuji
    px, top, base, half = 330, 104, 352, 330
    pts = []
    for x in range(-30, PW + 31, 6):
        d = abs(x - px)
        if d < 22:
            y = top + (2 if 6 < d < 13 else 0) + rng.uniform(-.8, .8)
        else:
            t = min(1, (d - 22) / (half - 22))
            y = top + (base - top) * (1 - (1 - t) ** 2.4)
        pts.append((x, y))
    fd = smooth(pts) + f" L{PW + 30},{base + 30} L-30,{base + 30} Z"
    o.append(wash(fd, PIG["lavender"], .42, f=1))
    o.append(wash(f"M{px + 4},{top} L{px + 160},{base} L{PW + 30},{base + 30} L{PW + 30},{top} Z", PIG["prussian"], .32, f=2,
                  extra=f'clip-path="url(#h1m)"'))
    o.insert(0, f'<clipPath id="h1m"><path d="{fd}"/></clipPath>')
    o.append('<g clip-path="url(#h1m)">' + tone(rng, "h1s", f"M{px + 4},{top} L{px + 170},{base} L{PW + 30},{base} L{PW + 30},{top} Z",
                  (px - 10, top, PW, base), layers=((3.6, 64), (6.5, 118)), lmin=6, lmax=22, sw=.5) + "</g>")
    # snow cap reserved as paper, with long fingers
    cap = [(x, y) for x, y in pts if abs(x - px) < 132]
    lower = []
    for x, _ in cap[::-1]:
        u = (x - px) / 132
        fing = abs(math.sin((x - px) / 10.5)) ** 4 * 48 * (1 - abs(u))
        y0 = next(y for xx, y in pts if xx == x)
        lower.append((x, y0 + 3 + (32 + fing) * (1 - u * u) ** 1.1))
    capd = smooth(cap) + " L" + smooth(lower)[1:] + " Z"
    o.append(f'<path d="{capd}" fill="{PIG["snow"]}" filter="url(#wc4)"/>')
    o.append(wash(f"M{px + 6},{top + 4} L{px + 130},{top + 80} L{px + 40},{top + 110} Z", PIG["cerulean"], .25, f=4,
                  extra=f'clip-path="url(#h1c)"'))
    o.insert(0, f'<clipPath id="h1c"><path d="{capd}"/></clipPath>')
    o.append(contour(rng, pts, 1.5))
    # gullies
    g = []
    for off in (-140, -90, -48, -14, 24, 64, 118):
        x0 = px + off * .12
        g.append(smooth([(x0 + off * j / 5 + rng.uniform(-2, 2), top + 14 + (base - top - 14) * j / 5 * (.7 + .25 * rng.random())) for j in range(6)]))
    o.append(stroke(" ".join(g), .55, GRAPHITE, .45, extra='clip-path="url(#h1m)"'))

    # Hakone hills, two layers
    for layer, (yb, amp, col, op, seed) in enumerate([(338, 26, PIG["slate"], .45, 3), (372, 30, PIG["indigo"], .42, 5)]):
        hp = [(x, yb - amp * (0.5 + 0.5 * math.sin(x / (70 + 30 * layer) + seed)) - 10 * math.sin(x / 23 + seed)) for x in range(-30, PW + 31, 8)]
        hd = smooth(hp) + f" L{PW + 30},420 L-30,420 Z"
        o.append(wash(hd, col, op, f=layer))
        o.append(tone(rng, f"h1h{layer}", hd, (-30, yb - 70, PW + 30, 420), layers=((4.5, 112), (8, 30)), lmin=4, lmax=14, ops=(.15, .3, .45), sw=.45))
        o.append(contour(rng, hp, 1.0 + .2 * layer, op=.8))
        crest = " ".join(f"M{f1(x - 3)},{f1(y + 1)} q3,-{rng.uniform(5, 9):.1f} 6,0" for x, y in hp[::1] if rng.random() < .7)
        o.append(stroke(crest, .6, INK, .7))

    # Lake Ashi
    o.append(wash("M-30,404 H710 V500 H-30 Z", PIG["cerulean"], .34, f=3))
    refl = [(x, 404 + (base - y) * .24) for x, y in pts if abs(x - px) < 300]
    o.append(wash(smooth(refl) + " L630,404 L30,404 Z", PIG["lavender"], .32, f=1))
    o.append(wash(smooth([(x, 404 + (base - y) * .24) for x, y in cap]) + " Z", PIG["snow"], .7, f=4))
    sparkle = " ".join(f"M{f1(rng.uniform(-10, PW))},{f1(rng.uniform(410, 495))} h{f1(rng.uniform(14, 60))}" for _ in range(60))
    o.append(f'<path d="{sparkle}" class="ripple" fill="none" stroke="{PIG["snow"]}" stroke-width="1.6" opacity=".85"/>')
    o.append(stroke(" ".join(f"M{f1(rng.uniform(-10, PW))},{f1(rng.uniform(412, 495))} h{f1(rng.uniform(10, 40))}" for _ in range(45)), .5, GRAPHITE, .5))
    o.append(contour(rng, [(x, 404 + rng.uniform(-1, 1)) for x in range(-30, PW + 31, 30)], 1.0, op=.7))

    # Heiwa torii in the water
    tx, tb, th = 470, 452, 70
    v = PIG["vermilion"]
    o.append(wash(f"M{tx - 23},{tb} L{tx - 19},{tb - th} L{tx - 14},{tb - th} L{tx - 17},{tb} Z M{tx + 23},{tb} L{tx + 19},{tb - th} L{tx + 14},{tb - th} L{tx + 17},{tb} Z", v, .85, f=4))
    o.append(wash(f"M{tx - 44},{tb - th - 3} Q{tx},{tb - th + 2} {tx + 44},{tb - th - 3} L{tx + 40},{tb - th - 11} Q{tx},{tb - th - 6} {tx - 40},{tb - th - 11} Z "
                  f"M{tx - 32},{tb - th + 10} h64 v6 h-64 Z", v, .85, f=4))
    o.append(stroke(f"M{tx - 44},{tb - th - 3} Q{tx},{tb - th + 2} {tx + 44},{tb - th - 3} M{tx - 23},{tb} L{tx - 19},{tb - th} M{tx + 23},{tb} L{tx + 19},{tb - th} M{tx - 32},{tb - th + 10} h64", .9, INK, .7))
    o.append(wash(f"M{tx - 22},{tb + 2} L{tx - 19},{tb + 46} L{tx - 15},{tb + 46} L{tx - 17},{tb + 2} Z M{tx + 22},{tb + 2} L{tx + 19},{tb + 46} L{tx + 15},{tb + 46} L{tx + 17},{tb + 2} Z", v, .35, f=2))

    # a rowing boat with one figure
    bx, by = 250, 470
    o.append(wash(f"M{bx - 26},{by} Q{bx},{by + 10} {bx + 28},{by - 2} L{bx + 22},{by - 6} L{bx - 22},{by - 5} Z", PIG["sepia"], .7, f=4))
    o.append(stroke(f"M{bx - 26},{by} Q{bx},{by + 10} {bx + 28},{by - 2} M{bx - 4},{by - 6} v-12 M{bx - 9},{by - 18} q5,-6 10,0 M{bx - 16},{by - 8} L{bx - 40},{by + 6}", 1, INK, .85))
    o.append(stroke(f"M{bx - 40},{by + 8} q34,4 80,0", .6, GRAPHITE, .5))

    # near shore and a great black pine framing the left
    o.append(wash("M-30,500 Q200,488 420,506 T710,500 V620 H-30 Z", PIG["snow"], 1, f=2))
    o.append(contour(rng, [(-30, 500), (120, 494), (260, 498), (420, 506), (560, 500), (710, 502)], 1.1, op=.75))
    o.append(wash("M-30,520 Q160,530 300,560 L-30,600 Z", PIG["cerulean"], .16, f=3))
    # a stone lantern on the shore, capped with snow, and reeds
    lx, ly = 150, 560
    lan = (f"M{lx - 16},{ly} h32 l-4,-8 h-24 Z M{lx - 5},{ly - 8} v-26 h10 v26 M{lx - 14},{ly - 34} h28 v-20 h-28 Z "
           f"M{lx - 26},{ly - 54} Q{lx},{ly - 74} {lx + 26},{ly - 54} Z M{lx},{ly - 68} v-8")
    o.append(wash(lan, PIG["slate"], .55, f=4))
    o.append(wash(f"M{lx - 7},{ly - 50} h14 v-12 h-14 Z", PIG["amber"], .8, f=4))
    o.append(f'<circle cx="{lx}" cy="{ly - 44}" r="18" fill="{PIG["amber"]}" opacity=".45" filter="url(#bloom)" class="flicker"/>')
    o.append(stroke(lan, 1, INK, .85))
    o.append(wash(f"M{lx - 30},{ly - 54} Q{lx},{ly - 82} {lx + 30},{ly - 54} Q{lx},{ly - 62} {lx - 30},{ly - 54} Z", PIG["snow"], 1, f=4))
    o.append(tone(rng, "h1l", lan, (lx - 30, ly - 80, lx + 30, ly), layers=((2.6, 70),), lmin=3, lmax=7, color=INK, ops=(.2, .35, .5), sw=.45))
    reeds = " ".join(f"M{f1(x)},{f1(y)} q{f1(rng.uniform(-4, 4))},{f1(-rng.uniform(10, 26) / 2)} {f1(rng.uniform(-6, 6))},{f1(-rng.uniform(10, 26))}"
                     for x, y in [(rng.uniform(40, 420), rng.uniform(510, 590)) for _ in range(44)])
    o.append(stroke(reeds, .7, INK, .55))
    o.append(swatches(330, 30, [("Prussian blue", PIG["prussian"]), ("rose madder", PIG["rose"]), ("vermilion", PIG["vermilion"])]))
    o.append(f'<g>{_snow(rng, 34)}</g>')
    return "".join(o)


# ======================================================================= II · Kyoto, snow evening

def kyoto_evening() -> str:
    rng = random.Random(22)
    o = []
    VX, VY = 340, 330
    # night sky: deep indigo, a paler glow around the pagoda
    o.append(wash(f"M-40,-40 H{PW + 40} V380 H-40 Z", PIG["indigo"], .62, f=3))
    o.append(wash(blob(rng, VX, 210, 190, 140, n=12), PIG["lavender"], .45, f=0))
    o.append(wash(blob(rng, VX + 20, 250, 110, 70), PIG["rose"], .18, f=1))

    def P(x, y, t):
        return (x + (VX - x) * t, y + (VY - y) * t)

    # Yasaka pagoda (Hōkan-ji), five tiers
    cx, b0 = VX + 4, 322
    tiers = [(b0 - i * 40, 78 - i * 7.5) for i in range(5)]
    for i, (y, w) in enumerate(tiers):
        bw = w * .58
        o.append(f'<path d="M{f1(cx - bw)},{f1(y - 12)} h{f1(2 * bw)} v-26 h{f1(-2 * bw)} Z" fill="{PIG["indigo"]}" fill-opacity=".85"/>')
        o.append(stroke(" ".join(f"M{f1(cx - bw + k * bw / 3)},{f1(y - 12)} v-26" for k in range(1, 6)), .5, PIG["amber"], .35))
        roof = (f"M{f1(cx - w - 14)},{f1(y - 22)} Q{f1(cx - w)},{f1(y - 10)} {f1(cx - w + 14)},{f1(y - 10)} L{f1(cx + w - 14)},{f1(y - 10)} "
                f"Q{f1(cx + w)},{f1(y - 10)} {f1(cx + w + 14)},{f1(y - 22)} L{f1(cx + w * .7)},{f1(y - 30)} L{f1(cx - w * .7)},{f1(y - 30)} Z")
        o.append(wash(roof, INK, .85, f=4))
        o.append(stroke(roof, .9, INK, .9))
        o.append(wash(f"M{f1(cx - w * .72)},{f1(y - 30)} Q{f1(cx)},{f1(y - 38)} {f1(cx + w * .72)},{f1(y - 30)} L{f1(cx + w + 8)},{f1(y - 21)} "
                      f"Q{f1(cx)},{f1(y - 26)} {f1(cx - w - 8)},{f1(y - 21)} Z", PIG["snow"], .95, f=4))
    ty = tiers[-1][0] - 30
    o.append(stroke(f"M{cx},{ty} V{ty - 58} " + " ".join(f"M{cx - 6},{ty - 12 - k * 8} h12" for k in range(6)), 1.2, INK, .95))
    o.append(stroke(f"M{cx - 4},{ty - 62} q4,-8 8,0", 1, INK, .9))

    # machiya on both sides of the street
    for side in (-1, 1):
        nx = -60 if side < 0 else PW + 60
        R = dict(roof=86, plaster_top=132, plaster_bot=236, hisashi=262, light_top=300, light_bot=470, ground=600)
        far = .78
        cuts = [0, .2, .36, .48, .58, .66, .72, far]

        def L(key, t):
            return P(nx, R[key], t)

        def quad(k1, k2, t0, t1):
            return poly([L(k1, t0), L(k1, t1), L(k2, t1), L(k2, t0)])

        for i in range(len(cuts) - 1):
            t0, t1 = cuts[i], cuts[i + 1]
            # upper storey: pale plaster with mushiko slots
            o.append(wash(quad("plaster_top", "plaster_bot", t0, t1), PIG["sand"], .55, f=i % 5))
            sx0, sx1 = t0 + (t1 - t0) * .2, t0 + (t1 - t0) * .8
            o.append(wash(quad("plaster_top", "plaster_bot", sx0, sx1).replace("M", "M", 1), INK, 0, f=4))
            slots = []
            for j in range(7):
                tt = sx0 + (sx1 - sx0) * j / 6
                a, b = L("plaster_top", tt), L("plaster_bot", tt)
                a = (a[0], a[1] + (b[1] - a[1]) * .3)
                b = (b[0], b[1] - (b[1] - a[1]) * .25)
                slots.append(f"M{f1(a[0])},{f1(a[1])} L{f1(b[0])},{f1(b[1])}")
            o.append(stroke(" ".join(slots), 2.6 * (1 - t0), INK, .75))
            # ground floor: dark timber, lattice glowing from inside
            o.append(wash(quad("hisashi", "ground", t0, t1), PIG["sepia"], .8, f=(i + 2) % 5))
            lit = quad("light_top", "light_bot", t0 + (t1 - t0) * .08, t1 - (t1 - t0) * .3)
            o.append(wash(lit, PIG["amber"], .75, f=4))
            o.append(f'<path d="{lit}" fill="{PIG["amber"]}" opacity=".5" filter="url(#bloom)" class="flicker"/>')
            lat = []
            for j in range(16):
                tt = t0 + (t1 - t0) * (.08 + .62 * j / 15)
                a, b = L("light_top", tt), L("light_bot", tt)
                lat.append(f"M{f1(a[0])},{f1(a[1])} L{f1(b[0])},{f1(b[1])}")
            o.append(stroke(" ".join(lat), 1.1 * (1 - t0 * .9), INK, .85))
            # a noren in the doorway
            if i % 2 == 0:
                d0 = t1 - (t1 - t0) * .26
                nr = quad("hisashi", "light_top", d0, t1 - (t1 - t0) * .04)
                o.append(wash(nr, PIG["indigo"], .9, f=4))
                a, b = L("hisashi", (d0 + t1) / 2), L("light_top", (d0 + t1) / 2)
                o.append(stroke(f"M{f1(a[0])},{f1(a[1])} L{f1(b[0])},{f1(b[1])}", .8, PIG["snow"], .8))
            # pillars
            a, b = L("roof", t0), L("ground", t0)
            o.append(stroke(f"M{f1(a[0])},{f1(a[1])} L{f1(b[0])},{f1(b[1])}", 1.6 * (1 - t0 * .8), INK, .9))
            # lantern by the door, its glow on the snow
            hx, hy = L("hisashi", t0 + (t1 - t0) * .72)
            sc = 1 - t0 * 1.05
            ly = hy + 22 * sc
            o.append(f'<circle cx="{f1(hx)}" cy="{f1(ly)}" r="{f1(30 * sc + 5)}" fill="{PIG["amber"]}" opacity=".55" filter="url(#bloom)" class="flicker"/>')
            o.append(wash(blob(rng, hx, ly, 8 * sc + 2, 12 * sc + 2.5, n=9, wob=.06), PIG["vermilion"], .95, f=4))
            o.append(stroke(f"M{f1(hx)},{f1(hy)} V{f1(ly - 12 * sc)} M{f1(hx - 4 * sc)},{f1(ly - 12 * sc)} h{f1(8 * sc)} M{f1(hx - 4 * sc)},{f1(ly + 12 * sc)} h{f1(8 * sc)}", 1.2 * sc + .3, INK, .85))
            gx, gy = L("ground", t0 + (t1 - t0) * .6)
            o.append(f'<ellipse cx="{f1(gx - side * 40 * sc)}" cy="{f1(gy - 6 * sc)}" rx="{f1(70 * sc + 8)}" ry="{f1(14 * sc + 2)}" fill="{PIG["amber"]}" opacity=".35" filter="url(#bloom)"/>')

        # roofs: the main roof and the lower hisashi, each with a heavy line of snow
        for top, bot in (("roof", "plaster_top"), ("hisashi", "plaster_bot")):
            band = poly([L(top, 0), L(top, far), L(bot, far), L(bot, 0)])
            o.append(wash(band, INK, .8, f=3))
            o.append('<g clip-path="url(#kc%d%s)">' % (side + 1, top) + "")
            o[-1] = ""
            tiles = []
            for j in range(60):
                tt = far * (1 - (1 - j / 60) ** 1.5)
                a, b = L(top, tt), L(bot, tt)
                tiles.append(f"M{f1(a[0])},{f1(a[1])} L{f1(b[0])},{f1(b[1])}")
            o.append(stroke(" ".join(tiles), .5, PIG["slate"], .5))
            sn = [L(top, 0), L(top, far)]
            o.append(wash(poly([(sn[0][0], sn[0][1] - 10), (sn[1][0], sn[1][1] - 3), (sn[1][0], sn[1][1] + 2), (sn[0][0], sn[0][1] + 9)]), PIG["snow"], 1, f=4))
            o.append(stroke(f"M{f1(L(bot, 0)[0])},{f1(L(bot, 0)[1])} L{f1(L(bot, far)[0])},{f1(L(bot, far)[1])}", 1.2, INK, .9))
        # snow banked against the walls
        g0, g1 = L("ground", 0), L("ground", far)
        o.append(wash(poly([(g0[0], g0[1] - 30), (g1[0], g1[1] - 4), (g1[0] - side * 30, g1[1] + 2), (g0[0] - side * 200, g0[1] + 10)]), PIG["snow"], 1, f=2))

    # the street: snow, blue shadows, footprints and paving
    gl, gr = P(-60, 600, .78), P(PW + 60, 600, .78)
    o.append(wash(f"M-40,610 L{f1(gl[0])},{f1(gl[1])} L{f1(gr[0])},{f1(gr[1])} L{PW + 40},610 Z", PIG["snow"], .9, f=2))
    o.append(wash(f"M-40,610 L{f1(gl[0])},{f1(gl[1])} L{f1(gl[0] + 40)},{f1(gl[1])} L240,610 Z", PIG["slate"], .25, f=1))
    paving = []
    for j in range(1, 14):
        t = .78 * (1 - (1 - j / 14) ** 2.4)
        a, b = P(-60, 600, t), P(PW + 60, 600, t)
        paving.append(f"M{f1(a[0])},{f1(a[1])} L{f1(b[0])},{f1(b[1])}")
    o.append(stroke(" ".join(paving), .5, GRAPHITE, .28))
    steps = " ".join(f"M{f1(P(330 + 14 * (k % 2), 600, k / 22)[0])},{f1(P(330, 600, k / 22)[1])} l3,-2" for k in range(16))
    o.append(stroke(steps, 2, PIG["slate"], .5))
    o.append(construction([(VX, VY, -60, 600), (VX, VY, PW + 60, 600), (VX, VY, -60, 86), (VX, VY, PW + 60, 86), (-40, VY, PW + 40, VY)], .12))

    # two figures under wagasa
    for (fx, fy, sc, col) in [(300, 548, 1.15, PIG["vermilion"]), (382, 452, .62, PIG["indigo"])]:
        um = f"M{fx - 30 * sc},{fy - 52 * sc} Q{fx},{fy - 78 * sc} {fx + 30 * sc},{fy - 52 * sc} Q{fx},{fy - 58 * sc} {fx - 30 * sc},{fy - 52 * sc} Z"
        o.append(wash(um, col, .92, f=4))
        o.append(stroke(um + " " + " ".join(f"M{fx},{fy - 66 * sc} L{f1(fx + k * 7.5 * sc)},{f1(fy - 54 * sc)}" for k in range(-4, 5)), .7 * sc + .2, INK, .85))
        o.append(wash(f"M{fx - 9 * sc},{fy} L{fx - 12 * sc},{fy - 34 * sc} Q{fx},{fy - 46 * sc} {fx + 11 * sc},{fy - 34 * sc} L{fx + 9 * sc},{fy} Z", INK, .85, f=4))
        o.append(wash(f"M{fx - 9 * sc},{fy - 22 * sc} h18 v4 h-18 Z", PIG["madder"], .9, f=4))
        o.append(stroke(f"M{fx},{fy - 66 * sc} V{fy - 30 * sc}", .7 * sc, INK, .9))
        o.append(f'<ellipse cx="{fx + 10 * sc}" cy="{fy + 3}" rx="{22 * sc}" ry="{4 * sc}" fill="{PIG["indigo"]}" opacity=".3"/>')
    o.append(swatches(330, 30, [("indigo", PIG["indigo"]), ("vermilion", PIG["vermilion"]), ("burnt sienna", PIG["sienna"])]))
    o.append(f'<g>{_snow(rng, 70)}</g>')
    return "".join(o)


# ======================================================================= III · Arashiyama, spring

def arashiyama_spring() -> str:
    rng = random.Random(33)
    o = []
    o.append(wash(f"M-30,-30 H{PW + 30} V220 H-30 Z", PIG["cerulean"], .16, f=3))
    # mountain in three layers of soft green, sakura dabbed through it
    layers = [(220, 60, PIG["slate"], .3), (262, 70, PIG["sap"], .45), (318, 46, PIG["sap"], .55)]
    for i, (yb, amp, col, op) in enumerate(layers):
        hp = [(x, yb - amp * math.exp(-((x - (250 + 120 * i)) / (260 - 40 * i)) ** 2) - 12 * math.sin(x / (31 + 9 * i))) for x in range(-30, PW + 31, 8)]
        hd = smooth(hp) + f" L{PW + 30},380 L-30,380 Z"
        o.append(wash(hd, col, op, f=i))
        o.append(tone(rng, f"a{i}", hd, (-30, yb - amp - 20, PW + 30, 380), layers=((5, 70 + 20 * i),), lmin=5, lmax=12, ops=(.12, .22, .32), sw=.45))
        # canopy: rows of small scallops, the way an illustrator draws a wooded slope
        sc = []
        yy = min(y for _, y in hp) + 6
        while yy < 376:
            x = -30 + rng.uniform(0, 12)
            while x < PW + 30:
                w = rng.uniform(7, 13) * (1 + .15 * i)
                sc.append(f"M{f1(x)},{f1(yy + rng.uniform(-2, 2))} q{f1(w / 2)},{f1(-w * .7)} {f1(w)},0")
                x += w + rng.uniform(-1, 3)
            yy += rng.uniform(8, 12) * (1 + .1 * i)
        o.append(f'<clipPath id="ac{i}"><path d="{hd}"/></clipPath><g clip-path="url(#ac{i})">' + stroke(" ".join(sc), .55, PIG["viridian"] if i else GRAPHITE, .45) + "</g>")
        o.append(contour(rng, hp, .9 + .2 * i, op=.7))
        for _ in range(22 + 8 * i):
            x = rng.uniform(-10, PW + 10)
            y = next(yy for xx, yy in hp if xx >= x) + rng.uniform(10, 60)
            if y > 372:
                continue
            for _ in range(rng.randint(6, 11)):
                bx, by = x + rng.gauss(0, 11), y + rng.gauss(0, 7)
                col = PIG["sakura"] if rng.random() < .8 else "#fbf6f4"
                o.append(wash(blob(rng, bx, by, rng.uniform(3, 7), rng.uniform(2.5, 5), n=7), col, rng.uniform(.45, .85), f=rng.randrange(5)))
        for _ in range(5 + 2 * i):
            x = rng.uniform(0, PW)
            y = next(yy for xx, yy in hp if xx >= x) + rng.uniform(10, 50)
            if y > 372:
                continue
            for _ in range(rng.randint(4, 7)):
                o.append(wash(blob(rng, x + rng.gauss(0, 7), y + rng.gauss(0, 4), rng.uniform(3, 6), rng.uniform(2, 4), n=7), PIG["viridian"], .55, f=4))
    # mist band
    o.append(wash("M-30,344 Q300,330 710,348 V384 Q340,392 -30,380 Z", "#fbf9f4", .85, f=3))

    # Togetsukyō: a long timber bridge
    deck = [(x, 400 - 5 * math.sin(math.pi * (x + 30) / 740)) for x in range(-30, PW + 31, 10)]
    dd = smooth(deck)
    o.append(wash(dd + " " + " ".join(f"L{f1(x)},{f1(y + 7)}" for x, y in deck[::-1]) + " Z", PIG["sepia"], .75, f=4))
    rail = [(x, y - 14) for x, y in deck]
    o.append(contour(rng, rail, .9, op=.85))
    o.append(contour(rng, deck, 1.3))
    posts = " ".join(f"M{f1(x)},{f1(y)} v-14" for x, y in deck[::2])
    o.append(stroke(posts, .8, INK, .8))
    piles = []
    for x, y in deck[1::4]:
        for dx in (-5, 0, 5):
            piles.append(f"M{f1(x + dx)},{f1(y + 7)} L{f1(x + dx * 1.3)},452")
        piles.append(f"M{f1(x - 8)},{f1(y + 20)} L{f1(x + 8)},{f1(y + 20)} M{f1(x - 7)},{f1(y + 34)} L{f1(x + 7)},{f1(y + 34)}")
    o.append(wash(" ".join(f"M{f1(x - 8)},{f1(y + 7)} h16 L{f1(x + 9)},452 h-18 Z" for x, y in deck[1::4]), PIG["sepia"], .32, f=2))
    o.append(stroke(" ".join(piles), .9, INK, .8))

    # the Katsura river
    o.append(wash(f"M-30,448 H{PW + 30} V610 H-30 Z", PIG["teal"], .32, f=3))
    o.append(wash(f"M-30,448 H{PW + 30} V490 H-30 Z", PIG["sap"], .22, f=1))
    refl = " ".join(f"M{f1(x + dx)},{456 + k * 7} v{rng.uniform(3, 6):.1f}" for x, _ in deck[1::4] for dx in (-5, 0, 5) for k in range(6))
    o.append(stroke(refl, 1.4, PIG["sepia"], .35))
    o.append(stroke(" ".join(f"M{f1(rng.uniform(-10, PW))},{f1(rng.uniform(460, 600))} h{f1(rng.uniform(16, 70))}" for _ in range(55)), .55, GRAPHITE, .45))
    o.append(f'<path d="{" ".join(f"M{f1(rng.uniform(-10, PW))},{f1(rng.uniform(460, 600))} h{f1(rng.uniform(16, 70))}" for _ in range(40))}" class="ripple" fill="none" stroke="#fbf9f4" stroke-width="1.5" opacity=".8"/>')
    # a covered boat
    bx, by = 440, 540
    o.append(wash(f"M{bx - 60},{by} Q{bx},{by + 12} {bx + 64},{by - 4} L{bx + 54},{by - 10} L{bx - 54},{by - 8} Z", PIG["sepia"], .75, f=4))
    o.append(wash(f"M{bx - 36},{by - 9} v-22 h70 v22 Z", "#fbf9f4", .9, f=4))
    o.append(wash(f"M{bx - 44},{by - 31} Q{bx},{by - 42} {bx + 42},{by - 31} Z", PIG["madder"], .55, f=4))
    o.append(stroke(f"M{bx - 60},{by} Q{bx},{by + 12} {bx + 64},{by - 4} M{bx - 36},{by - 9} v-22 h70 v22 M{bx - 44},{by - 31} Q{bx},{by - 42} {bx + 42},{by - 31} "
                    f"M{bx + 64},{by - 4} L{bx + 96},{by - 60}", .9, INK, .85))
    o.append(stroke(f"M{bx - 70},{by + 10} q60,6 140,0", .6, GRAPHITE, .5))

    # a sakura branch hanging into the top-left corner
    br = [(-30, 40), (40, 60), (110, 96), (170, 150), (196, 200)]
    o.append(contour(rng, br, 2.2, color=PIG["sepia"]))
    twigs = [[(40, 60), (66, 108), (70, 150)], [(110, 96), (150, 92), (196, 110)], [(170, 150), (150, 196), (160, 236)], [(80, 76), (100, 40)]]
    for tw in twigs:
        o.append(contour(rng, tw, 1.1, color=PIG["sepia"], ghost=False))
    for _ in range(46):
        tw = rng.choice(twigs + [br])
        x, y = tw[rng.randrange(len(tw))]
        x += rng.uniform(-22, 22)
        y += rng.uniform(-14, 22)
        r = rng.uniform(4, 8)
        o.append(wash(blob(rng, x, y, r, r * .85, n=7, wob=.25), PIG["sakura"], rng.uniform(.6, .95), f=4))
        if rng.random() < .5:
            o.append(f'<circle cx="{f1(x)}" cy="{f1(y)}" r="1" fill="{PIG["madder"]}" opacity=".7"/>')
    # falling petals
    petals = []
    for _ in range(26):
        dur = rng.uniform(10, 18)
        petals.append(f'<ellipse class="petal" cx="{f1(rng.uniform(0, PW))}" cy="0" rx="2.4" ry="1.5" fill="{PIG["sakura"]}" '
                      f'style="--dx:{rng.uniform(40, 120):.0f}px;animation-duration:{dur:.1f}s;animation-delay:-{rng.uniform(0, dur):.1f}s"/>')
    o.append("".join(petals))
    o.append(swatches(330, 30, [("sakura pink", PIG["sakura"]), ("sap green", PIG["sap"]), ("sepia", PIG["sepia"])]))
    return "".join(o)


# ======================================================================= IV · Kamakura coast, summer

def kamakura_summer() -> str:
    rng = random.Random(44)
    o = []
    o.append(wash(f"M-30,-30 H{PW + 30} V230 Q{PW / 2},180 -30,220 Z", PIG["cerulean"], .34, f=3))
    o.append(wash(f"M-30,214 Q{PW / 2},176 {PW + 30},222 V304 H-30 Z", PIG["coral"], .24, f=3))
    o.append(wash(blob(rng, 470, 250, 220, 40), PIG["rose"], .2, f=1))
    o.append(wash(blob(rng, 140, 120, 90, 26), "#fbf9f4", .9, f=1))
    o.append(wash(blob(rng, 420, 80, 120, 22), "#fbf9f4", .85, f=2))
    o.append(stroke("M70,128 q60,-12 140,0 M360,86 q80,-10 170,2", .6, GRAPHITE, .35))
    # distant Fuji, faint
    fp = [(x, 290 - 92 * max(0, 1 - abs(x - 520) / 150) ** 1.7) for x in range(360, 690, 6)]
    o.append(wash(smooth(fp) + " L690,300 L360,300 Z", PIG["lavender"], .45, f=1))
    o.append(stroke(smooth(fp), .8, GRAPHITE, .5))
    o.append(wash(smooth([(x, y) for x, y in fp if y < 230]) + " Z", "#fbf9f4", .8, f=4))
    # the horizon and the sea
    o.append(construction([(-30, 300, 710, 300)], .3))
    o.append(wash(f"M-30,298 H{PW + 30} V470 H-30 Z", PIG["teal"], .42, f=3))
    o.append(wash(f"M-30,298 H{PW + 30} V330 H-30 Z", PIG["prussian"], .25, f=1))
    o.append(stroke(" ".join(f"M{f1(rng.uniform(-10, PW))},{f1(rng.uniform(306, 460))} h{f1(rng.uniform(12, 50))}" for _ in range(70)), .55, GRAPHITE, .45))
    o.append(f'<path d="{" ".join(f"M{f1(rng.uniform(-10, PW))},{f1(rng.uniform(306, 460))} h{f1(rng.uniform(14, 60))}" for _ in range(50))}" class="ripple" fill="none" stroke="#fbf9f4" stroke-width="1.5" opacity=".85"/>')

    # Enoshima with its lighthouse
    ep = [(x, 300 - 58 * math.exp(-((x - 210) / 70) ** 2) - 18 * math.exp(-((x - 150) / 30) ** 2)) for x in range(90, 340, 6)]
    ed = smooth(ep) + " L340,302 L90,302 Z"
    o.append(wash(ed, PIG["viridian"], .55, f=2))
    o.append(tone(rng, "kE", ed, (90, 220, 340, 302), layers=((3, 70), (5, 150)), lmin=3, lmax=9, ops=(.25, .4, .55), sw=.45))
    o.append(contour(rng, ep, 1.1))
    lx, ly = 214, 246
    o.append(stroke(f"M{lx - 4},{ly} L{lx - 2},{ly - 40} L{lx + 2},{ly - 40} L{lx + 4},{ly} M{lx - 6},{ly - 40} h12 M{lx},{ly - 40} v-6", 1, INK, .9))
    o.append(f'<circle cx="{lx}" cy="{ly - 44}" r="6" fill="#fbf9f4" opacity=".9" filter="url(#soft)" class="flicker"/>')

    # Inamuragasaki: a wooded headland dropping into the sea at right
    hp = [(x, 298 - 64 * (1 - math.exp(-((x - 470) / 110) ** 2)) * (x > 470) + 4 * math.sin(x / 13)) for x in range(462, 720, 6)]
    hd = smooth(hp) + " L720,322 Q600,326 462,318 Z"
    o.append(wash(hd, PIG["sap"], .6, f=1))
    o.append(tone(rng, "kH", hd, (460, 220, 720, 330), layers=((3.2, 62), (6, 128)), lmin=4, lmax=12, ops=(.25, .4, .55), sw=.45))
    o.append(stroke(" ".join(f"M{f1(x)},{f1(y + 4)} l{f1(rng.uniform(-2, 2))},{f1(318 - y - 6)}" for x, y in hp[2::3]), .5, INK, .35))
    o.append(contour(rng, hp, 1.2))
    for _ in range(14):
        x = rng.uniform(480, 700)
        y = next(yy for xx, yy in hp if xx >= x) + rng.uniform(4, 20)
        o.append(wash(blob(rng, x, y, rng.uniform(6, 12), rng.uniform(4, 7), n=8), PIG["viridian"], .55, f=4))

    # sailboats
    for (sx, sy, s) in [(380, 360, 1.0), (470, 330, .6), (110, 380, .8)]:
        sail = f"M{sx},{sy} L{sx},{sy - 46 * s} L{sx + 26 * s},{sy - 4 * s} Z"
        o.append(wash(sail, "#fbf9f4", 1, f=4))
        o.append(stroke(sail + f" M{sx - 14 * s},{sy + 2} Q{sx + 6 * s},{sy + 8 * s} {sx + 30 * s},{sy + 1}", .8, INK, .85))

    # the shore: long swells, then a breaking wave with its foam left as paper
    for k, yy in enumerate((400, 428, 452)):
        sw_ = [(x, yy + 4 * math.sin(x / (40 + 8 * k) + k)) for x in range(-30, PW + 31, 12)]
        o.append(stroke(smooth(sw_), .7, PIG["prussian"], .45))
    crest = [(x, 486 + 7 * math.sin(x / 70) + rng.uniform(-1, 1)) for x in range(-30, PW + 31, 10)]
    o.append(wash(smooth([(x, y - 22) for x, y in crest]) + f" L{PW + 30},500 L-30,500 Z", PIG["teal"], .55, f=0))
    o.append(wash(smooth([(x, y - 22) for x, y in crest]) + f" L{PW + 30},480 L-30,480 Z", PIG["viridian"], .3, f=2))
    o.append(contour(rng, [(x, y - 22) for x, y in crest], 1.0, op=.7))
    foam = smooth(crest) + " " + " ".join(f"L{f1(x)},{f1(y + 18 + rng.uniform(-6, 6))}" for x, y in crest[::-1]) + " Z"
    o.append(wash(foam, "#fbf9f4", 1, f=3))
    o.append(stroke(" ".join(f"M{f1(x)},{f1(y + rng.uniform(4, 16))} q5,-3 10,0" for x, y in crest if rng.random() < .7), .6, GRAPHITE, .55))
    o.append(wash(smooth([(x, y + 26) for x, y in crest]) + f" L{PW + 30},540 L-30,540 Z", PIG["sand"], .45, f=4))

    # sand
    o.append(wash(f"M-30,540 Q340,528 710,546 V620 H-30 Z", PIG["sand"], .55, f=2))
    o.append(tone(rng, "kS", f"M-30,540 Q340,528 710,546 V620 H-30 Z", (-30, 528, 710, 620), layers=((5, 6),), lmin=3, lmax=7, ops=(.12, .2, .3), sw=.4, gap=.6))
    # a parasol and a bicycle on the sand
    px, py = 540, 560
    o.append(wash(f"M{px - 40},{py - 38} Q{px},{py - 66} {px + 40},{py - 38} Q{px},{py - 46} {px - 40},{py - 38} Z", PIG["coral"], .8, f=4))
    o.append(stroke(f"M{px - 40},{py - 38} Q{px},{py - 66} {px + 40},{py - 38} M{px},{py - 54} L{px + 6},{py + 14}", .9, INK, .85))
    bx, by = 140, 572
    o.append(stroke(f"M{bx - 18},{by} m-12,0 a12,12 0 1,0 24,0 a12,12 0 1,0 -24,0 M{bx + 26},{by} m-12,0 a12,12 0 1,0 24,0 a12,12 0 1,0 -24,0 "
                    f"M{bx - 18},{by} L{bx},{by - 18} L{bx + 26},{by} M{bx},{by - 18} L{bx + 18},{by - 18} L{bx + 26},{by} M{bx - 2},{by - 22} h8 M{bx + 18},{by - 18} l2,-8 h6", .9, INK, .85))
    o.append(swatches(330, 30, [("cerulean", PIG["cerulean"]), ("viridian", PIG["viridian"]), ("coral", PIG["coral"])]))
    return "".join(o)


SCENES = [
    ("Hakone · 芦ノ湖, l'aube", "PLANCHE II", fuji_dawn),
    ("Kyōto · 八坂, un soir de neige", "PLANCHE III", kyoto_evening),
    ("Arashiyama · 渡月橋, printemps", "PLANCHE IV", arashiyama_spring),
    ("Kamakura · 七里ヶ浜, été", "PLANCHE V", kamakura_summer),
]
