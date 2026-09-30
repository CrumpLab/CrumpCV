#!/usr/bin/env python3
"""Validate data/ against schema/, check ordering, privacy, and the bib. Exit 1 on any problem."""
import json, re, subprocess, sys
from pathlib import Path
import yaml, jsonschema

ROOT = Path(__file__).resolve().parents[1]
DATA, SCHEMA = ROOT / "data", ROOT / "schema"
problems = []
def err(msg): problems.append(msg)

def load(name):
    return yaml.safe_load((DATA / f"{name}.yml").read_text())

def sort_key(e):
    v = e.get("start", e.get("year"))
    return str(v) if v is not None else ""

# 1. schema
sections = {}
for sf in sorted(SCHEMA.glob("*.json")):
    name = sf.stem
    try:
        data = load(name)
    except FileNotFoundError:
        err(f"{name}: data/{name}.yml missing"); continue
    except yaml.YAMLError as e:
        err(f"{name}: YAML error: {e}"); continue
    sections[name] = data
    v = jsonschema.Draft202012Validator(json.loads(sf.read_text()))
    for e in sorted(v.iter_errors(data), key=lambda e: list(e.path)):
        path = "/".join(str(p) for p in e.path) or "(root)"
        err(f"{name}: {path}: {e.message}")

# 2. ordering: newest first within each list (by start/year), ignoring entries without dates
def check_order(name, items, group=None):
    prev, prev_group = None, None
    for i, e in enumerate(items):
        k = sort_key(e)
        g = e.get(group) if group else None
        if g != prev_group: prev = None; prev_group = g
        if not k: continue
        if prev is not None and k > prev:
            err(f"{name}: item {i} ({e.get('title', e.get('role', e.get('name', '')))[:50]!r}) is newer than the one above it; keep newest first")
        prev = k
for name in ("positions", "education", "awards"):
    if name in sections: check_order(name, sections[name])
if "talks" in sections:
    check_order("talks", sections["talks"], group="type")
if "grants" in sections:
    check_order("grants", sections["grants"], group="status")
if "service" in sections:
    check_order("service", sections["service"], group="category")
if "students" in sections:
    check_order("students.committees", sections["students"]["committees"])

# 3. privacy lint: personal phone numbers or street addresses outside profile.address
phone_re = re.compile(r"\b\d{3}[-.\s]\d{3}[-.\s]\d{4}\b")
for f in list(DATA.glob("*.yml")) + list(DATA.glob("*.bib")) + list((DATA / "narratives").glob("*.md")):
    text = f.read_text()
    if f.name == "profile.yml":
        prof = yaml.safe_load(text)
        if prof.get("phone"):
            err("profile: phone is set; the repo is public, remove it unless the office line is approved")
        continue
    for m in phone_re.finditer(text):
        err(f"{f.name}: looks like a phone number: {m.group(0)}")

# 4. bib checks via pandoc
bib = DATA / "publications.bib"
CATS = {"article", "review-article", "chapter", "proceedings", "book", "oer", "commentary", "book-review", "preprint", "other"}
try:
    out = subprocess.run(["quarto", "pandoc", str(bib), "-t", "csljson"], capture_output=True, text=True, check=True).stdout
    entries = json.loads(out)
except (subprocess.CalledProcessError, FileNotFoundError) as e:
    err(f"publications.bib: pandoc could not parse it: {getattr(e, 'stderr', e)}"); entries = []
ids = [e["id"] for e in entries]
for dup in {i for i in ids if ids.count(i) > 1}: err(f"publications.bib: duplicate key {dup}")
for e in entries:
    kw = {k.strip() for k in e.get("keyword", "").split(",") if k.strip()}
    if not kw & CATS: err(f"publications.bib: {e['id']} has no category keyword (one of {sorted(CATS)})")
    if not e.get("author"): err(f"publications.bib: {e['id']} has no author")
    if not e.get("title"): err(f"publications.bib: {e['id']} has no title")
    if not e.get("issued"): err(f"publications.bib: {e['id']} has no year")

# 5. mentee lookups are well formed
if "students" in sections:
    for m in sections["students"]["mentees"]:
        if not m.get("initials"): err(f"students: {m['name']} has no initials; needed to star co-authored work")

if problems:
    print(f"validate: {len(problems)} problem(s)")
    for p in problems: print("  -", p)
    sys.exit(1)
print(f"validate: OK ({len(sections)} sections, {len(entries)} publications)")
