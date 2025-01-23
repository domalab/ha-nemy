"""Sensor platform for the Nemy integration."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Final

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
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import StateType

from .const import DOMAIN
from .coordinator import NemyDataUpdateCoordinator
from .entity import NemyEntity

@dataclass
class NemySensorEntityDescription(SensorEntityDescription):
    """Class describing Nemy sensor entities."""
    value_fn: callable = lambda x: x  # Default value processor

SENSOR_TYPES: Final = [
    NemySensorEntityDescription(
        key="price_household",
        translation_key="price_household",
        name="Household Price",
        native_unit_of_measurement=CURRENCY_CENT,
        suggested_display_precision=2,
        device_class=SensorDeviceClass.MONETARY,
        state_class=SensorStateClass.TOTAL,  # Changed from MEASUREMENT to TOTAL
        value_fn=lambda x: float(x),
        entity_registry_enabled_default=True,
        icon="mdi:currency-usd",
    ),
    NemySensorEntityDescription(
        key="price_dispatch",
        translation_key="price_dispatch",
        name="Dispatch Price",
        native_unit_of_measurement=CURRENCY_DOLLAR,
        suggested_display_precision=2,
        device_class=SensorDeviceClass.MONETARY,
        state_class=SensorStateClass.TOTAL,  # Changed from MEASUREMENT to TOTAL
        value_fn=lambda x: float(x),
        entity_registry_enabled_default=True,
        icon="mdi:currency-usd",
    ),
    NemySensorEntityDescription(
        key="renewables",
        translation_key="renewables",
        name="Renewables Percentage",
        native_unit_of_measurement=PERCENTAGE,
        suggested_display_precision=1,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda x: float(x),
        entity_registry_enabled_default=True,
        icon="mdi:solar-power",
    ),
    NemySensorEntityDescription(
        key="renewables_no_rooftop",
        translation_key="renewables_no_rooftop",
        name="Grid Renewables",
        native_unit_of_measurement=PERCENTAGE,
        suggested_display_precision=1,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda x: float(x),
        entity_registry_enabled_default=True,
        icon="mdi:transmission-tower-export",
    ),
    NemySensorEntityDescription(
        key="renewables_category",
        translation_key="renewables_category",
        name="Renewables Category",
        value_fn=str,
        entity_registry_enabled_default=True,
        icon="mdi:leaf",
    ),
    NemySensorEntityDescription(
        key="price_category",
        translation_key="price_category",
        name="Price Category",
        value_fn=str,
        entity_registry_enabled_default=True,
        icon="mdi:currency-usd",
    ),
]

async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Nemy sensors based on a config entry."""
    coordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities(
        NemySensor(
            coordinator=coordinator,
            entry_id=entry.entry_id,
            description=description,
        )
        for description in SENSOR_TYPES
    )

class NemySensor(NemyEntity, SensorEntity):
    """Implementation of a Nemy sensor."""

    entity_description: NemySensorEntityDescription

    def __init__(
        self,
        coordinator: NemyDataUpdateCoordinator,
        entry_id: str,
        description: NemySensorEntityDescription,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator, entry_id, "sensor")
        self.entity_description = description
        self._attr_unique_id = f"{self._attr_unique_id_base}_{description.key}"
        self._attr_has_entity_name = True

    @property
    def native_value(self) -> StateType:
        """Return the state of the sensor."""
        try:
            value = self.coordinator.data.get(self.entity_description.key)
            if value is not None:
                return self.entity_description.value_fn(value)
            return None
        except (TypeError, ValueError) as err:
            self.coordinator._LOGGER.error(
                "Error converting value for %s: %s",
                self.entity_description.key,
                err
            )
            return None

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return additional state attributes."""
        attrs = super().extra_state_attributes
        
        # Add percentile information where applicable
        if self.entity_description.key in ["price_household", "renewables"]:
            percentile_key = f"{self.entity_description.key}_percentile"
            if percentile_value := self.coordinator.data.get(percentile_key):
                attrs["percentile"] = float(percentile_value)

        return attrs