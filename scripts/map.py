#!/usr/bin/env python3
"""
map.py -- Firecrawl `map()` equivalent: discover URLs on a site FAST, without
scraping content. Free, local, no API key.

Strategy (fastest -> slowest, stops as soon as it has enough):
  1. Parse robots.txt for Sitemap: directives, plus common default sitemap paths.
  2. Recursively parse sitemap indexes -> sitemap files -> URLs.
  3. If sitemaps are missing/empty, fall back to a shallow same-domain crawl
     (homepage + its direct links, depth 1) to at least get top-level structure.

Usage:
  python3 map.py <url> [--search "keyword"] [--limit 5000] [--include-subdomains]

Output: {"url": ..., "source": "sitemap"|"shallow_crawl"|"mixed", "links": [...], "count": N}
"""
import argparse
import sys
import urllib.parse as up
import xml.etree.ElementTree as ET

import requests

sys.path.insert(0, __file__.rsplit("/", 1)[0])
from _common import out, eprint, fetch_html, sitemap_urls, extract_links, normalize_url, same_domain, DEFAULT_HEADERS

SITEMAP_NS = {"sm": "http://www.sitemaps.org/schemas/sitemap/0.9"}


def parse_sitemap(xml_text, depth=0, max_depth=3, seen=None):
    """Recursively resolve a sitemap (or sitemap index) into a flat URL list."""
    seen = seen if seen is not None else set()
    urls = []
    try:
        root = ET.fromstring(xml_text.encode("utf-8") if isinstance(xml_text, str) else xml_text)
    except ET.ParseError:
        return urls

    tag = root.tag.lower()
    if tag.endswith("sitemapindex"):
        if depth >= max_depth:
            return urls
        sm_entries = root.findall("sm:sitemap", SITEMAP_NS)
        if not sm_entries:
            sm_entries = root.findall("sitemap")
        for sm in sm_entries:
            loc_el = sm.find("sm:loc", SITEMAP_NS)
            if loc_el is None:
                loc_el = sm.find("loc")
            if loc_el is None or not loc_el.text:
                continue
            loc = loc_el.text.strip()
            if loc in seen:
                continue
            seen.add(loc)
            try:
                resp = requests.get(loc, headers=DEFAULT_HEADERS, timeout=15)
                if resp.status_code == 200:
                    urls.extend(parse_sitemap(resp.text, depth + 1, max_depth, seen))
            except Exception as e:
                eprint(f"  [map] failed to fetch nested sitemap {loc}: {e}")
    elif tag.endswith("urlset"):
        url_entries = root.findall("sm:url", SITEMAP_NS)
        if not url_entries:
            url_entries = root.findall("url")
        for u in url_entries:
            loc_el = u.find("sm:loc", SITEMAP_NS)
            if loc_el is None:
                loc_el = u.find("loc")
            if loc_el is not None and loc_el.text:
                urls.append(loc_el.text.strip())
    return urls


def from_sitemaps(root_url):
    all_urls = set()
    for sm_url in sitemap_urls(root_url):
        try:
            resp = requests.get(sm_url, headers=DEFAULT_HEADERS, timeout=15)
            if resp.status_code == 200 and resp.content:
                all_urls.update(parse_sitemap(resp.text))
        except Exception:
            continue
    return all_urls


def shallow_crawl(root_url, include_subdomains=False):
    """Homepage + its direct outgoing links, same domain only."""
    parts = up.urlsplit(root_url)
    root_netloc = parts.netloc
    urls = set()
    try:
        resp = fetch_html(root_url, timeout=15)
        urls.add(normalize_url(resp.url))
        for link in extract_links(resp.text, resp.url):
            if same_domain(link, root_netloc, include_subdomains):
                urls.add(link)
    except Exception as e:
        eprint(f"[map] shallow crawl failed: {e}")
    return urls


def site_map(url, search=None, limit=5000, include_subdomains=False):
    parts = up.urlsplit(url)
    root_url = f"{parts.scheme}://{parts.netloc}/"

    sitemap_links = from_sitemaps(root_url)
    source = "sitemap"

    if not sitemap_links:
        sitemap_links = shallow_crawl(url, include_subdomains)
        source = "shallow_crawl"
    elif len(sitemap_links) < 5:
        sitemap_links |= shallow_crawl(url, include_subdomains)
        source = "mixed"

    links = sorted(sitemap_links)
    if search:
        needle = search.lower()
        links = [l for l in links if needle in l.lower()]

    links = links[:limit]
    return {"url": url, "source": source, "count": len(links), "links": links}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("url")
    ap.add_argument("--search", default=None, help="only keep URLs containing this substring")
    ap.add_argument("--limit", type=int, default=5000)
    ap.add_argument("--include-subdomains", action="store_true")
    args = ap.parse_args()

    result = site_map(args.url, search=args.search, limit=args.limit,
                       include_subdomains=args.include_subdomains)
    out(result)


if __name__ == "__main__":
    main()
