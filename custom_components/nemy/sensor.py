"""Sensor platform for the Nemy integration."""
from dataclasses import dataclass
from typing import Final

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import (
    PERCENTAGE,
    CURRENCY_CENT,
    CURRENCY_DOLLAR,
    UnitOfEnergy,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN
from .coordinator import NemyDataUpdateCoordinator
from .entity import NemyEntity

@dataclass
class NemySensorEntityDescription(SensorEntityDescription):
    """Class describing Nemy sensor entities."""

SENSOR_TYPES: Final = [
    NemySensorEntityDescription(
        key="price_household",
        name="Household Price",
        native_unit_of_measurement=CURRENCY_CENT,
        device_class=SensorDeviceClass.MONETARY,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    NemySensorEntityDescription(
        key="price_dispatch",
        name="Dispatch Price",
        native_unit_of_measurement=CURRENCY_DOLLAR,
        device_class=SensorDeviceClass.MONETARY,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    NemySensorEntityDescription(
        key="renewables",
        name="Renewables Percentage",
        native_unit_of_measurement=PERCENTAGE,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    NemySensorEntityDescription(
        key="renewables_category",
        name="Renewables Category",
        icon="mdi:leaf",
    ),
    NemySensorEntityDescription(
        key="price_category",
        name="Price Category",
        icon="mdi:currency-usd",
    ),
]

async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Nemy sensor based on a config entry."""
    coordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities(
        NemySensor(coordinator, entry.entry_id, description)
        for description in SENSOR_TYPES
    )

class NemySensor(NemyEntity, SensorEntity):
    """Representation of a Nemy sensor."""

    entity_description: NemySensorEntityDescription

    def __init__(
        self,
        coordinator: NemyDataUpdateCoordinator,
        entry_id: str,
        description: NemySensorEntityDescription,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator, entry_id)
        self.entity_description = description
        self._attr_unique_id = f"{entry_id}_{description.key}"

    @property
    def native_value(self):
        """Return the state of the sensor."""
        return self.coordinator.data.get(self.entity_description.key)