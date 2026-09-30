"""Seed data/publications.bib: clean the 2019 Zotero export and append the 2016-2023 entries from the 2024 CV."""
import re
from pathlib import Path

SRC = Path("CV Examples/rvitae/awesome/Crump_pr.bib")
DROP = {"file", "abstract", "urldate", "langid", "shorttitle", "keywords", "issn", "isbn", "note", "eprint", "eprinttype"}
RENAME = {"journaltitle": "journal", "date": "year"}
CATEGORY = {  # non-default categories; default is by entry type
    "crumpReviewGuitarZero2012": "book-review",
    "buggSupportDistinctionVoluntary2012": "review-article",
}
FIX = {  # corrections from the 2024 CV
    "crumpReproducingLocationbasedContextspecific2016": {"year": "2017", "volume": "70", "pages": "1792-1807"},
    "crumpInstanceTheoryPredictsInpress": {"year": "2019", "volume": "73", "pages": "203-215"},
    "aujlaSemanticLibrarianSearch2019": {"volume": "51", "pages": "2405-2418"},
}
AUTHOR_FIX = {"jrParallelRegulationPresent2018": "Behmer, Jr., Lawrence P. and Jantzen, Kelly J. and Martinez, S. and Walls, R. and Amir-Brownstein, E. and Jaye, A. and Leytze, M. and Lucier, K. and Crump, M. J. C."}
TYPE_CATEGORY = {"article": "article", "incollection": "chapter", "inproceedings": "proceedings", "book": "book", "misc": "other"}

def parse(text):
    entries = []
    for chunk in re.split(r"\n(?=@)", text.strip()):
        m = re.match(r"@(\w+)\{([^,]+),(.*)\}\s*$", chunk.strip(), flags=re.S)
        if not m: continue
        etype, key, body = m.group(1).lower(), m.group(2).strip(), m.group(3)
        fields, i = {}, 0
        while True:
            fm = re.compile(r"\s*(\w+)\s*=\s*\{", re.S).match(body, i)
            if not fm: break
            name, depth, j = fm.group(1).lower(), 1, fm.end()
            while depth:
                depth += {"{": 1, "}": -1}.get(body[j], 0); j += 1
            fields[name] = re.sub(r"\s+", " ", body[fm.end():j-1]).strip()
            i = j
            cm = re.compile(r"\s*,").match(body, i)
            if cm: i = cm.end()
        entries.append((etype, key, fields))
    return entries

def fmt(etype, key, fields, order=("title","author","editor","year","journal","booktitle","publisher","volume","number","pages","doi","url","keywords","status","note")):
    keys = [k for k in order if k in fields] + [k for k in fields if k not in order]
    body = ",\n".join(f"  {k} = {{{fields[k]}}}" for k in keys)
    return f"@{etype}{{{key},\n{body}\n}}"

import sys, json, subprocess
sys.path.insert(0, "scripts/harvest")
from parse_pdf import sections, numbered_items, split_citation
def norm(t): return re.sub(r"[^a-z0-9]+", " ", t.lower()).strip()
pdf_titles = {}
for it in numbered_items(sections()["PUBLICATIONS"]):
    d = split_citation(it["text"])
    if "title" in d: pdf_titles[(d["year"], norm(d["title"]))] = d["title"].strip().rstrip(".")
def pdf_title_for(f):
    y = int(f.get("year", "0")[:4]) if f.get("year", "")[:4].isdigit() else 0; t = norm(re.sub(r"[{}]", "", f.get("title", "")))
    words = set(t.split()[:6])
    for (py, pt), title in pdf_titles.items():
        if py in (y, y - 1, y + 1) and words and len(words & set(pt.split())) >= min(4, len(words)):
            return title
    return None

