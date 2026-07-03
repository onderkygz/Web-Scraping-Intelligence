#!/usr/bin/env python3
"""
crawl.py -- Firecrawl `crawl()` equivalent: recursively scrape a whole site
(or a subsection of it). Free, local, no API key.

Uses map.py's URL discovery when available (fast), then does a BFS crawl,
scraping each page to markdown concurrently and following in-domain links up
to --max-depth, stopping at --limit pages.

Usage:
  python3 crawl.py <url> [--limit 20] [--max-depth 2] [--include-subdomains]
                    [--include "regex"] [--exclude "regex"] [--concurrency 5]
                    [--formats markdown,links] [--delay 0.3]

Output: JSON list on stdout, one object per page:
  [{"url": ..., "markdown": "...", "depth": 0}, ...]

NOTE: this hits real sites with real requests. Always keep --limit reasonable
and --delay >= 0.2s to be a polite citizen. robots.txt is respected by default
(see scrape.py); pass --ignore-robots only if you have a legitimate reason to
(e.g. you own the site and its robots.txt is misconfigured).
"""
import argparse
import re
import sys
import time
import urllib.parse as up
from concurrent.futures import ThreadPoolExecutor, as_completed

sys.path.insert(0, __file__.rsplit("/", 1)[0])
from _common import (
    out, eprint, fetch_html, html_to_markdown, extract_links, extract_metadata,
    normalize_url, same_domain, robots_allowed, looks_thin, detect_blocking,
)
from scrape import render_with_playwright


def scrape_one(url, formats, only_main_content, respect_robots, render_if_thin, timeout):
    page = {"url": url}
    if respect_robots and not robots_allowed(url):
        page["error"] = "blocked_by_robots"
        return page, []
    try:
        resp = fetch_html(url, timeout=timeout)
        html = resp.text
        final_url = resp.url
    except Exception as e:
        page["error"] = str(e)
        return page, []

    block = detect_blocking(html, status_code=None)
    if block:
        page["blocked_signal"] = block

    md = html_to_markdown(html, url=final_url, only_main_content=only_main_content) if "markdown" in formats else None
    if render_if_thin and "markdown" in formats and looks_thin(md):
        try:
            html, final_url = render_with_playwright(url)
            md = html_to_markdown(html, url=final_url, only_main_content=only_main_content)
            page["rendered"] = True
        except Exception:
            pass

    page["url"] = final_url
    if "markdown" in formats:
        page["markdown"] = md
    if "html" in formats:
        page["html"] = html
    if "metadata" in formats:
        page["metadata"] = extract_metadata(html, final_url)

    links = extract_links(html, final_url)
    return page, links


def crawl(start_url, limit=20, max_depth=2, include_subdomains=False,
          include_re=None, exclude_re=None, formats=None, concurrency=5,
          delay=0.3, respect_robots=True, render_if_thin=True, timeout=20):
    formats = formats or ["markdown"]
    root_netloc = up.urlsplit(start_url).netloc
    inc = re.compile(include_re) if include_re else None
    exc = re.compile(exclude_re) if exclude_re else None

    seen = {normalize_url(start_url)}
    frontier = [(normalize_url(start_url), 0)]
    results = []

    with ThreadPoolExecutor(max_workers=concurrency) as pool:
        while frontier and len(results) < limit:
            batch = frontier[:concurrency]
            frontier = frontier[concurrency:]

            futures = {
                pool.submit(scrape_one, u, formats, True, respect_robots, render_if_thin, timeout): (u, d)
                for u, d in batch
            }
            for fut in as_completed(futures):
                u, depth = futures[fut]
                try:
                    page, links = fut.result()
                except Exception as e:
                    page, links = {"url": u, "error": str(e)}, []
                page["depth"] = depth
                results.append(page)
                eprint(f"[crawl] ({len(results)}/{limit}) depth={depth} {u}")

                if depth < max_depth:
                    for link in links:
                        link = normalize_url(link)
                        if link in seen:
                            continue
                        if not same_domain(link, root_netloc, include_subdomains):
                            continue
                        if inc and not inc.search(link):
                            continue
                        if exc and exc.search(link):
                            continue
                        seen.add(link)
                        frontier.append((link, depth + 1))
            time.sleep(delay)
            if len(results) >= limit:
                break

    return results[:limit]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("url")
    ap.add_argument("--limit", type=int, default=20)
    ap.add_argument("--max-depth", type=int, default=2)
    ap.add_argument("--include-subdomains", action="store_true")
    ap.add_argument("--include", default=None, help="regex; only follow links matching this")
    ap.add_argument("--exclude", default=None, help="regex; skip links matching this")
    ap.add_argument("--formats", default="markdown")
    ap.add_argument("--concurrency", type=int, default=5)
    ap.add_argument("--delay", type=float, default=0.3)
    ap.add_argument("--timeout", type=int, default=20)
    ap.add_argument("--ignore-robots", action="store_true")
    ap.add_argument("--no-render-fallback", action="store_true")
    args = ap.parse_args()

    formats = [f.strip() for f in args.formats.split(",") if f.strip()]
    results = crawl(
        args.url, limit=args.limit, max_depth=args.max_depth,
        include_subdomains=args.include_subdomains, include_re=args.include,
        exclude_re=args.exclude, formats=formats, concurrency=args.concurrency,
        delay=args.delay, respect_robots=not args.ignore_robots,
        render_if_thin=not args.no_render_fallback, timeout=args.timeout,
    )
    out(results)


if __name__ == "__main__":
    main()
