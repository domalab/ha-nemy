"""Config flow for Nemy integration."""
import voluptuous as vol
import logging
from typing import Any

from homeassistant import config_entries
from homeassistant.const import CONF_API_KEY
from homeassistant.data_entry_flow import FlowResult
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .api import NemyApi, NemyApiError, NemyRateLimitError
from .const import DOMAIN, CONF_STATE

_LOGGER = logging.getLogger(__name__)

VALID_STATES = ["NSW1", "QLD1", "SA1", "TAS1", "VIC1", "NEM"]

class NemyConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Nemy."""

    VERSION = 1

    async def async_step_user(self, user_input: dict[str, Any] | None = None) -> FlowResult:
        """Handle the initial step."""
        errors = {}

        if user_input is not None:
            _LOGGER.debug("Attempting to set up Nemy with state: %s", user_input[CONF_STATE])
            
            try:
                session = async_get_clientsession(self.hass)
                api = NemyApi(user_input[CONF_API_KEY], user_input[CONF_STATE], session)

                # Test the API connection
                _LOGGER.debug("Testing API connection...")
                try:
                    await api.get_current_summary()
                except NemyRateLimitError as err:
                    _LOGGER.error("Rate limit error during setup: %s", err)
                    errors["base"] = "rate_limit"
                except NemyApiError as err:
                    _LOGGER.error("API error during setup: %s", err)
                    error_msg = str(err).lower()
                    if "401" in error_msg:
                        errors["base"] = "invalid_api_key"
                    elif "403" in error_msg:
                        errors["base"] = "subscription_required"
                    elif "429" in error_msg:
                        errors["base"] = "rate_limit"
                    else:
                        errors["base"] = "cannot_connect"
                        _LOGGER.error("Full error details: %s", err)
                except Exception as err:
                    _LOGGER.exception("Unexpected error during setup: %s", err)
                    errors["base"] = "unknown"
                else:
                    _LOGGER.debug("API connection successful")
                    await self.async_set_unique_id(f"{user_input[CONF_STATE]}")
                    self._abort_if_unique_id_configured()
                    return self.async_create_entry(
                        title=f"Nemy {user_input[CONF_STATE]}",
                        data=user_input,
                    )

            except Exception as err:
                _LOGGER.exception("Error during setup: %s", err)
                errors["base"] = "unknown"

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_API_KEY): str,
                    vol.Required(CONF_STATE): vol.In(VALID_STATES),
                }
            ),
            errors=errors,
        )