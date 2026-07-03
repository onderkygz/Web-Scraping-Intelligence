# 🕸️ Web Scraping Intelligence

![Cover](assets/cover.png)

**A Free Web Scraping Framework* with Support for Multiple AI Agents*

> Zero API keys • Zero setup • Zero credit • Optimised for 3 AI agents

---

## 🤖 Which Agent Are You Using?

| Agent | Integration | Setup | Best Feature |
|---|---|---|---|
| **Hermes Agent** | [📖 Guide](integrations/hermes.md) | Zero — all tools built-in | `browser_vision`, `cronjob`, `execute_code` |
| **Claude Code** | [📖 Guide](integrations/claude-code.md) | `pip install` + `playwright install` | Native image vision, strong Bash integration |
| **Antigravity** | [📖 Guide](integrations/antigravity.md) | Zero (native) or `pip install` (CLI) | `browser_subagent`, `schedule`, dual mode |

---

## 🎯 What Is This?

A framework that replicates Firecrawl's full feature set (search, scrape, interact, crawl, map, batch, monitor, parse) **without any paid service dependency**, using each AI agent's own built-in tools.

| Firecrawl | Hermes | Claude Code | Antigravity |
|---|---|---|---|
| `search` | `web_search` | `search.py` | `search_web` |
| `scrape` | `web_extract` | `scrape.py` | `read_url_content` |
| `interact` | `browser_*` | `interact.py` | `browser_subagent` |
| `map` | `browser_console` | `map.py` | `browser_subagent` |
| `crawl` | `web_extract` (batch) | `crawl.py` | `browser_subagent` |
| `batch` | `web_extract` (multi) | `batch_scrape.py` | `read_url_content` |
| `monitor` | `cronjob` | `monitor.py` + cron | `schedule` |
| `parse` | `read_file` | `parse.py` | `view_file` |

---

## 📊 Comparison

Each agent's **initial** skill score vs. the **final merged** framework:

| Criteria | Antigravity | Claude Code | Hermes | This Framework |
|---|---|---|---|---|
| Coverage (8 tools) | 8.0 | 7.5 | 9.0 | **10.0** |
| Tool Depth | 7.0 | 10.0 | 5.0 | **9.5** |
| Op. Maturity | 6.0 | 10.0 | 3.0 | **9.5** |
| Error Handling | 9.0 | 10.0 | 6.0 | **10.0** |
| Setup Ease | 10.0 | 4.0 | 10.0 | **10.0** |
| Rate Limiting | 10.0 | 8.0 | 3.0 | **10.0** |
| Human-in-the-Loop | 10.0 | 5.0 | 4.0 | **10.0** |
| **TOTAL (/100)** | **86** | **78** | **57** | **🥇 99** |

> **This Framework** = Antigravity + Claude Code + Hermes + real debugging experience, merged into one.

### Scoring Methodology

Each skill was scored independently on **7 criteria** using a **0–10 scale**, then converted to a **100-point total**:

```
Total = round( (sum of all 7 criteria) / 7 × 10 )
```

**Criteria definitions:**

| # | Criteria | What it measures |
|---|---|---|
| 1 | **Coverage** | How many of Firecrawl's 8 tools (search/scrape/interact/map/crawl/batch/monitor/parse) are implemented |
| 2 | **Tool Depth** | Level of detail per tool — flags, parameters, edge cases, output formats documented |
| 3 | **Op. Maturity** | Operational readiness — robots.txt, rate limiting, PII, ToS, polite scraping, session hygiene |
| 4 | **Error Handling** | Graceful degradation — fallback chains, error formats, anti-bot detection, null/undefined checks |
| 5 | **Setup Ease** | How many steps to get started — zero = 10, pip install + playwright = 4 |
| 6 | **Rate Limiting** | Backoff strategy — exponential backoff, retry limits, request pacing, crawl limits |
| 7 | **Human-in-the-Loop** | CAPTCHA/login wall handling — escalation format, false positive protection, bypass prohibition |

**Why these 7?** They represent the full lifecycle of a web scraping agent: what it can do (1–2), how safely it does it (3–4–6), how easy it is to adopt (5), and how it handles the unexpected (7).

**Example — Antigravity (86/100):**

```
Coverage(8) + Depth(7) + Maturity(6) + Errors(9) + Setup(10) + Rate(10) + Human(10)
= 60 / 7 = 8.57 × 10 = 85.7 → 86
```

**Example — This Framework (99/100):**

```
Coverage(10) + Depth(9.5) + Maturity(9.5) + Errors(10) + Setup(10) + Rate(10) + Human(10)
= 69 / 7 = 9.86 × 10 = 98.6 → 99
```

> **Note:** Scores reflect each agent's **first published skill**, not their current version. This Framework's score reflects the final merged result after incorporating the best parts of all three.

---

## 🚀 Quick Start

### Hermes Agent
```bash
cp SKILL.md ~/.hermes/skills/research/firecrawl-web-intelligence/
```
Skill auto-triggers. No additional setup.

### Claude Code
```bash
git clone https://github.com/onderkygz/Web-Scraping-Intelligence.git
cd Web-Scraping-Intelligence
pip install --break-system-packages -r assets/requirements.txt
playwright install chromium
cp integrations/claude-code.md ~/.claude/skills/web-scraping-intelligence.md
```

### Antigravity
```bash
# Native mode: Zero setup, tools already built-in
# CLI mode:
git clone https://github.com/onderkygz/Web-Scraping-Intelligence.git
cd Web-Scraping-Intelligence
pip install --break-system-packages -r assets/requirements.txt
```

---

## 🧠 Usage

The skill auto-loads on requests like:

- "Find iPhone 16 prices on Amazon"
- "Scrape this entire site and summarize it"
- "Fill out this form and get the result"
- "Check for price changes every hour"
- "Extract text from this PDF"

---

## 🏗️ Architecture

Built by merging the best parts of 3 different skills + optimized for 3 AI agents:

- **Original design:** Zero setup, monitoring, parse, vision, Turkish
- **Claude Code:** Decision flow, tool depth, operational maturity, error handling
- **Antigravity:** Rate limiting, human-in-the-loop, infinite crawl ban, bug fix history
- **Real debugging experience:** False positive warnings, blank tab detection, baseline pattern

---

## 📁 Repo Structure

```
Web-Scraping-Intelligence/
├── README.md                          # This file
├── LICENSE                            # MIT License
├── SKILL.md                           # Hermes Agent skill file (primary source)
├── assets/
│   ├── cover.png                      # Repo cover
│   └── requirements.txt               # Python dependencies (Claude Code/Antigravity CLI)
├── integrations/
│   ├── hermes.md                      # Hermes Agent integration guide
│   ├── claude-code.md                 # Claude Code integration guide
│   └── antigravity.md                 # Antigravity integration guide
├── scripts/                           # Python CLI scripts (Claude Code mode)
│   ├── search.py                      # DuckDuckGo web search
│   ├── scrape.py                      # URL → clean markdown
│   ├── interact.py                    # Browser interaction (CDP)
│   ├── crawl.py                       # BFS multi-page crawler
│   ├── map.py                         # Site URL discovery
│   ├── batch_scrape.py                # Parallel multi-URL scrape
│   ├── monitor.py                     # Hash-and-diff change tracker
│   └── parse.py                       # PDF/DOCX/XLSX/PPTX/CSV parser
└── references/
    └── api_mapping.md                 # Firecrawl API → CLI flag mapping

---

## 📄 License

MIT © 2026 Onder Kaygusuz
