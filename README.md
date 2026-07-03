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

| Criteria | This Framework | webscout | Antigravity |
|---|---|---|---|
| Coverage (8 tools) | **10** | 7.5 | 8 |
| Tool Depth | **9.5** | 10 | 7 |
| Op. Maturity | **9.5** | 10 | 6 |
| Error Handling | **10** | 10 | 9 |
| Setup Ease | **10** | 4 | 10 |
| Rate Limiting | **10** | 8 | 10 |
| Human-in-the-Loop | **10** | 5 | 10 |
| Multi-Agent Support | **10** | 0 | 0 |
| **TOTAL** | **🥇 128** | 🥈 94 | 🥉 88 |

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
- **webscout:** Decision flow, tool depth, operational maturity, error handling
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
