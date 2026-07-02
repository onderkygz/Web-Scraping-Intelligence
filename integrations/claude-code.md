# Claude Code Entegrasyonu

> Claude Code için Web İstihbarat Ajansı — Python script'leri ile web kazıma

## Claude Code'un Araç Seti

| Claude Code Aracı | Bu Entegrasyonda Kullanımı |
|---|---|
| `Bash` | Python script'lerini çalıştırma (`python3 scripts/*.py`) |
| `View` | Screenshot görüntüleme, native image vision |
| `Read` | Dosya okuma |
| `Write` | Dosya yazma |

## Kurulum

```bash
# 1. Repoyu klonla
git clone https://github.com/onderkygz/web-istihbarat-ajansi.git
cd web-istihbarat-ajansi

# 2. Bağımlılıkları kur
pip install --break-system-packages -r assets/requirements.txt
playwright install chromium

# 3. Claude Code'a skill olarak ekle
# Claude Code için: SKILL.md dosyasını Claude'un okuyabileceği bir yere koy
cp integrations/claude-code.md ~/.claude/skills/web-istihbarat.md
```

## Araç Eşleştirme Tablosu

| Firecrawl | Claude Code | Komut |
|---|---|---|
| `search` | `Bash` | `python3 scripts/search.py "sorgu" --limit 5` |
| `scrape` | `Bash` | `python3 scripts/scrape.py "url" --formats markdown` |
| `interact` | `Bash` (zincirleme) | `interact_start.py` → `interact.py` → `interact_stop.py` |
| `map` | `Bash` | `python3 scripts/map.py "url"` |
| `crawl` | `Bash` | `python3 scripts/crawl.py "url" --limit 30` |
| `batch` | `Bash` | `python3 scripts/batch_scrape.py url1 url2 ...` |
| `monitor` | `Bash` + cron | `python3 scripts/monitor.py check "url" --label name` |
| `parse` | `Bash` | `python3 scripts/parse.py dosya.pdf` |
| JSON-mode | **Sen** (Claude) | Markdown'ı oku, alanları kendin çıkar |

## Karar Akışı

```
1. URL yok → search.py "sorgu"
2. URL var, statik → scrape.py <url>
3. URL var, JS gerekli → scrape.py <url> --render
4. Etkileşim gerekli → interact_start.py → interact.py → interact_stop.py
5. Çok sayfalı → crawl.py <url> --limit 30
6. Periyodik takip → monitor.py check + cron/launchd
7. Lokal dosya → parse.py <dosya>
```

## Çalışan Örnek

> "Amazon'da iPhone 16 fiyatlarını araştır."

```bash
# 1. Ara
python3 scripts/search.py "Amazon iPhone 16 price" --limit 5

# 2. Sonuçtan en alakalı URL'yi seç, scrape et
python3 scripts/scrape.py "https://www.amazon.com/.../dp/B0XXXXX..." --formats markdown

# 3. blocked_signal kontrolü yap
# → Eğer blocked_signal varsa Human-in-the-Loop'a geç

# 4. JS render gerekirse
python3 scripts/scrape.py "https://www.amazon.com/..." --render --wait-for 1500

# 5. Etkileşim gerekirse
SID=$(python3 scripts/interact_start.py "https://www.amazon.com/..." | python3 -c "import json,sys;print(json.load(sys.stdin)['scrape_id'])")
python3 scripts/interact.py "$SID" scroll --direction down
python3 scripts/interact.py "$SID" screenshot --out /tmp/check.png --full-page
# → View aracıyla /tmp/check.png'i gör
python3 scripts/interact_stop.py "$SID"
```

## Claude'a Özel İpuçları

### Görsel Doğrulama (Native Vision)

Claude'un native image vision yeteneği sayesinde, screenshot'ları doğrudan `View` aracıyla okuyabilirsin:

```bash
python3 scripts/interact.py "$SID" screenshot --out /tmp/verify.png
# Sonra View ile /tmp/verify.png'i aç ve içeriği analiz et
```

### Blocked Signal Kontrolü

Her script çıktısında `blocked_signal` ve `error` alanlarını kontrol et:

```bash
RESULT=$(python3 scripts/scrape.py "url")
echo "$RESULT" | python3 -c "import json,sys; d=json.load(sys.stdin); print('BLOCKED' if d.get('blocked_signal') else 'OK')"
```

### Human-in-the-Loop

Eğer `blocked_signal` alırsan:

> ⚠️ `[URL]` bir CAPTCHA/anti-bot koruması tarafından engelleniyor.
> Otomatik erişemiyorum. Sayfayı kendin açıp engeli aşman gerekiyor.

### Orphan Process Temizliği

```bash
python3 scripts/interact_stop.py --sweep-orphans
```

## JSON Mode (Yapılandırılmış Veri)

Firecrawl'ın `json` formatı arkada LLM çağırır. Claude olarak SEN zaten LLM'sin:

1. `scrape.py` ile markdown'ı al
2. Markdown içeriğini oku
3. Kullanıcının istediği şemaya göre alanları kendin çıkar
4. JSON/Tablo olarak sun

## Hata Yönetimi

| Hata | Aksiyon |
|---|---|
| `{"error": "..."}` | Hatayı kullanıcıya bildir, alternatif dene |
| `blocked_signal` | Human-in-the-Loop, kullanıcıya bildir |
| 429/503 | Exponential backoff: 2s → 4s → 8s (max 16s) |
| Boş markdown | `--render` ile tekrar dene |
| Orphan process | `interact_stop.py --sweep-orphans` |