"""The Smart MAIC integration."""

from __future__ import annotations

import logging
import asyncio

from homeassistant.components import mqtt
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant, callback
from homeassistant.exceptions import ConfigEntryNotReady
from homeassistant.util.json import json_loads_object

from .smart_maic import SmartMaic
from .coordinator import SmartMaicCoordinator
from .const import (
    DEVICE_ID,
    DOMAIN,
    PREFIX,
)

PLATFORMS = [Platform.SENSOR, Platform.NUMBER, Platform.SWITCH]

_LOGGER = logging.getLogger(__name__)


async def update_listener(hass, entry):
    """Handle options update."""
    coordinator: SmartMaicCoordinator = hass.data[DOMAIN][entry.entry_id]
    coordinator.set_update_interval()


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Smart MAIC from a config entry."""
    if not await mqtt.async_wait_for_mqtt_client(hass):
        raise ConfigEntryNotReady("MQTT is not available")

    smart_maic = SmartMaic(entry.data)
    coordinator = SmartMaicCoordinator(smart_maic, hass)
    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = coordinator

    json_received = False

    async def wait_for_json() -> None:
        while not json_received:
            await asyncio.sleep(5)
            _LOGGER.debug("Has no JSON")

    @callback
    def async_json_received(msg: mqtt.ReceiveMessage) -> None:
        nonlocal json_received
        json_received = True

        data = json_loads_object(msg.payload)
        _LOGGER.debug(f"MQTT data: {data}")
        coordinator.async_set_updated_data(data)

    topic = "/".join([PREFIX, entry.data[DEVICE_ID], "JSON"])
    _LOGGER.debug(f"Listening for MQTT topic: {topic}")
    entry.async_on_unload(await mqtt.async_subscribe(hass, topic, async_json_received))
    non_prefixed_topic = "/".join([entry.data[DEVICE_ID], "JSON"])
    _LOGGER.debug(f"Listening for non-prefixed MQTT topic: {non_prefixed_topic}")
    entry.async_on_unload(
        await mqtt.async_subscribe(hass, non_prefixed_topic, async_json_received)
    )

    try:
        async with hass.timeout.async_timeout(90):
            await wait_for_json()
    except asyncio.TimeoutError as ex:
        raise ConfigEntryNotReady(f"Timeout waiting for MQTT topic {topic}") from ex

    _LOGGER.debug("Has JSON!")

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    entry.async_on_unload(entry.add_update_listener(update_listener))

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok
