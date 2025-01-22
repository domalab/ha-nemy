"""API client for Nemy."""
import aiohttp
import async_timeout
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession

class NemyApiError(Exception):
    """Exception for Nemy API errors."""

class NemyApi:
    """Nemy API client."""

    def __init__(self, api_key: str, state: str, session: aiohttp.ClientSession) -> None:
        """Initialize the API client."""
        self._api_key = api_key
        self._state = state
        self._session = session
        self._base_url = "https://nemy.p.rapidapi.com"

    async def get_current_summary(self) -> dict:
        """Get current summary data."""
        headers = {
            "x-rapidapi-key": self._api_key,
            "x-rapidapi-host": "nemy.p.rapidapi.com"
        }
        
        url = f"{self._base_url}/NEM/summary/current"
        params = {"state": self._state}

        try:
            async with async_timeout.timeout(10):
                async with self._session.get(url, headers=headers, params=params) as response:
                    if response.status != 200:
                        raise NemyApiError(f"API request failed with status {response.status}")
                    return await response.json()
        except Exception as err:
            raise NemyApiError(f"Error communicating with API: {err}") from err