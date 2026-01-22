from unittest.mock import patch

import dagster as dg
import pandas as pd

from sports_analytics.defs.hockey.nhl import nhl_games_final


class TestNhlGames:
    @patch("sports_analytics.utils.apis.get")
    def test_nhl_games_final(
        self,
        mock_get,
        mock_nhl_api,
        mock_nhl_api_response,
        mock_duckdb,
        mock_io_manager,
    ):
        # Setup mock response
        mock_get.return_value = mock_nhl_api_response

        # Build context
        context = dg.build_asset_context(
            partition_key="2026-01-21",
            resources={
                "nhl_api": mock_nhl_api,
                "duckdb": mock_duckdb,
                "io_manager": mock_io_manager,
            },
        )

        # Call mock API and get result
        result = nhl_games_final(context=context)

        # Assertions
        assert isinstance(result, pd.DataFrame)
        assert len(result) == 6
        assert "id" in result.columns

    @patch("sports_analytics.utils.apis.get")
    def test_nhl_games_final_empty(
        self,
        mock_get,
        mock_nhl_api_response_empty,
        mock_duckdb,
        mock_io_manager,
    ):
        # Setup mock response
        mock_get.return_value = mock_nhl_api_response_empty

        # Build context
        context = dg.build_asset_context(
            partition_key="2026-01-21",
            resources={
                "nhl_api": mock_get,
                "duckdb": mock_duckdb,
                "io_manager": mock_io_manager,
            },
        )

        # Call mock API and get result
        result = nhl_games_final(context=context)

        # Assertions
        assert isinstance(result, pd.DataFrame)
        assert len(result) == 0
