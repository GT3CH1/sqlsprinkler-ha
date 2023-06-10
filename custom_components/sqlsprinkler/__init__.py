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
    system = System(host)
    await system.async_update()
    _LOGGER.info(f"System host: {host}")
    sys = MyCoordinator(hass,system)
    hass.data.setdefault(DOMAIN,{})[config_entry.entry_id] = sys
    await hass.config_entries.async_forward_entry_setups(config_entry, PLATFORMS)
    return True
