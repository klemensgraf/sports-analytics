import dagster as dg
from requests import Response, get


class NhlAPIResource(dg.ConfigurableResource):
    base_url: str

    def _handle_respone(self, response: Response) -> dict:
        """Handles API response and check for status code errors"""
        response.raise_for_status()

        # Try to parse JSON but only if content-type indicates JSON
        content_type: str = response.headers.get("content-type", "").lower()
        if response.status_code == 200 and "application/json" in content_type:
            try:
                _: dict = response.json()
            except ValueError as e:
                raise ValueError("Cannot parse JSON response:", e)
        else:
            raise ValueError("Content type of response is not in JSON:", content_type)

        return response.json()

    def get(
        self, url: str, params: dict[str, str] = {}, headers: dict[str, str] = {}
    ) -> dict:
        """Returns data with HTTP GET method from API endpoint"""
        url = f"{self.base_url}{url}"

        # Get response
        response: Response = get(url, params=params, headers=headers)

        # Check for errors and return response
        return self._handle_respone(response)
