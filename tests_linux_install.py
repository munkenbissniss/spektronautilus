"""Tests the Linux package: unpack, install into a fake home, check the menu entry, start through the launcher with a fake browser, uninstall."""
import os, subprocess, sys, tarfile, tempfile, time, urllib.request
from pathlib import Path
ROOT = Path(__file__).resolve().parent; T = Path(tempfile.mkdtemp(prefix="spkinst_")); bad = []
def check(c, m):
    print(("ok   " if c else "FAIL ") + m, flush=True)
    if not c: bad.append(m)
subprocess.run([sys.executable, str(ROOT / "linux/build_linux.py")], check=True, stdout=subprocess.DEVNULL)
with tarfile.open(ROOT / "dist/spektronautilus-linux.tar.gz") as t: t.extractall(T / "x")
pk = T / "x/spektronautilus-linux"; home = T / "home"; home.mkdir()
env = {**os.environ, "HOME": str(home), "XDG_DATA_HOME": "", "XDG_CONFIG_HOME": ""}; env.pop("XDG_DATA_HOME"); env.pop("XDG_CONFIG_HOME")
check(not (pk / "docs/tools/app/vendor").exists(), "the package has no wasm vendor folder")
r = subprocess.run(["sh", str(pk / "install.sh")], env=env, capture_output=True, text=True); check(r.returncode == 0, "install.sh runs: " + r.stdout.strip().splitlines()[0])
d = home / ".local/share/applications/spektronautilus.desktop"; check(d.exists() and "Exec=python3" in d.read_text(), "menu entry written")
if subprocess.run(["which", "desktop-file-validate"], capture_output=True).returncode == 0:
    v = subprocess.run(["desktop-file-validate", str(d)], capture_output=True, text=True); check(v.returncode == 0, "desktop file is valid " + v.stdout.strip())
check((home / ".local/bin/spektronautilus").is_symlink(), "command 'spektronautilus' installed")
# fake browser that records its arguments and stays open for 3 seconds, like a real window would
fake = T / "fakebrowser.sh"; fake.write_text(f'#!/bin/sh\necho "$@" > {T}/args.txt\nsleep 6\n'); fake.chmod(0o755)
env2 = {**env, "SPEKTRO_BROWSER": str(fake)}
p = subprocess.Popen([str(home / ".local/bin/spektronautilus"), "--port", "8792", "--path", "live-dj/"], env=env2, stdout=subprocess.PIPE, text=True)
time.sleep(2)
try:
    page = urllib.request.urlopen("http://127.0.0.1:8792/live-dj/", timeout=5).read().decode(); check("Video DJ" in page, "launcher serves the installed site")
    args = (T / "args.txt").read_text(); check("--app=http://127.0.0.1:8792/live-dj/" in args and "--autoplay-policy=no-user-gesture-required" in args and "--disable-renderer-backgrounding" in args and "--user-data-dir=" + str(home / ".config/spektronautilus/browser") in args, "browser opened as an app window with the live-visual flags")
    p.wait(timeout=15); check(p.returncode == 0, "the program ends when the window is closed")
finally:
    if p.poll() is None: p.kill()
check(subprocess.run(["sh", str(home / ".local/share/spektronautilus/uninstall.sh")], env=env, capture_output=True).returncode == 0 and not d.exists() and not (home / ".local/share/spektronautilus").exists(), "uninstall removes everything")
print("\nALL OK" if not bad else "\nFAILED: " + "; ".join(bad)); raise SystemExit(1 if bad else 0)
