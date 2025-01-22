"""Constants for the Nemy integration."""
from typing import Final

DOMAIN: Final = "nemy"
CONF_API_KEY: Final = "api_key"
CONF_STATE: Final = "state"

DEFAULT_SCAN_INTERVAL = 300  # 5 minutes
PLATFORMS = ["sensor"]