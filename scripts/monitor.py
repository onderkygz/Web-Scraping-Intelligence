#!/usr/bin/env python3
"""
monitor.py -- Firecrawl's cronjob-based "monitor" equivalent. Free, local,
no API key, no scheduler daemon of its own.

This script does ONE check-and-diff per invocation: scrape a URL, compare it
to the last stored snapshot, report what changed. It has no built-in
scheduler (Claude/most agent runtimes don't keep a process running between
turns), so *you* provide the "every N minutes" part with a real OS
scheduler that calls this script repeatedly. See the cron/launchd examples
below and in SKILL.md.

Usage:
  # first run for a label just establishes the baseline
  python3 monitor.py check "https://example.com/pricing" --label pricing

  # subsequent runs report whether anything changed since last check
  python3 monitor.py check "https://example.com/pricing" --label pricing

  # narrow to a specific part of the page (less noisy than whole-page diff)
  python3 monitor.py check "https://example.com/pricing" --label pricing --selector ".price"

  # list everything being tracked
  python3 monitor.py list

  # drop a tracked label (stop monitoring it)
  python3 monitor.py forget --label pricing

  # print ready-to-use cron / launchd snippets for real scheduling
  python3 monitor.py schedule-help --label pricing --url "https://example.com/pricing" --every 30m

Output of `check`: {"label":..., "url":..., "changed": bool, "first_check": bool,
                     "diff": "...", "old_excerpt":..., "new_excerpt":...}
"""
import argparse
import difflib
import hashlib
import json
import os
import re
import sys
import time

sys.path.insert(0, __file__.rsplit("/", 1)[0])
from _common import out, eprint, fetch_html, html_to_markdown, detect_blocking
from scrape import render_with_playwright

STORE_DIR = os.path.expanduser("~/.webscout_monitor")


def _slug(label):
    return re.sub(r"[^a-zA-Z0-9_-]+", "_", label).strip("_") or "unnamed"


def _store_path(label):
    os.makedirs(STORE_DIR, exist_ok=True)
    return os.path.join(STORE_DIR, f"{_slug(label)}.json")


def _content_for(url, selector=None, render=False, timeout=20):
    if render:
        html, final_url = render_with_playwright(url)
    else:
        resp = fetch_html(url, timeout=timeout)
        html, final_url = resp.text, resp.url

    block = detect_blocking(html, status_code=None)

    if selector:
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(html, "lxml")
        matches = [el.get_text(" ", strip=True) for el in soup.select(selector)]
        content = "\n".join(matches)
    else:
        content = html_to_markdown(html, url=final_url)

    return content, final_url, block


def check(url, label, selector=None, render=False, timeout=20):
    content, final_url, block = _content_for(url, selector=selector, render=render, timeout=timeout)
    new_hash = hashlib.sha256(content.encode("utf-8")).hexdigest()

    path = _store_path(label)
    prev = None
    if os.path.exists(path):
        with open(path) as f:
            prev = json.load(f)

    result = {
        "label": label, "url": final_url, "checked_at": time.time(),
        "first_check": prev is None,
    }
    if block:
        result["blocked_signal"] = block

    if prev is None:
        result["changed"] = False
        result["note"] = "baseline established -- nothing to compare against yet"
    else:
        result["changed"] = prev["hash"] != new_hash
        if result["changed"]:
            old_lines = prev["content"].splitlines()
            new_lines = content.splitlines()
            diff = list(difflib.unified_diff(
                old_lines, new_lines, lineterm="",
                fromfile=f"{label} (previous, {time.ctime(prev['checked_at'])})",
                tofile=f"{label} (now)",
                n=1,
            ))
            # cap diff size so a full page rewrite doesn't flood the output
            result["diff"] = "\n".join(diff[:200])
            result["diff_truncated"] = len(diff) > 200

    with open(path, "w") as f:
        json.dump({
            "label": label, "url": final_url, "hash": new_hash,
            "content": content, "checked_at": result["checked_at"],
        }, f)

    return result


