"""The profile cover: a folio of four Japanese plates that turn, one after another, beside the name.

    python scripts/cover.py                  # assets/cover.svg (animated folio)
    python scripts/cover.py --scene 2 x.svg  # one plate, still — for previews
"""
from __future__ import annotations

import argparse
import base64
from pathlib import Path

from plates import OUT as PLATES, split
from scenes import PW, SCENES
from sketch import (
    GRAPHITE, INK, RUST, SLATE, f1, paper_finish, path, svg_open, text, text_width,
)

W, H = 1280, 600
PX0 = W - PW  # 600: where the folio begins
CYCLE = 9.0  # seconds each plate holds
N = len(SCENES)
T = CYCLE * N

CSS = f"""
.sc{{opacity:0;animation:turn {T:.0f}s linear infinite}}
@keyframes turn{{0%{{opacity:0}}{100 * 1.4 / T:.2f}%{{opacity:1}}{100 * CYCLE / T:.2f}%{{opacity:1}}{100 * (CYCLE + 1.4) / T:.2f}%,100%{{opacity:0}}}}
.dot{{opacity:.28;animation:dot {T:.0f}s linear infinite}}
@keyframes dot{{0%{{opacity:.28}}{100 * 1.4 / T:.2f}%{{opacity:1}}{100 * CYCLE / T:.2f}%{{opacity:1}}{100 * (CYCLE + 1.4) / T:.2f}%,100%{{opacity:.28}}}}
.flake{{fill:#fbf9f4;stroke:#9aa6b8;stroke-width:.4;animation:fall linear infinite}}
.petal{{animation:fall linear infinite}}
@keyframes fall{{from{{transform:translate(0,-30px) rotate(0)}}to{{transform:translate(var(--dx),630px) rotate(240deg)}}}}
.ripple{{stroke-dasharray:18 26;animation:rip 10s linear infinite}}
@keyframes rip{{to{{stroke-dashoffset:-220}}}}
.flicker{{animation:flick 3.2s ease-in-out infinite alternate}}
@keyframes flick{{from{{opacity:.35}}to{{opacity:.6}}}}
.gull{{animation:gull 30s linear infinite;animation-delay:5s;opacity:0}}
@keyframes gull{{0%{{transform:translate(0,0);opacity:0}}3%{{opacity:1}}36%{{opacity:1}}40%,100%{{transform:translate(-560px,-60px);opacity:0}}}}
.flap{{animation:flap .55s ease-in-out infinite alternate;transform-origin:center;transform-box:fill-box}}
@keyframes flap{{to{{transform:scaleY(.45)}}}}
@media (prefers-reduced-motion:reduce){{.sc{{opacity:0}}.sc0{{opacity:1}}.dot{{opacity:.28}}.dot0{{opacity:1}}}}
"""


def plate_mask() -> str:
    """The folio's edge bleeds into the paper like an unfinished wash, not a hard frame."""
    return (
        '<linearGradient id="fadeL" x1="0" x2="1"><stop offset="0" stop-color="#fff" stop-opacity="0"/>'
        '<stop offset=".11" stop-color="#fff"/></linearGradient>'
        f'<mask id="folio" maskUnits="userSpaceOnUse" x="{PX0 - 80}" y="-40" width="{PW + 120}" height="{H + 80}">'
        f'<g filter="url(#edgefade)"><rect x="{PX0 + 14}" y="18" width="{PW - 30}" height="{H - 40}" fill="url(#fadeL)"/></g></mask>'
    )


