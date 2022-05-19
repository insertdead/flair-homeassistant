from datetime import timedelta
from homeassistant.components.cover import CoverDeviceClass, CoverEntityFeature, CoverEntity
from homeassistant.components.flair_systems.const import FLAIR_CLIENT
from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.entity_platform import AddEntitiesCallback
# from homeassistant.helpers.typing import ConfigType, DiscoveryInfoType
from flair_api.client import Client, Resource
from typing import List
from .const import DOMAIN


SCAN_INTERVAL = timedelta(seconds=10)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback
) -> None:
    """Setup the Vent cover platform."""
    client: Client = hass.data[DOMAIN][config_entry.entry_id][FLAIR_CLIENT]

    vents_res: list[Resource] = await hass.async_add_executor_job(client.get, "vents")
    vents: List[Vent] = []
    for vent in vents_res:
        vents.append(Vent(vent))
    async_add_entities(vents)


class Vent(CoverEntity):
    """Flair vent implementation for HomeAssistant."""
    _attr_device_class = CoverDeviceClass.DAMPER
    _attr_supported_features = CoverEntityFeature.OPEN | CoverEntityFeature.CLOSE

    def __init__(self, vent: Resource):
        self.vent = vent

    @property
    def name(self) -> str | None:
        return self.vent.attributes.get("name")

    @property
    def unique_id(self) -> str | None:
        return self.vent.id_
    
    @property
    def device_info(self):
        return {
            "identifiers": {(DOMAIN, self.vent.id_)},
            "name": self.vent.attributes.get("name"),
            "manufacturer": "Flair",
            "model": "Flair Vent",
            "configuration_url": "https://my.flair.co/",
        }

    @property
    def device_class(self) -> CoverDeviceClass | str | None:
        return CoverDeviceClass.DAMPER

    @property
    def current_cover_position(self) -> int | None:
        return self.vent.attributes.get("percent-open")

    @property
    def is_closed(self) -> bool | None:
        return True if self.vent.attributes.get("percent-open") == 0 else False
