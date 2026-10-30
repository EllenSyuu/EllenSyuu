"""Planches III–X — one hand-lettered card per piece of work, each with its own small drawing.

Text comes from the case studies on ellensyuu.github.io; edit WORKS below and re-run.
"""
from __future__ import annotations

import math
import random
import re
from pathlib import Path

from sketch import (
    AMBER, FAINT, GRAPHITE, INK, PAPER_DARK, PAPER_LIGHT, RUST, SLATE,
    f1, hatch_lines, paper_finish, path, sketch_rect, smooth, svg_open, text, text_width, wrap,
)

W, H = 600, 400
ROMAN = ["III", "IV", "V", "VI", "VII", "VIII", "IX", "X"]

WORKS = [
    dict(slug="covarchimax", over="M.SC. THESIS · MCGILL 2026", title="covarchimax",
         pkg="R package · Archimax copulas",
         q="Does heavy rain hit several places at the same time — and is that changing?",
         value="3.90 vs 5.73", label="six-station extremal coefficient, autumn vs early summer",
         tech="R · EXTREME VALUE THEORY · BLOCK BOOTSTRAP", go="open the repository", fig="rain", cap="six stations, one storm"),
    dict(slug="tailfm", over="DEEP LEARNING FOR EXTREMES", title="TailFM",
         pkg="PyTorch · amortized inference",
         q="Can a neural network learn how heavy a tail is — and how often extremes arrive together?",
         value="9 of 9", label="seed × family checks where Hill still wins — reported, not tuned away",
         tech="PYTORCH · DEEPSETS · SIMULATION DESIGN", go="read the case study", fig="tail", cap="how heavy is the tail?"),
    dict(slug="vvi", over="BIOSTATISTICS · PUBLIC HEALTH", title="VVI",
         pkg="hybrid immunity, in calendar time",
         q="Does a booster before your first Omicron infection protect you — or imprint you?",
         value="1M people · 13 s", label="a million-person synthetic cohort, fitted on a laptop",
         tech="PYTHON · CLOGLOG GLM · B-SPLINES", go="read the case study", fig="vvi", cap="V · V · I, along the calendar"),
    dict(slug="sdg", over="OFFICIAL STATISTICS", title="SDG 4 Revision Tracker",
         pkg="Python · Polars",
         q="How much do education statistics change from one data release to the next?",
         value="16 → 44", label="countries with a 2021 value as releases backfill it (synthetic)",
         tech="PYTHON · POLARS · MYPY --STRICT · HYPOTHESIS", go="open the repository", fig="sheets", cap="one indicator, four releases"),
    dict(slug="bcm", over="BAYESIAN MODELLING · WORK IN PROGRESS", title="Bayesian Cohort Model",
         pkg="R / Stan · SDG 4.1.4",
         q="How many children are out of school — when the surveys disagree and the gaps are wide?",
         value="reproduction", label="an independent rebuild of a published model, synthetic demo + tests",
         tech="STAN · NUMPYRO · JAX", go="open the repository", fig="cohort", cap="cohorts, flowing through school"),
    dict(slug="immca", over="CIVIC TOOL · LIVE", title="IMMCA",
         pkg="Canadian immigration pathways",
         q="Given who you are, which federal, Québec and provincial routes could fit — and what do they ask?",
         value="3 languages", label="English · French · Chinese, refreshed every day, runs in the browser",
         tech="STATIC SITE · GITHUB ACTIONS · PWA", go="open the live site", fig="sign", cap="which way in?"),
    dict(slug="hosicite", over="INTERACTIVE · LIVE", title="HosiCite",
         pkg="a citation atlas",
         q="What if exploring a research field felt like reading an old painted map?",
         value="map + timeline", label="who cites whom, drawn as islands and sea routes",
         tech="INTERACTIVE VIS · SEMANTIC SCHOLAR · VERCEL", go="open the live site", fig="map", cap="a map of who cites whom"),
    dict(slug="site", over="THIS SKETCHBOOK", title="ellensyuu.github.io",
         pkg="the full portfolio",
         q="Case studies, experience and public-interest work, drawn in ink on warm paper.",
         value="Planche I", label="Montréal from the river — where these drawings began",
         tech="GATSBY · REACT · GITHUB ACTIONS", go="visit the site", fig="site", cap="Montréal, vue du fleuve"),
]


