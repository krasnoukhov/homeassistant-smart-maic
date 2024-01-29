"""Config flow for Smart MAIC integration."""

from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.components import mqtt
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import AbortFlow
import homeassistant.helpers.config_validation as cv

from .const import (
    DEVICE_NAME,
    DEVICE_ID,
    DEVICE_TYPE,
    DOMAIN,
    IP_ADDRESS,
    PIN,
)
from .smart_maic import SmartMaic
from .coordinator import SmartMaicCoordinator

_LOGGER = logging.getLogger(__name__)

USER_SCHEMA = vol.Schema(
    {
        vol.Required(IP_ADDRESS): cv.string,
        vol.Required(PIN): cv.string,
        vol.Required(DEVICE_NAME, default="Energy"): cv.string,
    }
)


async def validate_input(hass: HomeAssistant, data: dict) -> dict[str, Any]:
    """Validate the user input allows us to connect.

    Data has the keys from USER_SCHEMA with values provided by the user.
    """

    if not await mqtt.async_wait_for_mqtt_client(hass):
        raise AbortFlow("mqtt_unavailable")

    smart_maic = SmartMaic(data)
    coordinator = SmartMaicCoordinator(smart_maic, hass)
    config = await coordinator.async_get_config()
    if not config["serv"]:
        raise AbortFlow("mqtt_unconfigured")

    config = await coordinator.async_set_mqtt_config()
    additional = {
        DEVICE_ID: config["about"][DEVICE_ID]["value"],
        DEVICE_TYPE: config["about"][DEVICE_TYPE]["value"],
    }

    return {"title": data[DEVICE_NAME], "additional": additional}


class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Smart MAIC."""

    VERSION = 1

    async def async_step_user(self, user_input=None):
        """Handle the initial step."""
        if user_input is None:
            return self.async_show_form(
                step_id="user", data_schema=USER_SCHEMA, errors={}
            )

        errors = {}

        try:
            info = await validate_input(self.hass, user_input)
            data = user_input | info["additional"]

            await self.async_set_unique_id(data[DEVICE_ID])
            self._abort_if_unique_id_configured()

            return self.async_create_entry(title=info["title"], data=data)
        except ConnectionError:
            errors["base"] = "cannot_connect"
        except AbortFlow as abort_flow_error:
            errors["base"] = abort_flow_error.reason
        except Exception as exception_error:  # pylint: disable=broad-except
            _LOGGER.exception(f"Unexpected exception {exception_error}")
            errors["base"] = "unknown"

        data_schema = self.add_suggested_values_to_schema(USER_SCHEMA, user_input)
        return self.async_show_form(
            step_id="user", data_schema=data_schema, errors=errors
        )
