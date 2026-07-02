# Hermes Agent Entegrasyonu

> Nous Research Hermes Agent için Web İstihbarat Ajansı — Yerleşik araçlarla sıfır kurulum

## Hermes'in Araç Seti

| Hermes Aracı | Bu Entegrasyonda Kullanımı |
|---|---|
| `web_search` | Web araması |
| `web_extract` | Tek/çoklu URL → temiz markdown |
| `browser_navigate` | Browser oturumu başlat |
| `browser_snapshot` | Sayfayı text olarak gör, ref ID'leri al |
| `browser_click` | Elemente tıkla |
| `browser_type` | Input'a yaz |
| `browser_press` | Klavye tuşu bas |
| `browser_scroll` | Sayfayı kaydır |
| `browser_console` | JavaScript çalıştır, DOM'dan veri çek |
| `browser_vision` | Screenshot + görsel analiz |
| `cronjob` | Periyodik monitoring |
| `read_file` | Dosya okuma (PDF/DOCX/XLSX otomatik) |
| `terminal` | Shell komutları |
| `execute_code` | Python script çalıştırma |

## Araç Eşleştirme Tablosu

| Firecrawl | Hermes | Kullanım |
|---|---|---|
| `search` | `web_search` | `web_search("sorgu", limit=10)` |
| `scrape` | `web_extract` | `web_extract(["url"])` |
| `interact` | `browser_navigate` + `browser_click/type/snapshot` | Zincirleme browser oturumu |
| `map` | `browser_navigate` + `browser_console` | Link keşfi |
| `crawl` | `web_extract` (çoklu) + `execute_code` | Batch'li çoklu çekme |
| `batch` | `web_extract` (toplu URL) | 5 URL'e kadar paralel |
| `monitor` | `cronjob` | `cronjob(action="create", ...)` |
| `parse` | `read_file` / `terminal` | PDF/DOCX/XLSX → metin |

## Karar Akışı

```
1. URL yok → web_search("sorgu", limit=10)
2. URL var, statik → web_extract(["url"])
3. web_extract boş döndü → browser_navigate (JS fallback)
4. Etkileşim gerekli → browser_navigate → browser_snapshot → browser_click/type → browser_snapshot
5. Çok sayfalı → web_extract([url1..url5]) (batch)
6. Periyodik takip → cronjob
7. Lokal dosya → read_file
```

## Çalışan Örnek

> "Amazon'da iPhone 16 fiyatlarını araştır."

```python
# 1. Ara
web_search("iPhone 16 fiyat site:amazon.com", limit=5)

# 2. Statik dene
web_extract(["https://www.amazon.com/.../dp/B0XXXXX..."])

# 3. Boş/eksik geldiyse browser'a geç
browser_navigate("https://www.amazon.com/.../dp/B0XXXXX...")
browser_snapshot()

# 4. Gerekirse scroll
browser_scroll(direction="down")
browser_snapshot()

# 5. DOM'dan direkt çek
browser_console(expression="document.querySelector('.a-price .a-offscreen')?.textContent")

# 6. Görsel doğrulama
browser_vision(question="Bu sayfadaki ürün adı, fiyatı ve stok durumu nedir?")
```

## Browser Session Hygiene

- Her `browser_click`/`browser_type` sonrası `browser_snapshot` ile DOĞRULA
- İlk yüklemede boş tab (`chrome://new-tab-page/`) kontrolü yap
- Snapshot sonrası ref ID'leri (`@e1`, `@e2`) yenilenir — güncel olanları kullan
- Körlemesine tıklama zinciri yapma

## Monitoring (cronjob)

```python
cronjob(
    action="create",
    name="Fiyat Takip",
    schedule="every 30m",
    prompt="web_extract ile https://example.com/pricing oku. İlk çalıştırmada baseline oluştur. Değişiklik varsa bildir.",
    deliver="all",
    skills=["firecrawl-web-intelligence"],
    enabled_toolsets=["web", "terminal", "file"]
)
```

## Rate Limiting

- Aynı siteye `web_extract` istekleri arasında en az 1 saniye
- 429 → exponential backoff: 2s → 4s → 8s (max 16s)
- 3 başarısız retry → kullanıcıya bildir
- Crawl: max 15 sayfa sert limit

## Human-in-the-Loop

CAPTCHA/login duvarı tespit edilirse:

```
⚠️ Manuel müdahale gerekli: [URL] bir CAPTCHA / login ekranı
tarafından engelleniyor. Lütfen sayfayı manuel açıp engeli aş.
```

**False positive:** Sayfada "captcha" kelimesi geçmesi engel DEĞİLDİR.
Gerçek engel: `cf-turnstile`, `g-recaptcha`, `h-captcha` widget'ları.

## Hermes'e Özel Avantajlar

Diğer ajanlarda olmayan, sadece Hermes'te bulunan yetenekler:

| Yetenek | Araç |
|---|---|
| Görsel sayfa analizi | `browser_vision` |
| DOM'dan JS ile veri çekme | `browser_console` |
| Anlık periyodik monitoring | `cronjob` (yerleşik) |
| Python ile özel crawler | `execute_code` |
| Otomatik döküman parse | `read_file` (.docx/.xlsx/.ipynb) |