#!/usr/bin/env python3
"""
search.py -- Firecrawl `search()` equivalent, powered by DuckDuckGo (free, no API key).

Usage:
  python3 search.py "query" [--limit 5] [--source web|news|images] [--scrape] [--only-main-content]

Output: JSON list on stdout:
  [{"title": "...", "url": "...", "snippet": "..."}]
If --scrape is passed, each result also gets a "markdown" field (fetched via scrape.py logic).
"""
import argparse
import sys

sys.path.insert(0, __file__.rsplit("/", 1)[0])
from _common import out, eprint, fetch_html, html_to_markdown, looks_thin


def search(query, limit=5, source="web", region="wt-wt"):
    from ddgs import DDGS

    results = []
    with DDGS() as ddgs:
        if source == "news":
            gen = ddgs.news(query, region=region, max_results=limit)
        elif source == "images":
            gen = ddgs.images(query, region=region, max_results=limit)
        else:
            gen = ddgs.text(query, region=region, max_results=limit)
        for r in gen:
            if source == "images":
                results.append({
                    "title": r.get("title"),
                    "url": r.get("image") or r.get("url"),
                    "source_page": r.get("url"),
                })
            elif source == "news":
                results.append({
                    "title": r.get("title"),
                    "url": r.get("url"),
                    "snippet": r.get("body"),
                    "date": r.get("date"),
                    "source_name": r.get("source"),
                })
            else:
                results.append({
                    "title": r.get("title"),
                    "url": r.get("href"),
                    "snippet": r.get("body"),
                })
    return results


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("query")
    ap.add_argument("--limit", type=int, default=5)
    ap.add_argument("--source", choices=["web", "news", "images"], default="web")
    ap.add_argument("--scrape", action="store_true", help="also fetch clean markdown for each result")
    ap.add_argument("--only-main-content", action="store_true", default=True)
    args = ap.parse_args()

    try:
        results = search(args.query, limit=args.limit, source=args.source)
    except Exception as e:
        out({"error": f"search failed: {e}"})
        sys.exit(1)

    if args.scrape:
        for r in results:
            try:
                resp = fetch_html(r["url"], timeout=15)
                md = html_to_markdown(resp.text, url=r["url"])
                r["markdown"] = md
                r["thin_content_warning"] = looks_thin(md)
            except Exception as e:
                r["markdown"] = None
                r["scrape_error"] = str(e)

    out(results)


if __name__ == "__main__":
    main()
