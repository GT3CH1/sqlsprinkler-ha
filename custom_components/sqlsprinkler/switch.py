"""Platform for light integration."""
from __future__ import annotations

import logging

# Import the device class from the component that you want to support
import homeassistant.helpers.config_validation as cv
import voluptuous as vol
from homeassistant.components.switch import (PLATFORM_SCHEMA,
                                             SwitchEntity)
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
        entities.append(SQLSprinklerZone(zone,hub))
        entities.append(SQLSprinklerEnabled(zone))
        entities.append(SQLSprinklerAutoOff(zone,hub))
    entities.append(SQLSprinklerMaster(hub))

    _LOGGER.info(entities)
    async_add_entities(entities, True)


class SQLSprinklerMaster(System, SwitchEntity):
    _attr_has_entity_name = True

    def __init__(self, switch) -> None:
        self._switch = switch
        self._name = "sqlsprinkler master"
        self._state = switch.system_state
        self._attr_unique_id = (f"sqlsprinkler_master")

    @property
    def name(self) -> str:
        return self._name

    @property
    def icon(self) -> str | None:
        return "mdi:electric-switch"

    @property
    def is_on(self) -> bool | None:
        return self._switch.system_state

    async def async_turn_on(self, **kwargs: Any) -> None:
        await self._switch.async_turn_on()
        self._state = self._switch.system_state

    async def async_turn_off(self, **kwargs: Any) -> None:
        await self._switch.async_turn_off()
        self._state = self._switch.system_state

    async def async_update(self) -> None:
        await self._switch.async_update()
        self._state = self._switch.system_state


class SQLSprinklerZone(Zone, System, SwitchEntity):

    _attr_has_entity_name = True
    def __init__(self, switch,system) -> None:
        self._switch = switch
        self._name = f"sqlsprinkler_zone_{switch.id}"
        self._state = switch.state
        self._attr_unique_id = (f"sqlsprinkler_zone_{switch.id}")
        self._system = system


    @property
    def name(self) -> str:
        return self._name

    @property
    def icon(self) -> str | None:
        return "mdi:sprinkler-variant"
    @property
    def is_on(self) -> bool | None:
        return self._switch.state

    async def async_turn_on(self, **kwargs: Any) -> None:
        await self._switch.async_turn_on()
        self._state = self._switch.state

    async def async_turn_off(self, **kwargs: Any) -> None:
        await self._switch.async_turn_off()
        self._state = self._switch.state

    async def async_update(self) -> None:
        self._state = self._system.get_zone_by_id(self._switch.id).state


class SQLSprinklerEnabled(Zone, SwitchEntity):
    _attr_has_entity_name = True

    def __init__(self, switch) -> None:
        self._switch = switch
        self._name = f"sqlsprinkler_zone_{switch.id}_enabled_state"
        self._attr_unique_id = (f"sqlsprinkler_zone_{switch.id}_enabled_state")


    @property
    def name(self) -> str:
        return self._name

    @property
    def icon(self) -> str | None:
        return "mdi:electric-switch"

    @property
    def is_on(self) -> bool | None:
        return self._switch.enabled

    async def async_turn_on(self, **kwargs: Any) -> None:
        await self._switch.async_enable()
        self._state = self._switch.state

    async def async_turn_off(self, **kwargs: Any) -> None:
        await self._switch.async_disable()
        self._state = self._switch.state

    async def async_update(self) -> None:
        await self._switch.async_update()


class SQLSprinklerAutoOff(Zone, System, SwitchEntity):
    _attr_has_entity_name = True

    def __init__(self, switch, system) -> None:
        self._switch = switch
        self._name = f"sqlsprinkler_zone_{switch.id}_autooff_state"
        self._state = switch.state
        self._attr_unique_id = (f"sqlsprinkler_zone_{switch.id}_autooff_state")
        self._system = system


    @property
    def name(self) -> str:
        return self._name

    @property
    def icon(self) -> str | None:
        return "mdi:electric-switch"

    @property
    def is_on(self) -> bool | None:
        return self._switch.auto_off

    async def async_turn_on(self, **kwargs: Any) -> None:
        await self._switch.async_set_auto_off(True)


    async def async_turn_off(self, **kwargs: Any) -> None:
        await self._switch.async_set_auto_off(False)

    async def async_update(self) -> None:
        self._state = self._system.get_zone_by_id(self._switch.id).auto_off
