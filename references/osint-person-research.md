# OSINT Person Research Pattern

## Step-by-Step Flow

```
web_search("Full Name") → primary source → RocketReach → news → PIVOT: username search → compile report
```

### Step 1: Primary Source
If the user gives you a URL (LinkedIn, personal site), start there.
Extract every visible field: name, title, company, location, education, bio.

**Also extract the USERNAME** from the URL (e.g., `linkedin.com/in/onderkygz` → `onderkygz`).

### Step 2: Cross-Reference Search (by Name)
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
Same username on multiple platforms is ✅ (single source). Cross-reference
with bio, location, profile photo for ✅✅.

### Step 7: PIVOT — Username-Based Search 🔑

**When you find the same username on 3+ platforms, STOP searching by name and START searching by username.** This uncovers information that name-based searches miss:

```python
# Instead of:
web_search('"Full Name" some_topic')

# Search by username:
web_search('"username" site:reddit.com', limit=5)
web_search('"username" site:twitter.com OR site:x.com', limit=5)
web_search('"username" site:medium.com', limit=5)
web_search('"username" site:dev.to OR site:hashnode.com', limit=5)
web_search('"username" site:stackoverflow.com', limit=5)
web_search('"username" site:youtube.com', limit=5)
web_search('"username" site:huggingface.co', limit=5)
web_search('"username" site:npmjs.com OR site:pypi.org', limit=5)
web_search('"username" site:discord.com OR site:telegram.org', limit=5)
web_search('"username"', limit=20)  # broad search
```

**Why this works:** People often reuse the same handle on platforms where they
don't use their real name, or on niche platforms that name-based searches
would never surface. A username match on a platform where the real name is
NOT displayed is still a valid hit if the content, interests, or linked
accounts match.

### Step 8: Compile Report
- Group by trust score
- Flag name collisions in ⚠️ section
- Provide confidence percentage

## Report Template

```markdown
# 🕵️ Intelligence Report: [Name]

**Primary Source:** [URL]
**Username:** [extracted from primary source]
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