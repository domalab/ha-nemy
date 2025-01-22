"""DataUpdateCoordinator for the Nemy integration."""
from datetime import timedelta
import logging
from typing import Any

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import DOMAIN, DEFAULT_SCAN_INTERVAL
from .api import NemyApi, NemyApiError, NemyDataValidationError, NemyRateLimitError

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
        """Update data via API.
        
        Returns:
            Dict containing the latest data from the Nemy API.
            
        Raises:
            UpdateFailed: If data update fails due to API, validation, or rate limit errors.
        """
        try:
            return await self.api.get_current_summary()
        except NemyRateLimitError as err:
            _LOGGER.warning("Rate limit exceeded: %s", err)
            # Increase update interval temporarily when rate limited
            self.update_interval = timedelta(seconds=int(str(err).split("after ")[1].split(" ")[0]))
            raise UpdateFailed(f"Rate limit exceeded: {err}") from err
        except NemyDataValidationError as err:
            _LOGGER.error("Data validation error: %s", err)
            raise UpdateFailed(f"Data validation error: {err}") from err
        except NemyApiError as err:
            _LOGGER.error("API error: %s", err)
            raise UpdateFailed(f"Error communicating with API: {err}") from err
        except Exception as err:
            _LOGGER.exception("Unexpected error updating Nemy data")
            raise UpdateFailed(f"Unexpected error: {err}") from err
        finally:
            # Reset update interval to default after any error
            if self.update_interval != timedelta(seconds=DEFAULT_SCAN_INTERVAL):
                self.update_interval = timedelta(seconds=DEFAULT_SCAN_INTERVAL)