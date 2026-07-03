#!/usr/bin/env python3
"""
batch_scrape.py -- Firecrawl `batchScrape()` equivalent: scrape many known
URLs concurrently. Free, local, no API key.

Usage:
  python3 batch_scrape.py url1 url2 url3 ... [--formats markdown,links] [--concurrency 5]
  python3 batch_scrape.py --file urls.txt [--formats markdown]   # one URL per line

Output: JSON list, one object per URL (same shape as scrape.py's output).
"""
import argparse
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed

sys.path.insert(0, __file__.rsplit("/", 1)[0])
from _common import out, eprint
from scrape import scrape


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("urls", nargs="*", help="URLs to scrape")
    ap.add_argument("--file", default=None, help="file with one URL per line")
    ap.add_argument("--formats", default="markdown")
    ap.add_argument("--full-page", action="store_true")
    ap.add_argument("--concurrency", type=int, default=5)
    ap.add_argument("--timeout", type=int, default=20)
    ap.add_argument("--ignore-robots", action="store_true")
    args = ap.parse_args()

    urls = list(args.urls)
    if args.file:
        with open(args.file) as f:
            urls += [line.strip() for line in f if line.strip() and not line.startswith("#")]

    if not urls:
        out({"error": "no URLs provided (pass as args or --file)"})
        sys.exit(1)

    formats = [f.strip() for f in args.formats.split(",") if f.strip()]
    results = {}

    with ThreadPoolExecutor(max_workers=args.concurrency) as pool:
        futures = {
            pool.submit(
                scrape, u, formats=formats, only_main_content=not args.full_page,
                timeout=args.timeout, respect_robots=not args.ignore_robots,
            ): u
            for u in urls
        }
        for i, fut in enumerate(as_completed(futures), 1):
            u = futures[fut]
            try:
                results[u] = fut.result()
            except Exception as e:
                results[u] = {"url": u, "error": str(e)}
            eprint(f"[batch_scrape] {i}/{len(urls)} done: {u}")

    # preserve input order
    out([results[u] for u in urls])


if __name__ == "__main__":
    main()
