"""News scraper for fetching headlines and article content from TradingView."""

import logging
from typing import Any, Dict, List, Optional

import requests
from bs4 import BeautifulSoup

from tv_scraper.core.base import BaseScraper
from tv_scraper.core.exceptions import ValidationError

logger = logging.getLogger(__name__)

# TradingView News Headlines API endpoint
NEWS_HEADLINES_URL = (
    "https://news-headlines.tradingview.com/v2/view/headlines/symbol"
)

# Valid sort options
VALID_SORT_OPTIONS = {"latest", "oldest", "most_urgent", "least_urgent"}

# Valid section options
VALID_SECTIONS = {"all", "esg", "press_release", "financial_statement"}


class News(BaseScraper):
    """Scraper for TradingView news headlines and article content.

    Fetches news headlines for a given symbol and exchange, with optional
    filters for provider, area, section, language, and sort order. Also
    supports scraping full article content given a story path.

    Args:
        export_result: Whether to export results to file.
        export_type: Export format, ``"json"`` or ``"csv"``.
        timeout: HTTP request timeout in seconds.
        cookie: Optional TradingView cookie for captcha avoidance.

    Example::

        from tv_scraper.scrapers.social import News

        scraper = News()
        headlines = scraper.scrape_headlines(exchange="BINANCE", symbol="BTCUSD")
        if headlines["status"] == "success" and headlines["data"]:
            content = scraper.scrape_content(headlines["data"][0]["storyPath"])
    """

    def __init__(
        self,
        export_result: bool = False,
        export_type: str = "json",
        timeout: int = 10,
        cookie: Optional[str] = None,
    ) -> None:
        super().__init__(
            export_result=export_result,
            export_type=export_type,
            timeout=timeout,
        )
        if cookie:
            self._headers["cookie"] = cookie

        # Cache validation data
        self._news_providers: List[str] = self.validator.get_news_providers()
        self._languages: Dict[str, str] = self.validator.get_languages()
        self._areas: Dict[str, str] = self.validator.get_areas()
        self._language_codes: List[str] = list(self._languages.values())

    def scrape_headlines(
        self,
        exchange: str,
        symbol: str,
        provider: Optional[str] = None,
        area: Optional[str] = None,
        sort_by: str = "latest",
        section: str = "all",
        language: str = "en",
    ) -> Dict[str, Any]:
        """Scrape news headlines for a symbol.

        Args:
            exchange: Exchange name (e.g. ``"BINANCE"``).
            symbol: Trading symbol (e.g. ``"BTCUSD"``).
            provider: Optional news provider filter (e.g. ``"cointelegraph"``).
            area: Optional region filter (e.g. ``"americas"``).
            sort_by: Sort order. One of ``"latest"``, ``"oldest"``,
                ``"most_urgent"``, ``"least_urgent"``.
            section: News section. One of ``"all"``, ``"esg"``,
                ``"press_release"``, ``"financial_statement"``.
            language: Language code (e.g. ``"en"``, ``"fr"``).

        Returns:
            Standardized response dict with keys
            ``status``, ``data``, ``metadata``, ``error``.
        """
        # Validate inputs
        try:
            self.validator.validate_exchange(exchange)
            self.validator.validate_symbol(exchange, symbol)
            self.validator.validate_choice("sort_by", sort_by, VALID_SORT_OPTIONS)
            self.validator.validate_choice("section", section, VALID_SECTIONS)

            if language not in self._language_codes:
                raise ValidationError(
                    f"Invalid language: '{language}'. "
                    f"Allowed values: {', '.join(sorted(self._language_codes))}"
                )

            if provider is not None and provider not in self._news_providers:
                raise ValidationError(
                    f"Invalid provider: '{provider}'. "
                    f"Allowed values: {', '.join(sorted(self._news_providers))}"
                )

            if area is not None and area not in self._areas:
                raise ValidationError(
                    f"Invalid area: '{area}'. "
                    f"Allowed values: {', '.join(sorted(self._areas.keys()))}"
                )
        except ValidationError as exc:
            return self._error_response(str(exc))

        # Build URL parameters
        area_code = self._areas[area] if area else ""
        provider_param = provider.replace(".", "_") if provider else ""
        section_param = "" if section == "all" else section

        url = (
            f"{NEWS_HEADLINES_URL}"
            f"?client=web"
            f"&lang={language}"
            f"&area={area_code}"
            f"&provider={provider_param}"
            f"&section={section_param}"
            f"&streaming="
            f"&symbol={exchange}:{symbol}"
        )

        try:
            response = requests.get(
                url,
                headers=self._headers,
                timeout=self.timeout,
            )
            response.raise_for_status()

            # Check captcha
            if "<title>Captcha Challenge</title>" in response.text:
                logger.error(
                    "Captcha Challenge encountered for %s on %s.",
                    symbol,
                    exchange,
                )
                return self._error_response(
                    f"Captcha challenge encountered for {symbol} on {exchange}. "
                    "Try updating the TRADINGVIEW_COOKIE."
                )

            response_json = response.json()
            items: List[Dict[str, Any]] = response_json.get("items", [])

            if not items:
                return self._success_response(
                    [],
                    symbol=symbol,
                    exchange=exchange,
                    total=0,
                )

            # Apply client-side sorting
            items = self._sort_news(items, sort_by)

            # Export if requested
            if self.export_result:
                self._export(
                    data=items,
                    symbol=f"{exchange}_{symbol}",
                    data_category="news",
                )

            return self._success_response(
                items,
                symbol=symbol,
                exchange=exchange,
                total=len(items),
            )

        except Exception as exc:
            return self._error_response(f"Request failed: {exc}")

    def scrape_content(self, story_path: str) -> Dict[str, Any]:
        """Scrape full article content from a TradingView news story.

        Args:
            story_path: Relative path of the story
                (e.g. ``"/news/story/12345"``).

        Returns:
            Standardized response dict with keys
            ``status``, ``data``, ``metadata``, ``error``.
        """
        url = f"https://tradingview.com{story_path}"

        try:
            response = requests.get(
                url,
                headers=self._headers,
                timeout=self.timeout,
            )
            response.raise_for_status()

            if "<title>Captcha Challenge</title>" in response.text:
                logger.error(
                    "Captcha Challenge encountered for story %s.",
                    story_path,
                )
                return self._error_response(
                    f"Captcha challenge encountered for story {story_path}. "
                    "Try updating the TRADINGVIEW_COOKIE."
                )

            article_data = self._parse_article(response.text)

            return self._success_response(
                article_data,
                story_path=story_path,
            )

        except Exception as exc:
            return self._error_response(f"Request failed: {exc}")

    def _sort_news(
        self,
        news_list: List[Dict[str, Any]],
        sort_by: str,
    ) -> List[Dict[str, Any]]:
        """Sort news items by the given criterion.

        Args:
            news_list: List of news headline dicts.
            sort_by: Sort criterion.

        Returns:
            Sorted list of news headline dicts.
        """
        if sort_by == "latest":
            return sorted(
                news_list, key=lambda x: x.get("published", 0), reverse=True
            )
        elif sort_by == "oldest":
            return sorted(
                news_list, key=lambda x: x.get("published", 0), reverse=False
            )
        elif sort_by == "most_urgent":
            return sorted(
                news_list, key=lambda x: x.get("urgency", 0), reverse=True
            )
        elif sort_by == "least_urgent":
            return sorted(
                news_list, key=lambda x: x.get("urgency", 0), reverse=False
            )
        return news_list

    def _parse_article(self, html: str) -> Dict[str, Any]:
        """Parse article HTML into structured content.

        Args:
            html: Raw HTML of the article page.

        Returns:
            Dict with breadcrumbs, title, published_datetime,
            related_symbols, body, and tags.
        """
        soup = BeautifulSoup(html, "html.parser")

        article_tag = soup.find("article")
        row_tags = soup.find(
            "div",
            class_=lambda x: x and x.startswith("rowTags-"),  # type: ignore[arg-type]
        )

        article_json: Dict[str, Any] = {
            "breadcrumbs": None,
            "title": None,
            "published_datetime": None,
            "related_symbols": [],
            "body": [],
            "tags": [],
        }

        if not article_tag:
            return article_json

        # Breadcrumbs
        breadcrumbs = article_tag.find("nav", {"aria-label": "Breadcrumbs"})
        if breadcrumbs:
            spans = breadcrumbs.find_all(
                "span", class_="breadcrumb-content-cZAS4vtj"
            )
            article_json["breadcrumbs"] = " > ".join(
                item.get_text(strip=True) for item in spans
            )

        # Title
        title = article_tag.find("h1", class_="title-KX2tCBZq")
        if title:
            article_json["title"] = title.get_text(strip=True)

        # Published datetime
        published_time = article_tag.find("time")
        if published_time:
            article_json["published_datetime"] = published_time.get("datetime", "")

        # Related symbols
        symbol_container = article_tag.find(
            "div", class_="symbolsContainer-cBh_FN2P"
        )
        if symbol_container:
            for anchor in symbol_container.find_all("a"):
                name_tag = anchor.find("span", class_="description-cBh_FN2P")
                if name_tag:
                    symbol_name = name_tag.get_text(strip=True)
                    if symbol_name:
                        img = anchor.find("img")
                        logo_src = img["src"] if img and img.get("src") else None
                        article_json["related_symbols"].append(
                            {"symbol": symbol_name, "logo": logo_src}
                        )

        # Body content
        body_content = article_tag.find("div", class_="body-KX2tCBZq")
        if body_content:
            for element in body_content.find_all(
                ["p", "img"], recursive=True
            ):
                if element.name == "p":
                    article_json["body"].append(
                        {
                            "type": "text",
                            "content": element.get_text(strip=True),
                        }
                    )
                elif element.name == "img":
                    article_json["body"].append(
                        {
                            "type": "image",
                            "src": element["src"],
                            "alt": element.get("alt", ""),
                        }
                    )

        # Tags
        if row_tags:
            for span in row_tags.find_all("span"):
                text = span.get_text(strip=True)
                if text:
                    article_json["tags"].append(text)

        return article_json
