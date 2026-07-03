"""
Shared helpers for the webscout toolkit (free/open-source Firecrawl-style scraping).
No API keys, no paid services. Everything runs locally with requests + trafilatura
+ Playwright (for JS-heavy pages).
"""
import json
import re
import sys
import time
import urllib.parse as up
from urllib import robotparser

import requests

USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
)

DEFAULT_HEADERS = {
    "User-Agent": USER_AGENT,
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9,tr;q=0.8",
}

_robots_cache = {}


def eprint(*a, **kw):
    print(*a, file=sys.stderr, **kw)


def out(obj):
    """Print a single JSON object to stdout (one call per invocation)."""
    print(json.dumps(obj, ensure_ascii=False, indent=2))


def normalize_url(url, base=None):
    if base:
        url = up.urljoin(base, url)
    parts = up.urlsplit(url)
    # drop fragment, normalize trailing slash on bare domain
    path = parts.path or "/"
    return up.urlunsplit((parts.scheme, parts.netloc, path, parts.query, ""))


def same_domain(url, root_netloc, include_subdomains=True):
    netloc = up.urlsplit(url).netloc
    if include_subdomains:
        return netloc == root_netloc or netloc.endswith("." + root_netloc.split(":")[0])
    return netloc == root_netloc


def robots_allowed(url, user_agent=USER_AGENT):
    """Best-effort robots.txt check. Fails open (allowed) if robots.txt can't be read."""
    parts = up.urlsplit(url)
    root = f"{parts.scheme}://{parts.netloc}"
    rp = _robots_cache.get(root)
    if rp is None:
        rp = robotparser.RobotFileParser()
        rp.set_url(root + "/robots.txt")
        try:
            resp = requests.get(root + "/robots.txt", headers=DEFAULT_HEADERS, timeout=8)
            if resp.status_code == 200:
                rp.parse(resp.text.splitlines())
            else:
                rp.parse([])  # no robots.txt -> allow all
        except Exception:
            rp.parse([])
        _robots_cache[root] = rp
    try:
        return rp.can_fetch(user_agent, url)
    except Exception:
        return True


def sitemap_urls(root_url):
    """Find sitemap URLs referenced from robots.txt, plus common default paths."""
    parts = up.urlsplit(root_url)
    root = f"{parts.scheme}://{parts.netloc}"
    found = set()
    try:
        resp = requests.get(root + "/robots.txt", headers=DEFAULT_HEADERS, timeout=8)
        if resp.status_code == 200:
            for line in resp.text.splitlines():
                if line.lower().startswith("sitemap:"):
                    found.add(line.split(":", 1)[1].strip())
    except Exception:
        pass
    for guess in ("/sitemap.xml", "/sitemap_index.xml"):
        found.add(root + guess)
    return list(found)


def fetch_html(url, timeout=20, headers=None, max_retries=3, backoff_base=2):
    """Fetch a URL with polite exponential backoff on 429/503.
    Retries: 2s, 4s, 8s (capped), then gives up and lets the caller decide.
    """
    h = dict(DEFAULT_HEADERS)
    if headers:
        h.update(headers)

    last_exc = None
    for attempt in range(max_retries + 1):
        try:
            resp = requests.get(url, headers=h, timeout=timeout, allow_redirects=True)
        except requests.RequestException as e:
            last_exc = e
            if attempt < max_retries:
                time.sleep(min(backoff_base ** (attempt + 1), 16))
                continue
            raise

        if resp.status_code in (429, 503) and attempt < max_retries:
            wait = min(backoff_base ** (attempt + 1), 16)
            retry_after = resp.headers.get("Retry-After")
            if retry_after:
                try:
                    wait = max(wait, float(retry_after))
                except ValueError:
                    pass
            eprint(f"[fetch] {resp.status_code} on {url}, retrying in {wait:.0f}s "
                   f"(attempt {attempt + 1}/{max_retries})")
            time.sleep(wait)
            continue

        resp.raise_for_status()
        return resp

    if last_exc:
        raise last_exc
    resp.raise_for_status()
    return resp


