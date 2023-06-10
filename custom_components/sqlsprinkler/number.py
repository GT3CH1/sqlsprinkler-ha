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

DOMAIN = "sqlsprinkler"

# Validation of the user's configuration


async def async_setup_platform(
        hass: HomeAssistant,
        config: ConfigType,
        async_add_entities,
        discovery_info: DiscoveryInfoType | None = None
) -> None:
    hub = hass.data[DOMAIN][config.entry_id]
    entities = []
    for zone in hub.zones:
        _LOGGER.info(zone)
        entities.append(SQLSprinklerTime(zone))

    _LOGGER.info(entities)
    async_add_entities(entities, True)


class SQLSprinklerTime(Zone, NumberEntity):
    _attr_has_entity_name = True
    _attr_max_value = 60
    _attr_min_value = 0
    _attr_native_step = 5
    _attr_native_unit_of_measurement: "minutes"
    def __init__(self, number) -> None:
        t = f"sqlsprinkler_zone_{number.id}_time"
        self._number = number
        self._name = t
        self._attr_unique_id = t


    @property
    def name(self) -> str:
        return self._name

    @property
    def icon(self) -> str | None:
        return "mdi:timer"

    @property
    def value(self) -> float:
        return self._number.time

    async def async_set_native_value(self, value: int) -> None:
        self._number.time = int(value)
        await self._number.async_set_time(int(value))

    async def async_update(self) -> None:
        await self._number.async_update()
