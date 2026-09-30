"""Parse the text extraction of Crump_CV_24_formatted.pdf into numbered items per section.

Used once to seed data/. Kept for reference and re-runs.
"""
import re, json, sys
from pathlib import Path

SRC = Path("CV Examples/extracted/Crump_CV_24_formatted.txt")
HEADINGS = ["POSITIONS HELD", "EDUCATION", "PUBLICATIONS", "INVITED TALKS",
            "ABSTRACTS AND PAPERS CONTRIBUTED AT PROFESSIONAL MEETINGS",
            "GRANTS (FUNDED)", "GRANTS (SUBMITTED)", "PROFESSIONAL AWARDS",
            "UNIVERSITY, COLLEGE AND COMMUNITY SERVICE", "MENTORSHIP", "TEACHING EXPERIENCE"]

def sections():
    lines = [l.rstrip() for l in SRC.read_text().splitlines()]
    lines = [l for l in lines if not re.match(r"^(--- page \d+ ---|3/5/24)\s*$", l)]
    out, cur = {}, None
    for l in lines:
        h = l.strip()
        key = next((k for k in HEADINGS if h.startswith(k)), None)
        if key:
            cur = key; out[cur] = []
        elif cur:
            out[cur].append(l)
    return out

def numbered_items(lines):
    """Join wrapped lines into items that start with a bare number line or 'N text'."""
    items, buf = [], None
    for l in lines:
        s = l.strip()
        if not s: continue
        m = re.match(r"^(\d{1,2})\s*$", s)
        m2 = re.match(r"^(\d{1,2})\s+(\S.*)$", s)
        if m:
            if buf: items.append(buf)
            buf = {"n": int(m.group(1)), "text": ""}
        elif m2 and (buf is None or int(m2.group(1)) == buf["n"] + 1):
            if buf: items.append(buf)
            buf = {"n": int(m2.group(1)), "text": m2.group(2)}
        elif buf is not None:
            buf["text"] = (buf["text"] + " " + s).strip()
    if buf: items.append(buf)
    for it in items:
        it["text"] = re.sub(r"\s+", " ", it["text"]).replace("- ", "-").strip()
    return items

def split_citation(text):
    """'Authors (Year). Title. Venue.' -> dict. Stars mark mentees; keep them."""
    m = re.match(r"^(?P<authors>.+?)\s*\((?P<year>\d{4})(?:,\s*(?P<month>\w+))?\)\.?\s*(?P<rest>.+)$", text)
    if not m: return {"raw": text}
    rest = m.group("rest").strip()
    # title ends at the first '. ' that is followed by a capital letter (venue), unless in quotes
    parts = re.split(r'(?<=[a-z0-9\)\]"”?!])\.\s+(?=[A-Z0-9"“])', rest, maxsplit=1)
    title = parts[0].strip().strip('"“”')
    venue = parts[1].strip().rstrip(".") if len(parts) > 1 else ""
    return {"authors": m.group("authors").strip().rstrip(","), "year": int(m.group("year")),
            "month": m.group("month"), "title": title, "venue": venue}

if __name__ == "__main__":
    S = sections()
    want = sys.argv[1] if len(sys.argv) > 1 else "INVITED TALKS"
    for it in numbered_items(S[want]):
        d = split_citation(it["text"]); d["n"] = it["n"]
        print(json.dumps(d, ensure_ascii=False))
