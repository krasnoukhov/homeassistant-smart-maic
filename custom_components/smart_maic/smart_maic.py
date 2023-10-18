"""Smart MAIC integration."""
from __future__ import annotations

import logging
from typing import Any

from urllib.parse import urlparse, urlencode
import requests

from .const import (
    DEVICE_ID,
    HTTP_TIMEOUT,
    IP_ADDRESS,
    PIN,
    PREFIX,
)


_LOGGER = logging.getLogger(__name__)


class SmartMaic:
    """Smart MAIC instance."""

    def __init__(self, data: dict[str, Any]) -> None:
        """Init Smart MAIC."""
        self._ip_address = data[IP_ADDRESS]
        self._pin = data[PIN]
        self._devid = data[DEVICE_ID]

    def get_wdata(self) -> dict[str, Any]:
        """Get "wdata" for Smart MAIC component."""
        self._login_request()
        return self._get_request(page="getwdata").json()

    def get_config(self) -> dict[str, Any]:
        """Get config for Smart MAIC component."""
        self._login_request()
        return self._get_request(page="webinit").json()

    def set_mqtt_config(self) -> dict[str, Any]:
        """Set Smart MAIC MQTT config."""
        config = self.get_config()

        self._get_request(
            page="mqtt",
            serv=config["serv"],
            port=config["port"],
            uname=config["uname"],
            **{"pass": config["pass"]},
            mqtt_on=1,
            mqttint=60,
            separat=2,
            prefix=f"{PREFIX}/",
        )

        return self.get_config()

    def set_consumption(self, key: str, value: float) -> None:
        """Set Smart MAIC consumption value."""
        self._login_request()
        self._get_request(page="initval", **{key: value})

    def set_dry_switch(self, value: int) -> dict[str, Any]:
        """Set Smart MAIC dry switch."""
        self._get_request(
            page="getdata", devid=self._devid, devpass=self._pin, pout=value
        )

    def _login_request(self) -> None:
        self._get_request(page="devlogin", devpass=self._pin)

    def _get_request(self, **kwargs) -> requests.Response:
        """Make GET request to the Smart MAIC API."""
        url = urlparse(f"http://{self._ip_address}/")
        url = url._replace(query=urlencode(kwargs))

        _LOGGER.debug(f"Smart MAIC request: GET {url.geturl()}")
        try:
            r = requests.get(url.geturl(), timeout=HTTP_TIMEOUT)
            r.raise_for_status()
            _LOGGER.debug(f"Smart MAIC status: {r.status_code}")
            _LOGGER.debug(f"Smart MAIC response: {r.text}")

            return r
        except TimeoutError as timeout_error:
            raise ConnectionError from timeout_error
        except requests.exceptions.ConnectionError as connection_error:
            raise ConnectionError from connection_error
        except requests.exceptions.HTTPError as http_error:
            if http_error.response.status_code == 400:
                return r
            raise ConnectionError from http_error
