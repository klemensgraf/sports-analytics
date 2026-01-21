import json
from pathlib import Path
from unittest.mock import MagicMock, Mock

import pytest

from sports_analytics.utils.apis import EspnAPIResource


@pytest.fixture
def mock_espn_api():
    return EspnAPIResource(base_url="http://test.com", version="v1")


@pytest.fixture
def mock_espn_api_response(nhl_scoreboard_response):
    response = Mock()
    response.json.return_value = nhl_scoreboard_response
    response.raise_for_status.return_value = None
    response.status_code = 200
    response.headers = {"content-type": "application/json"}
    return response


@pytest.fixture
def mock_espn_api_response_empty(mock_espn_api_response, nhl_scoreboard_response_empty):
    mock_espn_api_response.json.return_value = nhl_scoreboard_response_empty
    return mock_espn_api_response


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
    context.partition_key = "2026-01-19"
    return context


@pytest.fixture
def nhl_scoreboard_response():
    """Load example from file"""
    fixture_path = Path(__file__).parent / "fixtures" / "nhl_scoreboard_example.json"
    with open(fixture_path, "r") as f:
        return json.load(f)


@pytest.fixture
def nhl_scoreboard_response_empty():
    return {"events": []}