out = []
for etype, key, f in parse(SRC.read_text()):
    f = {RENAME.get(k, k): v for k, v in f.items() if k not in DROP}
    if "year" in f: f["year"] = f["year"][:4]
    if key in AUTHOR_FIX: f["author"] = AUTHOR_FIX[key]
    f.update(FIX.get(key, {}))
    t = pdf_title_for(f)
    f["title"] = t if t else re.sub(r"[{}]", "", f["title"])
    if "booktitle" in f: f["booktitle"] = re.sub(r"[{}]", "", f["booktitle"])
    f["keywords"] = CATEGORY.get(key, TYPE_CATEGORY[etype])
    out.append(fmt(etype, key, f))

NEW = r"""
@article{behmerMotorEvokedPotentials2023,
  title = {Motor-evoked potentials for early individual elements of an action sequence during planning reflect parallel activation processes},
  author = {Behmer, Jr., Lawrence P. and Crump, M. J. C. and Jantzen, Kelly J.},
  year = {2023},
  journal = {Motor Control},
  note = {Published online ahead of print},
  keywords = {article}
}

@article{brosowskyContextualRecruitmentSelective2021,
  title = {Contextual recruitment of selective attention can be updated via changes in task relevance},
  author = {Brosowsky, Nicholaus P. and Crump, M. J. C.},
  year = {2021},
  journal = {Canadian Journal of Experimental Psychology},
  volume = {75},
  pages = {19-34},
  doi = {10.1037/cep0000221},
  keywords = {article}
}

@book{crumpInstancesCognition2021,
  title = {Instances of cognition: Questions, methods, findings, explanations, applications, and implications},
  author = {Crump, M. J. C.},
  year = {2021},
  publisher = {Open educational resource},
  url = {https://www.crumplab.com/cognition/textbook/},
  note = {Undergraduate textbook},
  keywords = {oer}
}

@book{crumpReproducibleStatistics2021,
  title = {Reproducible statistics for psychologists with R: Lab tutorials},
  author = {Crump, M. J. C.},
  year = {2021},
  publisher = {Open educational resource},
  url = {https://www.crumplab.com/rstatsforpsych},
  note = {Graduate textbook},
  keywords = {oer}
}

@article{vuorreSharingOrganizingResearch2021,
  title = {Sharing and organizing research products as R packages},
  author = {Vuorre, Matti and Crump, M. J. C.},
  year = {2021},
  journal = {Behavior Research Methods},
  volume = {53},
  pages = {792-802},
  doi = {10.3758/s13428-020-01436-x},
  keywords = {article}
}

@inproceedings{crumpControllingRetrievalGeneral2020,
  title = {Controlling the retrieval of general vs specific semantic knowledge in the instance theory of semantic memory},
  author = {Crump, M. J. C. and Jamieson, Randall K. and Johns, Brendan T. and Jones, Michael N.},
  editor = {Denison, S. and Mack, M. and Xu, Y. and Armstrong, B. C.},
  year = {2020},
  booktitle = {Proceedings of the 42nd Annual Conference of the Cognitive Science Society},
  publisher = {Cognitive Science Society},
  pages = {3261-3267},
  keywords = {proceedings}
}

@article{johnsProductionWithoutRules2020,
  title = {Production without rules: Using an instance memory model to exploit structure in natural language},
  author = {Johns, Brendan T. and Jamieson, Randall K. and Crump, M. J. C. and Jones, Michael N. and Mewhort, D. J. K.},
  year = {2020},
  journal = {Journal of Memory and Language},
  volume = {115},
  pages = {104165},
  doi = {10.1016/j.jml.2020.104165},
  keywords = {article}
}

@article{crumpPortfolioProsper2019,
  title = {Portfolio and prosper},
  author = {Crump, M. J. C.},
  year = {2019},
  journal = {Nature Human Behaviour},
  volume = {3},
  pages = {1008},
  doi = {10.1038/s41562-019-0733-0},
  keywords = {commentary, invited}
}

@book{crumpAnsweringQuestionsLabManual2018,
  title = {Answering questions with data: The lab manual},
  author = {Crump, M. J. C. and Krishnan, Anjali and Volz, Stephen and Chavarga, Alla and Suzuki, Jeffrey},
  year = {2018},
  publisher = {Open educational resource},
  url = {https://crumplab.github.io/statisticsLab/},
  note = {Undergraduate textbook},
  keywords = {oer}
}

@book{crumpAnsweringQuestionsData2018,
  title = {Answering questions with data: Introductory statistics for psychology students},
  author = {Crump, M. J. C. and Navarro, Danielle and Suzuki, Jeffrey},
  year = {2018},
  publisher = {Open educational resource},
  url = {https://crumplab.github.io/statistics/},
  note = {Undergraduate textbook},
  keywords = {oer}
}

@book{crumpProgrammingPsychologists2017,
  title = {Programming for psychologists: Data creation and analysis},
  author = {Crump, M. J. C.},
  year = {2017},
  publisher = {Open educational resource},
  url = {https://crumplab.github.io/programmingforpsych/},
  note = {Undergraduate textbook},
  keywords = {oer}
}

@book{crumpResearchMethodsPsychology2017,
  title = {Research methods in psychology},
  author = {Crump, M. J. C. and Price, Paul C. and Jhangiani, Rajiv and Chiang, I-Chant A. and Leighton, Dana C.},
  year = {2017},
  publisher = {Open educational resource},
  url = {https://crumplab.github.io/ResearchMethods/},
  note = {Undergraduate textbook},
  keywords = {oer}
}

@article{zumstegEffectCarpalTunnel2017,
  title = {The effect of carpal tunnel release on typing performance},
  author = {Zumsteg, Justin W. and Crump, M. J. C. and Logan, Gordon D. and Weikert, Douglas R. and Lee, Donald H.},
  year = {2017},
  journal = {The Journal of Hand Surgery},
  volume = {42},
  pages = {17-23},
  doi = {10.1016/j.jhsa.2016.10.005},
  keywords = {article}
}

@inproceedings{johnsCombinatorialPowerExperience2016,
  title = {The combinatorial power of experience},
  author = {Johns, Brendan T. and Jamieson, Randall K. and Crump, M. J. C. and Jones, Michael N. and Mewhort, D. J. K.},
  year = {2016},
  booktitle = {Proceedings of the 38th Annual Conference of the Cognitive Science Society},
  publisher = {Cognitive Science Society},
  keywords = {proceedings}
}

@misc{brosowskyTeachingUndergraduateStudents2021,
  title = {Teaching undergraduate students to read empirical articles: An evaluation and revision of the QALMRI method},
  author = {Brosowsky, Nicholaus P. and Parshina, Olga and Locicero, Alexandra and Crump, M. J. C.},
  year = {2021},
  publisher = {PsyArXiv},
  doi = {10.31234/osf.io/p39sc},
  status = {inprogress},
  keywords = {preprint}
}

@misc{piechNegativeContingencyIllusion2021,
  title = {The negative contingency illusion: A cognitive bias leading to misjudgement of protection},
  author = {Piech, Richard M. and Crump, M. J. C. and Zald, David H.},
  year = {2021},
  publisher = {Research Square},
  doi = {10.21203/rs.3.rs-671507/v1},
  status = {inprogress},
  keywords = {preprint}
}
"""
header = """% Publications. Source of truth for the publication list.
% Conventions:
%   keywords = {category[, invited]} where category is one of
%     article | review-article | chapter | proceedings | book | oer | commentary | book-review | preprint | other
%   status = {inpress|inprogress} for work not yet published (omit when published)
%   Author names: the CV owner is "Crump, M. J. C." so it can be bolded when rendering.
%   Mentee co-authors are starred automatically by matching students.yml; no markup needed here.
% Keep entries roughly newest first; rendering sorts by year anyway.

"""
Path("data/publications.bib").write_text(header + NEW.strip() + "\n\n" + "\n\n".join(out) + "\n")
print(len(out), "cleaned +", NEW.count("@"), "new")
