# Antigravity Entegrasyonu

> Google Antigravity için Web Scraping Intelligence — Native araçlar + Webscout CLI

## Antigravity'nin Araç Seti

| Antigravity Aracı | Bu Entegrasyonda Kullanımı |
|---|---|
| `search_web` | Web araması (DuckDuckGo) |
| `read_url_content` | Statik sayfa → markdown |
| `browser_subagent` | Dinamik sayfa etkileşimi, link keşfi, crawl |
| `schedule` | Cron-job periyodik monitoring |
| `view_file` | PDF/DOCX/XLSX görüntüleme |
| `run_command` | Python script çalıştırma (Webscout CLI fallback) |

## İki Çalışma Modu

Antigravity'de **iki mod** arasında seçim yapabilirsin:

### Mod 1: Native Araçlar (Önerilen — sıfır kurulum)

Antigravity'nin kendi araçlarını kullan. Hiçbir ek kurulum gerektirmez.

### Mod 2: Webscout CLI (Gelişmiş — script bazlı)

Python script'lerini `run_command` ile çalıştır. Daha fazla kontrol, daha detaylı flag'ler.

## Araç Eşleştirme Tablosu

| Firecrawl | Antigravity Native | Webscout CLI |
|---|---|---|
| `search` | `search_web` | `search.py` |
| `scrape` | `read_url_content` | `scrape.py` |
| `interact` | `browser_subagent` | `interact.py` |
| `map` | `browser_subagent` | `map.py` |
| `crawl` | `browser_subagent` + `read_url_content` | `crawl.py` |
| `batch` | `read_url_content` (toplu) | `batch_scrape.py` |
| `monitor` | `schedule` | `monitor.py` + cron |
| `parse` | `view_file` | `parse.py` |

## Karar Akışı

```
1. URL yok → search_web("sorgu")
2. URL var, statik → read_url_content (önce bunu dene)
3. read_url_content başarısız → browser_subagent (JS fallback)
4. Etkileşim gerekli → browser_subagent (tıklama, form, scroll)
5. Çok sayfalı → browser_subagent (link keşfi) → read_url_content (batch)
6. Periyodik takip → schedule (cron)
7. Lokal dosya → view_file
```

## Çalışan Örnek

> "Amazon'da iPhone 16 fiyatlarını araştır."

### Native Mod:

```json
// 1. Ara
search_web: { "query": "iPhone 16 price site:amazon.com" }

// 2. Statik dene
read_url_content: { "Url": "https://www.amazon.com/.../dp/B0XXXXX..." }

// 3. Başarısızsa browser_subagent ile
browser_subagent: {
  "task": "Navigate to https://www.amazon.com/.../dp/B0XXXXX..., scroll down to the price section, and return the product title, price, and availability status."
}
```

### Webscout CLI Mod:

```bash
python3 scripts/search.py "Amazon iPhone 16 price" --limit 5
python3 scripts/scrape.py "<URL>" --formats markdown
# blocked_signal kontrolü yap
```

## Rate Limiting

- Native modda `read_url_content` istekleri arasında **en az 1 saniye** bırak
- 429 alırsan exponential backoff: 2s → 4s → 8s (max 16s)
- Browser subagent'da 3 başarısız retry'den sonra kullanıcıya bildir
- Crawl limiti: **max 15 sayfa**

## Human-in-the-Loop

Eğer `browser_subagent` veya `read_url_content` bir CAPTCHA/login duvarıyla karşılaşırsa:

```
⚠️ Manuel müdahale gerekli: [URL] adresine otomatik erişim
bir CAPTCHA / login ekranı tarafından engelleniyor.
Lütfen sayfayı manuel olarak açıp engeli aş, sonra bana "devam et" de.
```

**False positive uyarısı:** Sayfa içeriğinde "captcha" kelimesi geçmesi engel DEĞİLDİR.
Gerçek engel: `cf-turnstile`, `g-recaptcha`, `h-captcha` widget class'ları.

## Bug Fix Geçmişi (v5.2)

Antigravity + Webscout entegrasyonunda çözülen kritik hatalar:

1. **CDP Boş Tab:** Chromium yeni bağlantıda `chrome://new-tab-page/` açıyor → `BLANK_URLS` filtresi
2. **lxml Truthiness:** `Element.find(...) or Element.find(...)` → explicit `is not None`
3. **False Positive Blocking:** "captcha" kelimesi → `cf-turnstile`/`g-recaptcha` class fingerprint'leri
4. **Orphan Process:** `interact_stop` unutulunca → `--sweep-orphans`
5. **Monitor Diff:** Baseline/karşılaştırma → unified diff + hash state
6. **Parse OCR:** Scanned PDF → `--ocr` fallback (pytesseract + tesseract binary)

## Monitoring (schedule)

```json
// Antigravity schedule ile periyodik fiyat takibi
schedule: {
  "cron": "0 * * * *",
  "prompt": "read_url_content ile https://example.com/pricing sayfasını oku. İlk çalıştırmada baseline oluştur. Sonraki çalıştırmalarda değişiklik varsa bildir, yoksa sessiz kal."
}
```