from unittest.mock import Mock, patch

import pytest


class TestEspnAPIResource:
    endpoint_url = "/sports/hockey/nhl/scoreboard"

    @patch("sports_analytics.utils.apis.get")
    def test_get_successful_json_response(
        self, mock_get, mock_espn_api, mock_espn_api_response
    ):
        """Should return parsed JSON for successful response"""
        mock_get.return_value = mock_espn_api_response

        result = mock_espn_api.get(self.endpoint_url, params={"dates": "20260119"})

        assert "events" in result
        mock_get.assert_called_once_with(
            f"http://test.com/v1{self.endpoint_url}",
            params={"dates": "20260119"},
            headers={},
        )

    @patch("sports_analytics.utils.apis.get")
    def test_get_empty_response(
        self, mock_get, mock_espn_api, mock_espn_api_response_empty
    ):
        """Should hanlde empty events list"""
        mock_get.return_value = mock_espn_api_response_empty

        result = mock_espn_api.get(self.endpoint_url)

        assert result == {"events": []}

    @patch("sports_analytics.utils.apis.get")
    def test_get_http_error_raises_exception(self, mock_get, mock_espn_api):
        """Should raise HTTPError for 4xx/5xx responses"""
        from requests.exceptions import HTTPError

        mock_response = Mock()
        mock_response.raise_for_status.side_effect = HTTPError("404 Not Found")
        mock_get.return_value = mock_response

        with pytest.raises(HTTPError):
            mock_espn_api.get(self.endpoint_url)

    @patch("sports_analytics.utils.apis.get")
    def test_get_non_json_content_type_raises_error(self, mock_get, mock_espn_api):
        """Should raise ValueError when content-type is not JSON"""
        mock_response = Mock()
        mock_response.raise_for_status.return_value = None
        mock_response.status_code = 200
        mock_response.headers = {"content-type": "text/html"}
        mock_get.return_value = mock_response

        with pytest.raises(ValueError, match="Content type.*not in JSON"):
            mock_espn_api.get(self.endpoint_url)

    @patch("sports_analytics.utils.apis.get")
    def test_get_invalid_json_raises_error(self, mock_get, mock_espn_api):
        """Should raise ValueError when JSON parsing fails"""
        mock_response = Mock()
        mock_response.raise_for_status.return_value = None
        mock_response.status_code = 200
        mock_response.headers = {"content-type": "application/json"}
        mock_response.json.side_effect = ValueError("Invalid JSON")
        mock_get.return_value = mock_response

        with pytest.raises(ValueError, match="Cannot parse JSON"):
            mock_espn_api.get(self.endpoint_url)
