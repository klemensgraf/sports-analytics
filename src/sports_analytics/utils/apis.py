import dagster as dg
from requests import Response, get


class EspnAPIResource(dg.ConfigurableResource):
    base_url: str
    version: str

    def get(
        self, url: str, params: dict[str, str] = {}, headers: dict[str, str] = {}
    ) -> dict:
        # Construct URL
        url = f"{self.base_url}/{self.version}{url}"

        # Get response and p
        response: Response = get(url, params=params, headers=headers)
        return self._handle_response(response)

    def _handle_response(self, response: Response) -> dict:
        response.raise_for_status()

        # Try to parse JSON but only if content-type indicates JSON
        content_type: str = response.headers.get("content-type", "").lower()
        if response.status_code == 200 and "application/json" in content_type:
            try:
                data: dict = response.json()
            except ValueError as e:
                raise ValueError("Cannot parse JSON response:", e)
        else:
            raise ValueError("Content type of response is not in JSON:", content_type)

        return response.json()
