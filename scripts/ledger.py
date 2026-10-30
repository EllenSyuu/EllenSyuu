"""Carnet — the last five weeks as a sketchbook calendar: one hand tick for every day with work.

Replaces GitHub's green squares with something quieter. Run daily by .github/workflows/ledger.yml.

    python scripts/ledger.py                    # fetch from GitHub (needs GH_TOKEN or GITHUB_TOKEN)
    python scripts/ledger.py --sample           # offline preview with made-up counts
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import random
import urllib.request
from pathlib import Path
from zoneinfo import ZoneInfo

from sketch import (
    FAINT, GRAPHITE, INK, PAPER_LIGHT, RUST, SLATE,
    f1, paper_finish, path, sketch_rect, svg_open, text, text_width, tick_path,
)

USER = "EllenSyuu"
TZ = ZoneInfo("America/Toronto")  # Montréal time
WEEKS = 5
W, H = 1280, 452

QUERY = """query($login:String!,$from:DateTime!,$to:DateTime!){
  user(login:$login){contributionsCollection(from:$from,to:$to){
    contributionCalendar{weeks{contributionDays{date contributionCount}}}}}}"""


def fetch(start: dt.date, end: dt.date) -> dict[dt.date, int]:
    token = os.environ.get("GH_TOKEN") or os.environ.get("GITHUB_TOKEN")
    if not token:
        raise SystemExit("Set GH_TOKEN (or run with --sample).")
    body = json.dumps({"query": QUERY, "variables": {
        "login": USER,
        "from": f"{start.isoformat()}T00:00:00Z",
        "to": f"{end.isoformat()}T23:59:59Z",
    }}).encode()
    req = urllib.request.Request("https://api.github.com/graphql", body, {
        "Authorization": f"bearer {token}", "Content-Type": "application/json", "User-Agent": "carnet",
    })
    with urllib.request.urlopen(req, timeout=30) as r:
        data = json.load(r)
    if "errors" in data:
        raise SystemExit(f"GitHub API: {data['errors']}")
    weeks = data["data"]["user"]["contributionsCollection"]["contributionCalendar"]["weeks"]
    return {dt.date.fromisoformat(d["date"]): d["contributionCount"] for w in weeks for d in w["contributionDays"]}


def sample(start: dt.date, end: dt.date) -> dict[dt.date, int]:
    rng = random.Random(4)
    out, d = {}, start
    while d <= end:
        out[d] = 0 if (end - d).days > 16 else rng.choice([0, 1, 3, 6, 9, 14, 22, 0, 4])
        d += dt.timedelta(days=1)
    return out


def build(counts: dict[dt.date, int], today: dt.date) -> str:
    rng = random.Random(today.toordinal())
    monday = today - dt.timedelta(days=today.weekday())
    first = monday - dt.timedelta(weeks=WEEKS - 1)
    days = [first + dt.timedelta(days=i) for i in range(WEEKS * 7)]
    seen = [d for d in days if d <= today]
    ticked = sum(1 for d in seen if counts.get(d, 0) > 0)
    total = sum(counts.get(d, 0) for d in seen)

    out = [svg_open(
        W, H, "Recent work — the last five weeks",
        f"A hand-drawn calendar of the five weeks up to {today:%d %B %Y}: "
        f"{ticked} of {len(seen)} days ticked, {total} contributions.",
        fonts=("serif", "serif-i", "hand"),
        css=".tick{stroke-dasharray:80;animation:tickdraw .6s ease-out both}@keyframes tickdraw{from{stroke-dashoffset:80}}",
    )]

    # ---- left: the note
    lx = 70
    out.append(text(lx, 128, "01.", "ital", 26, "#a84a26"))
    out.append(text(lx + text_width("01.", "serif-i", 26) + 14, 130, "Recent work", "title", 44, "#34425a"))
    note = ["The last five weeks, one tick for every day", "something shipped — commits, pull requests,",
            "issues — across all my repositories.", "Redrawn each morning."]
    for k, s_ in enumerate(note):
        out.append(text(lx, 184 + k * 25, s_, "sans", 15.5, SLATE))
    out.append(text(lx, 316, f"{ticked} of {len(seen)} days", "title", 30, "#a84a26"))
    out.append(text(lx, 344, f"{total} contributions", "hand", 16, GRAPHITE))

    # ---- right: the calendar page
    gx, gy, cw, chh = 586, 92, 88, 58
    out.append(path(sketch_rect(rng, gx - 18, gy - 52, cw * 7 + 36, chh * WEEKS + 112, amp=1.4, overshoot=6), "pen", .8, extra='opacity=".6"'))
    for i, name in enumerate(["MON", "TUE", "WED", "THU", "FRI", "SAT", "SUN"]):
        out.append(text(gx + cw * i + cw / 2, gy - 18, name, "caps", 11, GRAPHITE, "middle"))
    grid = []
    for r in range(WEEKS + 1):
        grid.append(path_line(rng, gx, gy + r * chh, gx + 7 * cw, gy + r * chh))
    for c in range(8):
        grid.append(path_line(rng, gx + c * cw, gy, gx + c * cw, gy + WEEKS * chh))
    out.append(path(" ".join(grid), "pen", .7, extra='opacity=".75"'))

    delay = 0.3
    for i, d in enumerate(days):
        r, c = divmod(i, 7)
        x0, y0 = gx + c * cw, gy + r * chh
        future = d > today
        label = d.strftime("%b").lower() + " " + str(d.day) if d.day == 1 or i == 0 else str(d.day)
        out.append(text(x0 + 7, y0 + 16, label, "serif", 13, FAINT if future else GRAPHITE))
        if future:
            continue
        n = counts.get(d, 0)
        if d == today:
            out.append(f'<ellipse cx="{f1(x0 + cw / 2 + 6)}" cy="{f1(y0 + chh / 2 + 4)}" rx="30" ry="19" '
                       f'fill="none" stroke="{RUST}" stroke-width="1" stroke-dasharray="3 4" opacity=".8"/>')
        if n <= 0:
            continue
        cx, cy = x0 + cw / 2 + 6, y0 + chh / 2 + 7
        heavy = n >= 10
        col = RUST if heavy else INK
        sw = 2.4 if n >= 5 else 1.6
        out.append(f'<path d="{tick_path(cx, cy, 1.0, rng)}" class="ink tick" '
                   f'style="stroke:{col};stroke-width:{sw};animation-delay:{delay:.2f}s"/>')
        if heavy:
            out.append(text(x0 + cw - 8, y0 + chh - 8, str(n), "hand", 13, RUST, "end"))
        delay += 0.07

    # legend
    ly = gy + WEEKS * chh + 38
    out.append(f'<path d="{tick_path(gx + 14, ly - 4, .55)}" class="ink" style="stroke-width:1.3"/>')
    out.append(text(gx + 30, ly, "some work", "ital", 15, GRAPHITE))
    out.append(f'<path d="{tick_path(gx + 136, ly - 4, .55)}" class="ink" style="stroke-width:2.2"/>')
    out.append(text(gx + 152, ly, "a full day (5+)", "ital", 15, GRAPHITE))
    out.append(f'<path d="{tick_path(gx + 276, ly - 4, .55)}" class="ink" style="stroke:{RUST};stroke-width:2.2"/>')
    out.append(text(gx + 292, ly, "a big push (10+, with the count)", "ital", 15, GRAPHITE))
    out.append(text(gx + 7 * cw, ly, f"as of {today:%-d %b %Y}", "hand", 15, SLATE, "end"))

    out.append(paper_finish(W, H))
    return "".join(out)


def path_line(rng, x1, y1, x2, y2) -> str:
    from sketch import wobble_line
    return wobble_line(rng, x1, y1, x2, y2, amp=.8, overshoot=3)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--sample", action="store_true")
    ap.add_argument("--out", default="assets/ledger.svg")
    a = ap.parse_args()
    today = dt.datetime.now(TZ).date()
    monday = today - dt.timedelta(days=today.weekday())
    start = monday - dt.timedelta(weeks=WEEKS - 1)
    counts = sample(start, today) if a.sample else fetch(start, today)
    dest = Path(a.out)
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(build(counts, today), encoding="utf-8")
    print(f"wrote {dest}")


if __name__ == "__main__":
    main()