# ------------------------------------------------------------ vignettes (drawn in a 200×190 box)

def fig_rain(rng):
    o = []
    stations = [(40, 150), (78, 128), (112, 156), (146, 120), (172, 150), (98, 98)]
    links = [(0, 1), (1, 2), (1, 5), (2, 3), (3, 4), (5, 3), (0, 2), (2, 4)]
    o.append(path(" ".join(f"M{stations[a][0]},{stations[a][1]} L{stations[b][0]},{stations[b][1]}" for a, b in links),
                  "pen", .8, extra='stroke-dasharray="3 3"'))
    for k, (x, y) in enumerate(stations):
        hot = k in (1, 2, 5)
        o.append(f'<circle cx="{x}" cy="{y}" r="{5 if hot else 4}" fill="{RUST if hot else PAPER_LIGHT}" stroke="{INK}" stroke-width="1"/>')
    cloud = "M42,58 q-2,-22 22,-24 q8,-20 32,-12 q16,-14 34,2 q22,-2 22,20 q16,6 4,18 h-108 q-14,-2 -6,-4 Z"
    o.append(f'<path d="{cloud}" fill="{PAPER_LIGHT}" stroke="{INK}" stroke-width="1.2" stroke-linejoin="round"/>')
    o.append(path(hatch_lines(40, 30, 160, 76, 4, 70), "pen", .5, extra='opacity=".35" clip-path="url(#cl)"'))
    o.insert(0, f'<clipPath id="cl"><path d="{cloud}"/></clipPath>')
    rain = " ".join(f"M{x},{84 + rng.uniform(0, 6)} l-5,{rng.uniform(12, 20)}" for x in range(54, 156, 9))
    o.append(path(rain, "pen", .9, extra='opacity=".85"'))
    return o


def fig_tail(rng):
    o = []
    pts = [(10 + x * 1.8, 168 - 128 * math.exp(-((x - 12) / 9) ** 2) - 30 / (1 + (x / 22) ** 2.2) * (x > 12)) for x in range(0, 101)]
    curve = smooth(pts[::3])
    tail = [(x, y) for x, y in pts if x >= 120]
    td = "M" + " L".join(f"{f1(x)},{f1(y)}" for x, y in tail) + f" L{f1(tail[-1][0])},168 L120,168 Z"
    o.append(f'<clipPath id="tl"><path d="{td}"/></clipPath>')
    o.append(f'<g clip-path="url(#tl)">{path(hatch_lines(110, 100, 200, 170, 3.2, 55), "pen", .7, stroke=RUST)}</g>')
    o.append(path(f"M6,168 H196 M10,172 V24", "pen", .8))
    o.append(path(curve, "ink", 1.6))
    o.append(path("M120,168 v-36", "pen", .8, extra='stroke-dasharray="2 3"'))
    o.append(text(124, 128, "ξ ?", "ital", 16, RUST))
    # a tiny network, sketched above the curve
    layers = [[(104, 22), (104, 46)], [(136, 14), (136, 34), (136, 54)], [(168, 34)]]
    ln = []
    for a, b in zip(layers, layers[1:]):
        for p in a:
            for q in b:
                ln.append(f"M{p[0]},{p[1]} L{q[0]},{q[1]}")
    o.append(path(" ".join(ln), "pen", .6, extra='opacity=".8"'))
    for layer in layers:
        for x, y in layer:
            o.append(f'<circle cx="{x}" cy="{y}" r="4" fill="{PAPER_LIGHT}" stroke="{INK}" stroke-width="1"/>')
    return o


