"""Base entity for the Smart MAIC integration."""

from __future__ import annotations

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity import EntityDescription
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import (
    DEVICE_ID,
    DEVICE_NAME,
    DEVICE_TYPE,
    DOMAIN,
    IP_ADDRESS,
)
from .coordinator import SmartMaicCoordinator


class SmartMaicEntity(CoordinatorEntity[SmartMaicCoordinator]):
    """Defines a base Smart MAIC entity."""

    _attr_has_entity_name = True
    _attr_should_poll = False

    def __init__(
        self,
        hass: HomeAssistant,
        coordinator: SmartMaicCoordinator,
        entry: ConfigEntry,
        description: EntityDescription,
    ) -> None:
        """Initialize a Smart MAIC entity."""
        super().__init__(coordinator)

        self.entity_description = description
        self.hass = hass
        self._entry = entry

        self._attr_unique_id = "-".join(
            [
                entry.data[DEVICE_ID],
                description.key,
            ]
        )

    @property
    def device_info(self) -> DeviceInfo:
        """Return device information about this Smart MAIC device."""
        return DeviceInfo(
            identifiers={
                (
                    DOMAIN,
                    self._entry.data[DEVICE_ID],
                )
            },
            name=self._entry.data[DEVICE_NAME],
            manufacturer="Smart MAIC",
            model=self._entry.data[DEVICE_TYPE],
            configuration_url=f"http://{self._entry.data[IP_ADDRESS]}",
        )

    @property
    def name(self) -> str:
        """Return the name of the entity."""
        original = super().name
        key = self.entity_description.key
        suffix = f" {key[-1]}" if key[-1] in ["1", "2", "3", "4", "5"] else ""
        return f"{original}{suffix}"