# --- Anti-bot / CAPTCHA / login-wall detection -----------------------------
# Cannot and should not be bypassed -- this is purely for detecting the
# situation so the agent can stop and hand off to the human (see SKILL.md's
# "Human-in-the-loop" section) instead of silently returning junk/empty pages.

_BLOCK_TITLE_MARKERS = [
    "just a moment", "attention required", "access denied", "are you a human",
    "verify you are a human", "checking your browser", "please verify you are a human",
    "let us know you're not a robot", "unusual traffic",
]
# Deliberately specific technical fingerprints, not bare words like "captcha"
# or "recaptcha" -- those show up in ordinary prose all the time (docs pages
# describing anti-bot features, news articles about bot protection, etc.)
# and would make this heuristic useless through false positives.
_BLOCK_BODY_MARKERS = [
    "cf-chl-widget", "cf-turnstile", "g-recaptcha", "h-captcha",
    'id="challenge-form"', 'id="challenge-running"',
    "checking if the site connection is secure",
    "ddos protection by", "please enable cookies and reload",
]


def detect_blocking(html, status_code=None):
    """Best-effort detection of CAPTCHA / anti-bot walls / login gates.
    Returns None if the page looks normal, or a dict describing the signal
    that fired if it looks blocked. False negatives are expected (some
    blocks look like a normal page); false positives are possible on pages
    that legitimately mention 'captcha' in prose -- treat this as a strong
    hint, not a certainty.
    """
    if status_code in (403, 429, 503):
        return {"blocked": True, "reason": f"HTTP {status_code}", "signal": "status_code"}

    if not html:
        return None
    lower = html.lower()

    title_match = re.search(r"<title[^>]*>(.*?)</title>", lower, re.DOTALL)
    title = title_match.group(1).strip() if title_match else ""
    for marker in _BLOCK_TITLE_MARKERS:
        if marker in title:
            return {"blocked": True, "reason": f"page title suggests a challenge: '{title[:80]}'",
                    "signal": "title"}

    for marker in _BLOCK_BODY_MARKERS:
        if marker in lower:
            return {"blocked": True, "reason": f"page body contains anti-bot marker: '{marker}'",
                    "signal": "body"}

    return None


def html_to_markdown(html, url=None, only_main_content=True):
    """Convert raw HTML to clean markdown using trafilatura (falls back to markdownify)."""
    import trafilatura

    md = trafilatura.extract(
        html,
        url=url,
        output_format="markdown",
        favor_recall=True,
        include_links=True,
        include_images=True,
        include_tables=True,
        with_metadata=False,
        no_fallback=False,
    ) if only_main_content else None

    if md and md.strip():
        return md.strip()

    # fallback: whole-page conversion (used for only_main_content=False, or
    # when trafilatura can't find a "main content" block e.g. listing pages)
    try:
        from markdownify import markdownify as mdify
        from bs4 import BeautifulSoup

        soup = BeautifulSoup(html, "lxml")
        for tag in soup(["script", "style", "noscript", "svg"]):
            tag.decompose()
        return mdify(str(soup), heading_style="ATX").strip()
    except Exception:
        return trafilatura.extract(html, url=url, output_format="markdown") or ""


def extract_metadata(html, url=None):
    import trafilatura

    meta = trafilatura.extract_metadata(html, default_url=url)
    if not meta:
        return {}
    d = meta.as_dict() if hasattr(meta, "as_dict") else {}
    return {k: v for k, v in d.items() if v not in (None, "", [], {})}


def extract_links(html, base_url):
    from bs4 import BeautifulSoup

    soup = BeautifulSoup(html, "lxml")
    links = set()
    for a in soup.find_all("a", href=True):
        href = a["href"].strip()
        if href.startswith(("javascript:", "mailto:", "tel:", "#")):
            continue
        links.add(normalize_url(href, base=base_url))
    return sorted(links)


def looks_thin(markdown_text, min_chars=200):
    """Heuristic: does this look like a JS-rendered shell rather than real content?"""
    if not markdown_text:
        return True
    return len(markdown_text.strip()) < min_chars


def polite_sleep(seconds=0.5):
    time.sleep(seconds)
