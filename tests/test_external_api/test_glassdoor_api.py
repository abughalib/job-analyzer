import os
import unittest
from unittest.mock import patch, MagicMock, AsyncMock

from utils.vars import get_rapid_api_key
from utils.constants import (
    GLASSDOOR_API_URL,
    GLASSDOOR_LOCATION_API_URL,
    GLASSDOOR_HOST,
)
from job_analyzer.external_api.glassdoor import fetch_location_data, fetch_salary_data
from job_analyzer.external_api.models import GlassDoorSalaryResponse, GlassdoorLocation


class TestGlassdoorAPI(unittest.IsolatedAsyncioTestCase):

    def setUp(self):
        """Set up the test environment."""
        self.glassdoor_base_api = GLASSDOOR_API_URL
        self.glassdoor_location_api = GLASSDOOR_LOCATION_API_URL

    @unittest.skipIf(os.environ.get("TEST_EXTERNAL_API_REQUEST", "false"), "true")
    async def test_fetch_location_data(self):
        """Test Fetch Location Data API"""

        location_data = await fetch_location_data(
            self.glassdoor_location_api,
            {"x-rapidapi-key": get_rapid_api_key()},
            {"query": "New York"},
        )

        print(location_data)

        self.assertTrue(location_data)

        location_data_model = GlassdoorLocation(**location_data)
        self.assertIsNotNone(location_data_model)

    @unittest.skipIf(os.environ.get("TEST_EXTERNAL_API_REQUEST", "false"), "true")
    async def test_fetch_salary_data(self):
        """Test Fetch Salary Data API"""

        header = {
            "x-rapidapi-key": get_rapid_api_key(),
            "x-rapidapi-host": GLASSDOOR_HOST,
        }

        query = {"query": "Google"}

        salary_data = await fetch_salary_data(GLASSDOOR_API_URL, header, query)

        self.assertTrue(salary_data)

        salary_data_model = GlassDoorSalaryResponse(**salary_data)
        self.assertIsNotNone(salary_data_model)

        self.assertIsNotNone(salary_data_model.as_context())

    @patch("aiohttp.ClientSession")
    async def test_fetch_location_data_mock(self, mock_client_session):

        mock_response_data = {
            "data": [
                {
                    "countryId": 1,
                    "locationId": "eyJ0IjoiQyIsImlkIjoxMTMyMzQ4LCJuIjoiTmV3IFlvcmssIE5ZIn0=",
                    "locationName": "New York, NY",
                    "locationType": "C",
                },
                {
                    "countryId": 1,
                    "locationId": "eyJ0IjoiUyIsImlkIjo0MjgsIm4iOiJOZXcgWW9yayBTdGF0ZSJ9",
                    "locationName": "New York State",
                    "locationType": "S",
                },
            ],
            "status": True,
            "message": "Success",
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

        location_data = await fetch_location_data(
            self.glassdoor_location_api,
            {"x-rapidapi-key": get_rapid_api_key()},
            {"query": "New York"},
        )

        self.assertTrue(location_data)

        location_data_model = GlassdoorLocation(**location_data)
        self.assertIsNotNone(location_data_model)

    @patch("aiohttp.ClientSession")
    async def test_fetch_salary_data_mock(self, mock_client_session):

        mock_response_data = {
            "data": {
                "aggregateSalaryResponse": {
                    "numPages": 123,
                    "queryLocation": {
                        "id": 1,
                        "name": "United States",
                        "type": "COUNTRY",
                    },
                    "resultCount": 2449,
                    "results": [
                        {
                            "basePayStatistics": {"mean": 128223.04},
                            "currency": {"code": "USD", "id": 1},
                            "employer": {
                                "counts": {"globalJobCount": {"jobCount": 30}},
                                "id": 14048,
                                "name": "Iris Software Inc.",
                                "ratings": {"overallRating": 4},
                                "shortName": "Iris Software",
                                "squareLogoUrl": "https://media.glassdoor.com/sql/14048/iris-software-squareLogo-1615927868150.png",
                            },
                            "jobTitle": {
                                "gocId": 100092,
                                "id": 39671,
                                "text": "Senior Java Developer",
                            },
                            "payPeriod": "ANNUAL",
                            "totalAdditionalPayStatistics": {"mean": 0},
                            "totalPayStatistics": {
                                "__typename": "StatisticsResult",
                                "percentiles": [
                                    {"ident": "P10", "value": 95941.96},
                                    {"ident": "P75", "value": 149377.55},
                                    {"ident": "P90", "value": 171365.56},
                                ],
                            },
                        },
                        {
                            "basePayStatistics": {"mean": 76.05},
                            "currency": {"code": "USD", "id": 1},
                            "employer": {
                                "counts": {"globalJobCount": {"jobCount": 3670}},
                                "id": 3736,
                                "name": "Capital One Financial Corporation",
                                "ratings": {"overallRating": 3.8},
                                "shortName": "Capital One",
                                "squareLogoUrl": "https://media.glassdoor.com/sql/3736/capital-one-squareLogo-1667853695285.png",
                            },
                            "jobTitle": {
                                "gocId": 100092,
                                "id": 39671,
                                "text": "Senior Java Developer",
                            },
                            "payPeriod": "HOURLY",
                            "totalAdditionalPayStatistics": {"mean": 6.73},
                            "totalPayStatistics": {
                                "__typename": "StatisticsResult",
                                "percentiles": [
                                    {"ident": "P10", "value": 62.05},
                                    {"ident": "P90", "value": 111.78},
                                ],
                            },
                        },
                    ],
                },
                "lashedJobTitle": {"id": 39671, "text": "Senior Java Developer"},
                "occSalaryResponse": {
                    "additionalPayPercentiles": [
                        {"percentile": "P_10TH", "value": 23987.01},
                        {"percentile": "P_25TH", "value": 31017.69},
                    ],
                    "basePayPercentiles": [
                        {"percentile": "P_10TH", "value": 63014.0304},
                    ],
                    "confidence": "CONFIDENT",
                    "currency": {"code": "USD", "id": 1},
                    "employersCount": None,
                    "estimateSourceName": "V3",
                    "estimateSourceUpdateTime": "2024-06-06T23:59:59",
                    "estimateSourceVersion": "v55",
                    "jobTitle": {"id": 39671, "text": "Senior Java Developer"},
                    "payPeriod": "ANNUAL",
                    "queryLocation": {"name": "United States"},
                    "salariesCount": 5691,
                    "totalPayPercentiles": [
                        {"percentile": "P_50TH", "value": 150001.8},
                        {"percentile": "P_10TH", "value": 87001.0404},
                    ],
                },
            },
            "meta": {
                "currentPage": 1,
                "limit": 20,
                "totalRecords": 2449,
                "totalPage": 123,
            },
            "status": True,
            "message": "Successful",
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

        header = {
            "x-rapidapi-key": get_rapid_api_key(),
            "x-rapidapi-host": GLASSDOOR_HOST,
        }

        query = {"query": "Google"}

        salary_data = await fetch_salary_data(GLASSDOOR_API_URL, header, query)

        self.assertTrue(salary_data)

        salary_data_model = GlassDoorSalaryResponse(**salary_data)
        self.assertIsNotNone(salary_data_model)

        self.assertIsNotNone(salary_data_model.as_context())

        self.assertEqual(salary_data_model.status, True)
        self.assertEqual(salary_data_model.message, "Successful")
