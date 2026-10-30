"""The daily pass over the profile: what changed in my public repositories since yesterday.

1. assets/workbench.svg — the five public repositories I committed to most recently, each with
   the date and headline of my latest commit there (bot commits are ignored), in the house style.
2. README.md — rebuilt from scripts/README.template.md. A card that names a repository
   links to it when the repository is public, and to its fallback (case study or live site)
   while it is private. A repository going public is picked up the next morning.

Only public repositories are ever read, so nothing private reaches the page.
Run by .github/workflows/ledger.yml after the ledger.

    python scripts/daily.py            # needs GH_TOKEN or GITHUB_TOKEN
    python scripts/daily.py --sample   # offline preview
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import re
import urllib.error
import urllib.request
from pathlib import Path
from zoneinfo import ZoneInfo

from cards import DARK_SLATE, LIGHT_SLATE, doc
from draft import GRAPH, INK, SLATE, line, text
from sketch import text_width

USER = "EllenSyuu"
TZ = ZoneInfo("America/Toronto")
SKIP = {USER.lower()}  # the profile repository itself
ROOT = Path(__file__).resolve().parent.parent
TEMPLATE = ROOT / "scripts" / "README.template.md"
CARD_REPO = {"03-covarchimax": "SAC-thesis-2026", "06-sdg": "SDG", "04-tailfm": "TailFM"}
MORE_REPO = {0: "VVI", 1: "BCM"}
MORE_PRIVATE_GO = {0: "read the case study", 1: "visit the site"}
LINK = re.compile(r"\{\{repo:([A-Za-z0-9_.-]+)\|([^}]+)\}\}")

QUERY = """query($login:String!){ user(login:$login){ repositories(first:20, privacy:PUBLIC,
  ownerAffiliations:OWNER, orderBy:{field:PUSHED_AT, direction:DESC}){ nodes{ name url isFork pushedAt
  defaultBranchRef{ target{ ... on Commit{ history(first:30){ nodes{ messageHeadline committedDate
  author{ user{ login } } } } } } } } } } }"""


def _token() -> str:
    t = os.environ.get("GH_TOKEN") or os.environ.get("GITHUB_TOKEN")
    if not t:
        raise SystemExit("Set GH_TOKEN (or run with --sample).")
    return t


def _api(url: str, body: dict | None = None) -> dict | None:
    req = urllib.request.Request(
        url, json.dumps(body).encode() if body else None,
        {"Authorization": f"bearer {_token()}", "Content-Type": "application/json", "User-Agent": "workbench"})
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            return json.load(r)
    except urllib.error.HTTPError as e:
        if e.code == 404:
            return None
        raise


def recent_repos() -> list[dict]:
    data = _api("https://api.github.com/graphql", {"query": QUERY, "variables": {"login": USER}})
    if not data or "errors" in data:
        raise SystemExit(f"GitHub API: {data and data.get('errors')}")
    out = []
    for n in data["data"]["user"]["repositories"]["nodes"]:
        if n["name"].lower() in SKIP:
            continue
        hist = (((n.get("defaultBranchRef") or {}).get("target") or {}).get("history") or {}).get("nodes") or []
        mine = [h for h in hist if ((h.get("author") or {}).get("user") or {}).get("login", "").lower() == USER.lower()]
        if not mine:  # only bots (or nobody) committed lately: not news
            continue
        c = mine[0]
        when = c["committedDate"]
        out.append(dict(name=n["name"], url=n["url"], fork=n["isFork"],
                        when=dt.datetime.fromisoformat(when.replace("Z", "+00:00")).astimezone(TZ).date(),
                        msg=(c.get("messageHeadline") or "").strip()))
    out.sort(key=lambda r: r["when"], reverse=True)
    return out[:5]


def is_public(name: str) -> bool:
    data = _api(f"https://api.github.com/repos/{USER}/{name}")
    return bool(data) and not data.get("private", True)


def sample_repos(today: dt.date) -> list[dict]:
    rows = [("IMMCA", "Refresh Express Entry draws and official-page checks"), ("SDG", "Tighten the vintage diff tests"),
            ("VVI", "Add the calendar-time spline demo"), ("SAC-thesis-2026", "Document the block bootstrap"),
            ("BCM", "Wire the synthetic demo into CI")]
    return [dict(name=n, url=f"https://github.com/{USER}/{n}", fork=False, when=today - dt.timedelta(days=i * 2), msg=m)
            for i, (n, m) in enumerate(rows)]


def _fit(s: str, key: str, size: float, width: float) -> str:
    if text_width(s, key, size) <= width:
        return s
    while s and text_width(s + "…", key, size) > width:
        s = s[:-1]
    return s.rstrip() + "…"


def workbench(repos: list[dict], today: dt.date) -> str:
    w, row = 1280, 50
    h = 86 + row * len(repos) + 16
    o = [text(72, 46, "LATEST FROM THE WORKBENCH", "caps", 11.5, "#a84a26"),
         text(1208, 46, f"public repositories · redrawn {today:%-d %b %Y}", "hand", 14, GRAPH, "end"),
         line(f"M72,62 H1208", .75, INK, .35)]
    for k, r in enumerate(repos):
        y = 62 + row * (k + 1)
        days = (today - r["when"]).days
        ago = "today" if days <= 0 else "yesterday" if days == 1 else f"{days} days ago"
        o.append(text(72, y - 17, f"{r['when']:%-d %b}", "ital", 15, DARK_SLATE))
        o.append(text(170, y - 16, r["name"], "title", 20, LIGHT_SLATE))
        o.append(text(470, y - 18, _fit(r["msg"] or "—", "sans", 14, 560), "sans", 14, SLATE))
        o.append(text(1208, y - 17, ago, "hand", 14, "#a84a26" if days <= 1 else GRAPH, "end"))
        o.append(line(f"M72,{y} H1208", .5, INK, .18))
    desc = "; ".join(f"{r['name']} — {r['msg']} ({r['when']:%-d %b})" for r in repos)
    return doc(w, h, "Latest from the workbench", f"The most recently updated public repositories: {desc}.", "".join(o))


def build_readme(public: dict[str, bool]) -> str:
    def sub(m):
        name, fallback = m.group(1), m.group(2)
        return f"https://github.com/{USER}/{name}" if public.get(name) else fallback
    return LINK.sub(sub, TEMPLATE.read_text(encoding="utf-8"))


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--sample", action="store_true")
    a = ap.parse_args()
    today = dt.datetime.now(TZ).date()
    names = sorted(set(LINK.findall(TEMPLATE.read_text(encoding="utf-8"))))
    if a.sample:
        repos = sample_repos(today)
        public = {n: n in {"SDG", "SAC-thesis-2026", "BCM", "IMMCA", "VVI"} for n, _ in names}
    else:
        repos = recent_repos()
        public = {n: is_public(n) for n, _ in names}
    (ROOT / "assets" / "workbench.svg").write_text(workbench(repos, today), encoding="utf-8")
    # the cards' own "way in" follows the same rule as their links
    import cards
    for w in cards.WORKS:
        repo = CARD_REPO.get(w["slug"])
        if repo:
            w["go"] = "open the repository" if public.get(repo) else "read the case study"
    for i, repo in MORE_REPO.items():
        when, title, sub_, desc, go = cards.MORE[i]
        cards.MORE[i] = (when, title, sub_, desc, "open the repository" if public.get(repo) else MORE_PRIVATE_GO[i])
    os.chdir(ROOT)
    cards.main()
    (ROOT / "README.md").write_text(build_readme(public), encoding="utf-8")
    print("public:", ", ".join(n for n, p in public.items() if p) or "none",
          "| private:", ", ".join(n for n, p in public.items() if not p) or "none")


if __name__ == "__main__":
    main()
