---
name: firecrawl-web-intelligence
description: "Free, self-hosted web-intelligence toolkit using only Hermes built-in tools (web_search, web_extract, browser, cronjob, terminal). Full Firecrawl feature parity (search/scrape/map/crawl/batch/interact/monitor/parse) — zero API keys, zero install, zero credits. Use whenever the user wants to search the web, scrape a page to clean markdown, discover URLs on a site, crawl a whole site, batch-scrape URLs, interact with JS-heavy pages, monitor changes, or parse documents."
version: 5.1.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [web-scraping, search, research, monitoring, extraction, browser, open-source]
    related_skills: [arxiv, blogwatcher, polymarket]
---

# Web İstihbarat Ajansı v5.0

Hermes'in yerleşik araçlarıyla çalışan Firecrawl eşdeğeri. **Sıfır kurulum,
sıfır API anahtarı, sıfır kredi.** Her şey hazır.

| Firecrawl | Hermes | Nasıl? |
|---|---|---|
| `search` | `web_search` | Web araması, sonuçları `{title, url, description}` döner |
| `scrape` | `web_extract` | Tek/çoklu URL → temiz markdown |
| `map` | `browser_navigate` + `browser_console` | Link keşfi, sitemap taraması |
| `crawl` | `web_extract` (çoklu) + `execute_code` | Çok sayfalı tarama |
| `batchScrape` | `web_extract` (toplu URL) | Paralel çoklu URL |
| Interact | `browser_navigate` → `snapshot` → `click/type` → `snapshot` | Kalıcı browser oturumu |
| Monitor | `cronjob` | Periyodik kontroller |
| Parse | `read_file` / `terminal` | PDF/DOCX/XLSX → metin |
| JSON-mode | **Sen** (LLM) markdown'dan alanları kendin çıkar | Ücretsiz, daha doğru |

---

## Karar Akışı

1. **URL yok, sayfa bulman lazım** → `web_search("sorgu", limit=10)`. Sonuçlardan
   en alakalı URL'leri topla. `site:`, `-site:`, `"tam ifade"`, `filetype:pdf`
   operatörlerini kullan.
2. **URL var, içeriğini istiyorsun** → `web_extract(["url"])`. Statik sayfalar
   için yeterli. JS-gerektiren sayfalarda browser'a geç.
3. **Sayfa etkileşim gerektiriyor** (buton, form, "load more", çerez banner'ı,
   pagination) → `browser_navigate` ile başlat, `browser_snapshot` ile gör,
   `browser_click`/`browser_type`/`browser_press` ile sür. **Her adımdan sonra
   `browser_snapshot` ile sayfanın değiştiğini DOĞRULA.** Körlemesine tıklama
   zinciri yapma.
4. **Bir sitenin tüm URL'lerini keşfet (içerik değil)** → `browser_navigate`
   ile siteyi aç, `browser_snapshot(full=true)` ile yapıyı gör, veya
   `browser_console` ile `document.querySelectorAll('a[href]')` ile link çıkar.
