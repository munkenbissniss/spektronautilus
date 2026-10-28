#!/usr/bin/env python3
"""Builds dist/spektronautilus-linux.tar.gz from the current docs/ (run build.py first so the site is up to date)."""
import shutil, subprocess, sys, tarfile, tempfile
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent; OUT = ROOT / "dist"; NAME = "spektronautilus-linux"
subprocess.run([sys.executable, str(ROOT / "build.py")], check=True, stdout=subprocess.DEVNULL)
tmp = Path(tempfile.mkdtemp()) / NAME; tmp.mkdir()
shutil.copytree(ROOT / "docs", tmp / "docs", ignore=shutil.ignore_patterns("vendor", "__pycache__", "*.png~"))
for f in ("spektronautilus.py", "install.sh", "uninstall.sh", "README-LINUX.txt", "spektronautilus.svg"): shutil.copy2(ROOT / "linux" / f, tmp / f)
OUT.mkdir(exist_ok=True); dst = OUT / f"{NAME}.tar.gz"
with tarfile.open(dst, "w:gz") as t: t.add(tmp, arcname=NAME)
print("built", dst, round(dst.stat().st_size / 1e3), "kB")