def fig_vvi(rng):
    o = [path("M8,170 H196", "ink", 1.1)]
    for k, m in enumerate(["2021", "2022", "2023"]):
        x = 20 + k * 78
        o.append(path(f"M{x},166 v8", "pen", .8))
        o.append(text(x, 188, m, "serif", 12, GRAPHITE, "middle"))
    rows = [("V", 30, "V", 70, "I", 120), ("V", 44, "V", 96, "V", 112), ("V", 20, "I", 104, "", 0), ("V", 36, "V", 80, "V", 140)]
    for r, row in enumerate(rows):
        y = 34 + r * 34
        o.append(path(f"M14,{y} H192", "pen", .6, extra='stroke-dasharray="1 4"'))
        ev = [(row[i], row[i + 1]) for i in (0, 2, 4) if row[i]]
        for lab, x in ev:
            if lab == "I":
                o.append(f'<circle cx="{x}" cy="{y}" r="9" fill="{RUST}" fill-opacity=".14" stroke="{RUST}" stroke-width="1.2"/>')
                o.append(text(x, y + 5, "I", "ital", 15, RUST, "middle"))
            else:
                o.append(path(f"M{x - 6},{y - 7} L{x},{y + 6} L{x + 6},{y - 7}", "ink", 1.4))
    o.append(path("M100,24 V170", "pen", .8, stroke=RUST, extra='stroke-dasharray="4 4" opacity=".7"'))
    o.append(text(104, 20, "Omicron", "hand", 12, RUST))
    return o


def fig_sheets(rng):
    o = []
    for k in range(4):
        x, y = 18 + k * 14, 22 + k * 16
        o.append(f'<rect x="{x}" y="{y}" width="132" height="98" fill="{PAPER_LIGHT}" stroke="{INK}" stroke-width="1"/>')
        o.append(text(x + 6, y + 14, f"release {k + 1}", "hand", 11, GRAPHITE))
        pts = [(x + 12 + j * 22, y + 80 - 30 * math.sin(j * .7 + .5) - j * 4) for j in range(5)]
        if k == 3:
            pts[2] = (pts[2][0], pts[2][1] - 14)
            pts[3] = (pts[3][0], pts[3][1] - 18)
            pts.append((pts[-1][0] + 18, pts[-1][1] - 8))
        o.append(path(smooth(pts), "ink" if k == 3 else "pen", 1.4 if k == 3 else .9, stroke=RUST if k == 3 else None))
        for px, py in pts:
            o.append(f'<circle cx="{f1(px)}" cy="{f1(py)}" r="1.8" fill="{RUST if k == 3 else GRAPHITE}"/>')
    o.append(text(172, 98, "revised", "hand", 12, RUST, "middle"))
    o.append(path("M160,104 q-10,14 -24,18", "pen", .9, stroke=RUST))
    return o


def fig_cohort(rng):
    o = []
    for r in range(6):
        for c in range(6):
            x, y = 24 + c * 28, 30 + r * 24
            h = 14 * (0.55 + 0.45 * math.exp(-((r - c) ** 2) / 6))
            o.append(f'<rect x="{x}" y="{f1(y + 18 - h)}" width="16" height="{f1(h)}" fill="{PAPER_LIGHT}" stroke="{GRAPHITE}" stroke-width=".8"/>')
    for k in range(-2, 3):
        o.append(path(f"M{32 + max(k, 0) * 28},{40 + max(-k, 0) * 24} l{(5 - abs(k)) * 28},{(5 - abs(k)) * 24}", "ink", 1.1,
                      stroke=RUST if k == 0 else None, extra='opacity=".85"'))
    o.append(text(24, 186, "age", "hand", 12, GRAPHITE))
    o.append(text(196, 186, "years", "hand", 12, GRAPHITE, "end"))
    return o


def fig_sign(rng):
    o = [path("M96,186 V18", "ink", 1.8), path("M80,186 h34", "ink", 1.2)]
    boards = [("Fédéral", 26, 1), ("Québec", 70, -1), ("Provinces", 114, 1)]
    for lab, y, d in boards:
        w = 92
        x0 = 100 if d > 0 else 92 - w
        tip = x0 + w + 12 if d > 0 else x0 - 12
        if d > 0:
            pd = f"M{x0},{y} h{w} L{tip},{y + 14} L{x0 + w},{y + 28} h-{w} Z"
        else:
            pd = f"M{x0 + w},{y} h-{w} L{tip},{y + 14} L{x0},{y + 28} h{w} Z"
        fill = RUST if lab == "Québec" else PAPER_LIGHT
        o.append(f'<path d="{pd}" fill="{fill}" fill-opacity="{.16 if lab == "Québec" else 1}" stroke="{INK}" stroke-width="1.2" stroke-linejoin="round"/>')
        o.append(text(x0 + w / 2, y + 19, lab, "hand", 13, INK, "middle"))
    snow = " ".join(f"M{30 + k * 22},{184 - (k % 3) * 2} q8,-6 16,0" for k in range(7))
    o.append(path(snow, "pen", .8))
    return o


