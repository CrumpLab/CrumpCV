#!/usr/bin/env python3
"""Pre-render: turn data/ into _generated/*.md (Markdown plus raw Typst), _generated/meta.yml, and _generated/cv.json.

Each generated section carries two representations:
  - a raw ```{=typst} block calling the style's functions (used by the Typst PDF formats)
  - a Markdown fallback inside ::: {.content-visible unless-format="typst"} (Word, HTML)
"""
import json, subprocess, sys
from datetime import datetime, timezone
from pathlib import Path
import yaml

sys.path.insert(0, str(Path(__file__).resolve().parent))
from cvlib import *  # noqa

GEN = ROOT / "_generated"
GEN.mkdir(exist_ok=True)
(GEN / "bc").mkdir(exist_ok=True)

D = load_all()
P = D["profile"]
IDX = mentee_index(D["students"])

# ---------- emitters ----------
def both(typst, md):
    """Combine a Typst raw block and a Markdown fallback."""
    return f"```{{=typst}}\n{typst}\n```\n\n::: {{.content-visible unless-format=\"typst\"}}\n{md}\n:::\n"

def typ_content(s):
    return "[" + to_typst(s) + "]"

def rows_block(rows, left_width="1.15in"):
    """rows: list of (left, right) rich strings."""
    typ = "#cv-rows((\n" + "\n".join(f"  ({typ_content(l)}, {typ_content(r)})," for l, r in rows) + f"\n), left-width: {left_width})"
    md = "\n".join(f"| {to_md(l)} | {to_md(r)} |" for l, r in rows)
    md = "|  |  |\n|:--|:--|\n" + md + "\n\n: {tbl-colwidths=\"[18,82]\"}" if rows else ""
    return both(typ, md)

def numbered_block(items, start=1):
    typ = "#cv-numbered((\n" + "\n".join(f"  {typ_content(i)}," for i in items) + f"\n), start: {start})"
    md = "\n".join(f"{start + n}. {to_md(i)}" for n, i in enumerate(items))
    return both(typ, md)

def bullets_block(items):
    typ = "#cv-bullets((\n" + "\n".join(f"  {typ_content(i)}," for i in items) + "\n))"
    md = "\n".join(f"- {to_md(i)}" for i in items)
    return both(typ, md)

def table_block(header, rows, widths_typ, widths_md):
    typ = "#cv-table((" + ", ".join(typ_content(h) for h in header) + "), (\n" + \
          "\n".join("  (" + ", ".join(typ_content(c) for c in r) + ")," for r in rows) + f"\n), widths: ({widths_typ}))"
    md = "| " + " | ".join(to_md(h) for h in header) + " |\n|" + "|".join(":--" for _ in header) + "|\n" + \
         "\n".join("| " + " | ".join(to_md(c) for c in r) + " |" for r in rows) + f"\n\n: {{tbl-colwidths=\"[{widths_md}]\"}}"
    return both(typ, md)

def para(s):
    return both(to_typst(s), to_md(s))

def write(name, text):
    (GEN / name).write_text(text.strip() + "\n")

def h2(t): return f"\n## {t}\n\n"
def h3(t): return f"\n### {t}\n\n"

# ---------- header + metadata ----------
contact_left = [P["department"], P["affiliation_short"]] + list(P.get("address") or [])
contact_right = []
if P.get("phone"): contact_right.append(f"Phone: {P['phone']}")
contact_right.append(f"E-mail: {P['email']}")
if P.get("website"): contact_right.append(P["website"])
if P.get("github"): contact_right.append(f"GitHub: {P['github']}")
if P.get("orcid"): contact_right.append(f"ORCID: {P['orcid']}")
meta = {
    "title": P["name"],
    "subtitle": "Curriculum Vitae",
    "cv-contact-left": contact_left,
    "cv-contact-right": contact_right,
    "cv-date": today_str(),
    "cv-first-name": P.get("first_name", P["name"].split()[0]),
    "cv-last-name": P.get("last_name", P["name"].split()[-1]),
    "cv-position": P["title"],
    "cv-affiliation": P["affiliation"],
    "cv-email": P["email"],
    "cv-website": P.get("website", ""),
    "cv-github": P.get("github", ""),
}
(GEN / "meta.yml").write_text(yaml.safe_dump(meta, sort_keys=False, allow_unicode=True))
write("header.md", "::: {.content-visible unless-format=\"typst\"}\n" +
      "  \n".join(contact_left + contact_right) + f"  \nUpdated {today_str()}\n:::\n")

