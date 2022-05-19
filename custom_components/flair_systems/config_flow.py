"""Config flow for Flair integration."""
from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResult
from homeassistant.exceptions import HomeAssistantError
from homeassistant.const import (
    CONF_USERNAME,
    CONF_PASSWORD,
)
from flair_api.client import ApiError, make_client
import requests
from .const import DOMAIN, HOST

_LOGGER = logging.getLogger(__name__)

STEP_USER_DATA_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_USERNAME): str,
        vol.Required(CONF_PASSWORD): str,
    }
)

# TODO: fix docstrings


def _validate_input(hass: HomeAssistant, data: dict[str, Any]) -> str:
    c = make_client(data[CONF_USERNAME], data[CONF_PASSWORD], HOST)
    try:
        user = requests.get(f"{HOST}api/users", headers={"Authorization": f"Bearer {c.token}"})
    except TypeError:
        raise InvalidAuth()
    except ApiError:
        raise CannotConnect()
    except requests.HTTPError:
        raise CannotConnect()

    if user.status_code >= 400:
        raise InvalidAuth()
    elif user.status_code != 200:
        raise CannotConnect()

    try:
        user = user.json().get("data")[0].get("attributes").get("name")
    except Exception:  # pylint: disable=broad-except
        raise CannotConnect()

    return user


async def validate_input(hass: HomeAssistant, data: dict[str, Any]) -> dict[str, Any]:
    """Validate the user input allows us to connect.

    Data has the keys from STEP_USER_DATA_SCHEMA with values provided by the user.
    """
    username = await hass.async_add_executor_job(
        _validate_input, hass, data
    )

    return {"title": username}


class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Flair."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the initial step."""
        if user_input is None:
            return self.async_show_form(
                step_id="user", data_schema=STEP_USER_DATA_SCHEMA
            )

        errors = {}

        try:
            info = await validate_input(self.hass, user_input)
        except CannotConnect:
            errors["base"] = "cannot_connect"
        except InvalidAuth:
            errors["base"] = "invalid_auth"
        except Exception:  # pylint: disable=broad-except
            _LOGGER.exception("Unexpected exception")
            errors["base"] = "unknown"
        else:
            return self.async_create_entry(title=info["title"], data=user_input)

        return self.async_show_form(
            step_id="user", data_schema=STEP_USER_DATA_SCHEMA, errors=errors
        )


class CannotConnect(HomeAssistantError):
    """Error to indicate we cannot connect."""


class InvalidAuth(HomeAssistantError):
    """Error to indicate there is invalid auth."""
