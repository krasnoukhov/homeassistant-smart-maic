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


def phase_descriptions(index="") -> dict[str, SensorEntityDescription]:
    """Generate entity descriptions for a given phase"""
    return {
        f"V{index}": SensorEntityDescription(
            key=f"V{index}",
            translation_key="voltage",
            device_class=SensorDeviceClass.VOLTAGE,
            state_class=SensorStateClass.MEASUREMENT,
            native_unit_of_measurement=UnitOfElectricPotential.VOLT,
            suggested_display_precision=2,
        ),
        f"A{index}": SensorEntityDescription(
            key=f"A{index}",
            translation_key="current",
            device_class=SensorDeviceClass.CURRENT,
            state_class=SensorStateClass.MEASUREMENT,
            native_unit_of_measurement=UnitOfElectricCurrent.AMPERE,
            suggested_display_precision=2,
        ),
        f"W{index}": SensorEntityDescription(
            key=f"W{index}",
            translation_key="power",
            device_class=SensorDeviceClass.POWER,
            state_class=SensorStateClass.MEASUREMENT,
            native_unit_of_measurement=UnitOfPower.WATT,
            suggested_display_precision=0,
        ),
        f"rW{index}": SensorEntityDescription(
            key=f"rW{index}",
            translation_key="return_power",
            device_class=SensorDeviceClass.POWER,
            state_class=SensorStateClass.MEASUREMENT,
            native_unit_of_measurement=UnitOfPower.WATT,
            suggested_display_precision=0,
            entity_registry_enabled_default=False,
        ),
        f"Wh{index}": SensorEntityDescription(
            key=f"Wh{index}",
            translation_key="consumption",
            device_class=SensorDeviceClass.ENERGY,
            state_class=SensorStateClass.TOTAL_INCREASING,
            native_unit_of_measurement=UnitOfEnergy.WATT_HOUR,
            suggested_display_precision=0,
        ),
        f"rWh{index}": SensorEntityDescription(
            key=f"rWh{index}",
            translation_key="return",
            device_class=SensorDeviceClass.ENERGY,
            state_class=SensorStateClass.TOTAL,
            native_unit_of_measurement=UnitOfEnergy.WATT_HOUR,
            suggested_display_precision=0,
            entity_registry_enabled_default=False,
        ),
        f"PF{index}": SensorEntityDescription(
            key=f"PF{index}",
            translation_key="power_factor",
            device_class=SensorDeviceClass.POWER_FACTOR,
            state_class=SensorStateClass.MEASUREMENT,
            suggested_display_precision=2,
        ),
    }


ENTITY_DESCRIPTIONS: dict[str, SensorEntityDescription] = {
    **phase_descriptions(""),
    **phase_descriptions("1"),
    **phase_descriptions("2"),
    **phase_descriptions("3"),
    "Temp": SensorEntityDescription(
        key="Temp",
        translation_key="device_temperature",
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        suggested_display_precision=0,
    ),
}

# NOTE: dict keys here match API response
# But we align "key" values with single phase for consistency
TOTAL_ENTITY_DESCRIPTIONS: dict[str, SensorEntityDescription] = {
    "A": SensorEntityDescription(
        key="A",
        translation_key="total_current",
        device_class=SensorDeviceClass.CURRENT,
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement=UnitOfElectricCurrent.AMPERE,
        suggested_display_precision=2,
    ),
    "W": SensorEntityDescription(
        key="W",
        translation_key="total_power",
        device_class=SensorDeviceClass.POWER,
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement=UnitOfPower.WATT,
        suggested_display_precision=0,
    ),
    "rW": SensorEntityDescription(
        key="rW",
        translation_key="total_return_power",
        device_class=SensorDeviceClass.POWER,
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement=UnitOfPower.WATT,
        suggested_display_precision=0,
        entity_registry_enabled_default=False,
    ),
    "TWh": SensorEntityDescription(
        key="Wh",
        translation_key="total_consumption",
        device_class=SensorDeviceClass.ENERGY,
        state_class=SensorStateClass.TOTAL_INCREASING,
        native_unit_of_measurement=UnitOfEnergy.WATT_HOUR,
        suggested_display_precision=0,
    ),
    "rTWh": SensorEntityDescription(
        key="rWh",
        translation_key="total_return",
        device_class=SensorDeviceClass.ENERGY,
        state_class=SensorStateClass.TOTAL,
        native_unit_of_measurement=UnitOfEnergy.WATT_HOUR,
        suggested_display_precision=0,
        entity_registry_enabled_default=False,
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

    # NOTE: check if we're dealing with 3-phase device
    if coordinator.data.get("A1"):
        async_add_entities(
            [
                SmartMaicTotalSensor(hass, coordinator, entry, description)
                for ent in TOTAL_ENTITY_DESCRIPTIONS
                if (description := TOTAL_ENTITY_DESCRIPTIONS.get(ent))
            ]
        )


class SmartMaicSensor(SmartMaicEntity, SensorEntity):
    """Representation of the Smart MAIC sensor."""

    @property
    def native_value(self) -> StateType:
        """Return the state of the sensor."""
        value = self.coordinator.data[self.entity_description.key]
        return cast(StateType, value)


class SmartMaicTotalSensor(SmartMaicEntity, SensorEntity):
    """Representation of the Smart MAIC total sensor."""

    @property
    def native_value(self) -> StateType:
        """Return the state of the sensor."""
        base_key = self.entity_description.key
        data = self.coordinator.data
        value = data[f"{base_key}1"] + data[f"{base_key}2"] + data[f"{base_key}3"]
        return cast(StateType, value)
