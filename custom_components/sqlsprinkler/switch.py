"""Platform for light integration."""
from __future__ import annotations

import logging

import homeassistant.helpers.config_validation as cv
import voluptuous as vol

from homeassistant.components.switch import (PLATFORM_SCHEMA, SwitchEntity)
from homeassistant.const import CONF_HOST
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.typing import ConfigType, DiscoveryInfoType
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from sqlsprinkler import System, Zone
from .system import SqlSprinklerZoneEntity
from .const import DOMAIN, DEVICE_MANUFACTURER, DEVICE_MODEL, SW_VERSION

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass: HomeAssistant, config: ConfigType, async_add_entities) -> None:
    coordinator = hass.data[DOMAIN][config.entry_id]
    system = coordinator.sqlsprinklersystem
    entities = []
    for idx, zone in enumerate(system.zones):
        _LOGGER.info(f"Adding zone {zone}")
        entities.append(SQLSprinklerEnabled(coordinator,zone, idx))
        entities.append(SQLSprinklerAutoOff(coordinator,zone, idx))
        entities.append(SQLSprinklerZone(coordinator, zone, idx))
    entities.append(SQLSprinklerMaster(coordinator,system))
    async_add_entities(entities, True)


class SQLSprinklerMaster(CoordinatorEntity, SwitchEntity):
    """The master switch for the system schedule."""
    _attr_has_entity_name = True

    def __init__(self, coordinator, switch) -> None:
        super().__init__(coordinator)
        self._switch = switch
        self._name = "SQLSprinkler System State"
        self._state = switch.system_state
        self._attr_unique_id = (f"sqlsprinkler_master")

    @property
    def name(self) -> str:
        return self._name

    @property
    def icon(self) -> str | None:
        return "mdi:electric-switch"

    @property
    def device_info(self) -> DeviceInfo:
        return DeviceInfo(
            identifiers={(DOMAIN, self.unique_id)},
            name=self._name,
            manufacturer=DEVICE_MANUFACTURER,
            model=DEVICE_MODEL,
            sw_version=SW_VERSION,
        )

    async def async_turn_on(self, **kwargs: Any) -> None:
        await self._switch.async_turn_on()
        await self.coordinator.async_request_refresh()

    async def async_turn_off(self, **kwargs: Any) -> None:
        await self._switch.async_turn_off()
        await self.coordinator.async_request_refresh()

    @callback
    def _handle_coordinator_update(self) -> None:
        self._attr_is_on = self.coordinator.data["system_state"]
        self.async_write_ha_state()


class SQLSprinklerZone(CoordinatorEntity, SwitchEntity):
    """A switch representing a single zone, allowing it to turn on or off."""
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

    @property
    def device_info(self) -> DeviceInfo:
        zone_name = f"sqlsprinkler_zone_{self._switch.id}"
        return DeviceInfo(
            identifiers={(DOMAIN, zone_name)},
            name=self._switch.name,
            manufacturer=DEVICE_MANUFACTURER,
            model=DEVICE_MODEL,
            sw_version=SW_VERSION,
            via_device=(DOMAIN, "sqlsprinkler_master"),
        )

    async def async_turn_on(self, **kwargs: Any) -> None:
        await self._switch.async_turn_on()
        await self.coordinator.async_request_refresh()

    async def async_turn_off(self, **kwargs: Any) -> None:
        await self._switch.async_turn_off()
        await self.coordinator.async_request_refresh()

    @callback
    def _handle_coordinator_update(self) -> None:
        self._attr_is_on = self.coordinator.data["zones"][self.idx].state
        self.async_write_ha_state()


class SQLSprinklerEnabled(CoordinatorEntity, SwitchEntity):
    """A switch state representing whether this system is enabled to run during the system schedule."""
    _attr_has_entity_name = True
    def __init__(self,coordinator,zone,idx) -> None:
        super().__init__(coordinator)
        self._switch = zone
        self.idx = idx
        self._name = f"sqlsprinkler_zone_{self._switch.id}_enabled_state"
        self._attr_unique_id = (f"sqlsprinkler_zone_{self._switch.id}_enabled_state")

    @property
    def name(self) -> str:
        return self._name

    @property
    def icon(self) -> str | None:
        return "mdi:electric-switch"

    @property
    def device_info(self) -> DeviceInfo:
        zone_name = f"sqlsprinkler_zone_{self._switch.id}"
        return DeviceInfo(
            identifiers={(DOMAIN, zone_name)},
            name=self._switch.name,
            manufacturer=DEVICE_MANUFACTURER,
            model=DEVICE_MODEL,
            sw_version=SW_VERSION,
            via_device=(DOMAIN, zone_name),
        )
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
    """A switch representing whether or not a zone automatically shuts off if turned on manually."""
    _attr_has_entity_name = True

    def __init__(self, coordinator,zone,idx) -> None:
        super().__init__(coordinator)
        self.idx = idx
        self._switch = zone
        self._name = f"sqlsprinkler_zone_{zone.id}_autooff_state"
        self._state = zone.state
        self._attr_unique_id = (f"sqlsprinkler_zone_{zone.id}_autooff_state")

    @property
    def name(self) -> str:
        return self._name

    @property
    def icon(self) -> str | None:
        return "mdi:electric-switch"

    @property
    def device_info(self) -> DeviceInfo:
        zone_name = f"sqlsprinkler_zone_{self._switch.id}"
        return DeviceInfo(
            identifiers={(DOMAIN, zone_name)},
            name=self._switch.name,
            manufacturer=DEVICE_MANUFACTURER,
            model=DEVICE_MODEL,
            sw_version=SW_VERSION,
            via_device=(DOMAIN, zone_name),
        )

    async def async_turn_on(self, **kwargs: Any) -> None:
        await self._switch.async_set_auto_off(True)
        await self.coordinator.async_request_refresh()

    async def async_turn_off(self, **kwargs: Any) -> None:
        await self._switch.async_set_auto_off(False)
        await self.coordinator.async_request_refresh()

    @callback
    def _handle_coordinator_update(self) -> None:
        self._attr_is_on = self.coordinator.data["zones"][self.idx].auto_off
        self.async_write_ha_state()

