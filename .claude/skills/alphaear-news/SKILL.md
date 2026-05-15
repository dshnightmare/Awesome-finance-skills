---
name: alphaear-news
description: Fetch hot finance news, unified trends, prediction financial market data, and Zhihu KOL activity feeds. Use when the user needs real-time financial news, trend reports from multiple finance sources (Weibo, Zhihu, WallstreetCN, etc.), Polymarket finance market prediction data, or the latest posts/answers from a specific Zhihu user.
---

# AlphaEar News Skill

## Overview

Fetch real-time hot news, generate unified trend reports, retrieve Polymarket prediction data, and track Zhihu KOL activity feeds.

## Capabilities

### 1. Fetch Hot News & Trends

Use `scripts/news_tools.py` via `NewsNowTools`.

-   **Fetch News**: `fetch_hot_news(source_id, count)`
    -   See [sources.md](references/sources.md) for valid `source_id`s (e.g., `cls`, `weibo`).
-   **Unified Report**: `get_unified_trends(sources)`
    -   Aggregates top news from multiple sources.

### 2. Fetch Prediction Markets

Use `scripts/news_tools.py` via `PolymarketTools`.

-   **Market Summary**: `get_market_summary(limit)`
    -   Returns a formatted report of active prediction markets.

### 3. Fetch Zhihu KOL Activity Feed

Use `scripts/news_tools.py` via `ZhihuUserTools`. Requires a valid Zhihu login Cookie.

-   **Fetch Activities**: `fetch_user_activities(user_slug, limit)`
    -   `user_slug`: the identifier in the user's profile URL, e.g. `zhang-xue-feng-51` from `zhihu.com/people/zhang-xue-feng-51`
    -   Returns answers, articles, questions, and likes posted by the user.
-   **Format Report**: `format_activities(activities, user_slug)`
    -   Returns a Markdown-formatted activity report.

**Cookie setup** (required for authenticated content):
```python
# Option A: pass directly
tool = ZhihuUserTools(cookie="your_cookie_string")

# Option B: set environment variable
os.environ["ZHIHU_COOKIE"] = "your_cookie_string"
tool = ZhihuUserTools()
```

**How to get your Zhihu Cookie:**
1. Open `zhihu.com` in Chrome and log in.
2. Open DevTools → Network → refresh the page.
3. Click any `zhihu.com` request → Headers → copy the full `Cookie:` value.

**Example usage:**
```python
from scripts.news_tools import ZhihuUserTools
tool = ZhihuUserTools(cookie="z_c0=xxx; ...")
activities = tool.fetch_user_activities("zhang-xue-feng-51", limit=10)
print(tool.format_activities(activities, "zhang-xue-feng-51"))
```

## Dependencies

-   `requests`, `loguru`
-   `scripts/database_manager.py` (Local DB)
-   `ZHIHU_COOKIE` env var (optional, for Zhihu KOL feeds)
