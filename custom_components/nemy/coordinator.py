"""DataUpdateCoordinator for the Nemy integration."""
from datetime import timedelta
import logging
from typing import Any

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import DOMAIN, DEFAULT_SCAN_INTERVAL
from .api import NemyApi, NemyApiError

_LOGGER = logging.getLogger(__name__)

class NemyDataUpdateCoordinator(DataUpdateCoordinator[dict[str, Any]]):
    """Class to manage fetching data from Nemy API."""

    def __init__(self, hass: HomeAssistant, api: NemyApi) -> None:
        """Initialize coordinator."""
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(seconds=DEFAULT_SCAN_INTERVAL),
        )
        self.api = api

    async def _async_update_data(self) -> dict[str, Any]:
        """Update data via API."""
        try:
            return await self.api.get_current_summary()
        except NemyApiError as err:
            raise UpdateFailed(f"Error communicating with API: {err}") from err