# ---------- positions, education ----------
write("positions.md", rows_block([
    (fmt_span(p["start"], p["end"]), f"{p['title']}, {p.get('department', '')}, {p['institution']}".replace(", ,", ","))
    for p in D["positions"]]))
write("education.md", rows_block([
    (str(e["end"]), f"{e['degree']} {e['field']}, {e['institution']}, {e.get('location', '')}".rstrip(", "))
    for e in D["education"]]))

# ---------- publications ----------
seen = set()
pubs = [e for e in D["publications"] if e["category"] != "preprint"]
preprints = [e for e in D["publications"] if e["category"] == "preprint"]
strings = [fmt_pub(e, P, IDX, seen) for e in pubs]
pre_strings = [fmt_pub(e, P, IDX, seen) for e in preprints]
out = ""
legend = star_legend(seen)
if legend: out += para(legend) + "\n"
if CONFIG.get("publication_numbering") == "descending":
    out += numbered_block(strings, start=1)
else:
    out += numbered_block(list(reversed(strings)), start=1)
if pre_strings:
    out += h2("Preprints and Works in Progress") + numbered_block(pre_strings)
write("publications.md", out)

# ---------- talks ----------
for kind, name in (("invited", "talks-invited.md"), ("conference", "talks-conference.md")):
    items = [t for t in D["talks"] if (t["type"] in ("invited", "workshop") if kind == "invited" else t["type"] == "conference")]
    write(name, numbered_block([fmt_talk(t, P, IDX, seen) for t in items]))

# ---------- grants ----------
def money(g):
    a = g.get("amount")
    if a is None: return ""
    s = f"${a:,.2f}" if isinstance(a, float) and a != int(a) else f"${int(a):,}"
    return s + (f" ({g['amount_note']})" if g.get("amount_note") else "")
def grant_when(g): return g.get("when") or fmt_span(g.get("start"), g.get("end"))
funded = [g for g in D["grants"] if g["status"] == "funded"]
submitted = [g for g in D["grants"] if g["status"] != "funded"]
out = h2("Funded") + table_block(["Title", "Agency", "Amount", "Period"],
    [(g["title"], f"{g['funder']}" + (f" {g['program']}" if g.get("program") else "") + (f" (#{g['number']})" if g.get("number") else "") + (f", {g['role']}" if g.get("role") != "PI" else ""),
      money(g), grant_when(g)) for g in funded], "2.6fr, 1.4fr, 0.9fr, 1.1fr", "42,25,15,18")
if submitted:
    out += h2("Submitted") + table_block(["Title", "Agency", "Amount requested", "Submitted"],
        [(g["title"], f"{g['funder']} ({g['role']})", money(g), grant_when(g).replace("Submitted ", "")) for g in submitted],
        "2.6fr, 1.4fr, 0.9fr, 1.1fr", "42,25,15,18")
write("grants.md", out)

# ---------- awards, software ----------
def award_when(a):
    return a.get("when") or (fmt_span(a["start"], a["end"]) if a.get("start") else str(a["year"]))
write("awards.md", bullets_block([f"{a['title']}, {a['organization']} ({award_when(a)})" for a in D["awards"]]))
write("software.md", bullets_block([
    B(s["name"]) + f": {s['description'].rstrip('.')}." + (" " + U(s["url"]) if s.get("url") else "")
    for s in D["software"]]))

# ---------- service ----------
SERVICE_GROUPS = [
    ("Service to Brooklyn College", [("college", "College committees"), ("division", "School and division committees"),
                                     ("department", "Department committees"), ("student-activities", "Student activities"), ("other-college", "Other service")]),
    ("Service to the University and Graduate Center", [("university", "University Service"), ("doctoral-program", "Doctoral program committees")]),
    ("Service Off-Campus", [("professional", "Professional activities and memberships"), ("community", "Community service")]),
]
def svc_when(s): return s.get("when") or fmt_span(s.get("start"), s.get("end"))
out = ""
for group, cats in SERVICE_GROUPS:
    rows_all = []
    body = ""
    for cat, label in cats:
        items = [s for s in D["service"] if s["category"] == cat]
        if not items: continue
        body += h3(label) + rows_block([(svc_when(s), s["role"] + (f", {s['organization']}" if cat in ("professional", "community") else "")) for s in items], left_width="1.6in")
    if body: out += h2(group) + body
