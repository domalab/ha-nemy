"""Config flow for Nemy integration."""
import voluptuous as vol
from homeassistant import config_entries
from homeassistant.const import CONF_API_KEY
from homeassistant.data_entry_flow import FlowResult
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .api import NemyApi, NemyApiError
from .const import DOMAIN, CONF_STATE

VALID_STATES = ["NSW1", "QLD1", "SA1", "TAS1", "VIC1", "NEM"]

class NemyConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Nemy."""

    VERSION = 1

    async def async_step_user(self, user_input: dict | None = None) -> FlowResult:
        """Handle the initial step."""
        errors = {}

        if user_input is not None:
            session = async_get_clientsession(self.hass)
            api = NemyApi(user_input[CONF_API_KEY], user_input[CONF_STATE], session)

            try:
                await api.get_current_summary()
            except NemyApiError:
                errors["base"] = "cannot_connect"
            else:
                await self.async_set_unique_id(f"{user_input[CONF_STATE]}")
                self._abort_if_unique_id_configured()
                return self.async_create_entry(
                    title=f"Nemy {user_input[CONF_STATE]}",
                    data=user_input,
                )

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