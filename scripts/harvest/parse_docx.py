"""Parse the pipe-table extraction of Crump_CV_2024_BC.docx into rows per section."""
import re, json, sys
from pathlib import Path
SRC = Path("CV Examples/extracted/Crump_CV_2024_BC.txt")

def blocks():
    """Yield (heading_context, rows) where rows are lists of cells; headings are non-table lines."""
    ctx, rows, out = [], [], []
    for l in SRC.read_text().splitlines():
        if l.startswith("| "):
            rows.append([c.strip() for c in l.strip("| ").split(" | ")])
        else:
            if rows: out.append((list(ctx), rows)); rows = []
            if l.strip(): ctx = (ctx + [l.strip()])[-3:]
    if rows: out.append((list(ctx), rows))
    return out

if __name__ == "__main__":
    for ctx, rows in blocks():
        print("###", " / ".join(ctx[-2:]))
        for r in rows: print("   ", json.dumps(r, ensure_ascii=False))
