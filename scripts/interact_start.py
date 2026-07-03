#!/usr/bin/env python3
"""
interact_start.py -- begin a Firecrawl-style "scrape then interact" session.
Free, local, no API key.

Launches a detached headless Chromium (stays alive across separate script
calls), navigates to the URL, and returns a scrape_id you pass to interact.py
for follow-up actions (click, write, scroll, extract, screenshot, run JS),
and finally to interact_stop.py to tear it down.

Usage:
  python3 interact_start.py <url> [--ttl-minutes 15]

Output: {"scrape_id": "...", "url": ..., "markdown": "..." }
"""
import argparse
import subprocess
import sys
import time
import uuid

from playwright.sync_api import sync_playwright

sys.path.insert(0, __file__.rsplit("/", 1)[0])
from _common import out, eprint, html_to_markdown
from _sessions import free_port, save_session, wait_for_port

CHROMIUM_PATH = None


def get_chromium_path():
    global CHROMIUM_PATH
    if CHROMIUM_PATH:
        return CHROMIUM_PATH
    with sync_playwright() as p:
        CHROMIUM_PATH = p.chromium.executable_path
    return CHROMIUM_PATH


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("url")
    ap.add_argument("--ttl-minutes", type=int, default=15,
                     help="informational only -- remember to call interact_stop.py yourself")
    args = ap.parse_args()

    session_id = uuid.uuid4().hex[:12]
    port = free_port()
    user_data_dir = f"/tmp/webscout_session_{session_id}"

    chromium = get_chromium_path()
    cmd = [
        chromium,
        f"--remote-debugging-port={port}",
        f"--user-data-dir={user_data_dir}",
        "--headless=new",
        "--no-sandbox",
        "--disable-gpu",
        "--disable-dev-shm-usage",
    ]
    proc = subprocess.Popen(
        cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
        start_new_session=True,
    )

    if not wait_for_port(port, timeout=15):
        proc.kill()
        out({"error": "browser failed to start"})
        sys.exit(1)

    save_session(session_id, {
        "port": port, "pid": proc.pid, "user_data_dir": user_data_dir,
        "started_at": time.time(), "last_url": args.url,
    })

    # Now connect and navigate to the target URL.
    with sync_playwright() as p:
        browser = p.chromium.connect_over_cdp(f"http://127.0.0.1:{port}")
        try:
            ctx = browser.contexts[0] if browser.contexts else browser.new_context()
            page = ctx.new_page()
            page.goto(args.url, timeout=30000, wait_until="networkidle")
            html = page.content()
            final_url = page.url
        finally:
            browser.close()  # closes the CDP connection, NOT the detached browser process

    result = {
        "scrape_id": session_id,
        "url": final_url,
        "markdown": html_to_markdown(html, url=final_url),
    }
    out(result)
    eprint(f"[interact_start] session {session_id} running on port {port} (pid {proc.pid}). "
           f"Remember to call interact_stop.py {session_id} when done.")


if __name__ == "__main__":
    main()
