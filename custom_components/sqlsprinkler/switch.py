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
        entities.append(SQLSprinklerZone(zone))
        entities.append(SQLSprinklerEnabled(zone))
        entities.append(SQLSprinklerAutoOff(zone))
    entities.append(SQLSprinklerMaster(hub))

    _LOGGER.info(entities)
    add_entities(entities, True)


class SQLSprinklerMaster(System, SwitchEntity):
    _attr_has_entity_name = True

    def __init__(self, switch) -> None:
        self._switch = switch
        self._name = "sqlsprinkler master"
        self._state = switch.state
        self._attr_unique_id = (f"sqlsprinkler_master")

    @property
    def name(self) -> str:
        return self._name

    @property
    def icon(self) -> str | None:
        return "mdi:electric-switch"

    @property
    def is_on(self) -> bool | None:
        return self._switch.state

    def turn_on(self, **kwargs: Any) -> None:
        self._switch.turn_on()

    def turn_off(self, **kwargs: Any) -> None:
        self._switch.turn_off()

    def update(self) -> None:
        self._switch.update()
        self._state = self._switch.state


class SQLSprinklerZone(Zone, SwitchEntity):
    _attr_has_entity_name = True

    def __init__(self, switch) -> None:
        self._switch = switch
        self._name = f"sqlsprinkler_zone_{switch.name.lower().replace(' ', '_')}"
        self._state = switch.state
        self._attr_unique_id = (f"sqlsprinkler_zone_{switch.id}")

    @property
    def name(self) -> str:
        return self._name

    @property
    def icon(self) -> str | None:
        return "mdi:sprinkler-variant"

    @property
    def is_on(self) -> bool | None:
        return self._switch.state

    def turn_on(self, **kwargs: Any) -> None:
        self._switch.turn_on()

    def turn_off(self, **kwargs: Any) -> None:
        self._switch.turn_off()

    def update(self) -> None:
        self._switch.update()
        self._state = self._switch.state


class SQLSprinklerEnabled(Zone, SwitchEntity):
    _attr_has_entity_name = True

    def __init__(self, switch) -> None:
        self._switch = switch
        self._name = f"{switch.name} enabled"
        self._attr_unique_id = (f"sqlsprinkler_zone_{switch.name.lower().replace(' ', '_')}_enabled_state")

    @property
    def name(self) -> str:
        return self._name

    @property
    def icon(self) -> str | None:
        return "mdi:electric-switch"

    @property
    def is_on(self) -> bool | None:
        return self._switch.enabled

    def turn_on(self, **kwargs: Any) -> None:
        self._switch.enable()

    def turn_off(self, **kwargs: Any) -> None:
        self._switch.disable()

    def update(self) -> None:
        self._switch.update()


class SQLSprinklerAutoOff(Zone, SwitchEntity):
    _attr_has_entity_name = True

    def __init__(self, switch) -> None:
        self._switch = switch
        self._name = f"{switch.name} autooff"
        self._state = switch.state
        self._attr_unique_id = (f"sqlsprinkler_zone_{switch.name.lower().replace(' ', '_')}_autooff_state")

    @property
    def name(self) -> str:
        return self._name

    @property
    def icon(self) -> str | None:
        return "mdi:electric-switch"

    @property
    def is_on(self) -> bool | None:
        return self._switch.auto_off

    def turn_on(self, **kwargs: Any) -> None:
        self._switch.set_auto_off(True)

    def turn_off(self, **kwargs: Any) -> None:
        self._switch.set_auto_off(False)

    def update(self) -> None:
        self._switch.update()
        self._state = self._switch.auto_off
