# OSINT Person Research Pattern

## Step-by-Step Flow

```
web_search("Full Name") → LinkedIn → RocketReach → news → social media → compile report
```

### Step 1: Primary Source
If the user gives you a URL (LinkedIn, personal site), start there.
Extract every visible field: name, title, company, location, education, bio.

### Step 2: Cross-Reference Search
```python
web_search('"Full Name" company_name', limit=5)
web_search('"Full Name" university_name', limit=5)
web_search('"Full Name" city location', limit=5)
```

### Step 3: Professional Platforms
```python
web_extract(["https://rocketreach.co/first-last-email_XXXXXXXXX"])
# Note: RocketReach data is ✅ (single source) until cross-verified
```

### Step 4: GitHub / Tech
```python
web_search('"username" site:github.com', limit=5)
web_extract(["https://github.com/username"])
# If GitHub profile links to LinkedIn → ✅✅ (cross-verified)
```

### Step 5: News / Media
```python
web_search('"Full Name" news OR haber', limit=10)
web_extract([news_url1, news_url2, ...])
```

### Step 6: Social Media
Same username on multiple platforms is ✅ (not definitive).
Cross-reference with bio, location, profile photo for ✅✅.

### Step 7: Compile Report
- Group by trust score
- Flag name collisions in ⚠️ section
- Provide confidence percentage

## Report Template

```markdown
# 🕵️ Intelligence Report: [Name]

**Primary Source:** [URL]
**Methodology:** Cross-verification trust scoring

## 🔬 Scoring System
| ✅✅✅ | 3+ sources |
| ✅✅ | 2 sources |
| ✅ | 1 source |
| ⚠️ | Name collision |

## Confirmed Profile
[Table with ✅✅✅ and ✅✅ data]

## Pending Verification
[Table with ✅ data]

## Rejected (Name Collision)
[Table with ⚠️ data]

## Confidence Summary
X/Y confirmed = Z%
```