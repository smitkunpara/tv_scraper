"""Tests for News scraper module."""

from typing import Any, Dict, Iterator, List
from unittest.mock import MagicMock, patch

import pytest

from tv_scraper.core.base import BaseScraper
from tv_scraper.core.constants import STATUS_FAILED, STATUS_SUCCESS
from tv_scraper.scrapers.social.news import News


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _sample_headline(
    headline_id: str = "h123",
    title: str = "Bitcoin Hits New High",
    provider: str = "cointelegraph",
    published: int = 1678900000,
    urgency: int = 2,
    story_path: str = "/news/story/h123",
    link: str = "https://cointelegraph.com/news/bitcoin",
) -> Dict[str, Any]:
    """Build a headline item as returned by the TradingView news API."""
    return {
        "id": headline_id,
        "title": title,
        "provider": provider,
        "published": published,
        "urgency": urgency,
        "storyPath": story_path,
        "link": link,
    }


def _make_headlines_response(
    items: List[Dict[str, Any]] | None = None,
) -> Dict[str, Any]:
    """Build a TradingView news headlines API response."""
    if items is None:
        items = [_sample_headline()]
    return {"items": items}


def _mock_response(
    json_data: Dict[str, Any] | None = None,
    text: str = "",
    status_code: int = 200,
) -> MagicMock:
    """Create a mock ``requests.Response``."""
    resp = MagicMock()
    resp.status_code = status_code
    resp.text = text
    if json_data is not None:
        resp.json.return_value = json_data
    resp.raise_for_status.return_value = None
    return resp


_ARTICLE_HTML = """
<html>
<body>
<article>
  <nav aria-label="Breadcrumbs">
    <span class="breadcrumb-content-cZAS4vtj">Markets</span>
    <span class="breadcrumb-content-cZAS4vtj">Crypto</span>
  </nav>
  <h1 class="title-KX2tCBZq">Bitcoin Hits New High</h1>
  <time datetime="2025-01-15T10:00:00Z">Jan 15</time>
  <div class="symbolsContainer-cBh_FN2P">
    <a href="/symbols/BTCUSD">
      <span class="description-cBh_FN2P">BTCUSD</span>
      <img src="https://logo.com/btc.png" alt="BTC" />
    </a>
  </div>
  <div class="body-KX2tCBZq">
    <p>Bitcoin surged to a new all-time high today.</p>
    <img src="https://img.com/chart.png" alt="Chart" />
    <p>Market analysts are optimistic.</p>
  </div>
</article>
<div class="rowTags-XYZ">
  <span>Bitcoin</span>
  <span>Crypto</span>
</div>
</body>
</html>
"""


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def news() -> Iterator[News]:
    """Create a News instance for testing."""
    yield News()


# ---------------------------------------------------------------------------
# Inheritance
# ---------------------------------------------------------------------------


class TestInheritance:
    """Verify News inherits from BaseScraper."""

    def test_inherits_base_scraper(self) -> None:
        """News must be a subclass of BaseScraper."""
        assert issubclass(News, BaseScraper)


# ---------------------------------------------------------------------------
# scrape_headlines — success
# ---------------------------------------------------------------------------


class TestScrapeHeadlinesSuccess:
    """Tests for successful headline scraping."""

    @patch("tv_scraper.scrapers.social.news.requests.get")
    def test_scrape_headlines_success(
        self, mock_get: MagicMock, news: News
    ) -> None:
        """Standard headline retrieval returns success envelope."""
        mock_get.return_value = _mock_response(
            json_data=_make_headlines_response([_sample_headline()]),
        )

        result = news.scrape_headlines(exchange="BINANCE", symbol="BTCUSD")

        assert result["status"] == STATUS_SUCCESS
        assert result["error"] is None
        assert isinstance(result["data"], list)
        assert len(result["data"]) == 1

        item = result["data"][0]
        assert item["id"] == "h123"
        assert item["title"] == "Bitcoin Hits New High"

    @patch("tv_scraper.scrapers.social.news.requests.get")
    def test_scrape_headlines_with_provider(
        self, mock_get: MagicMock, news: News
    ) -> None:
        """Provider filter is passed through to the API URL."""
        mock_get.return_value = _mock_response(
            json_data=_make_headlines_response([_sample_headline()]),
        )

        result = news.scrape_headlines(
            exchange="BINANCE",
            symbol="BTCUSD",
            provider="cointelegraph",
        )

        assert result["status"] == STATUS_SUCCESS
        # Verify provider appears in the request URL
        call_url = mock_get.call_args[0][0]
        assert "provider=cointelegraph" in call_url

    @patch("tv_scraper.scrapers.social.news.requests.get")
    def test_scrape_headlines_with_area(
        self, mock_get: MagicMock, news: News
    ) -> None:
        """Area filter is converted to area code and passed through."""
        mock_get.return_value = _mock_response(
            json_data=_make_headlines_response([_sample_headline()]),
        )

        result = news.scrape_headlines(
            exchange="BINANCE",
            symbol="BTCUSD",
            area="americas",
        )

        assert result["status"] == STATUS_SUCCESS
        call_url = mock_get.call_args[0][0]
        assert "area=AME" in call_url

    @patch("tv_scraper.scrapers.social.news.requests.get")
    def test_scrape_headlines_with_language(
        self, mock_get: MagicMock, news: News
    ) -> None:
        """Language filter is passed through to the API URL."""
        mock_get.return_value = _mock_response(
            json_data=_make_headlines_response([_sample_headline()]),
        )

        result = news.scrape_headlines(
            exchange="BINANCE",
            symbol="BTCUSD",
            language="fr",
        )

        assert result["status"] == STATUS_SUCCESS
        call_url = mock_get.call_args[0][0]
        assert "lang=fr" in call_url

    @patch("tv_scraper.scrapers.social.news.requests.get")
    def test_scrape_headlines_empty_result(
        self, mock_get: MagicMock, news: News
    ) -> None:
        """No headlines returns success with empty list."""
        mock_get.return_value = _mock_response(
            json_data=_make_headlines_response([]),
        )

        result = news.scrape_headlines(exchange="BINANCE", symbol="BTCUSD")

        assert result["status"] == STATUS_SUCCESS
        assert result["data"] == []
        assert result["error"] is None


