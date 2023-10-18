"""DataUpdateCoordinator for the Smart MAIC integration."""
from __future__ import annotations

import logging
from typing import Any

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

from .smart_maic import SmartMaic
from .const import (
    DOMAIN,
)

_LOGGER = logging.getLogger(__name__)


class SmartMaicCoordinator(DataUpdateCoordinator[dict[str, Any]]):
    """Smart MAIC Coordinator class."""

    def __init__(self, smart_maic: SmartMaic, hass: HomeAssistant) -> None:
        """Initialize."""
        self._smart_maic = smart_maic

        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
        )

    def _set_mqtt_config(self) -> None:
        """Set Smart MAIC MQTT config."""
        return self._smart_maic.set_mqtt_config()

    async def async_set_mqtt_config(self) -> None:
        """Set Smart MAIC MQTT config."""
        return await self.hass.async_add_executor_job(self._set_mqtt_config)

    def _set_consumption(self, key: str, value: float) -> None:
        """Set Smart MAIC consumption value."""
        return self._smart_maic.set_consumption(key=key, value=value)

    async def async_set_consumption(self, key: str, value: float) -> None:
        """Set Smart MAIC consumption value."""
        return await self.hass.async_add_executor_job(self._set_consumption, key, value)

    def _set_dry_switch(self, value: int) -> None:
        """Set Smart MAIC dry switch value."""
        return self._smart_maic.set_dry_switch(value=value)

    async def async_set_dry_switch(self, value: int) -> None:
        """Set Smart MAIC dry switch value."""
        return await self.hass.async_add_executor_job(self._set_dry_switch, value)
