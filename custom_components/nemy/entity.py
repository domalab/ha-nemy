"""Base entity for the Nemy integration."""
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import NemyDataUpdateCoordinator

class NemyEntity(CoordinatorEntity[NemyDataUpdateCoordinator]):
    """Base entity for Nemy."""

    def __init__(self, coordinator: NemyDataUpdateCoordinator, entry_id: str) -> None:
        """Initialize the entity."""
        super().__init__(coordinator)
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, entry_id)},
            name=f"Nemy {coordinator.api._state}",
            manufacturer="Nemy",
            model="Energy API",
        )