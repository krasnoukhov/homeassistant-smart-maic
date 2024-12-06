"""Home Assistant component for accessing the Smart MAIC API.

The number component allows control of charging consumption.
"""

from __future__ import annotations

import sys
from typing import cast

from homeassistant.components.number import (
    NumberDeviceClass,
    NumberEntity,
    NumberEntityDescription,
    NumberMode,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import UnitOfEnergy
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import (
    DOMAIN,
)
from .coordinator import SmartMaicCoordinator
from .entity import SmartMaicEntity


def phase_descriptions(index="") -> dict[str, NumberEntityDescription]:
    """Generate entity descriptions for a given phase"""
    return {
        f"Wh{index}": NumberEntityDescription(
            key=f"Wh{index}",
            translation_key="consumption",
            device_class=NumberDeviceClass.ENERGY,
            mode=NumberMode.BOX,
            native_unit_of_measurement=UnitOfEnergy.WATT_HOUR,
            native_min_value=0,
            native_max_value=sys.maxsize,
            entity_registry_enabled_default=False,
        ),
    }


ENTITY_DESCRIPTIONS: dict[str, NumberEntityDescription] = {
    **phase_descriptions(""),
    **phase_descriptions("1"),
    **phase_descriptions("2"),
    **phase_descriptions("3"),
}


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """Create Smart MAIC number entities in HASS."""
    coordinator: SmartMaicCoordinator = hass.data[DOMAIN][entry.entry_id]

    async_add_entities(
        [
            SmartMaicNumber(hass, coordinator, entry, description)
            for ent in coordinator.data
            if (description := ENTITY_DESCRIPTIONS.get(ent))
        ]
    )


class SmartMaicNumber(SmartMaicEntity, NumberEntity):
    """Representation of the Smart MAIC number."""

    entity_description: NumberEntityDescription
    _attr_entity_registry_enabled_default = False

    @property
    def native_value(self) -> int | None:
        """Return the value of the entity."""
        value = self.coordinator.data.get(self.entity_description.key)
        return None if value is None else cast(int | None, value)

    async def async_set_native_value(self, value: int) -> None:
        """Set the value of the entity."""
        print(self.entity_description.key)
        await self.coordinator.async_set_consumption(self.entity_description.key, value)
