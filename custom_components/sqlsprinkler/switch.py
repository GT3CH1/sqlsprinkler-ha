"""Platform for light integration."""
from __future__ import annotations

import logging

# Import the device class from the component that you want to support
import homeassistant.helpers.config_validation as cv
import voluptuous as vol
from homeassistant.components.switch import (PLATFORM_SCHEMA,
                                             SwitchEntity)
from homeassistant.const import CONF_HOST
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import ConfigType, DiscoveryInfoType
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from sqlsprinkler import System, Zone
from .system import SqlSprinklerZoneEntity
from .const import DOMAIN
_LOGGER = logging.getLogger(__name__)

# Validation of the user's configuration
async def async_setup_entry(
        hass: HomeAssistant,
        config: ConfigType,
        async_add_entities,
        ) -> None:
    coordinator = hass.data[DOMAIN][config.entry_id]
    system = coordinator.sqlsprinklersystem
    entities = []
    for idx, zone in enumerate(system.zones):
        _LOGGER.info(f"Adding zone {zone}")
        entities.append(SQLSprinklerZone(coordinator,zone,idx))
        entities.append(SQLSprinklerEnabled(coordinator,zone, idx))
        entities.append(SQLSprinklerAutoOff(coordinator,zone, idx))
    entities.append(SQLSprinklerMaster(coordinator,system))
    async_add_entities(entities, True)


class SQLSprinklerMaster(CoordinatorEntity, SwitchEntity):
    _attr_has_entity_name = True

    def __init__(self, coordinator, switch) -> None:
        super().__init__(coordinator)
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

    async def async_turn_on(self, **kwargs: Any) -> None:
        await self._switch.async_turn_on()
        self._state = self._switch.system_state

    async def async_turn_off(self, **kwargs: Any) -> None:
        await self._switch.async_turn_off()
        self._state = self._switch.system_state

    @callback
    def _handle_coordinator_update(self) -> None:
        self._attr_is_on = self.coordinator.data["system_state"]
        self.async_write_ha_state()


class SQLSprinklerZone(CoordinatorEntity, SwitchEntity):

    _attr_has_entity_name = True
    def __init__(self, coordinator,zone,idx) -> None:
        super().__init__(coordinator)
        self.idx = idx
        self._switch = zone
        self._name = f"sqlsprinkler_zone_{zone.id}"
        self._state = zone.state
        self._attr_unique_id = (f"sqlsprinkler_zone_{zone.id}")

    @property
    def name(self) -> str:
        return self._name

    @property
    def icon(self) -> str | None:
        return "mdi:sprinkler-variant"

    async def async_turn_on(self, **kwargs: Any) -> None:
        await self._switch.async_turn_on()
        self._state = self._switch.state

    async def async_turn_off(self, **kwargs: Any) -> None:
        await self._switch.async_turn_off()
        self._state = self._switch.state

    @callback
    def _handle_coordinator_update(self) -> None:
        self._attr_is_on = self.coordinator.data["zones"][self.idx].state
        self.async_write_ha_state()


class SQLSprinklerEnabled(CoordinatorEntity, SwitchEntity):
    _attr_has_entity_name = True
    def __init__(self,coordinator,zone,idx) -> None:
        super().__init__(coordinator)
        self._switch = zone
        self.idx = idx
        self._name = f"sqlsprinkler_zone_{self._switch.id}_enabled_state"
        self._attr_unique_id = (f"sqlsprinkler_zone_{self._switch.id}_enabled_state")
        _LOGGER.info(f"Enabled Switch for {self._switch.id}, {self._switch}")

    @property
    def name(self) -> str:
        return self._name

    @property
    def icon(self) -> str | None:
        return "mdi:electric-switch"

    async def async_turn_on(self, **kwargs: Any) -> None:
        await self._switch.async_enable()
        await self.coordinator.async_request_refresh()

    async def async_turn_off(self, **kwargs: Any) -> None:
        await self._switch.async_disable()
        await self.coordinator.async_request_refresh()

    @callback
    def _handle_coordinator_update(self) -> None:
        self._attr_is_on = self.coordinator.data["zones"][self.idx].enabled
        self.async_write_ha_state()

class SQLSprinklerAutoOff(CoordinatorEntity, SwitchEntity):
    _attr_has_entity_name = True

    def __init__(self, coordinator,zone,idx) -> None:
        super().__init(coordinator)
        self.idx = idx
        self._switch = zone
        self._name = f"sqlsprinkler_zone_{zone.id}_autooff_state"
        self._state = zone.state
        self._attr_unique_id = (f"sqlsprinkler_zone_{zone.id}_autooff_state")
        self._system = system

    @property
    def name(self) -> str:
        return self._name

    @property
    def icon(self) -> str | None:
        return "mdi:electric-switch"

    async def async_turn_on(self, **kwargs: Any) -> None:
        await self._switch.async_set_auto_off(True)

    async def async_turn_off(self, **kwargs: Any) -> None:
        await self._switch.async_set_auto_off(False)

    @callback
    def _handle_coordinator_update(self) -> None:
        self._attr_is_on = self.coordinator.data["zones"][self.idx].auto_off
        self.async_write_ha_state()

