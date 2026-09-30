"""Shared helpers: load data, format publications and talks, emit Typst and Markdown."""
import json, re, subprocess
from datetime import date
from pathlib import Path
import yaml

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
CONFIG = yaml.safe_load((ROOT / "cv-config.yml").read_text())

# ---------- data ----------
def load(name):
    return yaml.safe_load((DATA / f"{name}.yml").read_text())

def load_all():
    d = {n: load(n) for n in ("profile", "positions", "education", "grants", "awards", "software",
                              "talks", "teaching", "students", "service", "reviewing")}
    d["publications"] = load_publications()
    return d

def load_publications():
    out = subprocess.run(["quarto", "pandoc", str(DATA / "publications.bib"), "-t", "csljson"],
                         capture_output=True, text=True, check=True).stdout
    entries = json.loads(out)
    for e in entries:
        kws = [k.strip() for k in e.get("keyword", "").split(",") if k.strip()]
        e["category"] = next((k for k in kws if k in CATEGORIES), "other")
        e["invited"] = "invited" in kws
        e["refereed"] = e["category"] in REFEREED
        e["year"] = year_of(e)
        e["status"] = e.get("status") or ("published" if e["category"] != "preprint" else "inprogress")
    entries.sort(key=lambda e: (-(e["year"] or 0), authors_sort_key(e)))
    return entries

CATEGORIES = ["article", "review-article", "chapter", "proceedings", "book", "oer", "commentary", "book-review", "preprint", "other"]
REFEREED = {"article", "review-article", "chapter", "proceedings"}

def year_of(e):
    try:
        return int(e["issued"]["date-parts"][0][0])
    except (KeyError, IndexError, TypeError, ValueError):
        return None

def authors_sort_key(e):
    a = e.get("author") or e.get("editor") or []
    return " ".join((p.get("family") or p.get("literal", "")) for p in a).lower()

# ---------- names, stars, bold ----------
def initials(given):
    """'Matthew J C' -> 'M. J. C.'; 'JC' -> 'J. C.'; 'Jean-Paul' -> 'J.-P.'"""
    if not given: return ""
    out = []
    for token in re.split(r"[\s.]+", given.strip()):
        if not token: continue
        if "-" in token:
            out.append("-".join(t[0] + "." for t in token.split("-") if t)); continue
        if token.isupper() and len(token) <= 3:
            out.extend(c + "." for c in token); continue
        out.append(token[0] + ".")
    return " ".join(out)

def person_short(p):
    """CSL name -> 'Family, I. I.'"""
    if "literal" in p: return p["literal"]
    fam = p.get("family", "")
    suffix = p.get("suffix")
    s = f"{fam}, {initials(p.get('given', ''))}".rstrip(", ")
    if suffix: s += f", {suffix}"
    return s

def mentee_index(students):
    idx = {}
    for m in students["mentees"]:
        idx.setdefault(m["surname"].lower(), []).append(m)
    return idx

def mentee_level(name_str, idx):
    """'Family, I. I.' -> mentee level or None. Match surname, then any shared initial when both have them."""
    fam, _, ini = name_str.partition(",")
    cands = idx.get(fam.strip().lower())
    if not cands: return None
    letters = {c for c in ini.replace(".", " ").split()}
    for m in cands:
        mi = {c for c in (m.get("initials") or "").replace(".", " ").split()}
        if not letters or not mi or letters & mi:
            return m["level"]
    return None

def is_owner(name_str, profile):
    fam = profile["last_name"].lower()
    return name_str.lower().startswith(fam + ",") or name_str.lower() == fam

def decorate_author(name_str, profile, idx, seen_levels):
    """Return markdown-ish string: stars + optional bold."""
    s = name_str
    if CONFIG.get("mentee_stars") and idx is not None:
        lvl = mentee_level(name_str, idx)
        if lvl:
            seen_levels.add(lvl)
            s = CONFIG["mentee_symbols"].get(lvl, "*") + s
    if CONFIG.get("bold_own_name") and is_owner(name_str, profile):
        s = B(s)
    return s

def join_authors(names):
    if len(names) == 1: return names[0]
    if len(names) == 2: return f"{names[0]}, & {names[1]}"
    return ", ".join(names[:-1]) + f", & {names[-1]}"

def format_author_list(name_strs, profile, idx, seen_levels):
    return join_authors([decorate_author(n, profile, idx, seen_levels) for n in name_strs])

