#!/usr/bin/env python3
"""Post-render: copy cv.json into the output directory."""
import shutil
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
out = ROOT / "_output"; out.mkdir(exist_ok=True)
src = ROOT / "_generated" / "cv.json"
if src.exists():
    shutil.copy(src, out / "cv.json")
    print(f"postrender: copied cv.json to {out / 'cv.json'}")
