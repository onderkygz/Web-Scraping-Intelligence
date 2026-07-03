# OSINT Trust Scoring Methodology

## Why This Exists

When researching a person or entity across multiple web sources, the most
common failure mode is **name collision** — merging data from two different
people who share the same name. This methodology prevents that by requiring
cross-verification on discriminating fields before merging.

## Trust Scoring System

| Score | Meaning | Action |
|---|---|---|
| ✅✅✅ | Confirmed by 3+ independent sources | **Definitive** — include in report |
| ✅✅ | Confirmed by 2 independent sources | **High confidence** — include, note source |
| ✅ | Found in 1 source only | **Pending verification** — include with caveat |
| ⚠️ | Contradicts primary source or discriminating fields | **Rejected** — flag as name collision |

## What Counts as an "Independent Source"?

Two sources are independent when they are **different platforms** or
**different organizations**:

| Independent | NOT Independent |
|---|---|
| LinkedIn + GitHub | LinkedIn snippet + LinkedIn full profile |
| RocketReach + news article | Two news articles from the same publisher |
| Company website + Instagram | Two search result snippets from the same page |

## Discriminating Fields (Name Collision Detection)

When two data clusters share the same name but differ on ANY of these fields,
they belong to **different people**:

1. **Location** (city, region) — e.g., İstanbul vs. İzmir/Torbalı
2. **Industry/sector** — e.g., telecom/corporate vs. PVC/manufacturing
3. **Career trajectory** — e.g., HR/Process Engineering vs. factory ownership
4. **Education** — e.g., Ankara University vs. no university record
5. **Birth year/place** — e.g., "Van 1989" vs. unknown
6. **Family** — spouse name, number of children
7. **Username** — same username on different platforms may indicate the same person, but is NOT sufficient alone

## Research Flow

```
1. PRIMARY SOURCE (user-provided URL)
   ↓
2. Extract what's visible (snippets, metadata, public fields)
   ↓
3. Search for cross-references (other platforms, news, profiles)
   ↓
4. For each new piece of data:
   ├── Matches discriminating fields? → Score ✅ or ✅✅
   ├── New field, no contradiction? → Score ✅, note "pending"
   └── Contradicts discriminating fields? → ⚠️ REJECT as name collision
   ↓
5. Compile report with trust scores
```

## When the Primary Source is Inaccessible

If the user provides a URL (e.g., LinkedIn) and you cannot access it:

1. **SAY SO.** "I cannot access `<URL>`. I can see X, Y, Z from search snippets."
2. **DO NOT substitute** with third-party data and present it as definitive.
3. **ASK** the user to confirm or provide alternative access.
4. If proceeding with third-party data, **explicitly downgrade** all scores
   and flag the report as "unverified primary source."

## Example: Önder Kaygusuz

| Data Cluster A (İstanbul) | Data Cluster B (İzmir/Torbalı) | Verdict |
|---|---|---|
| Turkcell Global Bilgi | LiderPen/ÜrkbayPen | ⚠️ Different sectors |
| Sancaktepe, İstanbul | Torbalı, İzmir | ⚠️ Different locations |
| Ankara University YBS | 1989 Van doğumlu | ⚠️ Different education/origin |
| Proses Mühendisliği Yöneticisi | AK Parti İlçe Yönetimi | ⚠️ Different career paths |

**Conclusion:** Two different people. Do not merge.