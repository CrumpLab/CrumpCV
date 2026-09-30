"""Generate _generated/bc/*.md for the Brooklyn College personnel-form CV (cv-bc.qmd).

Word-first: everything is plain Markdown (tables, lists); no Typst blocks.
Called from build.py as build_bc.run(D, P, IDX, g) where g is build.py's namespace.
"""
from pathlib import Path
from cvlib import *  # noqa

def run(D, P, IDX, g):
    GEN = ROOT / "_generated" / "bc"
    GEN.mkdir(parents=True, exist_ok=True)
    fmt_span, today = g["fmt_span"], g["today_str"]
    money, grant_when = g["money"], g["grant_when"]

    def write(name, text): (GEN / name).write_text(text.strip() + "\n")
    def table(header, rows, widths):
        if not rows: rows = [tuple("" for _ in header)]
        return ("| " + " | ".join(to_md(h) for h in header) + " |\n|" + "|".join(":--" for _ in header) + "|\n" +
                "\n".join("| " + " | ".join(to_md(str(c)) for c in r) + " |" for r in rows) + f"\n\n: {{tbl-colwidths=\"[{widths}]\"}}\n")
    def numbered(items): return "\n".join(f"{i}. {to_md(s)}" for i, s in enumerate(items, 1)) + "\n" if items else "*None.*\n"
    def bullets(items): return "\n".join(f"- {to_md(s)}" for s in items) + "\n" if items else "*None.*\n"
    def fmt_month(s):
        s = str(s)
        if len(s) == 7:
            import calendar; return f"{calendar.month_name[int(s[5:7])]} {s[:4]}"
        return s
    A = P.get("appointment", {})

    # I. Personal data
    write("personal.md", "\n".join([
        f"**Date:** {today()}  ",
        f"**Name:** {P['name']}  ",
        f"**Department:** {P['department'].replace('Department of ', '')}  ",
        f"**Candidate for:** {', '.join(A.get('candidate_for') or []) or '—'}  ",
        f"**Projected/Actual Tenure Date:** {A.get('tenure_date', '')}  ",
        f"**Promotion Effective On (if applicable):** {A.get('promotion_effective', '')}  ",
        f"**Present Academic Rank:** {A.get('present_rank', '')}  ",
        f"**Initial Date in Present Rank:** {A.get('present_rank_since', '')}  ",
        f"**Initial Appointment Date to Tenure- or CCE-Track Position:** {A.get('initial_appointment', '')}  ",
    ]))

    # II. Higher education
    ed = D["education"]
    out = "**Degrees:**\n\n" + table(["Institution", "Dates Attended", "Degree and Major", "Date Conferred"],
        [(f"{e['institution']}, {e.get('location', '')}", fmt_span(e.get("start"), e["end"]), f"{e['degree']} ({e['field']})", e.get("conferred", str(e["end"]))) for e in ed],
        "35,15,25,25")
    diss = [e for e in ed if e.get("dissertation")]
    if diss: out += f"\n**Title of Dissertation (if applicable):** {to_md(diss[0]['dissertation'])}\n"
    post = [p for p in D["positions"] if "postdoc" in p["title"].lower()]
    if post:
        out += "\n**Additional Higher Education and/or Education in Progress:**\n\n" + bullets([f"{p['title']}, {p['institution']}, {fmt_span(p['start'], p['end'])}" for p in post])
    write("education.md", out)

    # III. Teaching career
    home = P["affiliation"]
    at_bc = [p for p in D["positions"] if p["institution"] == home]
    outside = [p for p in D["positions"] if p["institution"] != home]
    out = "**At Brooklyn College (reverse chronological order):**\n\n" + table(["Dates", "Rank", "Department"],
        [(f"{fmt_month(p['start'])} - {fmt_month(p['end']) if p['end'] else 'present'}", p["title"], p.get("department", "").replace("Department of ", "")) for p in at_bc], "35,35,30")
    out += "\n**Outside of Brooklyn College (reverse chronological order):**\n\n" + table(["Institution", "Dates", "Rank", "Department"],
        [(p["institution"], fmt_span(p["start"], p["end"]), p["title"], p.get("department", "").replace("Department of ", "")) for p in outside] +
        [(e["institution"], fmt_span(e.get("start"), e["end"]), "Graduate Student", e["field"]) for e in ed if e["degree"].startswith("Ph")], "30,20,25,25")
    write("career.md", out)

    # IV.A Teaching experience
    T = D["teaching"]
    out = (f"*Notes: {T['notes']}*\n\n" if T.get("notes") else "")
    for lvl, label in (("undergraduate", "Undergraduate Courses"), ("masters", "Master's Courses"), ("doctoral", "Doctoral Courses"), ("other", "Other Courses")):
        cs = [c for c in T["courses"] if c["level"] == lvl]
        if cs:
            out += f"\n**{label}**\n\n" + table(["PSYC #", "Title", "Notes"], [(c["code"].replace("PSYC ", ""), c["title"], c.get("note") or "") for c in cs], "15,55,30")
    write("teaching.md", out)

    LEVELS = [("postdoc", "Postdoctoral Associates"), ("doctoral", "Doctoral Students"), ("masters", "Master's Students"), ("undergraduate", "Undergraduate Students")]
    out = ""
    for lvl, label in LEVELS:
        ms = [m for m in D["students"]["mentees"] if m["level"] == lvl]
        if ms:
            out += f"\n**{label}**\n\n" + table(["Name", "Details"], [(f"{m['surname']}, {m['name'].replace(m['surname'], '').strip()}", g["mentee_right"](m)) for m in ms], "35,65")
    write("mentorship.md", out)

    oer = [(c["code"].replace("PSYC ", ""), c["title"], c["oer"]) for c in T["courses"] if c.get("oer")]
    for c in T["courses"]:
        for x in c.get("oer_extra", []): oer.append((c["code"].replace("PSYC ", ""), x["title"], x["url"]))
    out = (ROOT / "data/narratives/curriculum-development.md").read_text() + "\n\n" + table(["PSYC #", "Title", "OER URL"], oer, "12,43,45")
    write("curriculum.md", out)
    certs = T.get("certificates") or []
    write("certificates.md", "\n\n".join(f"**{c['title']}**\n\nIn {c.get('when') or c['year']}, {c.get('note', '').rstrip('.') + ' conducted by ' if c.get('note') else ''}{c['organization']}." for c in certs))

    # V.A Publications, split as the form asks
    since = int(CONFIG.get("recent_since", 2016))
    pubs = D["publications"]
    def strs(items): return [fmt_pub(e, P, IDX, set()) for e in items]
    recent = [e for e in pubs if e["status"] == "published" and (e["year"] or 0) >= since]
    accepted = [e for e in pubs if e["status"] == "inpress"]
    progress = [e for e in pubs if e["status"] == "inprogress"]
    previous = [e for e in pubs if e["status"] == "published" and (e["year"] or 0) < since]
    out = "*Using as many pages as may be necessary, please list your publications in reverse chronological order under the subject headings provided below.*\n\n"
    out += "**1. Recent Published Works/Creative Works**\n\n" + numbered(strs(recent))
    out += "\n**2. Works Accepted for Publication**\n\n" + numbered(strs(accepted))
    out += "\n**3. Works in Progress**\n\n" + numbered(strs(progress))
    out += "\n**4. Previous Publications**\n\n" + numbered(strs(previous))
    write("publications.md", out)

    # V.B Other evidence
    inv = [t for t in D["talks"] if t["type"] in ("invited", "workshop")]
    conf = [t for t in D["talks"] if t["type"] == "conference"]
    out = "*Using as many pages as may be necessary, please list your other scholarly or creative activity in reverse chronological order under the subject headings provided below.*\n\n"
    out += "**1. Invited Presentations (talks, lecture series, exhibits, performance, etc.)**\n\n" + numbered([fmt_talk(t, P, IDX, set()) for t in inv])
    out += "\n**2. Abstracts and Papers Contributed at Professional Meetings**\n\n" + numbered([fmt_talk(t, P, IDX, set()) for t in conf])
    out += "\n**3. Other Creative Work and Scholarly Activity**\n\n" + numbered([f"{s['name']}: {s['description'].rstrip('.')}." + (f" {'Open-source software package for R.' if s['type'] == 'r-package' else ''}") + (" " + U(s["url"]) if s.get("url") else "") for s in D["software"]])
    write("other.md", out)

    # VI. Grants
    funded = [x for x in D["grants"] if x["status"] == "funded"]
    submitted = [x for x in D["grants"] if x["status"] != "funded"]
    def agency(x): return x["funder"] + (f" {x['program']}" if x.get("program") else "") + (f" ({x['role']})" if x.get("role") != "PI" else "")
    def gtitle(x): return x["title"] + (f" (#{x['number']})" if x.get("number") else "")
    out = "*Please list in reverse chronological order and be certain to provide the inclusive date for each grant listed.*\n\n"
    out += "**A. Funded Grants**\n\n" + table(["Title", "Agency", "Amount Funded", "Period of Grant"], [(gtitle(x), agency(x), money(x), grant_when(x)) for x in funded], "45,25,15,15")
    out += "\n**B. Grant Proposals Submitted**\n\n" + table(["Title", "Agency", "Amount Requested", "Period of Grant"], [(gtitle(x), agency(x), money(x), grant_when(x)) for x in submitted], "45,25,15,15")
    write("grants.md", out)

    # VII. Awards
    aw = D["awards"]
    def award_when(a): return a.get("when") or (fmt_span(a["start"], a["end"]) if a.get("start") else str(a["year"]))
    out = "*Please list in reverse chronological order.*\n\n**A. Fellowships:**\n\n" + bullets([f"{a['title']}, {a['organization']} ({award_when(a)})" for a in aw if "fellow" in a["title"].lower()])
    out += "\n**B. Lectureships:**\n\n" + bullets([f"{a['title']}, {a['organization']} ({award_when(a)})" for a in aw if "lectur" in a["title"].lower()])
    out += "\n**C. Honors and Awards:**\n\n" + numbered([f"{a['title']}, {a['organization']} ({award_when(a)})" for a in aw if not any(k in a["title"].lower() for k in ("fellow", "lectur"))])
    write("awards.md", out)

    # VIII. Service
    def svc_when(s): return s.get("when") or fmt_span(s.get("start"), s.get("end"))
    def svc(cat, cols=("Name of Committee", "Dates of Service"), widths="70,30", with_org=False):
        items = [s for s in D["service"] if s["category"] == cat]
        rows = [((s["role"] + (f", {s['organization']}" if with_org else "")), svc_when(s)) for s in items]
        return table(list(cols), rows, widths)
    out = "*Include only those functions, organizations or committees in which you were a participating and productive member.*\n\n"
    out += "**A. Service to Brooklyn College:**\n\n"
    out += "*1. Administrative Service*\n\n" + table(["Title/Description", "Dates of Service"], [], "70,30")
    out += "\n*2. Service on College and/or Presidential Committees*\n\n" + svc("college")
    out += "\n*3. Service on School and/or Division Committees*\n\n" + svc("division")
    out += "\n*4. Service on Department Committees*\n\n" + svc("department")
    out += "\n*5. Student Activities (Advisement, Counseling)*\n\n" + svc("student-activities", cols=("Name of Activity", "Dates of Service"))
    out += "\n*6. Other Service*\n\n" + svc("other-college", cols=("Name of Activity", "Dates of Service"))
    out += "\n**B. Service to University and Graduate Center:**\n\n"
    out += "*1. Administrative Service*\n\n" + table(["Title/Description", "Dates of Service"], [], "70,30")
    out += "\n*2. University Committees*\n\n" + svc("university")
    out += "\n*3. Doctoral Program Committees*\n\n" + svc("doctoral-program")
    out += "\n**C. Service Off-Campus:**\n\n"
    rev = D["reviewing"]
    prof = [(s["organization"], s["role"], svc_when(s)) for s in D["service"] if s["category"] == "professional"]
    prof += [(r["organization"], r["role"], r.get("when") or str(r["year"])) for r in rev["grant_reviewing"]]
    prof += [("; ".join(rev["journals"]["titles"]), rev["journals"].get("role", "Ad hoc reviewer"), rev["journals"].get("when", ""))]
    out += "*1. Professional Activities and Memberships*\n\n" + table(["Organization", "Office Held (if applicable)", "Dates of Service"], prof, "50,25,25")
    out += "\n*Dissertation Committees*\n\n" + table(["Institution", "Role", "Year"],
        [(c["institution"] + (f", {c['location']}" if c.get("location") else ""), f"{c['role']} ({c['student']})", str(c["year"])) for c in D["students"]["committees"]], "45,40,15")
    out += "\n*2. Community Service*\n\n" + table(["Description", "Dates of Service"], [(s["role"] + f", {s['organization']}", svc_when(s)) for s in D["service"] if s["category"] == "community"], "70,30")
    write("service.md", out)
    print(f"build_bc: wrote {len(list(GEN.glob('*.md')))} form sections")
