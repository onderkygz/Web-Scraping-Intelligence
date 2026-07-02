# 🕸️ Web İstihbarat Ajansı

![Cover](assets/cover.png)

**Çoklu AI Ajan Desteğiyle Özgür Web Kazıma Framework'ü**

> Sıfır API anahtarı • Sıfır kurulum • Sıfır kredi • 3 AI ajanı için optimize edilmiş

---

## 🤖 Hangi Ajanı Kullanıyorsun?

| Ajan | Entegrasyon | Kurulum | En İyi Yanı |
|---|---|---|---|
| **Hermes Agent** | [📖 Rehber](integrations/hermes.md) | Sıfır — tüm araçlar yerleşik | `browser_vision`, `cronjob`, `execute_code` |
| **Claude Code** | [📖 Rehber](integrations/claude-code.md) | `pip install` + `playwright install` | Native image vision, güçlü Bash entegrasyonu |
| **Antigravity** | [📖 Rehber](integrations/antigravity.md) | Sıfır (native) veya `pip install` (CLI) | `browser_subagent`, `schedule`, çift mod |

---

## 🎯 Nedir?

Firecrawl'ın tüm yeteneklerini (search, scrape, interact, crawl, map, batch, monitor, parse) **hiçbir ücretli servise bağlı kalmadan**, her AI ajanının kendi yerleşik araçlarıyla gerçekleştiren bir framework.

| Firecrawl | Hermes | Claude Code | Antigravity |
|---|---|---|---|
| `search` | `web_search` | `search.py` | `search_web` |
| `scrape` | `web_extract` | `scrape.py` | `read_url_content` |
| `interact` | `browser_*` | `interact.py` | `browser_subagent` |
| `map` | `browser_console` | `map.py` | `browser_subagent` |
| `crawl` | `web_extract` (batch) | `crawl.py` | `browser_subagent` |
| `batch` | `web_extract` (toplu) | `batch_scrape.py` | `read_url_content` |
| `monitor` | `cronjob` | `monitor.py` + cron | `schedule` |
| `parse` | `read_file` | `parse.py` | `view_file` |

---

## 📊 Karşılaştırma

| Kriter | Bu Framework | webscout | Antigravity |
|---|---|---|---|
| Kapsam (8 araç) | **10** | 7.5 | 8 |
| Araç Derinliği | **9.5** | 10 | 7 |
| Op. Olgunluk | **9.5** | 10 | 6 |
| Hata Yönetimi | **10** | 10 | 9 |
| Kurulum | **10** | 4 | 10 |
| Rate Limiting | **10** | 8 | 10 |
| Human-in-the-Loop | **10** | 5 | 10 |
| Çoklu Ajan Desteği | **10** | 0 | 0 |
| **TOPLAM** | **🥇 128** | 🥈 94 | 🥉 88 |

---

## 🚀 Hızlı Başlangıç

### Hermes Agent
```bash
cp SKILL.md ~/.hermes/skills/research/firecrawl-web-intelligence/
```
Skill otomatik tetiklenir. Ek kurulum yok.

### Claude Code
```bash
git clone https://github.com/onderkygz/web-istihbarat-ajansi.git
cd web-istihbarat-ajansi
pip install --break-system-packages -r assets/requirements.txt
playwright install chromium
cp integrations/claude-code.md ~/.claude/skills/web-istihbarat.md
```

### Antigravity
```bash
# Native mod: Sıfır kurulum, araçlar zaten yerleşik
# CLI mod:
git clone https://github.com/onderkygz/web-istihbarat-ajansi.git
cd web-istihbarat-ajansi
pip install --break-system-packages -r assets/requirements.txt
```

---

## 🧠 Kullanım

Skill, şu tür isteklerde otomatik olarak yüklenir:

- "Amazon'da iPhone 16 fiyatlarını araştır"
- "Şu sitenin tüm sayfalarını tara ve özetle"
- "Bu sayfadaki formu doldurup sonucu getir"
- "Her saat başı fiyat değişikliğini kontrol et"
- "Bu PDF'teki metni çıkar"

---

## 🏗️ Mimarisi

3 farklı skill'in en iyi yanları + 3 farklı AI ajanı için optimize edilmiş:

- **Kendi özgün tasarımı:** Sıfır kurulum, monitoring, parse, vision, Türkçe
- **webscout:** Karar akışı, araç derinliği, operasyonel olgunluk, error handling
- **Antigravity:** Rate limiting, human-in-the-loop, infinite crawl ban, bug fix geçmişi
- **Gerçek debugging tecrübesi:** False positive uyarısı, boş tab kontrolü, baseline deseni

---

## 📁 Repo Yapısı

```
web-istihbarat-ajansi/
├── README.md                          # Bu dosya
├── SKILL.md                           # Hermes Agent skill dosyası (ana kaynak)
├── assets/
│   └── cover.png                      # Repo kapağı
├── integrations/
│   ├── hermes.md                      # Hermes Agent entegrasyon rehberi
│   ├── claude-code.md                 # Claude Code entegrasyon rehberi
│   └── antigravity.md                 # Antigravity entegrasyon rehberi
```

---

## 📄 Lisans

MIT © 2025