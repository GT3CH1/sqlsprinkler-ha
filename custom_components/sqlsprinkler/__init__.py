""" SQLSprinkler """
import logging
from sqlsprinkler import System

from .const import DOMAIN
from homeassistant.core import HomeAssistant, callback
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from .system import MyCoordinator
PLATFORMS = [
        Platform.NUMBER,
        Platform.SWITCH,
        ]

ATTR_TYPE="type"


_LOGGER = logging.getLogger(__name__)
async def async_setup_entry(hass: HomeAssistant, config_entry: ConfigEntry):
    host = config_entry.data["host"]
    interval = config_entry.data["interval"]
    system = System(host)
    await system.async_update()
    _LOGGER.info(f"System host: {host}")
    sys = MyCoordinator(hass,system,interval)
    hass.data.setdefault(DOMAIN,{})[config_entry.entry_id] = sys
    config_entry.async_on_unload(config_entry.add_update_listener(update_listener))
    await hass.config_entries.async_forward_entry_setups(config_entry, PLATFORMS)
    return True

async def update_listener(hass, entry):
    _LOGGER.info("Received an update!")
    interval = entry.options["interval"]
    host = entry.options["host"]
    sys = MyCoordinator(hass,system,interval)
    hass.data[DOMAIN][entry.entry_id] = sys
    _LOGGER.info(f"set coordinator interval and host to {interval}, {host}")

