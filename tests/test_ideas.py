import os
import sys
import pytest
from unittest import mock

# Add the current working directory to the system path
path = str(os.getcwd())
if path not in sys.path:
    sys.path.append(path)

from tradingview_scraper.symbols.ideas import Ideas

class TestIdeas:
    @pytest.fixture
    def ideas_scraper(self):
        """Fixture to create an instance of Ideas for testing."""
        return Ideas(export_result=False)

    @mock.patch('tradingview_scraper.symbols.ideas.requests.get')
    def test_scrape_recent_ideas_success(self, mock_get, ideas_scraper):
        """Test scraping recent ideas successfully with mocked response."""
        # Mock response for recent ideas
        mock_response = mock.Mock()
        mock_response.status_code = 200
        mock_response.text = ""  # No captcha
        mock_response.json.return_value = {
            'data': {
                'ideas': {
                    'data': {
                        'items': [
                            {
                                "name": "Recent Idea Title",
                                "description": "Recent Idea Description",
                                "symbol": {"logo_urls": ["image_url"]},
                                "chart_url": "chart_url",
                                "comments_count": 10,
                                "views_count": 100,
                                "user": {"username": "Recent Author"},
                                "likes_count": 5,
                                "date_timestamp": 1672531200
                            }
                        ]
                    }
                }
            }
        }
        mock_get.return_value = mock_response
        ideas = ideas_scraper.scrape(symbol="NASDAQ-NDX", sort="recent", startPage=1, endPage=1)
        assert len(ideas) == 1
        assert ideas[0]['title'] == "Recent Idea Title"
        assert ideas[0]['description'] == "Recent Idea Description"
        assert ideas[0]['author'] == "Recent Author"
        assert ideas[0]['comments_count'] == 10
        assert ideas[0]['views_count'] == 100
        assert ideas[0]['likes_count'] == 5

    @mock.patch('tradingview_scraper.symbols.ideas.requests.get')
    def test_scrape_no_ideas(self, mock_get, ideas_scraper):
        """Test handling of no ideas found with mocked response."""
        mock_response = mock.Mock()
        mock_response.status_code = 200
        mock_response.text = ""  # No captcha
        mock_response.json.return_value = {
            'data': {
                'ideas': {
                    'data': {
                        'items': []
                    }
                }
            }
        }
        mock_get.return_value = mock_response

        ideas = ideas_scraper.scrape(symbol="NASDAQ-NDX", sort="popular", startPage=1, endPage=1)

        assert ideas == []

    @mock.patch('tradingview_scraper.symbols.ideas.requests.get')
    def test_scrape_invalid_sort(self, mock_get, ideas_scraper):
        """Test handling of invalid sort argument."""
        ideas = ideas_scraper.scrape(symbol="NASDAQ-NDX", sort="invalid_sort", startPage=1, endPage=1)

        assert ideas == []

    @mock.patch('tradingview_scraper.symbols.ideas.requests.get')
    def test_scrape_recent_sorting_option(self, mock_get, ideas_scraper):
        """Test scraping recent ideas with mocked API call."""
        mock_response = mock.Mock()
        mock_response.status_code = 200
        mock_response.text = ""
        mock_response.json.return_value = {
            'data': {
                'ideas': {
                    'data': {
                        'items': [
                            {
                                "name": "Recent Idea",
                                "description": "Desc",
                                "symbol": {"logo_urls": ["url"]},
                                "chart_url": "url",
                                "comments_count": 1,
                                "views_count": 1,
                                "user": {"username": "User"},
                                "likes_count": 1,
                                "date_timestamp": 1234567890
                            }
                        ]
                    }
                }
            }
        }
        mock_get.return_value = mock_response

        ideas = ideas_scraper.scrape(symbol="BTCUSD", sort="recent", startPage=1, endPage=1)

        assert ideas is not None
        assert isinstance(ideas, list)
        if ideas:
            idea = ideas[0]
            assert 'title' in idea
            assert 'description' in idea
            assert 'author' in idea
            assert 'comments_count' in idea
            assert 'views_count' in idea
            assert 'likes_count' in idea
            assert 'timestamp' in idea

    @mock.patch('tradingview_scraper.symbols.ideas.requests.get')
    def test_scrape_popular_sorting_option(self, mock_get, ideas_scraper):
        """Test scraping popular ideas with mocked API call."""
        mock_response = mock.Mock()
        mock_response.status_code = 200
        mock_response.text = ""
        mock_response.json.return_value = {
            'data': {
                'ideas': {
                    'data': {
                        'items': [
                            {
                                "name": "Popular Idea",
                                "description": "Desc",
                                "symbol": {"logo_urls": ["url"]},
                                "chart_url": "url",
                                "comments_count": 100,
                                "views_count": 1000,
                                "user": {"username": "User"},
                                "likes_count": 50,
                                "date_timestamp": 1234567890
                            }
                        ]
                    }
                }
            }
        }
        mock_get.return_value = mock_response

        ideas = ideas_scraper.scrape(symbol="BTCUSD", sort="popular", startPage=1, endPage=1)
        
        assert ideas is not None
        assert isinstance(ideas, list)
        if ideas:
            idea = ideas[0]
            assert 'title' in idea
            assert 'description' in idea
            assert 'author' in idea
            assert 'comments_count' in idea
            assert 'views_count' in idea
            assert 'likes_count' in idea
            assert 'timestamp' in idea

    @mock.patch('tradingview_scraper.symbols.ideas.requests.get')
    def test_threading_avoids_rate_limiting(self, mock_get, ideas_scraper):
        """Test that threading works when scraping multiple pages (mocked)."""
        mock_response = mock.Mock()
        mock_response.status_code = 200
        mock_response.text = ""
        mock_response.json.return_value = {
            'data': {
                'ideas': {
                    'data': {
                        'items': [
                            {
                                "name": "Idea",
                                "description": "Desc",
                                "symbol": {"logo_urls": ["url"]},
                                "chart_url": "url",
                                "comments_count": 1,
                                "views_count": 1,
                                "user": {"username": "User"},
                                "likes_count": 1,
                                "date_timestamp": 1234567890
                            }
                        ]
                    }
                }
            }
        }
        mock_get.return_value = mock_response

        # Use fewer pages for mock test as speed is not the issue, just logic
        ideas = ideas_scraper.scrape(symbol="BTCUSD", sort="popular", startPage=1, endPage=5)
        
        assert ideas is not None  
        assert isinstance(ideas, list)
        # 5 pages * 1 item per page = 5 items
        assert len(ideas) == 5
        for idea in ideas[:5]: 
            assert 'title' in idea
            assert 'description' in idea
            assert 'author' in idea
            assert 'comments_count' in idea
            assert 'views_count' in idea
            assert 'likes_count' in idea
            assert 'timestamp' in idea