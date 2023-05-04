"""Platform for light integration."""
from __future__ import annotations

import logging

from sqlsprinkler import System, Zone
import voluptuous as vol

# Import the device class from the component that you want to support
import homeassistant.helpers.config_validation as cv
from homeassistant.components.switch import (PLATFORM_SCHEMA,
                                            SwitchEntity)
from homeassistant.const import CONF_HOST, CONF_PASSWORD, CONF_USERNAME
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import ConfigType, DiscoveryInfoType

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
        entities.append(SQLSprinklerSwitch(zone))
    _LOGGER.info(entities)
    add_entities(entities, True)


class SQLSprinklerSwitch(Zone, SwitchEntity):
    """Representation of an Awesome Light."""
    _attr_has_entity_name = True
    
    def __init__(self, switch) -> None:
        """Initialize an AwesomeLight."""
        self._switch = switch
        self._name = f"zone-{switch.id}"
        self._state = switch.state
        self._attr_unique_id = (f"sqlsprinklerha-zone-{switch.id}")

    @property
    def name(self) -> str:
        """Return the display name of this light."""
        return f"sqlsprinkler {self._name} "
    @property
    def icon(self) -> str | None:
        return "mdi:sprinkler"
    
    @property
    def is_on(self) -> bool | None:
        """Return true if light is on."""
        return self._state

    def turn_on(self, **kwargs: Any) -> None:
        """Instruct the light to turn on. """
        self._switch.turn_on()

    def turn_off(self, **kwargs: Any) -> None:
        """Instruct the light to turn off."""
        self._switch.turn_off()

    def update(self) -> None:
        """Fetch new state data for this light.

        This is the only method that should fetch new data for Home Assistant.
        """
        self._switch.update()
        self._state = self._switch.state
