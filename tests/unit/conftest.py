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
def mock_nhl_games_final_response(mock_nhl_api_response):
    """Mocks response from API with example content from a point-in-time"""
    content = get_file_content("nhl_score_by_date.json")

    mock_nhl_api_response.json.return_value = content
    return mock_nhl_api_response


@pytest.fixture
def mock_nhl_standings_now_response(mock_nhl_api_response):
    """Mocks response from API with example content from a point-in-time"""
    content = get_file_content("nhl_standings_now.json")

    mock_nhl_api_response.json.return_value = content
    return mock_nhl_api_response


@pytest.fixture
def mock_nhl_players_response(mock_nhl_api_response):
    """Mocks response from API with example content from a point-in-time"""
    content = get_file_content("nhl_players_by_team.json")

    mock_nhl_api_response.json.return_value = content
    return mock_nhl_api_response


@pytest.fixture
def mock_nhl_api_response_empty(mock_nhl_api_response):
    def _make_response(key):
        mock_nhl_api_response.json.return_value = {key: []}
        return mock_nhl_api_response

    return _make_response


@pytest.fixture
def mock_duckdb():
    mock_resource = MagicMock()
    mock_connection = MagicMock()

    # Setup context manager for `with duckdb.get_connection() as conn:`
    mock_resource.get_connection.return_value.__enter__.return_value = mock_connection
    mock_resource.get_connection.return_value.__exit__.return_value = None

    # Expose connection for easy test access
    mock_resource._mock_connection = mock_connection

    return mock_resource


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


def get_file_content(filename) -> dict:
    """Reads content of a JSON file and returns it"""
    fixture_path = Path(__file__).parent / "fixtures" / filename
    with open(fixture_path, "r") as f:
        return json.load(f)
