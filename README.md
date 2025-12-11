
# TradingView Scraper

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![MIT License](https://img.shields.io/github/license/smitkunpara/tradingview-scraper.svg?color=brightgreen)](https://opensource.org/licenses/MIT)

**A powerful, real-time Python library for extracting financial data, ideas, and indicators from [TradingView.com](https://www.tradingview.com).**

---

## 📚 Documentation

For complete documentation, installation guides, API references, and examples, visit:

**[📖 Full Documentation](https://smitkunpara.github.io/tradingview-scraper/)**

### Quick Links
- [🚀 Quick Start Guide](https://smitkunpara.github.io/tradingview-scraper/quick_start/)
- [📦 Installation](https://smitkunpara.github.io/tradingview-scraper/installation/)
- [📊 Supported Data](https://smitkunpara.github.io/tradingview-scraper/supported_data/)
- [🔧 API Reference](https://smitkunpara.github.io/tradingview-scraper/)

---

## 🚀 Quick Start

This library requires Python 3.11+ and uses `uv` for dependency management.

### Installation

```bash
# Clone the repository
git clone https://github.com/smitkunpara/tradingview-scraper.git
cd tradingview-scraper

# Install dependencies (uv auto-creates virtual environment)
uv sync
```

### Basic Usage Examples

#### Fetching Technical Indicators

Get RSI and Stochastic indicators for Bitcoin on Binance:

```python
from tradingview_scraper.symbols.technicals import Indicators

# Initialize scraper
indicators_scraper = Indicators()

# Scrape indicators for BTCUSD
result = indicators_scraper.scrape(
    exchange="BINANCE",
    symbol="BTCUSD",
    timeframe="1d",
    indicators=["RSI", "Stoch.K"]
)

print(result)
```

#### Scraping Trading Ideas

Get popular trading ideas for Ethereum:

```python
from tradingview_scraper.symbols.ideas import Ideas

# Initialize scraper
ideas_scraper = Ideas()

# Scrape popular ideas for ETHUSD
result = ideas_scraper.scrape(
    symbol="ETHUSD",
    startPage=1,
    endPage=1,
    sort="popular"
)

print(f"Found {len(result)} ideas.")
```

## ✨ Key Features

- **📊 Real-Time Data**: Stream live OHLCV and indicator values via WebSocket
- **📰 Comprehensive Coverage**: Scrape Ideas, News, Market Movers, and Screener data
- **📈 Fundamental Data**: Access detailed financial statements and profitability ratios
- **🔧 Advanced Tools**: Symbol Markets lookup, Symbol Overview, and Minds Community discussions
- **📋 Structured Output**: All data returned as clean JSON/Python dictionaries
- **🌍 Multi-Market Support**: 260+ exchanges across stocks, crypto, forex, and commodities
- **⚡ Fast & Reliable**: Built with async support and robust error handling

## 📋 What's Included

### Core Modules
- **Indicators**: 81+ technical indicators (RSI, MACD, Stochastic, etc.)
- **Ideas**: Community trading ideas and strategies
- **News**: Financial news with provider filtering
- **Real-Time**: WebSocket streaming for live data
- **Screener**: Advanced stock screening with custom filters
- **Market Movers**: Top gainers, losers, and active stocks
- **Fundamentals**: Financial statements and ratios
- **Calendar**: Earnings and dividend events

### Data Sources
- **260+ Exchanges**: Binance, Coinbase, NASDAQ, NYSE, and more
- **16+ Markets**: Stocks, Crypto, Forex, Futures, Bonds
- **Real-Time Updates**: Live price feeds and indicators
- **Historical Data**: Backtesting and analysis support

---

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guide](https://smitkunpara.github.io/tradingview-scraper/contributing/) for details.

- **🐛 Bug Reports**: [Open an issue](https://github.com/smitkunpara/tradingview-scraper/issues)
- **💡 Feature Requests**: [Start a discussion](https://github.com/smitkunpara/tradingview-scraper/discussions)
- **📝 Code Style**: We use `black` for consistent formatting

---

## 📄 License

This project is licensed under the **MIT License** - see the [LICENSE](LICENSE) file for details.