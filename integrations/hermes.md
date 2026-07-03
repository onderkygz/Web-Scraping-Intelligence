# Hermes Agent Integration

> Web Scraping Intelligence for Nous Research Hermes Agent — Zero setup with built-in tools

## Hermes Tool Set

| Hermes Tool | Usage in This Integration |
|---|---|
| `web_search` | Web search |
| `web_extract` | Single/multi URL → clean markdown |
| `browser_navigate` | Start browser session |
| `browser_snapshot` | View page as text, get ref IDs |
| `browser_click` | Click element |
| `browser_type` | Type into input |
| `browser_press` | Press keyboard key |
| `browser_scroll` | Scroll page |
| `browser_console` | Run JavaScript, extract DOM data |
| `browser_vision` | Screenshot + visual analysis |
| `cronjob` | Periodic monitoring |
| `read_file` | File reading (PDF/DOCX/XLSX auto-detect) |
| `terminal` | Shell commands |
| `execute_code` | Python script execution |

## Tool Mapping

| Firecrawl | Hermes | Usage |
|---|---|---|
| `search` | `web_search` | `web_search("query", limit=10)` |
| `scrape` | `web_extract` | `web_extract(["url"])` |
| `interact` | `browser_navigate` + `browser_click/type/snapshot` | Chained browser session |
| `map` | `browser_navigate` + `browser_console` | Link discovery |
| `crawl` | `web_extract` (multi) + `execute_code` | Batched multi-extraction |
| `batch` | `web_extract` (batch URLs) | Up to 5 parallel URLs |
| `monitor` | `cronjob` | `cronjob(action="create", ...)` |
| `parse` | `read_file` / `terminal` | PDF/DOCX/XLSX → text |

## Decision Flow

```
1. No URL → web_search("query", limit=10)
2. Have URL, static → web_extract(["url"])
3. web_extract empty → browser_navigate (JS fallback)
4. Interaction needed → browser_navigate → browser_snapshot → browser_click/type → browser_snapshot
5. Many pages → web_extract([url1..url5]) (batch)
6. Periodic tracking → cronjob
7. Local file → read_file
```

## Worked Example

> "Find iPhone 16 prices on Amazon."

```python
# 1. Search
web_search("iPhone 16 price site:amazon.com", limit=5)

# 2. Try static
web_extract(["https://www.amazon.com/.../dp/B0XXXXX..."])

# 3. If empty/incomplete, switch to browser
browser_navigate("https://www.amazon.com/.../dp/B0XXXXX...")
browser_snapshot()

# 4. Scroll if needed
browser_scroll(direction="down")
browser_snapshot()

# 5. Extract directly from DOM
browser_console(expression="document.querySelector('.a-price .a-offscreen')?.textContent")

# 6. Visual verification
browser_vision(question="What is the product name, price, and stock status on this page?")
```

## Browser Session Hygiene

- After every `browser_click`/`browser_type`, VERIFY with `browser_snapshot`
- On first load, check for blank tab (`chrome://new-tab-page/`) — verify the real page loaded
- Snapshot ref IDs (`@e1`, `@e2`) refresh on every page change — use current ones
- Don't chain clicks blindly

## Monitoring (cronjob)

```python
cronjob(
    action="create",
    name="Price Tracker",
    schedule="every 30m",
    prompt="Use web_extract to read https://example.com/pricing. "
           "On first run, establish baseline. Report changes if any.",
    deliver="all",
    skills=["firecrawl-web-intelligence"],
    enabled_toolsets=["web", "terminal", "file"]
)
```

## Rate Limiting

- At least 1 second between `web_extract` requests to the same domain
- 429 → exponential backoff: 2s → 4s → 8s (max 16s)
- 3 failed retries → notify user
- Crawl: hard limit of 15 pages

## Human-in-the-Loop

If CAPTCHA/login wall detected:

```
⚠️ Manual intervention required: [URL] is blocked by a
CAPTCHA / login screen. Please open the page manually,
resolve the block, and tell me to continue.
```

**False positive:** The word "captcha" in page content does NOT mean blocked.
Real blocks: `cf-turnstile`, `g-recaptcha`, `h-captcha` widget classes.

## Hermes-Exclusive Advantages

Features available only in Hermes, not in other agents:

| Feature | Tool |
|---|---|
| Visual page analysis | `browser_vision` |
| DOM data extraction via JS | `browser_console` |
| Built-in periodic monitoring | `cronjob` |
| Custom Python crawlers | `execute_code` |
| Auto document parsing | `read_file` (.docx/.xlsx/.ipynb) |