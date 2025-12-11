# Technical Indicators

## Overview

Fetch technical analysis indicators (RSI, MACD, etc.) for any symbol on any exchange.

!!! note "Supported Data"
    See [Supported Data](supported_data.md) for valid exchanges, timeframes, and indicators.

## Input Specification

### Constructor

```python
Indicators(export_result: bool = False, export_type: str = 'json')
```

### Scrape Method

```python
scrape(exchange="BITSTAMP", symbol="BTCUSD", timeframe="1d", indicators=None, allIndicators=False)
```

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `exchange` | str | "BITSTAMP" | Valid exchange (e.g., "BINANCE") |
| `symbol` | str | "BTCUSD" | Trading symbol |
| `timeframe` | str | "1m" | `1m`, `5m`, `1h`, `1d`, etc. |
| `indicators` | List[str] | None | Specific indicators (e.g., `["RSI", "MACD.macd"]`) |
| `allIndicators` | bool | False | If `True`, fetches all available indicators |

### Constraints

- **Exchange**: Must be a valid exchange from [Supported Exchanges](supported_data.md#supported-exchanges)
- **Timeframe**: Must be one of the supported timeframes from [Supported Timeframes](supported_data.md#supported-timeframes)
- **Indicators**: Must be valid indicator names from [Supported Indicators](supported_data.md#supported-indicators)
- **Conditional**: `indicators` cannot be empty unless `allIndicators=True`.

## Output Specification

Returns a dictionary with status and data.

```python
{
    "status": "success",
    "data": {
        "RSI": 58.4,
        "Stoch.K": 76.2,
        "MACD.macd": 150.5
    }
}
```

## Usage Examples

```python
from tradingview_scraper.symbols.technicals import Indicators

scraper = Indicators()

# Specific indicators
data = scraper.scrape(
    exchange="BINANCE",
    symbol="BTCUSDT",
    timeframe="4h",
    indicators=["RSI", "EMA50"]
)
print(data)

# All indicators
full_data = scraper.scrape(
    exchange="COINBASE",
    symbol="ETHUSD",
    timeframe="1d",
    allIndicators=True
)
```