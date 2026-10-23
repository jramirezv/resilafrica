#!/usr/bin/env python3
"""Deterministic gate for the resilafrica Pages site and its public repo.

verify.py           local checks on site/
verify.py --live    local checks + checks against the deployed Pages site
"""
import argparse, hashlib, json, re, subprocess, sys, urllib.error, urllib.request
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parent.parent
SITE = ROOT / "site"
DATA = SITE / "data"
MANIFEST = DATA / "manifest.json"
LIVE_URL = "https://jramirezv.github.io/resilafrica/"

# Owner, 2026-10-23: noindex for now. Lifting it is a human gate.
REQUIRE_NOINDEX = True
# Hosts the page may load resources from. Empty = everything vendored. Additions need the owner.
ALLOWED_HOSTS = set()
MAX_FILE_BYTES = 25 * 1024 * 1024
MANIFEST_FIELDS = ("file", "title", "source", "retrieved")
TEXT_SUFFIXES = {".html", ".htm", ".css", ".js", ".mjs", ".json", ".csv", ".tsv",
                 ".md", ".txt", ".svg", ".geojson", ".topojson"}

EMAIL_RE = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")
PHONE_RES = [
    # Lookbehind skips numeric constants in vendored libraries (e.g. "1e+21"), which a
    # human-written phone number is never immediately preceded by.
    re.compile(r"(?<![\w.])\+\d[\d\s().-]{7,}\d"),  # international format
    re.compile(r"\b\d{3}[-.]\d{3}[-.]\d{4}\b"),     # US-style
]
# Resource-loading references; plain <a href> to external sources is allowed.
CSS_URL_RE = re.compile(r"""url\(\s*['"]?([^'")]+)['"]?\s*\)""")
JS_IMPORT_RE = re.compile(r"""(?:import\s*(?:[^'"]*?from\s*)?|fetch\(\s*)['"]([^'"]+)['"]""")

results = []


def report(name, ok, detail=""):
    print(f"PASS {name}" if ok else f"FAIL {name}: {detail}")
    results.append(ok)


class PageScan(HTMLParser):
    def __init__(self):
        super().__init__()
        self.title = False
        self.noindex = False
        self.loads = []   # resources the browser fetches on view
        self.links = []   # navigational hrefs

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == "title":
            self.title = True
        if tag == "meta" and (a.get("name") or "").lower() == "robots":
            self.noindex = "noindex" in (a.get("content") or "").lower()
        if tag in ("script", "img", "iframe", "source", "audio", "video", "embed") and a.get("src"):
            self.loads.append(a["src"])
        if tag == "link" and a.get("href"):
            self.loads.append(a["href"])
        if tag == "a" and a.get("href"):
            self.links.append(a["href"])


def site_files():
    return sorted(p for p in SITE.rglob("*") if p.is_file() and p.name != ".DS_Store")


def tracked_files():
    """Every file git tracks. The repo is public, so all of them fall under the PII gate."""
    out = subprocess.run(["git", "ls-files", "-z"], cwd=ROOT, capture_output=True)
    if out.returncode != 0:
        return None
    return [ROOT / n for n in out.stdout.decode("utf-8").split("\0") if n and (ROOT / n).is_file()]


def is_external(ref):
    s = urlsplit(ref)
    return bool(s.scheme or s.netloc)


def resolves(src_file, ref):
    path = urlsplit(ref).path
    if not path:
        return True  # pure fragment or query
    if path.startswith("/"):
        return False  # absolute paths break under the /resilafrica/ subpath
    target = (src_file.parent / path).resolve()
    if target.is_dir():
        target = target / "index.html"
    try:
        target.relative_to(SITE.resolve())
    except ValueError:
        return False
    return target.is_file()


def check_pages():
    pages = [p for p in site_files() if p.suffix in (".html", ".htm")]
    report("index-exists", (SITE / "index.html").is_file(), "site/index.html missing")
    missing_title, missing_noindex, broken, foreign = [], [], [], []
    for p in pages:
        scan = PageScan()
        scan.feed(p.read_text(encoding="utf-8", errors="replace"))
        rel = p.relative_to(SITE)
        if not scan.title:
            missing_title.append(str(rel))
        if REQUIRE_NOINDEX and not scan.noindex:
            missing_noindex.append(str(rel))
        for ref in scan.loads:
            if ref.startswith("data:"):
                continue
            if is_external(ref):
                if urlsplit(ref).hostname not in ALLOWED_HOSTS:
                    foreign.append(f"{rel}: {ref}")
            elif not resolves(p, ref):
                broken.append(f"{rel}: {ref}")
        for ref in scan.links:
            if not is_external(ref) and not ref.startswith(("mailto:", "#")) and not resolves(p, ref):
                broken.append(f"{rel}: {ref}")
    report("html-title", not missing_title, ", ".join(missing_title))
    if REQUIRE_NOINDEX:
        report("html-noindex", not missing_noindex, ", ".join(missing_noindex))
    for p in site_files():
        if p.suffix == ".css":
            refs = CSS_URL_RE.findall(p.read_text(encoding="utf-8", errors="replace"))
        elif p.suffix in (".js", ".mjs") and "vendor" not in p.relative_to(SITE).parts:
            refs = JS_IMPORT_RE.findall(p.read_text(encoding="utf-8", errors="replace"))
        else:
            continue
        rel = p.relative_to(SITE)
        for ref in refs:
            if ref.startswith("data:"):
                continue
            if is_external(ref):
                if urlsplit(ref).hostname not in ALLOWED_HOSTS:
                    foreign.append(f"{rel}: {ref}")
            elif not resolves(p, ref):
                broken.append(f"{rel}: {ref}")
    report("refs-resolve", not broken, "; ".join(broken))
    report("no-third-party-loads", not foreign, "; ".join(foreign))


