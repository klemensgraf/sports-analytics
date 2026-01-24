import json
from pathlib import Path
from unittest.mock import MagicMock, Mock

import pytest

from sports_analytics.utils.apis import NhlAPIResource


@pytest.fixture
def mock_nhl_api():
    return NhlAPIResource(base_url="http://test.com/v1")


@pytest.fixture
def mock_nhl_api_response():
    response = Mock()
    response.raise_for_status.return_value = None
    response.status_code = 200
    response.headers = {"content-type": "application/json"}
    return response


@pytest.fixture
def mock_nhl_games_final_response(mock_nhl_api_response, nhl_score_by_date_response):
    mock_nhl_api_response.json.return_value = nhl_score_by_date_response
    return mock_nhl_api_response


@pytest.fixture
def mock_nhl_standings_now_response(mock_nhl_api_response, nhl_standings_now_response):
    mock_nhl_api_response.json.return_value = nhl_standings_now_response
    return mock_nhl_api_response


@pytest.fixture
def mock_nhl_api_response_empty(mock_nhl_api_response):
    def _make_response(key):
        mock_nhl_api_response.json.return_value = {key: []}
        return mock_nhl_api_response

    return _make_response


@pytest.fixture
def mock_duckdb():
    return MagicMock()


@pytest.fixture
def mock_io_manager():
    return MagicMock()


@pytest.fixture
def mock_context():
    """Mock context for helper function tests"""
    context = MagicMock()
    context.asset_key.path = ["test_table"]
    context.resources.io_manager._schema = "test_schema"
    context.partition_key = "2026-01-21"
    return context


@pytest.fixture
def nhl_score_by_date_response():
    """Load example from file"""
    fixture_path = Path(__file__).parent / "fixtures" / "nhl_score_by_date_example.json"
    with open(fixture_path, "r") as f:
        return json.load(f)


@pytest.fixture
def nhl_standings_now_response():
    """Load example from file"""
    fixture_path = Path(__file__).parent / "fixtures" / "nhl_standings_now.json"
    with open(fixture_path, "r") as f:
        return json.load(f)
