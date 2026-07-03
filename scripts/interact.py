#!/usr/bin/env python3
"""
interact.py -- perform one action against a session started by interact_start.py.
Free, local, no API key. Mirrors Firecrawl's Interact actions: click, write,
press, scroll, wait, screenshot, scrape (re-extract), goto, execute_js.

Usage examples:
  python3 interact.py <scrape_id> click --selector "button.load-more"
  python3 interact.py <scrape_id> write --selector "input[name=q]" --text "firecrawl"
  python3 interact.py <scrape_id> press --key Enter
  python3 interact.py <scrape_id> scroll --direction down
  python3 interact.py <scrape_id> wait --ms 1000
  python3 interact.py <scrape_id> wait --selector ".results" --timeout-ms 10000
  python3 interact.py <scrape_id> goto --url "https://example.com/page2"
  python3 interact.py <scrape_id> scrape                     # re-extract markdown
  python3 interact.py <scrape_id> extract --selector ".price"  # innerText of matches
  python3 interact.py <scrape_id> screenshot --out /tmp/shot.png [--full-page]
  python3 interact.py <scrape_id> execute_js --script "document.title"

Every action (except screenshot) returns the resulting page state so you can
see the effect immediately: {"url":..., "markdown": "...", "action": "click"}
"""
import argparse
import sys

from playwright.sync_api import sync_playwright

sys.path.insert(0, __file__.rsplit("/", 1)[0])
from _common import out, eprint, html_to_markdown, detect_blocking
from _sessions import load_session, pid_alive


BLANK_URLS = {"about:blank", "chrome://new-tab-page/", "chrome://newtab/", ""}


def get_page(browser):
    """Pick the real content page, not an auto-opened blank/new-tab page.
    Chromium sometimes spawns a fresh blank tab when a new CDP client
    connects, so we can't just take contexts[0].pages[-1] blindly."""
    ctx = browser.contexts[0]
    pages = ctx.pages
    if not pages:
        return ctx.new_page()
    real_pages = [pg for pg in pages if pg.url not in BLANK_URLS]
    if real_pages:
        return real_pages[-1]
    return pages[-1]


def page_state(page, action_name, extra=None):
    html = page.content()
    state = {
        "action": action_name,
        "url": page.url,
        "markdown": html_to_markdown(html, url=page.url),
    }
    block = detect_blocking(html, status_code=None)
    if block:
        state["blocked_signal"] = block
    if extra:
        state.update(extra)
    return state


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("scrape_id")
    ap.add_argument("action", choices=[
        "click", "write", "press", "scroll", "wait", "goto",
        "scrape", "extract", "screenshot", "execute_js",
    ])
    ap.add_argument("--selector", default=None)
    ap.add_argument("--text", default=None)
    ap.add_argument("--key", default=None)
    ap.add_argument("--direction", default="down", choices=["up", "down"])
    ap.add_argument("--ms", type=int, default=1000)
    ap.add_argument("--timeout-ms", type=int, default=15000)
    ap.add_argument("--url", default=None)
    ap.add_argument("--script", default=None)
    ap.add_argument("--out", default="/tmp/webscout_screenshot.png")
    ap.add_argument("--full-page", action="store_true")
    ap.add_argument("--click-all", action="store_true")
    args = ap.parse_args()

    session = load_session(args.scrape_id)
    if not session:
        out({"error": f"no such session '{args.scrape_id}'. Start one with interact_start.py."})
        sys.exit(1)
    if not pid_alive(session["pid"]):
        out({"error": f"session '{args.scrape_id}' process is no longer running."})
        sys.exit(1)

    port = session["port"]
    with sync_playwright() as p:
        browser = p.chromium.connect_over_cdp(f"http://127.0.0.1:{port}")
        try:
            page = get_page(browser)

            if args.action == "click":
                if not args.selector:
                    out({"error": "click requires --selector"})
                    sys.exit(1)
                if args.click_all:
                    els = page.query_selector_all(args.selector)
                    for el in els:
                        el.click()
                else:
                    page.click(args.selector, timeout=args.timeout_ms)
                page.wait_for_load_state("networkidle", timeout=args.timeout_ms)
                result = page_state(page, "click")

            elif args.action == "write":
                if not args.selector or args.text is None:
                    out({"error": "write requires --selector and --text"})
                    sys.exit(1)
                page.fill(args.selector, args.text, timeout=args.timeout_ms)
                result = page_state(page, "write")

            elif args.action == "press":
                if not args.key:
                    out({"error": "press requires --key (e.g. Enter, Tab, Escape)"})
                    sys.exit(1)
                page.keyboard.press(args.key)
                page.wait_for_load_state("networkidle", timeout=args.timeout_ms)
                result = page_state(page, "press")

            elif args.action == "scroll":
                if args.selector:
                    page.eval_on_selector(
                        args.selector,
                        "(el, dir) => el.scrollBy(0, dir === 'down' ? el.clientHeight : -el.clientHeight)",
                        args.direction,
                    )
                else:
                    delta = "window.innerHeight" if args.direction == "down" else "-window.innerHeight"
                    page.evaluate(f"window.scrollBy(0, {delta})")
                page.wait_for_timeout(500)
                result = page_state(page, "scroll")

            elif args.action == "wait":
                if args.selector:
                    page.wait_for_selector(args.selector, timeout=args.timeout_ms)
                else:
                    page.wait_for_timeout(args.ms)
                result = page_state(page, "wait")

            elif args.action == "goto":
                if not args.url:
                    out({"error": "goto requires --url"})
                    sys.exit(1)
                page.goto(args.url, timeout=30000, wait_until="networkidle")
                result = page_state(page, "goto")

            elif args.action == "scrape":
                result = page_state(page, "scrape")

            elif args.action == "extract":
                if not args.selector:
                    out({"error": "extract requires --selector"})
                    sys.exit(1)
                els = page.query_selector_all(args.selector)
                texts = [el.inner_text() for el in els]
                result = page_state(page, "extract", {"matches": texts, "count": len(texts)})

            elif args.action == "screenshot":
                page.screenshot(path=args.out, full_page=args.full_page)
                result = {"action": "screenshot", "url": page.url, "saved_to": args.out}

            elif args.action == "execute_js":
                if not args.script:
                    out({"error": "execute_js requires --script"})
                    sys.exit(1)
                js_result = page.evaluate(args.script)
                result = page_state(page, "execute_js", {"return_value": js_result})

            out(result)
        finally:
            browser.close()  # disconnect only; the detached session stays alive


if __name__ == "__main__":
    main()
