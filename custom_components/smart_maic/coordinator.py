"""DataUpdateCoordinator for the Smart MAIC integration."""

from __future__ import annotations

from datetime import timedelta, datetime
import logging
from typing import Any

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator
from homeassistant.util.dt import utcnow

from .smart_maic import SmartMaic
from .const import (
    DEFAULT_EXPIRATION,
    DOMAIN,
    EXPIRATION,
)

_LOGGER = logging.getLogger(__name__)


class SmartMaicCoordinator(DataUpdateCoordinator[dict[str, Any]]):
    """Smart MAIC Coordinator class."""

    _smart_maic: SmartMaic | None = None
    _last_update_at: datetime | None = None

    def __init__(self, smart_maic: SmartMaic, hass: HomeAssistant) -> None:
        """Initialize."""
        self._smart_maic = smart_maic

        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
        )

        self.set_update_interval()

    def set_update_interval(self):
        """Set update interval."""
        self.update_interval = timedelta(
            seconds=self.config_entry.options.get(EXPIRATION) or DEFAULT_EXPIRATION
        )

    def async_set_updated_data(self, data: dict[str, Any]):
        """Set updated data and note the time."""
        super().async_set_updated_data(data)
        self._last_update_at = utcnow().replace(microsecond=0)

    async def _async_update_data(self) -> dict[str, Any]:
        """Check for stale data and reset it or return the latest data."""
        return await self.hass.async_add_executor_job(self._update_data)

    def _update_data(self) -> dict[str, Any]:
        """Check for stale data and reset it or return the latest data."""
        _LOGGER.debug(f"Last data update: {self._last_update_at}")

        if (
            self._last_update_at
            and self.data
            and utcnow().replace(microsecond=0) - self._last_update_at
            >= self.update_interval
        ):
            _LOGGER.debug("Data expired")
            self.data = {}

        return self.data

    def _get_config(self) -> None:
        """Get Smart MAIC config."""
        return self._smart_maic.set_mqtt_config()

    async def async_get_config(self) -> None:
        """Get Smart MAIC config."""
        return await self.hass.async_add_executor_job(self._get_config)

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