# ---------------------------------------------------------------------------
# scrape_headlines — validation errors
# ---------------------------------------------------------------------------


class TestScrapeHeadlinesValidation:
    """Validation failures return error responses — never raise."""

    def test_scrape_headlines_invalid_exchange(self, news: News) -> None:
        """Invalid exchange returns error response."""
        result = news.scrape_headlines(exchange="FAKEXCHANGE", symbol="BTCUSD")

        assert result["status"] == STATUS_FAILED
        assert result["data"] is None
        assert result["error"] is not None
        assert "exchange" in result["error"].lower() or "invalid" in result["error"].lower()

    def test_scrape_headlines_empty_symbol(self, news: News) -> None:
        """Empty symbol returns error response."""
        result = news.scrape_headlines(exchange="BINANCE", symbol="")

        assert result["status"] == STATUS_FAILED
        assert result["data"] is None
        assert result["error"] is not None

    def test_scrape_headlines_invalid_sort(self, news: News) -> None:
        """Invalid sort_by value returns error response."""
        result = news.scrape_headlines(
            exchange="BINANCE",
            symbol="BTCUSD",
            sort_by="invalid_sort",
        )

        assert result["status"] == STATUS_FAILED
        assert result["data"] is None
        assert "sort" in result["error"].lower() or "invalid" in result["error"].lower()

    def test_scrape_headlines_invalid_section(self, news: News) -> None:
        """Invalid section value returns error response."""
        result = news.scrape_headlines(
            exchange="BINANCE",
            symbol="BTCUSD",
            section="invalid_section",
        )

        assert result["status"] == STATUS_FAILED
        assert result["data"] is None
        assert "section" in result["error"].lower() or "invalid" in result["error"].lower()


# ---------------------------------------------------------------------------
# scrape_headlines — runtime errors
# ---------------------------------------------------------------------------


class TestScrapeHeadlinesErrors:
    """Runtime errors return error responses."""

    @patch("tv_scraper.scrapers.social.news.requests.get")
    def test_scrape_headlines_network_error(
        self, mock_get: MagicMock, news: News
    ) -> None:
        """Network failure returns error response, does not raise."""
        mock_get.side_effect = Exception("Connection refused")

        result = news.scrape_headlines(exchange="BINANCE", symbol="BTCUSD")

        assert result["status"] == STATUS_FAILED
        assert result["data"] is None
        assert result["error"] is not None

    @patch("tv_scraper.scrapers.social.news.requests.get")
    def test_scrape_headlines_captcha(
        self, mock_get: MagicMock, news: News
    ) -> None:
        """Captcha challenge returns error response."""
        mock_get.return_value = _mock_response(
            text="<title>Captcha Challenge</title>",
        )

        result = news.scrape_headlines(exchange="BINANCE", symbol="BTCUSD")

        assert result["status"] == STATUS_FAILED
        assert result["data"] is None
        assert "captcha" in result["error"].lower()


# ---------------------------------------------------------------------------
# scrape_content — success
# ---------------------------------------------------------------------------


class TestScrapeContentSuccess:
    """Tests for article content scraping."""

    @patch("tv_scraper.scrapers.social.news.requests.get")
    def test_scrape_content_success(
        self, mock_get: MagicMock, news: News
    ) -> None:
        """Successfully parse article HTML into structured content."""
        mock_get.return_value = _mock_response(text=_ARTICLE_HTML)

        result = news.scrape_content(story_path="/news/story/h123")

        assert result["status"] == STATUS_SUCCESS
        assert result["error"] is None

        data = result["data"]
        assert data["title"] == "Bitcoin Hits New High"
        assert "2025-01-15T10:00:00Z" in data["published_datetime"]
        assert data["breadcrumbs"] == "Markets > Crypto"
        assert len(data["related_symbols"]) == 1
        assert data["related_symbols"][0]["symbol"] == "BTCUSD"
        assert len(data["body"]) >= 2
        assert data["tags"] == ["Bitcoin", "Crypto"]


# ---------------------------------------------------------------------------
# scrape_content — errors
# ---------------------------------------------------------------------------


class TestScrapeContentErrors:
    """Error handling for content scraping."""

    @patch("tv_scraper.scrapers.social.news.requests.get")
    def test_scrape_content_network_error(
        self, mock_get: MagicMock, news: News
    ) -> None:
        """Network failure returns error response."""
        mock_get.side_effect = Exception("Connection refused")

        result = news.scrape_content(story_path="/news/story/h123")

        assert result["status"] == STATUS_FAILED
        assert result["data"] is None
        assert result["error"] is not None


# ---------------------------------------------------------------------------
# Response format
# ---------------------------------------------------------------------------


class TestResponseFormat:
    """Verify the standardized response envelope."""

    @patch("tv_scraper.scrapers.social.news.requests.get")
    def test_response_has_standard_envelope(
        self, mock_get: MagicMock, news: News
    ) -> None:
        """Response contains exactly status/data/metadata/error keys."""
        mock_get.return_value = _mock_response(
            json_data=_make_headlines_response([_sample_headline()]),
        )

        result = news.scrape_headlines(exchange="BINANCE", symbol="BTCUSD")

        assert set(result.keys()) == {"status", "data", "metadata", "error"}
