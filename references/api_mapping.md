# Firecrawl API -> webscout mapping

A field-level reference for porting Firecrawl-based prompts/code to this free
toolkit. Not everything has a free equivalent — those are called out
explicitly rather than faked.

## /search -> search.py

| Firecrawl param | webscout flag | Notes |
|---|---|---|
| `query` (positional) | positional arg | same |
| `limit` | `--limit` | same meaning |
| `sources: [{type: "web"\|"news"\|"images"}]` | `--source web\|news\|images` | one source per call, not a mixed list |
| `scrapeOptions: {formats:[...]}` | `--scrape` | boolean only; always fetches markdown, no per-format control |

No equivalent: paid/ranked "deep search", `sources: [{type:"news"}]` with
publisher filters. DuckDuckGo results are unranked beyond what DDG itself
returns.

## /scrape -> scrape.py

| Firecrawl param | webscout flag | Notes |
|---|---|---|
| `url` (positional) | positional arg | same |
| `formats: ["markdown","html","links",...]` | `--formats markdown,html,links,metadata` | subset: no `screenshot`, `summary`, `branding`, `product`, `audio`, `video`, `question`, `highlights` as first-class formats — screenshots exist only via the Interact flow (`interact.py ... screenshot`) |
| `formats: [{type:"json", schema}]` | *(none — do it yourself)* | you are the LLM; scrape to markdown then extract per the user's schema in your own response |
| `onlyMainContent` | `--full-page` (inverted) | default `true` like Firecrawl; pass `--full-page` to disable |
| `waitFor` | `--wait-for` (ms, only applies when rendering) | |
| `timeout` | `--timeout` (seconds, not ms) | |
| `mobile` | *(none)* | not implemented; add a mobile UA via a code edit if needed |
| `actions: [...]` | Interact flow (`interact_start.py`/`interact.py`) | one action per call instead of a batched array, but covers click/write/press/scroll/wait/screenshot/executeJavascript |
| `location: {country, languages}` | *(none)* | no proxy geo-targeting available |
| `proxy: "basic"\|"enhanced"\|"auto"` | *(none)* | no proxy network; anti-bot-hardened sites may simply fail |
| `redactPII` | *(none)* | do PII scrubbing yourself downstream if needed |
| `maxAge` / cache | *(none)* | every call is a fresh fetch; no caching layer |

## /map -> map.py

| Firecrawl param | webscout flag | Notes |
|---|---|---|
| `url` (positional) | positional arg | same |
| `search` | `--search` | substring filter, not fuzzy ranking |
| `limit` | `--limit` | same |
| `sitemap: "include"\|"skip"\|"only"` | *(always "include"-like behavior)* | always tries sitemap first, falls back to shallow crawl; no "sitemap-only" mode flag yet — filter `source` in the output if you need to know which path was used |
| `includeSubdomains` | `--include-subdomains` | default `false` here (Firecrawl defaults `true`) |

## /crawl -> crawl.py

| Firecrawl param | webscout flag | Notes |
|---|---|---|
| `url` (positional) | positional arg | same |
| `limit` | `--limit` | same, but Firecrawl defaults to 10,000 — **default here is 20**, be deliberate about raising it |
| `maxDiscoveryDepth` | `--max-depth` | same concept |
| `includePaths` / `excludePaths` | `--include` / `--exclude` | regex against full URL, not just pathname (equivalent to Firecrawl's `regexOnFullURL: true`) |
| `allowSubdomains` | `--include-subdomains` | |
| `allowExternalLinks` | *(none)* | always same-domain only; cross-domain crawling isn't supported (avoids accidentally crawling the whole internet) |
| `crawlEntireDomain` | *(none — use a high `--limit`/`--max-depth` instead)* | |
| `delay` | `--delay` | seconds, applied per-batch not strictly per-request |
| `scrapeOptions.formats` | `--formats` | same subset limits as scrape.py |
| `deduplicateSimilarURLs` | *(partial — exact-URL dedup only)* | no `www.`/trailing-slash/`index.html` normalization |

## /batch/scrape -> batch_scrape.py

Same shape, no async job/polling model — it just runs concurrently and
returns when done. No webhook support.

## Interact (`/scrape/{id}/interact`) -> interact_start.py / interact.py / interact_stop.py

| Firecrawl action | webscout action |
|---|---|
| `wait` (ms or selector) | `wait --ms N` or `wait --selector "..."` |
| `click` (`selector`, `all`) | `click --selector "..." [--click-all]` |
| `write` (`text`, after a click) | `write --selector "..." --text "..."` (selector required — no separate focus step needed) |
| `press` (`key`) | `press --key Enter` |
| `scroll` (`direction`, `selector`) | `scroll --direction down [--selector "..."]` |
| `screenshot` (`fullPage`, `quality`, `viewport`) | `screenshot --out path.png [--full-page]` (no quality/viewport control) |
| `scrape` (capture HTML at this point) | `scrape` (re-extracts current markdown) |
| `executeJavascript` (`script`) | `execute_js --script "..."` (return value comes back as `return_value`) |
| `pdf` (generate PDF) | *(none)* |
| natural-language `prompt` mode | *(none — decide the selector/action yourself)* Firecrawl's prompt mode uses an LLM to translate "click the button that says X" into an action; you (the agent) do that translation directly by reading the returned markdown/screenshot and picking a CSS selector, so there's no separate "prompt" action needed |

`stop_interaction` -> `interact_stop.py <scrape_id>`. Always call it —
unlike Firecrawl's managed sessions (which expire automatically), this one
is a real local process that keeps running until killed.

## Monitor (cronjob-based) -> monitor.py

Firecrawl doesn't have a first-class "monitor" endpoint in the same shape as
`search`/`scrape`/`crawl` — monitoring is typically built by an agent
platform on top of scheduled scrape calls (e.g. a `cronjob` tool that
re-invokes `scrape` on a timer and diffs results). `monitor.py` implements
that pattern directly: one `check` call = one scrape + hash comparison
against the last stored snapshot, with the actual "every N minutes" part
delegated to a real OS scheduler (`monitor.py schedule-help` prints the
cron/launchd snippets). No first-class API to compare parameters against —
this is a from-scratch free implementation of the concept.

## Parse -> parse.py

| Format | webscout | Notes |
|---|---|---|
| PDF text extraction | `parse.py file.pdf` | via pymupdf, page-separated |
| PDF OCR mode | `parse.py file.pdf --ocr` | via pytesseract+pillow (optional installs) |
| DOCX/XLSX/PPTX/CSV | `parse.py file.docx\|.xlsx\|.pptx\|.csv` | added because local document parsing is a common companion need, not a port of a specific Firecrawl field |

## Things with no free equivalent at all

- Proxy rotation / anti-bot bypass beyond a normal browser UA — Cloudflare
  "I'm not a robot" challenges and similar will generally still block this
  toolkit (though `blocked_signal` now at least tells you when this is
  happening instead of returning junk silently).
- CAPTCHA solving.
- `branding` / `product` deterministic structured extractors (Firecrawl's
  proprietary parsers for design systems and e-commerce product schemas) —
  approximate by scraping to markdown/HTML and extracting fields yourself.
- Audio/video extraction formats.
- Async job model with webhooks — everything here is synchronous.
- Response caching (`maxAge`/`minAge`).
- Zero Data Retention guarantees — this all runs locally already, so there's
  nothing to "retain" server-side, but there's also no formal ZDR mode/flag.
