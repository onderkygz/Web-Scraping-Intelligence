"""
Session registry for interact.py's persistent headless-browser sessions.

Each session = one detached headless Chromium process, launched with a fixed
remote-debugging port, that stays alive between separate script invocations.
interact_start.py launches it; interact.py reconnects to it via CDP
(playwright's connect_over_cdp) for each subsequent action; interact_stop.py
kills it. This mirrors Firecrawl's scrape -> interact -> stop_interaction flow
without needing a long-running server process of our own.
"""
import json
import os
import socket
import time

SESSIONS_DIR = os.path.expanduser("~/.webscout_sessions")


def _ensure_dir():
    os.makedirs(SESSIONS_DIR, exist_ok=True)


def free_port():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(("127.0.0.1", 0))
    port = s.getsockname()[1]
    s.close()
    return port


def session_path(session_id):
    return os.path.join(SESSIONS_DIR, f"{session_id}.json")


def save_session(session_id, data):
    _ensure_dir()
    with open(session_path(session_id), "w") as f:
        json.dump(data, f)


def load_session(session_id):
    p = session_path(session_id)
    if not os.path.exists(p):
        return None
    with open(p) as f:
        return json.load(f)


def delete_session(session_id):
    p = session_path(session_id)
    if os.path.exists(p):
        os.remove(p)


def list_sessions():
    _ensure_dir()
    out = []
    for fn in os.listdir(SESSIONS_DIR):
        if fn.endswith(".json"):
            out.append(fn[:-5])
    return out


def wait_for_port(port, timeout=15):
    deadline = time.time() + timeout
    while time.time() < deadline:
        try:
            with socket.create_connection(("127.0.0.1", port), timeout=1):
                return True
        except OSError:
            time.sleep(0.2)
    return False


def pid_alive(pid):
    try:
        os.kill(pid, 0)
        return True
    except (OSError, ProcessLookupError):
        return False