5. **Çok sayıda sayfanın içeriği lazım** → Bilinen URL'leri `web_extract` ile
   toplu çek (5'e kadar paralel). Bilinmeyen URL'ler için önce link keşfi yap,
   sonra toplu çek. `execute_code` ile batch'le.

**En ucuz araçla başla:** `web_extract`, `browser`'dan önce. Tek sayfa
yeterliyse tüm siteyi tarama. `map` önce, `crawl` sonra. `scrape` önce,
`interact` sonra.

---

## Aşama 1: Keşif — `web_search`

```python
web_search("site:docs.example.com pricing", limit=5)
web_search('"iPhone 16" fiyat site:amazon.com', limit=10)
web_search("open source AI tools 2025", limit=8)
```

**Operatörler:** `site:domain`, `-site:domain`, `"tam ifade"`, `-hariç`,
`filetype:pdf`, `intitle:kelime`, `inurl:kelime`.

**Çıktı:** `{title, url, description}` listesi. En alakalı URL'leri
`web_extract` ile okumak üzere topla. `limit` varsayılan 5, max 10 önerilir.

---

## Aşama 2: Veri Çıkarma — `web_extract`

```python
# Tek sayfa — temiz markdown
web_extract(["https://example.com/article"])

# Çoklu sayfa — paralel, 5 URL'e kadar tek çağrıda
web_extract([
    "https://example.com/page1",
    "https://example.com/page2",
    "https://example.com/page3"
])

# 5'ten fazla URL varsa batch'lere böl:
# Batch 1: web_extract([url1..url5])
# Batch 2: web_extract([url6..url10])
```

**Çıktı:** Temiz **markdown**. Başlıklar, listeler, tablolar, linkler korunur.
Varsayılan olarak nav/footer/ads temizlenir (ana içerik odaklı).

**JS-gerektiren sayfalar:** `web_extract` boş veya eksik içerik dönerse sayfa
JS render gerektiriyordur → Aşama 3'e (browser) geç.

**Yapılandırılmış veri (JSON mode):** Firecrawl'ın `json` formatı arkada LLM
çağırır. Sen zaten LLM'sin — `web_extract` ile markdown'ı al, sonra kendin
analiz edip alanları çıkar. Bu hem ücretsiz hem de genellikle daha doğru.

---

## Aşama 3: Dinamik Etkileşim — Browser Araçları

Firecrawl'ın "scrape → interact → stop" akışının Hermes karşılığı.
Her `browser_navigate` bir oturum başlatır. Aynı sitede zincirleme işlem
yapabilirsin.

### Temel Akış

```python
# 1. Sayfayı aç
browser_navigate("https://www.amazon.com")

# 2. Sayfayı gör — @e1, @e2 gibi ref ID'leri gösterir
browser_snapshot()

# 3. Etkileşim — HER ADIMDAN SONRA snapshot ile doğrula
browser_type(ref="@e1", text="iPhone 16 Pro Max")   # arama kutusuna yaz
browser_press(key="Enter")                            # Enter'a bas
browser_snapshot()                                    # ← sonuçları GÖR ve DOĞRULA

# 4. Tıklama, scroll, gezinme
browser_click(ref="@e5")                  # ilk sonuca tıkla
browser_snapshot()                        # ← ürün sayfasını GÖR
browser_scroll(direction="down")          # aşağı kaydır
browser_press(key="Escape")               # Escape (modal kapatma)
```

### Mevcut Aksiyonlar

| Aksiyon | Kullanım | Açıklama |
|---|---|---|
| `browser_navigate` | `browser_navigate(url)` | Sayfayı aç, oturum başlat |
| `browser_snapshot` | `browser_snapshot()` / `browser_snapshot(full=true)` | Sayfayı text olarak gör, ref ID'leri al |
| `browser_click` | `browser_click(ref="@e5")` | Elemente tıkla |
| `browser_type` | `browser_type(ref="@e1", text="...")` | Input'a yaz (önce temizler) |
| `browser_press` | `browser_press(key="Enter")` | Klavye tuşu bas (Enter, Tab, Escape, ArrowDown) |
| `browser_scroll` | `browser_scroll(direction="down")` | Sayfayı kaydır (up/down) |
| `browser_back` | `browser_back()` | Önceki sayfaya dön |
| `browser_console` | `browser_console(expression="...")` | JavaScript çalıştır, DOM'dan veri çek |
| `browser_vision` | `browser_vision(question="...")` | Screenshot al, görsel analiz yap |
| `browser_get_images` | `browser_get_images()` | Sayfadaki tüm görselleri listele |

### Browser Console ile Veri Çekme

```python
# Tek element
browser_console(expression="document.querySelector('.price')?.textContent")

# Çoklu element — JSON.stringify ile
browser_console(expression="JSON.stringify(Array.from(document.querySelectorAll('.product-card')).map(c => ({title: c.querySelector('h2')?.textContent, price: c.querySelector('.price')?.textContent})))")

# Sayfa başlığı, URL
browser_console(expression="document.title")
browser_console(expression="window.location.href")
```

**Uyarı:** `null`/`undefined` dönebilir. Selector yanlışsa önce
`browser_snapshot` ile sayfa yapısını gör, doğru elementleri tespit et.

### Görsel Doğrulama

```python
# CAPTCHA, karmaşık layout, fiyat/ürün kontrolü
browser_vision(question="Bu sayfadaki ürün fiyatı ve stok durumu nedir?")
browser_vision(question="Bu bir CAPTCHA mı? Ne yazıyor?", annotate=true)
```

### Session Hygiene (Önemli)

- Her `browser_click`/`browser_type` sonrası `browser_snapshot` ile sayfanın
  değiştiğini **DOĞRULA**. Körlemesine tıklama zinciri yapma.
- **İlk yükleme kontrolü:** `browser_navigate` sonrası sayfanın gerçekten
  hedef sayfa olduğunu kontrol et. Boş tab (`about:blank`,
  `chrome://new-tab-page/`), hata sayfası veya yönlendirme olmadığından
  emin ol. İlk snapshot'ta sayfa başlığını ve URL'yi doğrula.
- `browser_snapshot` çıktısındaki `@eN` ref ID'leri sayfa her değiştiğinde
  **yenilenir**. Eski ref ID'leri geçersiz olur — her snapshot'tan sonra
  güncel ref'leri kullan.
- Aynı sitede işlemleri zincirle: navigate → snapshot → click → snapshot →
  type → snapshot. Her seferinde yeni `browser_navigate` çağırma.

---

## Aşama 4: Derin Tarama

### A. Bilinen URL listesi → `web_extract` (batch)

```python
# 5 URL'e kadar tek çağrıda
web_extract([url1, url2, url3, url4, url5])

# 5'ten fazla → execute_code ile batch'le
from hermes_tools import web_extract
urls = [url1, url2, ..., url20]
for i in range(0, len(urls), 5):
    batch = urls[i:i+5]
    results = web_extract(batch)
```

### B. Bilinmeyen site → Link keşfi + toplu extract

```python
# 1. Browser ile linkleri keşfet
browser_navigate("https://docs.example.com")
browser_console(expression="JSON.stringify(Array.from(document.querySelectorAll('a[href^=\"/\"]')).map(a => a.href))")
# → link listesini al

# 2. Aynı domain'dekileri filtrele, web_extract ile toplu çek
web_extract(filtered_urls)
```

### C. wget ile yerel site mirror

```bash
wget --recursive --level=2 --no-parent \
     --wait=0.5 --random-wait \
     --accept '*.html' \
     https://docs.example.com/guide/
```

### D. execute_code ile özel crawler

```python
from hermes_tools import web_extract, terminal

# Karmaşık crawl mantığı gerekiyorsa Python ile
pages = web_extract(["https://docs.example.com"])
# Linkleri parse et, filtrele, batch'le
```

---

## 📊 Monitoring — `cronjob` ile Periyodik Takip

**Çalışma prensibi:** İlk çalıştırmada bir **baseline** (referans) oluştur,
sonraki her çalıştırmada güncel içeriği baseline ile karşılaştır. Sadece
değişiklik varsa bildir. Bu sayede her çalıştırmada gürültü yapmazsın.

```python
# Sayfa değişikliği izleme
cronjob(
    action="create",
    name="Fiyat Takip - Example.com",
    schedule="every 30m",
    prompt="web_extract ile https://example.com/pricing sayfasını oku. "
           "İlk çalıştırmada içeriği baseline olarak kaydet. "
           "Sonraki çalıştırmalarda güncel içerikle baseline'ı karşılaştır. "
           "Eğer fiyatlar, plan isimleri veya özellikler değişmişse "
           "ESKI vs YENI formatında bildir. Değişiklik yoksa sessiz kal.",
    deliver="all",
    skills=["firecrawl-web-intelligence"],
    enabled_toolsets=["web", "terminal", "file"]
)

# Web arama ile yeni içerik takibi
cronjob(
    action="create",
    name="AI Haber Takip",
    schedule="every 2h",
    prompt="web_search ile 'open source AI coding assistant launch' ara "
           "(limit=5). DAHA ÖNCE GÖRÜLMEMİŞ yeni sonuç varsa özetle. "
           "Yeni sonuç yoksa sessiz kal.",
    deliver="all",
    enabled_toolsets=["web"]
)
```

**Cronjob kısıtları:** Headless çalışır, browser araçları sınırlı olabilir.
`web_extract` ve `web_search` tercih et. `enabled_toolsets` ile gereksiz
araçları kapat.

---

## 📄 Doküman İşleme — `read_file` + Terminal

```bash
# PDF → metin
pdftotext document.pdf -                          # poppler-utils (brew install poppler)
python3 -c "import pymupdf; print(chr(12).join([p.get_text() for p in pymupdf.open('doc.pdf')]))"

# DOCX → metin
python3 -c "from docx import Document; print('\n'.join([p.text for p in Document('doc.docx').paragraphs]))"

# XLSX → metin
python3 -c "import pandas as pd; print(pd.read_excel('file.xlsx').to_markdown())"
```

**En kolay yol:** `read_file` aracı `.ipynb`, `.docx`, `.xlsx` dosyalarını
otomatik olarak metne çevirir — çoğu durumda `pdftotext`/`pymupdf`'e gerek
kalmaz.

---

## Operasyonel Kurallar

### Verimlilik

1. **Önce `web_search`, sonra `web_extract`.** Aramayla en doğru sayfayı bul,
   sonra içeriğini oku. Tüm siteyi taramak yerine hedefli çalış.
2. **Statik sayfalar için `web_extract` yeterli.** Sadece JS-gerektiren
   sayfalarda `browser`'a geç. `web_extract` boş içerik dönerse → browser
   fallback.
3. **Paralel extract.** Bağımsız URL'leri aynı `web_extract` çağrısında
   toplu gönder (5 URL'e kadar). Daha fazlasını `execute_code` ile batch'le.
4. **Browser'da her snapshot sonrası karar ver.** Körlemesine tıklama zinciri
   yapma. Her adımda sayfanın değiştiğini doğrula.

### Etik ve Saygılı Davranış

- **robots.txt ve ToS:** `web_extract` ve `web_search` Hermes altyapısı
  üzerinden çalışır. Yine de hedef sitenin kullanım şartlarına uy.
- **Aşırı istekten kaçın:** Aynı siteye kısa sürede çok sayıda istek yapma.
  Batch'leri aralıklı gönder. `web_extract` batch'leri arasında bekle.
- **PII / gizlilik:** E-posta, telefon, özel profil gibi kişisel verileri
  kullanıcı açıkça istemedikçe toplama. Şüpheli durumda ham veri yerine özet
  çıkar.
- **Login duvarı / paywall:** Bu araç setinde proxy rotasyonu veya CAPTCHA
  çözme YOKTUR. Cloudflare challenge, login duvarı, paywall olan siteler
  başarısız olabilir. Kullanıcıya dürüstçe bildir — sessizce boş sayfa dönme.

### Rate Limiting ve İstek Kontrolü

- **İstek aralığı:** Aynı siteye ardışık `web_extract` istekleri arasında
  en az **1 saniye** bırak. `execute_code` ile batch yapıyorsan `time.sleep(1)`
  ekle.
- **429 (Rate Limited) yanıtı:** Eğer bir istek 429 dönerse (Hermes seviyesinde
  olabilir) **exponential backoff** uygula:
  - İlk retry: 2 saniye bekle
  - İkinci retry: 4 saniye bekle
  - Üçüncü retry: 8 saniye bekle
  - Max: 16 saniye
  - 3 başarısız retry'den sonra dur, kullanıcıya bildir.
- **Sonsuz crawl yasağı:** Asla limitsiz crawl başlatma. Her zaman bir
  **sert sayfa limiti** belirle (max 15 sayfa önerilir). Büyük crawl'lar
  context limitini aşar ve kaynakları tüketir.
- **Batch stratejisi:** 5'ten fazla URL varsa `execute_code` ile 5'erli
  batch'lere böl, batch'ler arası 1-2 saniye bekle.

### Hata Yönetimi

| Hata | Teşhis | Aksiyon |
|---|---|---|
| `web_extract` boş/eksik içerik | Sayfa JS render gerektiriyor | `browser_navigate` ile dene |
| `browser_navigate` timeout | Anti-bot (Cloudflare, login duvarı) | `browser_vision` ile kontrol et → Human-in-the-Loop (aşağıya bak) |
| `browser_console` `null` dönüyor | Selector yanlış veya element yok | `browser_snapshot` ile sayfa yapısını gör, DOM hiyerarşisini analiz et, doğru selector bul |
| `browser_snapshot` ref ID'leri değişmiş | Sayfa yeniden render oldu | Yeni snapshot'taki güncel ref ID'leri kullan |
| Site tamamen erişilemez | Anti-bot koruması, geo-block, kapalı site | Kullanıcıya "site erişilemez" bildirimi yap, alternatif source öner |
| `web_search` sonuçları alakasız | Query çok geniş veya yanlış | `site:`, `"tam ifade"`, `-hariç` operatörleriyle daralt |

### Human-in-the-Loop (CAPTCHA / Login Duvarı)

Eğer browser bir **CAPTCHA**, **login ekranı** veya **manuel doğrulama**
gerektiren bir engelle karşılaşırsa:

1. **Kör bypass deneme.** CAPTCHA çözmeye veya login duvarını aşmaya
   çalışma.
2. **False positive'a dikkat:** Sayfa içeriğinde "captcha" kelimesinin
   geçmesi engellendiğin anlamına GELMEZ. Örneğin bir dokümantasyon
   sayfası "CAPTCHA'yı nasıl çözeriz"den bahsediyor olabilir. Gerçek
   engel işaretleri: `cf-turnstile`, `g-recaptcha`, `h-captcha` gibi
   spesifik widget class'ları, `challenge` platformu URL'leri, veya
   sayfanın ana içeriğinin tamamen bir doğrulama formu olması.
3. **Otomasyonu durdur** ve kullanıcıya şu formatta bildir:

   > ⚠️ **Manuel müdahale gerekli:** `[URL]` adresine otomatik erişim
   > bir CAPTCHA / login ekranı tarafından engelleniyor. Lütfen sayfayı
   > manuel olarak açıp engeli aş, sonra bana "devam et" de.

4. Kullanıcı onay vermeden işleme devam etme.

### Format

- **Varsayılan çıktı:** Temiz markdown. `web_extract` ana içeriğe odaklanır
  (nav/footer/ads temizlenir).
- **Yapılandırılmış veri:** Markdown'ı aldıktan sonra LLM olarak SEN analiz
  et ve tablo/JSON olarak yapılandır. Harici bir servise gerek yok.

---

## Çalışan Örnek

> "Amazon'da iPhone 16 fiyatlarını araştır."

```python
# 1. ARA — en alakalı ürün sayfasını bul
web_search("iPhone 16 fiyat site:amazon.com", limit=5)
# → sonuçlardan en alakalı ürün URL'sini seç

# 2. DENE (statik) — önce web_extract
web_extract(["https://www.amazon.com/.../dp/B0XXXXX..."])
# → fiyat JS ile yükleniyorsa boş/eksik gelebilir

# 3. FALLBACK (browser) — JS gerekiyorsa
browser_navigate("https://www.amazon.com/.../dp/B0XXXXX...")
browser_snapshot()
# → fiyatı snapshot'ta gördün mü? Görmediysen scroll:

# 4. ETKİLEŞİM — gerekirse
browser_scroll(direction="down")
browser_snapshot()

# 5. DOM'DAN ÇEK — en kesin yöntem
browser_console(expression="document.querySelector('.a-price .a-offscreen')?.textContent")
# → "$1,199.00"

# 6. GÖRSEL DOĞRULAMA — emin olmak için
browser_vision(question="Bu sayfadaki ürün adı, fiyatı ve stok durumu nedir?")
```

Fiyatlar scroll/click ile yükleniyorsa veya bölge seçici varsa, browser
etkileşim zincirini uzat: `browser_click` → `browser_snapshot` → `browser_console`.

---

## Sık Kullanılan Desenler

### 1. Araştırma Akışı
```
web_search → en iyi 3 URL → web_extract → analiz et → özetle
```

### 2. Fiyat/Ürün Takibi
```
web_extract (ürün sayfası) → veriyi yapılandır → cronjob ile tekrarla
```

### 3. Dinamik Sayfa Verisi
```
browser_navigate → browser_snapshot → browser_click/type → browser_snapshot → browser_console
```

### 4. Site Haritası + İçerik
```
browser_navigate → browser_console (linkleri çıkar) → web_extract (toplu URL)
```

### 5. Görsel Doğrulama
```
browser_navigate → browser_vision → gerekirse browser_click → browser_vision
```

---

## Common Pitfalls

1. **Statik sayfalar için browser kullanma.** `web_extract` çok daha hızlıdır.
   Sadece JS-gerektiren sayfalarda browser'a geç.

2. **Browser oturumunu zincirleme.** Her `browser_navigate` yeni sayfa açar.
   Aynı sitede: navigate → snapshot → click → snapshot → click → snapshot
   şeklinde zincirle.

3. **Snapshot'tan sonra eski ref ID'lerini kullanma.** Sayfa her değiştiğinde
   ref ID'leri (`@e1`, `@e2`) yenilenir. Her zaman son snapshot'taki ref'leri
   kullan.

4. **`web_extract` her sayfada çalışmaz.** Amazon, Cloudflare korumalı siteler
   başarısız olabilir. Browser ile dene, başarısız olursa kullanıcıya bildir.

5. **Çok fazla paralel `web_extract`.** Aynı anda 5'ten fazla URL gönderme.
   Gerekirse `execute_code` ile batch'lere böl.

6. **`browser_console` çıktısını kontrol etmeden kullanma.** `null`/`undefined`
   dönebilir. Önce `browser_snapshot` ile sayfa yapısını gör.

7. **Cronjob'da browser kullanımı.** Cronjob'lar headless çalışır.
   `web_extract` ve `web_search` tercih et, `enabled_toolsets` ile browser'ı
   kapat.

8. **Anti-bot engelini sessizce geçme.** Cloudflare, login duvarı, CAPTCHA
   varsa kullanıcıya dürüstçe bildir. Boş sayfayı içerik gibi sunma.

---

## Verification Checklist

- [ ] Doğru araç seçildi mi? (`web_search` / `web_extract` / `browser` / `cronjob`)
- [ ] Statik sayfa için `web_extract`, dinamik için `browser` kullanıldı mı?
- [ ] Her `browser_click`/`browser_type` sonrası `browser_snapshot` ile doğrulandı mı?
- [ ] `browser_snapshot` sonrası güncel ref ID'leri kullanıldı mı?
- [ ] `web_extract` çoklu URL'leri paralel gönderildi mi (5'e kadar)?
- [ ] Boş içerik durumunda browser fallback denendi mi?
- [ ] `browser_console` null dönüyorsa alternatif selector denendi mi?
- [ ] Anti-bot engeli durumunda kullanıcıya bildirildi mi?
- [ ] Sonuçlar temiz Markdown/Tablo formatında sunuldu mu?