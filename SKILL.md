---
name: firecrawl-web-intelligence
description: "Free, self-hosted web-intelligence toolkit using only Hermes built-in tools (web_search, web_extract, browser, cronjob, terminal). Full Firecrawl feature parity (search/scrape/map/crawl/batch/interact/monitor/parse) — zero API keys, zero install, zero credits. Use whenever the user wants to search the web, scrape a page to clean markdown, discover URLs on a site, crawl a whole site, batch-scrape URLs, interact with JS-heavy pages, monitor changes, or parse documents."
version: 5.2.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [web-scraping, search, research, monitoring, extraction, browser, open-source]
    related_skills: [arxiv, blogwatcher, polymarket]
---

# Web Scraping Intelligence v5.2

A Firecrawl-equivalent toolkit powered entirely by Hermes built-in tools.
**Zero setup, zero API keys, zero credits.** Everything is ready to use.

| Firecrawl | Hermes | How? |
|---|---|---|
| `search` | `web_search` | Web search, returns `{title, url, description}` |
| `scrape` | `web_extract` | Single/multi URL → clean markdown |
| `map` | `browser_navigate` + `browser_console` | Link discovery, sitemap scanning |
| `crawl` | `web_extract` (multi) + `execute_code` | Multi-page extraction |
| `batchScrape` | `web_extract` (batch URLs) | Parallel multi-URL |
| Interact | `browser_navigate` → `snapshot` → `click/type` → `snapshot` | Persistent browser session |
| Monitor | `cronjob` | Periodic checks |
| Parse | `read_file` / `terminal` | PDF/DOCX/XLSX → text |
| JSON-mode | **You** (LLM) extract fields from markdown yourself | Free, more accurate |

---

## Decision Flow

1. **No URL, need to find pages** → `web_search("query", limit=10)`. Collect the most
   relevant URLs. Use operators: `site:`, `-site:`, `"exact phrase"`, `filetype:pdf`.
2. **Have a URL, want its content** → `web_extract(["url"])`. Sufficient for static
   pages. Switch to browser for JS-heavy pages.
3. **Page needs interaction** (buttons, forms, "load more", cookie banners,
   pagination) → Start with `browser_navigate`, view with `browser_snapshot`,
   drive with `browser_click`/`browser_type`/`browser_press`. **After every action,
   VERIFY with `browser_snapshot` that the page changed.** Don't chain clicks blindly.
4. **Discover all URLs on a site (no content)** → `browser_navigate` to open the
   site, `browser_snapshot(full=true)` to see structure, or `browser_console` with
   `document.querySelectorAll('a[href]')` to extract links.
5. **Need content from many pages** → Send known URLs to `web_extract` in batches
   (up to 5 parallel). For unknown URLs, discover links first, then batch extract.
   Use `execute_code` for batching.

**Start with the cheapest tool:** `web_extract` before `browser`. If a single page
answers the question, don't crawl the whole site. `map` before `crawl`. `scrape`
before `interact`.

---

## Phase 1: Discovery — `web_search`

```python
web_search("site:docs.example.com pricing", limit=5)
web_search('"iPhone 16" price site:amazon.com', limit=10)
web_search("open source AI tools 2025", limit=8)
```

**Operators:** `site:domain`, `-site:domain`, `"exact phrase"`, `-exclude`,
`filetype:pdf`, `intitle:word`, `inurl:word`.

**Output:** List of `{title, url, description}`. Collect the most relevant URLs
for `web_extract` reading. Default `limit` is 5, max 10 recommended.

---

## Phase 2: Extraction — `web_extract`

```python
# Single page — clean markdown
web_extract(["https://example.com/article"])

# Multiple pages — parallel, up to 5 URLs per call
web_extract([
    "https://example.com/page1",
    "https://example.com/page2",
    "https://example.com/page3"
])

# More than 5 URLs? Split into batches:
# Batch 1: web_extract([url1..url5])
# Batch 2: web_extract([url6..url10])
```

**Output:** Clean **markdown**. Headings, lists, tables, links preserved.
Nav/footer/ads stripped by default (main content focus).

**JS-heavy pages:** If `web_extract` returns empty or incomplete content, the
page requires JS rendering → switch to Phase 3 (browser).

**Structured data (JSON mode):** Firecrawl's `json` format calls an LLM behind
the scenes. You already ARE the LLM — grab the markdown with `web_extract`,
then analyze it yourself and extract the fields. This is both free and usually
more accurate.

---

## Phase 3: Dynamic Interaction — Browser Tools

The Hermes equivalent of Firecrawl's "scrape → interact → stop" flow.
Each `browser_navigate` starts a session. Chain operations within the same site.

### Basic Flow