def left_column(o: list[str]) -> None:
    lx = 70
    o.append(path(f"M{lx},204 h38", "ink", 1))
    o.append(text(lx + 52, 209, "STATISTICIAN & DATA ENGINEER · MONTRÉAL", "caps", 14, SLATE))
    size = 80
    parts = [("Ziyi ", "serif", INK), ("(Ellen)", "serif-i", RUST), (" Zhou.", "serif", INK)]
    x = lx - 4
    spans = []
    for s, key, col in parts:
        cls = "ital" if key == "serif-i" else "serif"
        spans.append(f'<tspan x="{f1(x)}" class="{cls}" fill="{col}">{s.replace(" ", "&#160;")}</tspan>')
        x += text_width(s, key, size)
    o.append(f'<text y="298" font-size="{size}" class="serif fade" style="animation-delay:.1s">{"".join(spans)}</text>')
    lines = [("I model ", "rare, high-impact events", " — floods,"),
             ("financial tail risk, gaps in education data —", "", ""),
             ("and build the software that makes those", "", ""),
             ("models trustworthy.", "", "")]
    for k, (a, em, b) in enumerate(lines):
        y = 356 + k * 29
        if em:
            sp = [f'<tspan x="{lx}">{a.replace(" ", "&#160;")}</tspan>']
            x = lx + text_width(a, "sans", 18)
            sp.append(f'<tspan x="{f1(x)}" class="ital" font-size="21">{em}</tspan>')
            x += text_width(em, "serif-i", 21)
            sp.append(f'<tspan x="{f1(x)}">{b.replace(" ", "&#160;")}</tspan>')
            o.append(f'<text y="{y}" class="sans fade" font-size="18" fill="{SLATE}" style="animation-delay:.5s">{"".join(sp)}</text>')
        else:
            o.append(text(lx, y, a, "sans fade", 18, SLATE, extra='style="animation-delay:.5s"'))
    o.append(text(lx, 498, "UNESCO INSTITUTE FOR STATISTICS  ·  M.SC. MCGILL  ·  B.SC. HKU", "caps", 11.5, GRAPHITE))


def build(only: int | None = None) -> str:
    o = [svg_open(
        W, H,
        "Ziyi (Ellen) Zhou — statistician and data engineer, Montréal",
        "A folio of pencil-and-watercolour plates of Japan that turn one after another: Fuji at dawn across Lake Ashi, "
        "a snowy evening below the Yasaka pagoda in Kyoto, the Togetsukyō bridge at Arashiyama in spring, and the "
        "Kamakura coast in summer. Beside it: Ziyi (Ellen) Zhou, statistician and data engineer in Montréal.",
        css=CSS,
    )]
    o.append("<defs></defs>")

    def anim(k):
        return "" if only is not None else f' class="sc sc{k}" style="animation-delay:{k * CYCLE - 1.5:.1f}s"'

    o.append(f'<clipPath id="plateclip"><rect x="{PX0 + 20}" y="10" width="{PW - 30}" height="{H - 30}"/></clipPath>')
    for k, (cap, num, draw) in enumerate(SCENES):
        if only is None or k == only:
            img = base64.b64encode((PLATES / f"plate-{k + 2}.webp").read_bytes()).decode()
            _, live = split(k)
            o.append(f'<g{anim(k)}><image x="{PX0}" y="0" width="{PW}" height="{H}" href="data:image/webp;base64,{img}"/>'
                     f'<g clip-path="url(#plateclip)"><g transform="translate({PX0},0)">{live}</g></g></g>')

    for k, (cap, num, _) in enumerate(SCENES):
        if only is None or k == only:
            o.append(f'<g{anim(k)}>{text(1168, 590, cap, "ital", 15, SLATE, "end")}{text(1180, 590, num, "caps", 10.5, GRAPHITE)}</g>')
    if only is None:
        for k in range(N):
            o.append(f'<circle class="dot dot{k}" cx="{PX0 + 40 + k * 16}" cy="586" r="3.2" fill="{INK}" '
                     f'style="animation-delay:{k * CYCLE - 1.5:.1f}s"/>')

    o.append(f'<g class="gull"><g transform="translate({W + 10},92)"><path class="flap" d="M-11,0 Q-5,-6 0,0 Q5,-6 11,0" '
             f'fill="none" stroke="{INK}" stroke-width="1.3" stroke-linecap="round"/></g></g>')
    left_column(o)
    o.append(paper_finish(W, H))
    return "".join(o)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("out", nargs="?", default="assets/cover.svg")
    ap.add_argument("--scene", type=int)
    a = ap.parse_args()
    dest = Path(a.out)
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(build(a.scene), encoding="utf-8")
    print(f"wrote {dest} ({dest.stat().st_size / 1024:.0f} KB)")
