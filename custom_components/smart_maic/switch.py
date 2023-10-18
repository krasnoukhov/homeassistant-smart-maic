"""Home Assistant component for accessing the Smart MAIC API.

The switch component allows control of charging dry switch.
"""
from __future__ import annotations

from homeassistant.components.switch import SwitchEntity, SwitchEntityDescription
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import (
    DOMAIN,
)
from .coordinator import SmartMaicCoordinator
from .entity import SmartMaicEntity


ENTITY_DESCRIPTIONS: dict[str, SwitchEntityDescription] = {
    "OUT": SwitchEntityDescription(
        key="OUT", translation_key="dry_switch", icon="mdi:home-switch"
    ),
}


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """Create Smart MAIC switch entities in HASS."""
    coordinator: SmartMaicCoordinator = hass.data[DOMAIN][entry.entry_id]

    async_add_entities(
        [
            SmartMaicSwitch(hass, coordinator, entry, description)
            for ent in coordinator.data
            if (description := ENTITY_DESCRIPTIONS.get(ent))
        ]
    )


class SmartMaicSwitch(SmartMaicEntity, SwitchEntity):
    """Representation of the Smart MAIC switch."""

    entity_description: SwitchEntityDescription

    @property
    def is_on(self) -> bool:
        """Return the status of the switch."""
        return self.coordinator.data[self.entity_description.key] == 1

    async def async_turn_on(self) -> None:
        """Switch dry switch."""
        await self._set_dry_swtich(1)

    async def async_turn_off(self) -> None:
        """Unswitch dry switch."""
        await self._set_dry_swtich(0)

    async def _set_dry_swtich(self, value):
        await self.coordinator.async_set_dry_switch(value)
        data = {} | self.coordinator.data
        data[self.entity_description.key] = value
        self.coordinator.async_set_updated_data(data)
