"""The Flair integration."""
from __future__ import annotations

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_PASSWORD, CONF_USERNAME, Platform
from homeassistant.core import HomeAssistant
from flair_api import make_client

from .const import DOMAIN, FLAIR_CLIENT, HOST

PLATFORMS: list[Platform] = [
    Platform.COVER,
    # Platform.CLIMATE,
]


def _setup_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Set up Flair from a config entry."""
    config = entry.data

    username = config[CONF_USERNAME]
    password = config[CONF_PASSWORD]
    host = HOST

    client = make_client(username, password, host)

    return client


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    client = await hass.async_add_executor_job(
        _setup_entry, hass, entry
    )

    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = {
        FLAIR_CLIENT: client
    }

    hass.config_entries.async_setup_platforms(entry, PLATFORMS)

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    if unload_ok := await hass.config_entries.async_unload_platforms(entry, PLATFORMS):
        hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok
