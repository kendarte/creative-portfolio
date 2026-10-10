"""Check internal links in extracted Creative Portfolio HTML."""
from pathlib import Path
from urllib.parse import urlsplit, unquote
from html.parser import HTMLParser
from collections import Counter

ROOT = Path(__file__).resolve().parents[1]
BASE = "/creative-portfolio/"
missing = []
external = Counter()
checked = 0

class Links(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.urls = []
    def handle_starttag(self, tag, attrs):
        for name, value in attrs:
            if name in {"href", "src", "poster"} and value:
                self.urls.append(value)

def path_for(raw, page):
    value = raw.strip()
    if value.startswith(("data:", "mailto:", "tel:", "javascript:", "#")):
        return None
    parts = urlsplit(value)
    if parts.scheme in {"https", "http"}:
        if parts.netloc != "kendarte.github.io":
            external[parts.netloc] += 1
            return None
        if not parts.path.startswith(BASE):
            # An intentional link back to the main Unity portfolio.
            return None
        return ROOT / unquote(parts.path[len(BASE):])
    if parts.path.startswith(BASE):
        return ROOT / unquote(parts.path[len(BASE):])
    if parts.path.startswith("/"):
        return ("ROOT_NOT_MIGRATED", value)
    return (page.parent / unquote(parts.path)).resolve()

for page in ROOT.rglob("*.html"):
    if "templates" in page.parts:
        continue  # Server-side Django templates are not standalone HTML pages.
    parser = Links()
    parser.feed(page.read_text(encoding="utf-8", errors="replace"))
    for raw in parser.urls:
        dest = path_for(raw, page)
        if dest is None:
            continue
        checked += 1
        if isinstance(dest, tuple):
            missing.append((str(page.relative_to(ROOT)), dest[1], dest[0]))
        else:
            if dest.is_dir():
                dest = dest / "index.html"
            if not dest.is_file():
                missing.append((str(page.relative_to(ROOT)), raw, "MISSING"))
print("HTML pages:", len(list(ROOT.rglob("*.html"))))
print("Local links checked:", checked)
print("Missing paths:", len(missing))
for item in missing[:70]:
    print("  ", *item, sep=" | ")
print("Top external hosts:", external.most_common(12))