def check_data():
    try:
        manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
        entries = manifest["files"]
    except (OSError, ValueError, KeyError, TypeError) as e:
        report("manifest-wellformed", False, str(e))
        return
    problems = []
    registered = set()
    for i, e in enumerate(entries):
        missing = [f for f in MANIFEST_FIELDS if not str(e.get(f, "")).strip()]
        if missing:
            problems.append(f"entry {i}: missing {', '.join(missing)}")
        if not re.match(r"^\d{4}-\d{2}-\d{2}$", str(e.get("retrieved", ""))):
            problems.append(f"entry {i}: retrieved must be YYYY-MM-DD")
        if e.get("file"):
            registered.add(e["file"])
            if not (DATA / e["file"]).is_file():
                problems.append(f"{e['file']}: registered but missing")
    report("manifest-wellformed", not problems, "; ".join(problems))
    on_disk = {str(p.relative_to(DATA)) for p in DATA.rglob("*")
               if p.is_file() and p != MANIFEST and p.name != ".DS_Store"}
    unregistered = sorted(on_disk - registered)
    report("data-provenance", not unregistered, "unregistered: " + ", ".join(unregistered))
    bad_json = []
    for name in on_disk:
        p = DATA / name
        if p.suffix in (".json", ".geojson", ".topojson"):
            try:
                json.loads(p.read_text(encoding="utf-8"))
            except ValueError as e:
                bad_json.append(f"{name}: {e}")
    report("data-json-parses", not bad_json, "; ".join(bad_json))


def check_pii_and_size():
    hits, big = [], []
    tracked = tracked_files()
    report("git-tracked-files", tracked is not None, "git ls-files failed; repo-wide PII scan skipped")
    files = sorted(set(site_files()) | set(tracked or []))
    for p in files:
        rel = p.relative_to(ROOT)
        if p.stat().st_size > MAX_FILE_BYTES:
            big.append(f"{rel} ({p.stat().st_size // (1024 * 1024)} MB)")
        raw = p.read_bytes()
        if p.suffix.lower() not in TEXT_SUFFIXES and b"\0" in raw:
            continue  # binary
        text = raw.decode("utf-8", errors="replace")
        for m in EMAIL_RE.findall(text):
            hits.append(f"{rel}: email {m}")
        for rx in PHONE_RES:
            for m in rx.findall(text):
                if sum(c.isdigit() for c in m) >= 9:
                    hits.append(f"{rel}: phone {m}")
    report("pii-mechanical", not hits, "; ".join(hits[:20]))
    report("file-size", not big, ", ".join(big))


def check_live():
    def get(url):
        req = urllib.request.Request(url, headers={"Cache-Control": "no-cache"})
        with urllib.request.urlopen(req, timeout=20) as r:
            return r.status, r.read()
    try:
        status, body = get(LIVE_URL)
    except (urllib.error.URLError, OSError) as e:
        report("live-index", False, f"{LIVE_URL}: {e}")
        return
    report("live-index", status == 200, f"status {status}")
    local = (SITE / "index.html").read_bytes()
    same = hashlib.sha256(body).hexdigest() == hashlib.sha256(local).hexdigest()
    report("live-matches-local", same, "deployed index.html differs from site/index.html "
           "(deploy pending, or local edits not pushed)")
    if REQUIRE_NOINDEX:
        report("live-noindex", b'name="robots" content="noindex' in body, "noindex meta absent")


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--live", action="store_true", help="also check the deployed site")
    args = ap.parse_args()
    if not SITE.is_dir():
        report("site-dir", False, f"{SITE} missing")
    else:
        check_pages()
        check_data()
        check_pii_and_size()
        if args.live:
            check_live()
    failed = results.count(False)
    print(f"\n{len(results) - failed}/{len(results)} checks passed")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
