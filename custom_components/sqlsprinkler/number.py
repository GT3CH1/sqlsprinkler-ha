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
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from sqlsprinkler import System, Zone

_LOGGER = logging.getLogger(__name__)

DOMAIN = "sqlsprinkler"

# Validation of the user's configuration


async def async_setup_entry(
        hass: HomeAssistant,
        config: ConfigType,
        async_add_entities,
        ) -> None:
    coordinator = hass.data[DOMAIN][config.entry_id]
    entities = []
    hub = coordinator.sqlsprinklersystem
    for idx, zone in enumerate(hub.zones):
        _LOGGER.info(zone)
        entities.append(SQLSprinklerTime(coordinator,zone,idx))
    async_add_entities(entities, True)

class SQLSprinklerTime(CoordinatorEntity, NumberEntity):
    _attr_has_entity_name = True
    _attr_max_value = 60
    _attr_min_value = 0
    _attr_native_step = 5
    _attr_native_unit_of_measurement: "minutes"
    _system = None
    def __init__(self, coordinator,zone) -> None:
        super().__init__(coordinator)
        t = f"sqlsprinkler_zone_{zone.id}_time"
        self._zone = zone
        self._name = t
        self._attr_unique_id = t

    @property
    def name(self) -> str:
        return self._name

    @property
    def icon(self) -> str | None:
        return "mdi:timer"

    async def async_set_native_value(self, value: int) -> None:
        self._zone.time = int(value)
        await self._zone.async_set_time(int(value))

    @callback
    def _handle_coordinator_update(self) -> None:
        self._attr_value = self.coordinator.data["zones"][self.idx].time
        self.async_write_ha_state()
