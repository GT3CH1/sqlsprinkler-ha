"""Platform for light integration."""
from __future__ import annotations

import logging

# Import the device class from the component that you want to support
import homeassistant.helpers.config_validation as cv
import voluptuous as vol
from homeassistant.components.number import (PLATFORM_SCHEMA,
                                             NumberEntity)
from homeassistant.const import CONF_HOST
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import ConfigType, DiscoveryInfoType
from sqlsprinkler import System, Zone

_LOGGER = logging.getLogger(__name__)

# Validation of the user's configuration
PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend({
    vol.Required(CONF_HOST): cv.string,
})


def setup_platform(
        hass: HomeAssistant,
        config: ConfigType,
        add_entities: AddEntitiesCallback,
        discovery_info: DiscoveryInfoType | None = None
) -> None:
    host = config[CONF_HOST]
    hub = System(host)
    entities = []
    for zone in hub.zones:
        _LOGGER.info(zone)
        entities.append(SQLSprinklerTime(zone))

    _LOGGER.info(entities)
    add_entities(entities, True)


class SQLSprinklerTime(Zone, NumberEntity):
    _attr_has_entity_name = True

    def __init__(self, number) -> None:
        t = f"sqlsprinklerha-{number.name}-time"
        self._number = number
        self._name = t
        self.native_value = number.state
        self._attr_unique_id = t

    @property
    def name(self) -> str:
        return f"sqlsprinkler master"

    @property
    def icon(self) -> str | None:
        return "mdi:switch"

    @property
    def value(self) -> float:
        return self._number.time

    def set_native_value(self, value: float) -> None:
        self._number.time = value
        self._number.update()

    def update(self) -> None:
        self._number.update()
        self.native_value = self._number.state
