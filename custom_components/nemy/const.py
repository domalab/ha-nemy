"""Constants for the Nemy integration."""
from typing import Final

DOMAIN: Final = "nemy"
CONF_API_KEY: Final = "api_key"
CONF_STATE: Final = "state"

DEFAULT_SCAN_INTERVAL: Final = 300  # 5 minutes
PLATFORMS: Final = ["sensor"]

# Attribution required by Home Assistant
ATTRIBUTION: Final = "Data provided by Nemy Energy API"

# Valid states
VALID_STATES: Final = ["NSW1", "QLD1", "SA1", "TAS1", "VIC1", "NEM"]