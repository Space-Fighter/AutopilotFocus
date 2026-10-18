"""Render PNG previews of an Excalidraw board, one per frame plus the whole sheet.

Usage: python render.py BOARD.excalidraw [--out DIR] [--frames 1,3,5] [--serve]

Uses headless Microsoft Edge or Google Chrome and the official Excalidraw
renderer (loaded from unpkg, so it needs internet). --serve just starts the
viewer at http://127.0.0.1:<port>/ for interactive viewing and blocks.
"""
import argparse
import functools
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import threading
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer

HERE = os.path.dirname(os.path.abspath(__file__))
VIEWER = os.path.join(HERE, "..", "assets", "viewer.html")

BROWSERS = [
    r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
    r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
    r"C:\Program Files\Google\Chrome\Application\chrome.exe",
    "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
    "/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge",
]


def find_browser():
    for p in BROWSERS:
        if os.path.exists(p):
            return p
    for name in ("msedge", "google-chrome", "chromium", "chromium-browser", "chrome"):
        p = shutil.which(name)
        if p:
            return p
    sys.exit("No Edge/Chrome found for headless rendering.")


def slug(s):
    return re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")[:40]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("board")
    ap.add_argument("--out", default=None)
    ap.add_argument("--frames", default=None, help="comma list of frame numbers")
    ap.add_argument("--serve", action="store_true")
    ap.add_argument("--width", type=int, default=1800)
    a = ap.parse_args()

    board = os.path.abspath(a.board)
    out = os.path.abspath(a.out or os.path.join(os.path.dirname(board), "previews"))
    site = tempfile.mkdtemp(prefix="excal-site-")
    shutil.copy(VIEWER, os.path.join(site, "index.html"))
    shutil.copy(board, os.path.join(site, "board.excalidraw"))

    class Quiet(SimpleHTTPRequestHandler):
        def log_message(self, *args):
            pass

    handler = functools.partial(Quiet, directory=site)
    srv = ThreadingHTTPServer(("127.0.0.1", 0), handler)
    port = srv.server_address[1]
    base = f"http://127.0.0.1:{port}/index.html"

    if a.serve:
        print(f"viewer: {base}  (Ctrl+C to stop; edits here are NOT saved to the file)")
        srv.serve_forever()
        return

    threading.Thread(target=srv.serve_forever, daemon=True).start()
    with open(board, encoding="utf-8") as f:
        frames = [e for e in json.load(f)["elements"] if e.get("type") == "frame" and not e.get("isDeleted")]
    wanted = set(a.frames.split(",")) if a.frames else None

    jobs = [] if wanted else [("00-sheet", base, a.width, 1100)]
    for fr in frames:
        num = (fr.get("name") or "").split(" ")[0]
        if wanted and num not in wanted:
            continue
        h = int(min(max(a.width * fr["height"] / fr["width"] + 140, 700), 2600))
        jobs.append((f"{int(num):02d}-{slug(fr['name'].split('·', 1)[-1])}", f"{base}?frame={num}&ui=0", a.width, h))

    os.makedirs(out, exist_ok=True)
    browser = find_browser()
    profile = tempfile.mkdtemp(prefix="excal-profile-")
    for name, url, w, h in jobs:
        png = os.path.join(out, name + ".png")
        subprocess.run([browser, "--headless=new", "--disable-gpu", "--hide-scrollbars",
                        f"--user-data-dir={profile}", "--virtual-time-budget=15000",
                        f"--window-size={w},{h}", f"--screenshot={png}", url],
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=120)
        print(("ok   " if os.path.exists(png) else "FAIL ") + png)
    srv.shutdown()
    shutil.rmtree(site, ignore_errors=True)
    shutil.rmtree(profile, ignore_errors=True)


if __name__ == "__main__":
    main()