```python
# 1. Open the page
browser_navigate("https://www.amazon.com")

# 2. View the page — shows ref IDs like @e1, @e2
browser_snapshot()

# 3. Interact — VERIFY with snapshot after EVERY action
browser_type(ref="@e1", text="iPhone 16 Pro Max")   # type in search box
browser_press(key="Enter")                            # press Enter
browser_snapshot()                                    # ← SEE and VERIFY results

# 4. Click, scroll, navigate
browser_click(ref="@e5")                  # click first result
browser_snapshot()                        # ← SEE product page
browser_scroll(direction="down")          # scroll down
browser_press(key="Escape")               # Escape (close modal)
```

### Available Actions

| Action | Usage | Description |
|---|---|---|
| `browser_navigate` | `browser_navigate(url)` | Open page, start session |
| `browser_snapshot` | `browser_snapshot()` / `browser_snapshot(full=true)` | View page as text, get ref IDs |
| `browser_click` | `browser_click(ref="@e5")` | Click element |
| `browser_type` | `browser_type(ref="@e1", text="...")` | Type into input (clears first) |
| `browser_press` | `browser_press(key="Enter")` | Press key (Enter, Tab, Escape, ArrowDown) |
| `browser_scroll` | `browser_scroll(direction="down")` | Scroll page (up/down) |
| `browser_back` | `browser_back()` | Go back to previous page |
| `browser_console` | `browser_console(expression="...")` | Run JavaScript, extract DOM data |
| `browser_vision` | `browser_vision(question="...")` | Screenshot + visual analysis |
| `browser_get_images` | `browser_get_images()` | List all images on page |

### Browser Console Data Extraction

```python
# Single element
browser_console(expression="document.querySelector('.price')?.textContent")

# Multiple elements — use JSON.stringify
browser_console(expression="JSON.stringify(Array.from(document.querySelectorAll('.product-card')).map(c => ({title: c.querySelector('h2')?.textContent, price: c.querySelector('.price')?.textContent})))")

# Page title, URL
browser_console(expression="document.title")
browser_console(expression="window.location.href")
```

**Warning:** May return `null`/`undefined`. If the selector is wrong, first use
`browser_snapshot` to see the page structure and identify correct elements.

### Visual Verification

```python
# CAPTCHA, complex layout, price/product verification
browser_vision(question="What is the product price and stock status on this page?")
browser_vision(question="Is this a CAPTCHA? What does it say?", annotate=true)
```

### Session Hygiene (Important)

- After every `browser_click`/`browser_type`, **VERIFY** with `browser_snapshot`
  that the page changed. Don't chain clicks blindly.
- **First load check:** After `browser_navigate`, verify the page actually loaded
  the target URL. Make sure it's not a blank tab (`about:blank`,
  `chrome://new-tab-page/`), error page, or redirect. Check the page title and
  URL in the first snapshot.
- `@eN` ref IDs in `browser_snapshot` output **refresh** every time the page
  changes. Old ref IDs become invalid — always use the most recent snapshot's refs.
- Chain operations within the same site: navigate → snapshot → click → snapshot →
  type → snapshot. Don't call `browser_navigate` repeatedly.

---

## Phase 4: Deep Crawling

### A. Known URL list → `web_extract` (batch)

```python
# Up to 5 URLs in a single call
web_extract([url1, url2, url3, url4, url5])

# More than 5 → batch with execute_code
from hermes_tools import web_extract
urls = [url1, url2, ..., url20]
for i in range(0, len(urls), 5):
    batch = urls[i:i+5]
    results = web_extract(batch)
```

### B. Unknown site → Link discovery + batch extract

```python
# 1. Discover links with browser
browser_navigate("https://docs.example.com")
browser_console(expression="JSON.stringify(Array.from(document.querySelectorAll('a[href^=\"/\"]')).map(a => a.href))")
# → get link list

# 2. Filter same-domain URLs, batch extract
web_extract(filtered_urls)
```

### C. wget for local site mirror

```bash
wget --recursive --level=2 --no-parent \
     --wait=0.5 --random-wait \
     --accept '*.html' \
     https://docs.example.com/guide/
```

### D. Custom crawler with execute_code

```python
from hermes_tools import web_extract, terminal

# For complex crawl logic, use Python
pages = web_extract(["https://docs.example.com"])
# Parse links, filter, batch
```

---

## 📊 Monitoring — `cronjob` for Periodic Tracking

**How it works:** On the first run, establish a **baseline** (reference). On every
subsequent run, compare current content against the baseline. Only alert when
there's a change. This avoids noise on every run.

