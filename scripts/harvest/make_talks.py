"""Seed data/talks.yml from the 2024 PDF extraction (invited talks + conference presentations)."""
import re, sys, yaml
sys.path.insert(0, "scripts/harvest")
from parse_pdf import sections, numbered_items, split_citation

def split_authors(s):
    s = s.replace("*", "")
    s = re.sub(r"\s+", " ", s).strip().rstrip(",")
    s = re.sub(r",?\s*&\s*", ", ", s)                  # "A, & B" -> "A, B"
    s = re.sub(r"(\w)\s+([A-Z]\.)", r"\1, \2", s, count=0) if not "," in s.split(" ")[0] else s
    # split before "Surname," tokens: a capitalised word (possibly hyphenated) followed by a comma and initials
    parts = re.split(r",\s+(?=[A-Z][\w'’-]+(?:\s[A-Z][\w'’-]+)?,\s*[A-Z]\.)", s)
    out = []
    for p in parts:
        p = p.strip().rstrip(",")
        p = re.sub(r"^([A-Z][\w'’-]+) ([A-Z]\. ?[A-Z]?\.?)$", r"\1, \2", p)   # "Chammany M. B." -> "Chammany, M. B."
        if p: out.append(p)
    return out

S = sections()
talks = []
for kind, sec in [("invited", "INVITED TALKS"), ("conference", "ABSTRACTS AND PAPERS CONTRIBUTED AT PROFESSIONAL MEETINGS")]:
    for it in numbered_items(S[sec]):
        d = split_citation(it["text"])
        title, venue = d["title"], d["venue"]
        if not venue and '."' in title or (not venue and '." ' in title):   # quoted title case
            t, v = re.split(r'\."\s*', title, maxsplit=1); title, venue = t.strip('"“” '), v.rstrip(".")
        entry = {"type": kind, "year": d["year"]}
        if d.get("month"): entry["month"] = d["month"]
        entry["authors"] = split_authors(d["authors"])
        entry["title"] = title
        entry["venue"] = venue
        if kind == "invited" and "Invited Workshop" in venue: entry["type"] = "workshop"
        talks.append(entry)

header = """# Talks and presentations, newest first. type: invited | conference | workshop
# authors: list of "Surname, I. I." strings; mentee co-authors are starred automatically from students.yml.
# venue: meeting or host, with location.
"""
with open("data/talks.yml", "w") as f:
    f.write(header)
    yaml.safe_dump(talks, f, sort_keys=False, allow_unicode=True, width=1000)
print(len(talks), "talks written")
