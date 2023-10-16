"""Home Assistant component for accessing the Smart MAIC API.

The sensor component creates multipe sensors regarding Smart MAIC status.
"""
from __future__ import annotations

from typing import cast

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import (
    UnitOfTemperature,
    UnitOfElectricCurrent,
    UnitOfElectricPotential,
    UnitOfEnergy,
    UnitOfPower,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import StateType

from .const import (
    DOMAIN,
)
from .coordinator import SmartMaicCoordinator
from .entity import SmartMaicEntity

ENTITY_DESCRIPTIONS: dict[str, SensorEntityDescription] = {
    "V": SensorEntityDescription(
        key="V",
        translation_key="voltage",
        device_class=SensorDeviceClass.VOLTAGE,
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement=UnitOfElectricPotential.VOLT,
        suggested_display_precision=2,
    ),
    "A": SensorEntityDescription(
        key="A",
        translation_key="current",
        device_class=SensorDeviceClass.CURRENT,
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement=UnitOfElectricCurrent.AMPERE,
        suggested_display_precision=2,
    ),
    "W": SensorEntityDescription(
        key="W",
        translation_key="power",
        device_class=SensorDeviceClass.POWER,
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement=UnitOfPower.WATT,
        suggested_display_precision=0,
    ),
    "Wh": SensorEntityDescription(
        key="Wh",
        translation_key="consumption",
        device_class=SensorDeviceClass.ENERGY,
        state_class=SensorStateClass.TOTAL_INCREASING,
        native_unit_of_measurement=UnitOfEnergy.WATT_HOUR,
        suggested_display_precision=0,
    ),
    "PF": SensorEntityDescription(
        key="PF",
        translation_key="power_factor",
        device_class=SensorDeviceClass.POWER_FACTOR,
        state_class=SensorStateClass.MEASUREMENT,
        suggested_display_precision=2,
    ),
    "Temp": SensorEntityDescription(
        key="Temp",
        translation_key="device_temperature",
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        suggested_display_precision=0,
    ),
}


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """Create Smart MAIC sensor entities in HASS."""
    coordinator: SmartMaicCoordinator = hass.data[DOMAIN][entry.entry_id]

    async_add_entities(
        [
            SmartMaicSensor(hass, coordinator, entry, description)
            for ent in coordinator.data
            if (description := ENTITY_DESCRIPTIONS.get(ent))
        ]
    )


class SmartMaicSensor(SmartMaicEntity, SensorEntity):
    """Representation of the Smart MAIC sensor."""

    @property
    def native_value(self) -> StateType:
        """Return the state of the sensor."""
        value = self.coordinator.data[self.entity_description.key]
        return cast(StateType, value)
