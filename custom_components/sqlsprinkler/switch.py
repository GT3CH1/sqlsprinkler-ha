"""Platform for light integration."""
from __future__ import annotations

import logging

import sqlsprinkler
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
    """Set up the Awesome Light platform."""
    # Assign configuration variables.
    # The configuration check takes care they are present.
    host = config[CONF_HOST]

    # Setup connection with devices/cloud
    hub = sqlsprinkler.System(host)

    # Verify that passed in configuration works
    #if not hub.is_valid_login():
    #    _LOGGER.error("Could not connect to AwesomeLight hub")
    #    return

    # Add devices
    add_entities(SQLSprinklerSwitch(zone) for zone in hub.zones)


class SQLSprinklerSwitch(Zone):
    """Representation of an Awesome Light."""

    def __init__(self, switch) -> None:
        """Initialize an AwesomeLight."""
        self._switch = switch
        self._name = switch.name
        self._state = switch.state

    @property
    def name(self) -> str:
        """Return the display name of this light."""
        return self._name

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
