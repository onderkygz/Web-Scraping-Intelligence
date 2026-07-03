#!/usr/bin/env python3
"""
interact_stop.py -- stop an interact session (kills the detached headless
browser and cleans up). Always call this when done with a session.

Usage:
  python3 interact_stop.py <scrape_id>
  python3 interact_stop.py --all              # stop every tracked session
  python3 interact_stop.py --sweep-orphans    # also kill any webscout_session_*
                                               # chrome processes even if their
                                               # registry entry was lost (belt
                                               # and suspenders cleanup)
"""
import argparse
import os
import shutil
import signal
import subprocess
import sys

sys.path.insert(0, __file__.rsplit("/", 1)[0])
from _common import out, eprint
from _sessions import load_session, delete_session, list_sessions, pid_alive


def stop_one(session_id):
    session = load_session(session_id)
    if not session:
        return {"scrape_id": session_id, "status": "not_found"}
    pid = session["pid"]
    if pid_alive(pid):
        try:
            os.kill(pid, signal.SIGTERM)
        except ProcessLookupError:
            pass
    user_data_dir = session.get("user_data_dir")
    if user_data_dir and os.path.isdir(user_data_dir):
        shutil.rmtree(user_data_dir, ignore_errors=True)
    delete_session(session_id)
    return {"scrape_id": session_id, "status": "stopped"}


def sweep_orphans():
    """Kill any leftover webscout_session_* chrome processes whose registry
    entry is gone (e.g. this script crashed, or the shell/session died)."""
    killed = []
    try:
        ps = subprocess.run(["pgrep", "-f", "webscout_session_"], capture_output=True, text=True)
        for pid_str in ps.stdout.split():
            try:
                pid = int(pid_str)
                os.kill(pid, signal.SIGKILL)
                killed.append(pid)
            except (ValueError, ProcessLookupError, PermissionError):
                pass
    except FileNotFoundError:
        pass  # pgrep not available; skip silently
    import glob
    for d in glob.glob("/tmp/webscout_session_*"):
        shutil.rmtree(d, ignore_errors=True)
    return killed


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("scrape_id", nargs="?")
    ap.add_argument("--all", action="store_true")
    ap.add_argument("--sweep-orphans", action="store_true")
    args = ap.parse_args()

    if args.sweep_orphans:
        killed = sweep_orphans()
        out({"orphans_killed": killed})
        return

    if args.all:
        results = [stop_one(sid) for sid in list_sessions()]
        out(results)
        return

    if not args.scrape_id:
        out({"error": "provide a scrape_id, --all, or --sweep-orphans"})
        sys.exit(1)

    out(stop_one(args.scrape_id))


if __name__ == "__main__":
    main()