rev = D["reviewing"]
out += h2("Reviewing")
out += h3("Grant reviewing") + rows_block([(r.get("when") or str(r["year"]), f"{r['role']}, {r['organization']}") for r in rev["grant_reviewing"]], left_width="1.6in")
out += h3(f"{rev['journals'].get('role', 'Ad hoc reviewer')} ({rev['journals'].get('when', '')})") + para("; ".join(rev["journals"]["titles"]))
write("service.md", out)

# ---------- mentorship ----------
LEVELS = [("postdoc", "Postdoctoral Associates"), ("doctoral", "Doctoral Students"), ("masters", "Master's Students"), ("undergraduate", "Undergraduate Students")]
def mentee_right(m):
    parts = []
    if m.get("start") or m.get("when"): parts.append(m.get("when") or fmt_span(m["start"], m.get("end"), present="current"))
    if m.get("program"): parts.append(m["program"])
    if m.get("note"): parts.append(m["note"])
    return "; ".join(parts)
out = ""
for lvl, label in LEVELS:
    ms = [m for m in D["students"]["mentees"] if m["level"] == lvl]
    if ms: out += h2(label) + rows_block([(m["name"], mentee_right(m)) for m in ms], left_width="1.9in")
out += h2("Dissertation Committees") + rows_block([(str(c["year"]), f"{c['role']} ({c['student']}), {c['institution']}" + (f", {c['location']}" if c.get("location") else "")) for c in D["students"]["committees"]], left_width="0.6in")
write("mentorship.md", out)

# ---------- teaching ----------
T = D["teaching"]
out = para(T["notes"]) + "\n" if T.get("notes") else ""
for lvl, label in (("undergraduate", "Undergraduate Courses"), ("masters", "Master's Courses"), ("doctoral", "Doctoral Courses"), ("other", "Other Courses")):
    cs = [c for c in T["courses"] if c["level"] == lvl]
    if not cs: continue
    out += h2(label) + table_block(["Course", "Title", "Notes"],
        [(c["code"], c["title"] + (" " + U(c["oer"]) if c.get("oer") else ""), c.get("note", "") or "") for c in cs], "1fr, 3.2fr, 1.8fr", "15,55,30")
if T.get("certificates"):
    out += h2("Teaching Certificates") + bullets_block([f"{c['title']}, {c['organization']} ({c.get('when') or c['year']})." + (f" {c['note']}" if c.get("note") else "") for c in T["certificates"]])
write("teaching.md", out)

# ---------- Brooklyn College form sections (used by cv-bc.qmd) ----------
try:
    import build_bc  # noqa: F401  (generates _generated/bc/*.md)
    build_bc.run(D, P, IDX, globals())
except ImportError:
    pass

# ---------- cv.json ----------
def jsonable(o):
    if isinstance(o, dict): return {k: jsonable(v) for k, v in o.items()}
    if isinstance(o, list): return [jsonable(v) for v in o]
    if hasattr(o, "isoformat"): return o.isoformat()
    return o
pub_json = []
for e in D["publications"]:
    j = {k: v for k, v in e.items() if k != "keyword"}
    j["formatted"] = to_md(fmt_pub(e, P, IDX, set(), refereed_marker=False))
    j["formatted_plain"] = re.sub(r"[⸨⸩/biu]{3,5}", "", fmt_pub(e, P, IDX, set(), refereed_marker=False))
    pub_json.append(j)
try:
    commit = subprocess.run(["git", "rev-parse", "--short", "HEAD"], capture_output=True, text=True, cwd=ROOT).stdout.strip()
except Exception:
    commit = None
cv = {"meta": {"generated": datetime.now(timezone.utc).isoformat(timespec="seconds"), "commit": commit or None, "schema": 1},
      "profile": {k: v for k, v in P.items() if k != "phone"},
      "positions": D["positions"], "education": D["education"], "publications": pub_json,
      "talks": [dict(t, formatted=to_md(fmt_talk(t, P, IDX, set())), formatted_plain=to_plain(fmt_talk(t, P, IDX, set()))) for t in D["talks"]],
      "grants": D["grants"], "awards": D["awards"], "software": D["software"],
      "teaching": D["teaching"], "students": D["students"], "service": D["service"], "reviewing": D["reviewing"]}
(GEN / "cv.json").write_text(json.dumps(jsonable(cv), indent=2, ensure_ascii=False) + "\n")
print(f"build: wrote {len(list(GEN.glob('*.md')))} sections, meta.yml, cv.json ({len(pub_json)} publications, {len(D['talks'])} talks)")
