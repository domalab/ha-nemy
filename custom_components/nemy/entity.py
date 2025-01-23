"""Base entity for the Nemy integration."""
from typing import Any

from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.const import ATTR_ATTRIBUTION

from .const import DOMAIN, ATTRIBUTION
from .coordinator import NemyDataUpdateCoordinator

class NemyEntity(CoordinatorEntity[NemyDataUpdateCoordinator]):
    """Base entity class for Nemy integration."""

    _attr_has_entity_name = True
    _attr_attribution = ATTRIBUTION

    def __init__(
        self,
        coordinator: NemyDataUpdateCoordinator,
        entry_id: str,
        entity_type: str
    ) -> None:
        """Initialize the entity.
        
        Args:
            coordinator: The data update coordinator.
            entry_id: The config entry ID.
            entity_type: Type of entity (e.g., "sensor", "binary_sensor").
        """
        super().__init__(coordinator)

        # Set up unique ID base using entry_id and state
        self._attr_unique_id_base = f"{entry_id}_{coordinator.api._state}"
        self._entry_id = entry_id
        self._state = coordinator.api._state

        # Device Info
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, self._attr_unique_id_base)},
            name=f"Nemy Energy {self._state}",
            manufacturer="Nemy",
            model="Energy API",
            sw_version="1.0.0",  # Consider moving to const.py
            configuration_url="https://rapidapi.com/nemy/api/nemy",
        )

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return common entity attributes."""
        return {
            ATTR_ATTRIBUTION: self._attr_attribution,
            "state": self._state,
            "last_update": self.coordinator.last_update_success_time.isoformat()
                if hasattr(self.coordinator, "last_update_success_time") 
                and self.coordinator.last_update_success_time else None,
            "update_success": self.coordinator.last_update_success,
        }

    @property
    def available(self) -> bool:
        """Return if entity is available."""
        return self.coordinator.last_update_success and super().available