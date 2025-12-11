# News Scraper

## Overview

Scrape headlines and full article content from TradingView news providers.

!!! note "Supported Data"
    See [Supported Data](supported_data.md) for providers, areas, and languages.

## Input Specification

### Constructor

```python
NewsScraper(export_result=False, export_type='json', cookie=None)
```

### Scrape Headlines

```python
scrape_headlines(symbol, exchange, provider=None, area=None, sort="latest", section="all", language="en")
```

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `symbol` | str | - | Trading symbol (e.g., "AAPL") |
| `exchange` | str | - | Exchange (e.g., "NASDAQ") |
| `provider` | str | None | Provider code (e.g., "cointelegraph") |
| `area` | str | None | Region code (e.g., "americas") |
| `sort` | str | "latest" | `latest`, `oldest`, `most_urgent` |
| `section` | str | "all" | `all`, `esg`, `press_release` |
| `language` | str | "en" | Language code (e.g., "en", "fr") |

### Scrape Content

```python
scrape_news_content(story_path: str)
```

- `story_path`: Relative path from headline object (e.g., `/news/story/123`).

## Output Schema

### Headlines

List of dictionaries:

```python
{
    "id": "12345",
    "title": "Bitcoin Hits New High",
    "provider": "cointelegraph",
    "published": 1678900000,
    "urgency": 2,
    "storyPath": "/news/story/12345"
}
```

### Story Content

Dictionary with article details:

```python
{
    "title": "Article Title",
    "published_datetime": "2023-03-15T10:00:00Z",
    "body": [
        {"type": "text", "content": "Paragraph 1..."},
        {"type": "image", "src": "..."}
    ],
    "tags": ["Bitcoin", "Crypto"]
}
```

## Usage Examples

```python
from tradingview_scraper.symbols.news import NewsScraper

scraper = NewsScraper()

# 1. Get Headlines
headlines = scraper.scrape_headlines(
    symbol='BTCUSD',
    exchange='BINANCE',
    sort='most_urgent'
)

# 2. Get Full Content
if headlines:
    story = scraper.scrape_news_content(headlines[0]['storyPath'])
    print(story['title'])
```