def fig_map(rng):
    o = []
    isles = [(56, 60, 26), (150, 52, 20), (120, 140, 30), (40, 150, 16)]
    for k, (x, y, r) in enumerate(isles):
        pts = [(x + r * (1 + rng.uniform(-.25, .2)) * math.cos(t), y + r * .7 * (1 + rng.uniform(-.25, .2)) * math.sin(t))
               for t in [i * math.pi / 6 for i in range(12)]]
        o.append(f'<path d="{smooth(pts, closed=True)}" fill="{PAPER_DARK}" stroke="{INK}" stroke-width="1.1"/>')
        o.append(path(smooth([(x - r * .9 + j * 4, y + r * .8 + rng.uniform(-1, 1)) for j in range(int(r / 2))]), "pen", .6))
    routes = [(0, 1), (0, 2), (2, 1), (3, 2)]
    o.append(path(" ".join(f"M{isles[a][0]},{isles[a][1]} Q{(isles[a][0] + isles[b][0]) / 2 + 14},{(isles[a][1] + isles[b][1]) / 2 - 18} {isles[b][0]},{isles[b][1]}" for a, b in routes),
                  "pen", 1.1, stroke=RUST, extra='stroke-dasharray="3 4"'))
    cx, cy = 174, 158
    o.append(f'<circle cx="{cx}" cy="{cy}" r="14" fill="none" stroke="{INK}" stroke-width=".9"/>')
    o.append(path(f"M{cx},{cy - 20} L{cx + 4},{cy} L{cx},{cy + 20} L{cx - 4},{cy} Z M{cx - 20},{cy} L{cx + 20},{cy}", "ink", .9))
    o.append(text(cx, cy - 23, "N", "serif", 11, INK, "middle"))
    return o


def fig_site(rng):
    o = []
    hill = smooth([(10, 120), (50, 92), (100, 64), (150, 80), (194, 112)])
    o.append(path(hill, "ink", 1.3))
    o.append(f'<clipPath id="hl"><path d="{hill} L194,150 L10,150 Z"/></clipPath>')
    o.append(f'<g clip-path="url(#hl)">{path(hatch_lines(10, 60, 194, 150, 5, 120), "pen", .5, extra='opacity=".5"')}</g>')
    towers = [(56, 34), (74, 52), (90, 70), (118, 44), (140, 28), (158, 40)]
    o.append(path(" ".join(f"M{x},132 V{132 - h} h12 V132" for x, h in towers), "ink", 1))
    o.append(path("M100,64 v-16 M94,54 h12", "ink", 1))
    o.append(path("M6,140 H198 M10,140 Q60,112 110,140 M110,140 Q160,112 198,138", "ink", 1.1))
    o.append(path(" ".join(f"M{x},140 v14" for x in range(20, 200, 22)), "pen", .8))
    for x, y in [(160, 30), (176, 46), (30, 40)]:
        o.append(f'<path d="M{x},{y} l4,-7 l3,5 l5,-2 l-2,6 l5,3 l-7,1 l1,6 l-5,-4 l-4,4 l0,-6 l-6,-1 l5,-3 Z" fill="{AMBER}" fill-opacity=".7" stroke="{RUST}" stroke-width=".7"/>')
    o.append(path("M0,168 H200", "pen", .6, extra='stroke-dasharray="10 6"'))
    return o


FIGS = dict(rain=fig_rain, tail=fig_tail, vvi=fig_vvi, sheets=fig_sheets, cohort=fig_cohort, sign=fig_sign, map=fig_map, site=fig_site)


