#!/usr/bin/env python3
"""
scrape.py -- Firecrawl `scrape()` equivalent. Free, local, no API key.

Fetches a single URL and returns clean markdown (like formats: ["markdown"]),
falling back to a headless Playwright browser automatically when the static
HTML looks like a JS-rendered shell (thin content).

Usage:
  python3 scrape.py <url> [--formats markdown,html,links,metadata] [--full-page]
                     [--render] [--wait-for MS] [--selector CSS] [--timeout SEC]

  --full-page   include boilerplate (nav/footer) instead of only main content
  --render      force headless-browser rendering even if static HTML looks fine
  --wait-for    extra milliseconds to wait after page load when rendering (for
                lazy content / XHR-populated widgets)
  --selector    if given, also return innerText of matching elements (CSS selector)

Output: single JSON object on stdout, e.g.
  {"url": ..., "markdown": "...", "links": [...], "metadata": {...}, "rendered": false}

For structured ("JSON mode") extraction: do NOT try to do this in Python.
Firecrawl's json mode calls an LLM under the hood -- you (Claude) are that LLM
for free. Scrape the page to markdown, then extract the fields yourself
following the user's schema. This keeps the toolkit free and model-agnostic.
"""
import argparse
import sys

sys.path.insert(0, __file__.rsplit("/", 1)[0])
from _common import (
    out, eprint, fetch_html, html_to_markdown, extract_links,
    extract_metadata, looks_thin, robots_allowed, normalize_url, detect_blocking,
)


def render_with_playwright(url, wait_for=0, timeout=30000):
    from playwright.sync_api import sync_playwright

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True, args=["--no-sandbox"])
        try:
            page = browser.new_page(user_agent=(
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
            ))
            page.goto(url, timeout=timeout, wait_until="networkidle")
            if wait_for:
                page.wait_for_timeout(wait_for)
            html = page.content()
            final_url = page.url
            return html, final_url
        finally:
            browser.close()


def scrape(url, formats=None, only_main_content=True, render=False,
           wait_for=0, selector=None, timeout=20, respect_robots=True):
    formats = formats or ["markdown"]
    result = {"url": url, "rendered": False}

    if respect_robots and not robots_allowed(url):
        result["error"] = "Blocked by robots.txt for this user-agent."
        return result

    html = None
    final_url = url

    if not render:
        try:
            resp = fetch_html(url, timeout=timeout)
            html = resp.text
            final_url = resp.url
        except Exception as e:
            result["fetch_error"] = str(e)
            status = getattr(getattr(e, "response", None), "status_code", None)
            block = detect_blocking(getattr(getattr(e, "response", None), "text", None), status_code=status)
            if block:
                result["blocked_signal"] = block

    need_render = render or html is None
    if not need_render and "markdown" in formats:
        md_preview = html_to_markdown(html, url=final_url, only_main_content=only_main_content)
        if looks_thin(md_preview):
            need_render = True

    if need_render:
        try:
            html, final_url = render_with_playwright(url, wait_for=wait_for)
            result["rendered"] = True
        except Exception as e:
            result["render_error"] = str(e)
            if html is None:
                return result

    result["url"] = final_url

    block = detect_blocking(html, status_code=None)
    if block:
        result["blocked_signal"] = block
        eprint(f"[scrape] possible anti-bot/CAPTCHA wall on {final_url}: {block['reason']}")

    if "markdown" in formats:
        result["markdown"] = html_to_markdown(html, url=final_url, only_main_content=only_main_content)
    if "html" in formats:
        result["html"] = html
    if "links" in formats:
        result["links"] = extract_links(html, final_url)
    if "metadata" in formats:
        result["metadata"] = extract_metadata(html, final_url)

    if selector:
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(html, "lxml")
        result["selector_matches"] = [el.get_text(" ", strip=True) for el in soup.select(selector)]

    return result


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("url")
    ap.add_argument("--formats", default="markdown", help="comma-separated: markdown,html,links,metadata")
    ap.add_argument("--full-page", action="store_true", help="disable only-main-content filtering")
    ap.add_argument("--render", action="store_true", help="force Playwright rendering")
    ap.add_argument("--wait-for", type=int, default=0, help="ms to wait after render load")
    ap.add_argument("--selector", default=None)
    ap.add_argument("--timeout", type=int, default=20)
    ap.add_argument("--ignore-robots", action="store_true")
    args = ap.parse_args()

    formats = [f.strip() for f in args.formats.split(",") if f.strip()]
    result = scrape(
        args.url, formats=formats, only_main_content=not args.full_page,
        render=args.render, wait_for=args.wait_for, selector=args.selector,
        timeout=args.timeout, respect_robots=not args.ignore_robots,
    )
    out(result)


if __name__ == "__main__":
    main()