def list_monitors():
    if not os.path.isdir(STORE_DIR):
        return []
    items = []
    for fn in sorted(os.listdir(STORE_DIR)):
        if not fn.endswith(".json"):
            continue
        with open(os.path.join(STORE_DIR, fn)) as f:
            d = json.load(f)
        items.append({
            "label": d["label"], "url": d["url"],
            "last_checked": time.ctime(d["checked_at"]),
            "content_hash": d["hash"][:12],
        })
    return items


def forget(label):
    path = _store_path(label)
    if os.path.exists(path):
        os.remove(path)
        return {"label": label, "status": "forgotten"}
    return {"label": label, "status": "not_found"}


def schedule_help(label, url, every):
    script_path = os.path.abspath(__file__)
    python_bin = sys.executable
    cmd = f'{python_bin} {script_path} check "{url}" --label "{label}"'

    cron_map = {"m": "*/{n} * * * *", "h": "0 */{n} * * *", "d": "0 0 */{n} * *"}
    m = re.match(r"(\d+)([mhd])", every)
    cron_expr = None
    if m:
        n, unit = m.groups()
        cron_expr = cron_map.get(unit, "*/{n} * * * *").format(n=n)

    text = f"""# --- cron (Linux/macOS) ---
# crontab -e ile ekle:
{cron_expr or '*/30 * * * *'} {cmd} >> {os.path.expanduser('~/.webscout_monitor/log.txt')} 2>&1

# --- launchd (macOS, cron'dan daha güvenilir) ---
# ~/Library/LaunchAgents/com.webscout.monitor.{_slug(label)}.plist dosyası oluştur:
cat > ~/Library/LaunchAgents/com.webscout.monitor.{_slug(label)}.plist << 'EOF'
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0"><dict>
  <key>Label</key><string>com.webscout.monitor.{_slug(label)}</string>
  <key>ProgramArguments</key>
  <array><string>{python_bin}</string><string>{script_path}</string>
    <string>check</string><string>{url}</string>
    <string>--label</string><string>{label}</string></array>
  <key>StartInterval</key><integer>{int(m.group(1)) * {'m': 60, 'h': 3600, 'd': 86400}[m.group(2)] if m else 1800}</integer>
  <key>StandardOutPath</key><string>{os.path.expanduser('~/.webscout_monitor/log.txt')}</string>
  <key>StandardErrorPath</key><string>{os.path.expanduser('~/.webscout_monitor/log.txt')}</string>
</dict></plist>
EOF
launchctl load ~/Library/LaunchAgents/com.webscout.monitor.{_slug(label)}.plist

# Sonra her "check" çalıştığında sonucu (JSON) log.txt'ye yaz.
# "changed": true olduğunda kendine bildirim göndermek istersen,
# bu script'i bir wrapper'a sar: check() true dönerse `terminal-notifier`,
# `osascript -e 'display notification'`, ya da bir webhook POST'u tetikle.
"""
    return text


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)

    p_check = sub.add_parser("check")
    p_check.add_argument("url")
    p_check.add_argument("--label", required=True)
    p_check.add_argument("--selector", default=None)
    p_check.add_argument("--render", action="store_true")
    p_check.add_argument("--timeout", type=int, default=20)

    sub.add_parser("list")

    p_forget = sub.add_parser("forget")
    p_forget.add_argument("--label", required=True)

    p_sched = sub.add_parser("schedule-help")
    p_sched.add_argument("--label", required=True)
    p_sched.add_argument("--url", required=True)
    p_sched.add_argument("--every", default="30m", help="e.g. 30m, 2h, 1d")

    args = ap.parse_args()

    if args.cmd == "check":
        out(check(args.url, args.label, selector=args.selector,
                  render=args.render, timeout=args.timeout))
    elif args.cmd == "list":
        out(list_monitors())
    elif args.cmd == "forget":
        out(forget(args.label))
    elif args.cmd == "schedule-help":
        print(schedule_help(args.label, args.url, args.every))


if __name__ == "__main__":
    main()