def card(k: int, w: dict) -> str:
    rng = random.Random(100 + k)
    o = [svg_open(W, H, f"{w['title']} — {w['pkg']}", f"{w['q']} {w['value']}: {w['label']}.",
                  css=".card-in{animation:fade 1s ease both}")]
    o.append(path(sketch_rect(rng, 14, 14, W - 28, H - 28, amp=1.2, overshoot=5), "pen", .9, extra='opacity=".75"'))
    o.append(path(sketch_rect(rng, 20, 20, W - 40, H - 40, amp=.8, overshoot=2), "pen", .5, extra='opacity=".45"'))

    lx = 44
    o.append(text(lx, 58, f"PLANCHE {ROMAN[k]}", "caps", 11, RUST))
    o.append(text(lx + text_width(f"PLANCHE {ROMAN[k]}", "serif", 11, .2) + 12, 58, "· " + w["over"], "caps", 11, GRAPHITE))
    if re.search(r"[A-Z]{3}", w["title"]):  # capitals read badly in the script hand
        tkey, tcls, tsize = "serif-i", "ital", 50
    else:
        tkey, tcls, tsize = "hand", "hand", 46
    while text_width(w["title"], tkey, tsize) > 296 and tsize > 26:
        tsize -= 1
    o.append(text(lx - 2, 114, w["title"], tcls, tsize, INK))
    o.append(text(lx, 150, w["pkg"], "ital", 19, RUST))
    for j, line in enumerate(wrap(w["q"], "serif", 19, 288)[:4]):
        o.append(text(lx, 186 + j * 23, line, "serif", 19, INK))

    o.append(path(f"M{lx},284 h40", "pen", .8))
    o.append(text(lx, 314, w["value"], "serif", 27, RUST))
    for j, line in enumerate(wrap(w["label"], "sans", 12, 290)[:2]):
        o.append(text(lx, 334 + j * 16, line, "sans", 12, SLATE))
    o.append(text(lx, 374, w["tech"], "caps", 9.5, GRAPHITE))

    # vignette
    fx, fy = 362, 92
    o.append(f'<rect x="{fx - 8}" y="{fy - 8}" width="216" height="206" fill="{PAPER_LIGHT}" fill-opacity=".6"/>')
    o.append(path(sketch_rect(rng, fx - 8, fy - 8, 216, 206, amp=.7, overshoot=4), "pen", .7, extra='opacity=".7"'))
    o.append(f'<g transform="translate({fx},{fy})" filter="url(#pencil)" class="card-in">{"".join(FIGS[w["fig"]](rng))}</g>')
    o.append(text(fx + 100, fy + 222, w["cap"], "ital", 15, SLATE, "middle"))

    # the way in
    o.append(text(W - 46, 360, w["go"], "hand", 17, RUST, "end"))
    gw = text_width(w["go"], "hand", 17)
    o.append(path(f"M{f1(W - 46 - gw)},368 q{f1(gw / 2)},5 {f1(gw + 4)},-1 l-7,-4 m7,4 l-6,5", "pen", 1.1, stroke=RUST))

    o.append(paper_finish(W, H))
    return "".join(o)


def heading(title: str, over: str, note: str, dest: Path) -> None:
    rng = random.Random(len(title))
    hw, hh = 1280, 132
    o = [svg_open(hw, hh, title, f"{over} — {note}", fonts=("serif", "serif-i", "hand"))]
    o.append(path(f"M70,52 h38", "ink", 1))
    o.append(text(122, 57, over, "caps", 14, SLATE))
    o.append(text(68, 108, title, "hand", 44, INK))
    tw = text_width(title, "hand", 44)
    o.append(path(f"M{f1(84 + tw)},92 " + " ".join(f"L{f1(x)},{f1(92 + rng.uniform(-.8, .8))}" for x in range(int(110 + tw), 1210, 40)), "pen", .8, extra='opacity=".6"'))
    o.append(text(1210, 68, note, "ital", 17, GRAPHITE, "end"))
    o.append(paper_finish(hw, hh))
    dest.write_text("".join(o), encoding="utf-8")


def main() -> None:
    heading("selected work", "PLANCHES III – X", "each card opens the repository, the live site or the case study",
            Path("assets/heading-work.svg"))
    out = Path("assets/works")
    out.mkdir(parents=True, exist_ok=True)
    for k, w in enumerate(WORKS):
        (out / f"{k + 3:02d}-{w['slug']}.svg").write_text(card(k, w), encoding="utf-8")
    print(f"wrote {len(WORKS)} cards to {out}")


if __name__ == "__main__":
    main()
