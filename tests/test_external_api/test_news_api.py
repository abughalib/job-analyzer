import os
import unittest
from unittest.mock import patch, MagicMock, AsyncMock

from utils.vars import get_news_api_key
from utils.constants import NEWS_API_URL
from job_analyzer.external_api.news_api import fetch_news
from job_analyzer.external_api.models import NewsResponse


class TestNewsAPI(unittest.IsolatedAsyncioTestCase):

    def setUp(self):
        self.news_base_api = NEWS_API_URL
        self.params = {
            "q": "TEST",
            "apiKey": get_news_api_key(),
        }

    @patch("aiohttp.ClientSession")
    async def test_fetch_news_with_mock(self, mock_client_session):
        mock_response_data = {
            "status": "ok",
            "totalResults": 1,
            "articles": [
                {
                    "source": {"id": "test-id", "name": "Test Source"},
                    "author": "Test Author",
                    "title": "Test Title",
                    "description": "Test Description",
                    "url": "http://test.com",
                    "urlToImage": "http://test.com/image.jpg",
                    "publishedAt": "2023-01-01T00:00:00Z",
                    "content": "Test content",
                }
            ],
        }

        # Fake inner response .json()
        mock_response = MagicMock()
        mock_response.json = AsyncMock(return_value=mock_response_data)
        mock_response.__aenter__.return_value = mock_response
        mock_response.__aexit__.return_value = None

        # Fake session for .get() method
        fake_session = MagicMock()
        fake_session.get.return_value = mock_response

        # Fake session for ClientSession()
        fake_session_cm = MagicMock()
        fake_session_cm.__aenter__.return_value = fake_session
        fake_session_cm.__aexit__.return_value = None
        mock_client_session.return_value = fake_session_cm

        result = await fetch_news(self.news_base_api, self.params)

        self.assertEqual(result["status"], "ok")
        self.assertEqual(result["totalResults"], 1)
        self.assertEqual(result["articles"][0]["title"], "Test Title")

    @unittest.skipIf(os.environ.get("TEST_EXTERNAL_API_REQUEST", "false"), "true")
    async def test_fetch_news(self):
        """Test fetch news API"""
        fetched_news = await fetch_news(self.news_base_api, self.params)
        assert fetched_news
        self.news_response_model = NewsResponse(**fetched_news)
        assert self.news_response_model
        self.assertIsNotNone(self.news_response_model.status)
        self.assertIsNotNone(self.news_response_model.totalResults)
        self.assertIsNotNone(self.news_response_model.articles)

    async def test_fetch_new_dummy(self):
        """Test fetch news API"""
        pass