```python
# Page change monitoring
cronjob(
    action="create",
    name="Price Tracker - Example.com",
    schedule="every 30m",
    prompt="Use web_extract to read https://example.com/pricing. "
           "On first run, save the content as baseline. "
           "On subsequent runs, compare current content with baseline. "
           "If prices, plan names, or features have changed, "
           "report in OLD vs NEW format. If no change, stay silent.",
    deliver="all",
    skills=["firecrawl-web-intelligence"],
    enabled_toolsets=["web", "terminal", "file"]
)

# Web search for new content
cronjob(
    action="create",
    name="AI News Tracker",
    schedule="every 2h",
    prompt="Use web_search to find 'open source AI coding assistant launch' "
           "(limit=5). If there are NEW results not seen before, summarize. "
           "If no new results, stay silent.",
    deliver="all",
    enabled_toolsets=["web"]
)
```

**Cronjob limitations:** Runs headless; browser tools may be limited.
Prefer `web_extract` and `web_search`. Disable unnecessary tools with
`enabled_toolsets`.

---

## 📄 Document Parsing — `read_file` + Terminal

```bash
# PDF → text
pdftotext document.pdf -                          # poppler-utils (brew install poppler)
python3 -c "import pymupdf; print(chr(12).join([p.get_text() for p in pymupdf.open('doc.pdf')]))"

# DOCX → text
python3 -c "from docx import Document; print('\n'.join([p.text for p in Document('doc.docx').paragraphs]))"

# XLSX → text
python3 -c "import pandas as pd; print(pd.read_excel('file.xlsx').to_markdown())"
```

**Easiest path:** The `read_file` tool auto-converts `.ipynb`, `.docx`, `.xlsx`
files to text — in most cases you won't need `pdftotext`/`pymupdf`.

---

## Operational Rules

### Efficiency

1. **`web_search` first, then `web_extract`.** Find the right page with search,
   then read its content. Don't crawl an entire site for one answer.
2. **`web_extract` is enough for static pages.** Only switch to `browser` for
   JS-heavy pages. If `web_extract` returns empty → browser fallback.
3. **Parallel extract.** Send independent URLs in the same `web_extract` call
   (up to 5 URLs). Batch more with `execute_code`.
4. **Decide after every browser snapshot.** Don't chain clicks blindly. Verify
   the page changed after every action.

### Ethics & Polite Behavior

- **robots.txt & ToS:** `web_extract` and `web_search` run through Hermes
  infrastructure. Still comply with the target site's terms of use.
- **Avoid excessive requests:** Don't hammer the same site with rapid requests.
  Space out batches. Wait between `web_extract` batches.
- **PII / privacy:** Don't harvest personal data (emails, phone numbers, private
  profiles) unless the user explicitly requests it from a legitimate source.
  When in doubt, summarize instead of bulk-extracting personal fields.
- **Login walls / paywalls:** This toolkit has NO proxy rotation or CAPTCHA
  solving. Cloudflare challenges, login walls, and paywalled sites may fail.
  Tell the user honestly — don't silently return an empty page.

### Rate Limiting & Request Control

- **Request pacing:** Leave at least **1 second** between consecutive
  `web_extract` requests to the same domain. If batching with `execute_code`,
  add `time.sleep(1)`.
- **429 (Rate Limited) response:** If a request returns 429 (may happen at
  Hermes level), apply **exponential backoff**:
  - 1st retry: wait 2 seconds
  - 2nd retry: wait 4 seconds
  - 3rd retry: wait 8 seconds
  - Max: 16 seconds
  - After 3 failed retries, stop and notify the user.
- **No infinite crawls:** Never start a crawl without a limit. Always set a
  **hard page limit** (max 15 pages recommended). Large crawls exceed context
  limits and exhaust resources.
- **Batch strategy:** For more than 5 URLs, split into batches of 5 with
  `execute_code`, wait 1-2 seconds between batches.

### Error Handling

| Error | Diagnosis | Action |
|---|---|---|
| `web_extract` empty/incomplete | Page requires JS rendering | Try `browser_navigate` |
| `browser_navigate` timeout | Anti-bot (Cloudflare, login wall) | Check with `browser_vision` → Human-in-the-Loop (see below) |
| `browser_console` returns `null` | Wrong selector or element missing | Use `browser_snapshot` to see page structure, analyze DOM hierarchy, find correct selector |
| `browser_snapshot` ref IDs changed | Page re-rendered | Use the updated ref IDs from the latest snapshot |
| Site completely inaccessible | Anti-bot protection, geo-block, down | Notify user "site inaccessible", suggest alternative source |
| `web_search` results irrelevant | Query too broad or wrong | Narrow with `site:`, `"exact phrase"`, `-exclude` operators |