# ---------- publication formatting (APA-like, matching the 2024 CV) ----------
def fmt_pub(e, profile, idx, seen_levels, refereed_marker=None):
    if refereed_marker is None: refereed_marker = CONFIG.get("refereed_marker", True)
    names = [person_short(p) for p in (e.get("author") or [])]
    authors = format_author_list(names, profile, idx, seen_levels) if names else ""
    year = e["year"] or "n.d."
    title = e.get("title", "").rstrip(".")
    cat = e["category"]
    marker = ""
    if e["invited"]: marker = " Invited."
    elif refereed_marker and e["refereed"]: marker = " R."
    doi = e.get("DOI"); url = e.get("URL")
    tail = ""
    if cat in ("article", "review-article", "commentary", "book-review", "other") and e.get("container-title"):
        vol = e.get("volume"); issue = e.get("issue"); pages = e.get("page")
        tail = " " + I(e["container-title"])
        if vol: tail += ", " + I(str(vol))
        if issue: tail += f"({issue})"
        if pages: tail += f", {pages}"
        tail += "."
    elif cat in ("chapter", "proceedings"):
        eds = [person_short(p) for p in (e.get("editor") or [])]
        eds_str = ""
        if eds:
            eds_ini = [f"{n.split(',')[1].strip()} {n.split(',')[0]}" if "," in n else n for n in eds]
            eds_str = join_authors(eds_ini) + (" (Eds.), " if len(eds) > 1 else " (Ed.), ")
        tail = f" In {eds_str}" + I(e.get("container-title", ""))
        if e.get("volume"): tail += f" (Vol. {e['volume']}"
        if e.get("page"): tail += (", " if e.get("volume") else " (") + f"pp. {e['page']}"
        if e.get("volume") or e.get("page"): tail += ")"
        tail += "."
        if e.get("publisher"): tail += f" {e['publisher']}."
    elif cat in ("book", "oer"):
        title = I(title)
        if e.get("note"): tail = f" {e['note']}."
        if e.get("publisher"): tail += f" {e['publisher']}."
    elif cat == "preprint":
        if e.get("publisher"): tail = f" {e['publisher']}."
    else:
        if e.get("container-title"): tail = " " + I(e["container-title"]) + "."
        elif e.get("publisher"): tail = f" {e['publisher']}."
    if e.get("note") and cat not in ("book", "oer"): tail += f" {e['note']}."
    link = ""
    if doi: link = " " + U(f"https://doi.org/{doi}")
    elif url: link = " " + U(url)
    s = f"{authors} ({year}). {title}.{marker}{tail}{link}"
    return re.sub(r"\s+", " ", s).replace("..", ".").strip()

def fmt_talk(t, profile, idx, seen_levels):
    authors = format_author_list(t["authors"], profile, idx, seen_levels)
    when = f"{t['year']}, {t['month']}" if t.get("month") else str(t["year"])
    venue = t.get("venue", "").rstrip(".")
    loc = f", {t['location']}" if t.get("location") else ""
    return f"{authors} ({when}). {t['title'].rstrip('.')}. {venue}{loc}."

def star_legend(seen_levels):
    parts = [f"{CONFIG['mentee_symbols'][l]} = {CONFIG['mentee_labels'][l]}"
             for l in ("postdoc", "doctoral", "masters", "undergraduate") if l in seen_levels]
    return "(" + ", ".join(parts) + ")" if parts else ""

# ---------- dates ----------
def fmt_span(start, end, present="present"):
    if start is None and end is None: return ""
    s = str(start)[:4] if start is not None else ""
    e = present if end is None else str(end)[:4]
    return s if s == e else f"{s}-{e}"

def today_str():
    return date.today().strftime("%B %Y")

# ---------- markup: internal markers -> Typst or Markdown ----------
# Internal rich text uses these markers so literal asterisks (mentee stars) never clash with bold.
B0, B1, I0, I1, U0, U1 = "\u2e28b\u2e29", "\u2e28/b\u2e29", "\u2e28i\u2e29", "\u2e28/i\u2e29", "\u2e28u\u2e29", "\u2e28/u\u2e29"
def B(s): return f"{B0}{s}{B1}"
def I(s): return f"{I0}{s}{I1}"
def U(s): return f"{U0}{s}{U1}"

_TYPST_ESC = re.compile(r'([\\#*_@<>\[\]$`~/"\'])')
def typst_escape(s):
    return _TYPST_ESC.sub(r"\\\1", s)

_TOKEN = re.compile(f"{B0}(.+?){B1}|{I0}(.+?){I1}|{U0}(.+?){U1}")

def to_typst(s):
    out, i = [], 0
    for m in _TOKEN.finditer(s):
        out.append(typst_escape(s[i:m.start()]))
        if m.group(1) is not None: out.append(f"#strong[{typst_escape(m.group(1))}];")
        elif m.group(2) is not None: out.append(f"#emph[{typst_escape(m.group(2))}];")
        else:
            u = m.group(3); out.append(f'#link("{u}")[{typst_escape(u)}];')
        i = m.end()
    out.append(typst_escape(s[i:]))
    return "".join(out)

def to_plain(s):
    """Drop the internal markers, keeping their text (for plain-text consumers)."""
    return _TOKEN.sub(lambda m: m.group(1) or m.group(2) or m.group(3) or "", s)

_MD_ESC = re.compile(r"([\\*_#<>\[\]`])")
def md_escape(s):
    return _MD_ESC.sub(r"\\\1", s)

def to_md(s):
    out, i = [], 0
    for m in _TOKEN.finditer(s):
        out.append(md_escape(s[i:m.start()]))
        if m.group(1) is not None: out.append(f"**{md_escape(m.group(1))}**")
        elif m.group(2) is not None: out.append(f"*{md_escape(m.group(2))}*")
        else: out.append(f"<{m.group(3)}>")
        i = m.end()
    out.append(md_escape(s[i:]))
    return "".join(out)
