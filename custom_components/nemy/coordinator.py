"""DataUpdateCoordinator for the Nemy integration."""
from datetime import timedelta, datetime
import logging
from typing import Any
from collections import deque

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
        # Add diagnostic tracking
        self._update_history = deque(maxlen=50)  # Keep last 50 updates
        self.last_exception = None
        self.last_update_success_time = None

    async def _async_update_data(self) -> dict[str, Any]:
        """Update data via API.
        
        Returns:
            Dict containing the latest data from the Nemy API.
            
        Raises:
            UpdateFailed: If data update fails due to API, validation, or rate limit errors.
        """
        start_time = datetime.now()
        success = False
        error = None
        data = None

        try:
            # Log diagnostic information if recent failures
            if (len(self._update_history) >= 2 and 
                any(not update["success"] for update in list(self._update_history)[-2:])):
                _LOGGER.debug(
                    "Update attempt after recent failure - Rate limits: %d requests in last minute",
                    len(self.api._minute_requests)
                )

            data = await self.api.get_current_summary()
            success = True
            self.last_exception = None
            self.last_update_success_time = datetime.now()
            return data

        except NemyRateLimitError as err:
            error = err
            _LOGGER.warning("Rate limit exceeded: %s", err)
            # Increase update interval temporarily when rate limited
            self.update_interval = timedelta(seconds=int(str(err).split("after ")[1].split(" ")[0]))
            raise UpdateFailed(f"Rate limit exceeded: {err}") from err

        except NemyDataValidationError as err:
            error = err
            _LOGGER.error("Data validation error: %s", err)
            raise UpdateFailed(f"Data validation error: {err}") from err

        except NemyApiError as err:
            error = err
            _LOGGER.error("API error: %s", err)
            raise UpdateFailed(f"Error communicating with API: {err}") from err

        except Exception as err:
            error = err
            _LOGGER.exception("Unexpected error updating Nemy data")
            raise UpdateFailed(f"Unexpected error: {err}") from err

        finally:
            # Record update history for diagnostics
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()
            
            update_record = {
                "timestamp": start_time,
                "success": success,
                "duration": duration,
                "error": str(error) if error else None,
                "data_received": bool(data),
                "update_interval": self.update_interval.total_seconds()
            }
            self._update_history.append(update_record)
            
            # Store last exception for diagnostics
            if error:
                self.last_exception = error

            # Reset update interval to default after any error
            if self.update_interval != timedelta(seconds=DEFAULT_SCAN_INTERVAL):
                self.update_interval = timedelta(seconds=DEFAULT_SCAN_INTERVAL)
                
            # Log extended diagnostic info on failures
            if not success:
                _LOGGER.debug(
                    "Update failed - Duration: %.2fs, Error: %s",
                    duration,
                    error
                )