### Human-in-the-Loop (CAPTCHA / Login Wall)

If the browser encounters a **CAPTCHA**, **login screen**, or any challenge
requiring **manual verification**:

1. **Don't attempt blind bypass.** Don't try to solve CAPTCHAs or break through
   login walls.
2. **Watch for false positives:** The word "captcha" appearing in page content
   does NOT mean you're blocked. For example, a documentation page might discuss
   "how CAPTCHAs work." Real blocking signals: `cf-turnstile`, `g-recaptcha`,
   `h-captcha` widget classes, challenge platform URLs, or the page's main
   content being entirely a verification form.
3. **Stop automation** and notify the user in this format:

   > ⚠️ **Manual intervention required:** Automated access to `[URL]` is blocked
   > by a CAPTCHA / login screen. Please open the page manually, resolve the
   > block, and tell me to continue.

4. Don't proceed without explicit user confirmation.

### Format

- **Default output:** Clean markdown. `web_extract` focuses on main content
  (nav/footer/ads stripped).
- **Structured data:** After getting markdown, YOU as the LLM analyze and
  structure it as a table/JSON. No external service needed.

---

## Worked Example

> "Find iPhone 16 prices on Amazon."

```python
# 1. SEARCH — find the most relevant product page
web_search("iPhone 16 price site:amazon.com", limit=5)
# → pick the most relevant product URL from results

# 2. TRY (static) — start with web_extract
web_extract(["https://www.amazon.com/.../dp/B0XXXXX..."])
# → if price is JS-injected, may return empty/incomplete

# 3. FALLBACK (browser) — if JS needed
browser_navigate("https://www.amazon.com/.../dp/B0XXXXX...")
browser_snapshot()
# → see the price in snapshot? If not, scroll:

# 4. INTERACT — if needed
browser_scroll(direction="down")
browser_snapshot()

# 5. DOM EXTRACTION — most reliable method
browser_console(expression="document.querySelector('.a-price .a-offscreen')?.textContent")
# → "$1,199.00"

# 6. VISUAL VERIFICATION — to be sure
browser_vision(question="What is the product name, price, and stock status on this page?")
```

If prices load only after scrolling/clicking a region selector, extend the
browser interaction chain: `browser_click` → `browser_snapshot` → `browser_console`.

---

## Common Patterns

### 1. Research Flow
```
web_search → top 3 URLs → web_extract → analyze → summarize
```

### 2. Price/Product Tracking
```
web_extract (product page) → structure data → repeat via cronjob
```

### 3. Dynamic Page Data
```
browser_navigate → browser_snapshot → browser_click/type → browser_snapshot → browser_console
```

### 4. Site Map + Content
```
browser_navigate → browser_console (extract links) → web_extract (batch URLs)
```

### 5. Visual Verification
```
browser_navigate → browser_vision → if needed browser_click → browser_vision
```

---

## Common Pitfalls

1. **Using browser for static pages.** `web_extract` is much faster. Only switch
   to browser for JS-heavy pages.

2. **Not chaining browser sessions.** Each `browser_navigate` opens a new page.
   Chain within the same site: navigate → snapshot → click → snapshot → click →
   snapshot.

3. **Using old ref IDs after snapshot.** Ref IDs (`@e1`, `@e2`) refresh every
   time the page changes. Always use refs from the most recent snapshot.

4. **`web_extract` doesn't work on every page.** Amazon, Cloudflare-protected
   sites may fail. Try browser, and if that fails, tell the user.

5. **Too many parallel `web_extract` calls.** Don't send more than 5 URLs at once.
   Split into batches with `execute_code` if needed.

6. **Using `browser_console` output without checking.** It may return
   `null`/`undefined`. First use `browser_snapshot` to see the page structure.

7. **Using browser in cronjobs.** Cronjobs run headless. Prefer `web_extract`
   and `web_search`, disable browser with `enabled_toolsets`.

8. **Silently passing through anti-bot blocks.** If there's a Cloudflare
   challenge, login wall, or CAPTCHA, tell the user honestly. Don't present
   an empty page as content.

---

## Verification Checklist

- [ ] Right tool selected? (`web_search` / `web_extract` / `browser` / `cronjob`)
- [ ] Static pages use `web_extract`, dynamic use `browser`?
- [ ] Every `browser_click`/`browser_type` followed by `browser_snapshot` verification?
- [ ] Current ref IDs used after each `browser_snapshot`?
- [ ] `web_extract` multi-URLs sent in parallel (up to 5)?
- [ ] Browser fallback attempted on empty content?
- [ ] Alternative selector tried if `browser_console` returns null?
- [ ] User notified on anti-bot block?
- [ ] Results presented in clean Markdown/Table format?