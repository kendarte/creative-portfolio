"""Convert copied creative pages into a GitHub Pages project site.

Run from the repository root with: python tools/adjust_paths.py
Idempotent: only recognizes original-root URLs, not already prefixed links.
"""
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
BASE = "/creative-portfolio/"
HOST = "https://kendarte.github.io/"
ROUTES = (
    "media", "3d", "illustration", "commercials", "rivarica",
    "rivarica-source-v08", "projects", "siza-mobile-test",
    "siza-core", "siza-world-engine", "siza-card-generator",
    "styles.css", "favicon.svg",
)
FILE_SUFFIXES = {".html", ".css", ".js", ".mjs", ".json"}
original_url = re.compile(
    r"https://kendarte\.github\.io/(?!projects/(?:taek-won-cop|horse-racer)/)(?=" +
    "|".join(re.escape(s) + r"(?:/|[?\"'#]|$)" for s in ROUTES) +
    r")"
)
root_url = re.compile(
    r"(?<![A-Za-z0-9/.])/(%s)(?=/|[?\"'#\s)]|$)"
    % "|".join(re.escape(x) for x in ROUTES)
)
updated = 0
for file in ROOT.rglob("*"):
    if not file.is_file() or file.suffix.lower() not in FILE_SUFFIXES:
        continue
    if ".git" in file.parts or file.resolve() == Path(__file__).resolve():
        continue
    try:
        raw = file.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        continue
    content = raw
    # Unity remains hosted on the main GitHub Pages portfolio.
    for slug in ("taek-won-cop", "horse-racer"):
        content = re.sub(
            r"(?<![A-Za-z0-9/])/projects/" + re.escape(slug) + r"/",
            HOST + 'projects/' + slug + '/',
            content
        )
    # The CV belongs to the Unity-focused main portfolio.
    content = content.replace(
        '="/Kendall_Angulo_Jhonson_CV_2026.pdf"',
        '="' + HOST + 'Kendall_Angulo_Jhonson_CV_2026.pdf"'
    )
    content = original_url.sub(HOST + BASE.lstrip('/'), content)
    content = root_url.sub(lambda match: BASE + match.group(1), content)
    # A bare root link now leads to this independent site.
    content = content.replace('href="/"', 'href="' + BASE + '"')
    if content != raw:
        file.write_text(content, encoding="utf-8", newline="")
        updated += 1
print("Adjusted files:", updated)
