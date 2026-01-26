from unittest.mock import patch

import dagster as dg
import pandas as pd

from sports_analytics.defs.nhl.raw import (
    nhl_games_final,
    nhl_players,
    nhl_standings_now,
)


class TestNhlGamesFinal:
    @patch("sports_analytics.utils.apis.get")
    def test_nhl_games_final(
        self,
        mock_get,
        mock_nhl_api,
        mock_nhl_games_final_response,
        mock_duckdb,
        mock_io_manager,
    ):
        # Setup mock response
        mock_get.return_value = mock_nhl_games_final_response

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
        mock_get.return_value = mock_nhl_api_response_empty("games")

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


class TestNhlStandingsNow:
    @patch("sports_analytics.utils.apis.get")
    def test_nhl_standings_now(
        self,
        mock_get,
        mock_nhl_api,
        mock_nhl_standings_now_response,
    ):
        # Setup mock response
        mock_get.return_value = mock_nhl_standings_now_response

        # Build context
        context = dg.build_asset_context(
            resources={
                "nhl_api": mock_nhl_api,
            },
        )

        # Call mock API and get result
        result = nhl_standings_now(context=context)

        # Assertions
        assert isinstance(result, pd.DataFrame)
        assert len(result) == 32
        assert "conference_name" in result.columns


class TestNhlPlayers:
    @patch("sports_analytics.utils.apis.get")
    def test_nhl_players(
        self,
        mock_get,
        mock_nhl_api,
        mock_nhl_players_response,
        mock_duckdb,
        mock_io_manager,
    ):
        # Setup mock response
        mock_get.return_value = mock_nhl_players_response

        # Fake DB query results returned by DuckDB
        fake_teams = [
            ("BOS", "Boston Bruins"),
            ("CHI", "Chicago Blackhawks"),
        ]
        mock_duckdb._mock_connection.execute.return_value.fetchall.return_value = (
            fake_teams
        )

        # Build context
        context = dg.build_asset_context(
            resources={
                "nhl_api": mock_nhl_api,
                "duckdb": mock_duckdb,
                "io_manager": mock_io_manager,
            }
        )

        # Call mock API and get result
        result = nhl_players(context=context)

        # Assertions
        assert isinstance(result, pd.DataFrame)
        assert len(result) > 30  # It should contains two teams
        assert "sweater_number" in result.columns
        assert "BOS" in result["team_abbrev"].to_list()
        assert "CHI" in result["team_abbrev"].to_list()
