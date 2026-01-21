from datetime import date
from unittest.mock import Mock, patch

import dagster as dg
import pandas as pd

from sports_analytics.defs.hockey.nhl import nhl_games
from sports_analytics.utils.apis import EspnAPIResource

today = date.today()  # Returns today's date in yyyy-mm-dd
today_fmt = today.strftime("%Y%m%d")


class TestNhlGames:
    @patch("sports_analytics.utils.apis.get")
    def test_nhl_games(
        self,
        mock_get,
        mock_espn_api,
        mock_espn_api_response,
        mock_duckdb,
        mock_io_manager,
    ):
        # Setup mock response
        mock_get.return_value = mock_espn_api_response

        # Build context
        context = dg.build_asset_context(
            partition_key="2026-01-19",
            resources={
                "espn_api": mock_espn_api,
                "duckdb": mock_duckdb,
                "io_manager": mock_io_manager,
            },
        )

        # Call mock API and get result
        result = nhl_games(context=context)

        # Assertions
        assert isinstance(result, pd.DataFrame)
        assert len(result) == 10
        assert "id" in result.columns

    @patch("sports_analytics.utils.apis.get")
    def test_nhl_games_empty(
        self,
        mock_get,
        mock_espn_api,
        mock_espn_api_response_empty,
        mock_duckdb,
        mock_io_manager,
    ):
        # Setup mock response
        mock_get.return_value = mock_espn_api_response_empty

        # Build context
        context = dg.build_asset_context(
            partition_key="2026-01-19",
            resources={
                "espn_api": mock_espn_api,
                "duckdb": mock_duckdb,
                "io_manager": mock_io_manager,
            },
        )

        # Call mock API and get result
        result = nhl_games(context=context)

        # Assertions
        assert isinstance(result, pd.DataFrame)
        assert len(result) == 0
