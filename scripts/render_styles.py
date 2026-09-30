#!/usr/bin/env python3
"""Render cv.qmd with every Typst style in _extensions/ and write page-1 previews to styles/previews/.

Usage: python3 scripts/render_styles.py [--pages N]
Outputs: _output/cv-<style>.pdf and styles/previews/<style>-p<n>.png
"""
import subprocess, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PAGES = int(sys.argv[sys.argv.index("--pages") + 1]) if "--pages" in sys.argv else 1
styles = sorted(p.name.removeprefix("cv-") for p in (ROOT / "_extensions").glob("cv-*"))
for style in styles:
    fmt = f"cv-{style}-typst"
    print(f"== {style}")
    subprocess.run(["quarto", "render", "cv.qmd", "--to", fmt, "--output", f"cv-{style}.pdf"], cwd=ROOT, check=True)
try:
    import pymupdf
except ImportError:
    print("pymupdf not installed; skipping previews (pip install pymupdf)"); sys.exit(0)
out = ROOT / "styles" / "previews"; out.mkdir(parents=True, exist_ok=True)
for style in styles:
    pdf = ROOT / "_output" / f"cv-{style}.pdf"
    doc = pymupdf.open(pdf)
    for i in range(min(PAGES, doc.page_count)):
        doc[i].get_pixmap(dpi=80).save(out / f"{style}-p{i + 1}.png")
    print(f"{style}: {doc.page_count} pages, previews written")
