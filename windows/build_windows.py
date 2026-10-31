#!/usr/bin/env python3
"""Stages the Windows app in build/win/spektronautilus/ (run on Windows, normally by .github/workflows/windows.yml).

  python windows/build_windows.py --ffmpeg C:\\path\\to\\ffmpeg.exe     (--ffmpeg is optional: without it the app uses the browser engine)

Needs: Python 3.8+, `pip install pyinstaller`. Then Inno Setup turns the folder into Spektronautilus-Setup.exe:
  iscc /DAppVersion=1.0.0 windows\\spektronautilus.iss
"""
import argparse, shutil, subprocess, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent; OUT = ROOT / "build" / "win"; APP = OUT / "spektronautilus"
ap = argparse.ArgumentParser(); ap.add_argument("--ffmpeg", help="path to a Windows ffmpeg.exe to bundle"); ap.add_argument("--ffmpeg-license", help="licence text of that ffmpeg build")
a = ap.parse_args()
subprocess.run([sys.executable, str(ROOT / "build.py")], check=True, stdout=subprocess.DEVNULL)
shutil.rmtree(OUT, ignore_errors=True); OUT.mkdir(parents=True)
subprocess.run([sys.executable, "-m", "PyInstaller", "--noconfirm", "--onedir", "--console", "--name", "spektronautilus", "--icon", str(ROOT / "windows" / "spektronautilus.ico"),
                "--distpath", str(OUT), "--workpath", str(ROOT / "build" / "pyi"), "--specpath", str(ROOT / "build"), str(ROOT / "linux" / "spektronautilus.py")], check=True)
shutil.copytree(ROOT / "docs", APP / "docs", ignore=shutil.ignore_patterns("vendor", "__pycache__", "*.png~"))
if a.ffmpeg:
    (APP / "ffmpeg").mkdir(); shutil.copy2(a.ffmpeg, APP / "ffmpeg" / "ffmpeg.exe")
    if a.ffmpeg_license: shutil.copy2(a.ffmpeg_license, APP / "ffmpeg" / "LICENSE-ffmpeg.txt")
for f in ("LICENSE",): shutil.copy2(ROOT / f, APP / f)
shutil.copy2(ROOT / "windows" / "README-WINDOWS.txt", APP / "README-WINDOWS.txt")
shutil.copy2(ROOT / "windows" / "spektronautilus.ico", APP / "spektronautilus.ico")
print("staged", APP)
