""" SQLSprinkler """
from sqlsprinkler import System

from .const import DOMAIN
from homeassistant.core import HomeAssistant, callback
from homeassistant.config_entries import ConfigEntry
async def async_setup_entry(hass: HomeAssistant, config_entry: ConfigEntry, async_add_devices):
    system = System(config_entry.data)
    await system.async_update()
    hass.data.setdefault(DOMAIN,{})[entry.entry_id] = system
    await self.hass.config_entries.async_forward_entry_unload(self.config_entry, "switch")
    await self.hass.config_entries.async_forward_entry_unload(self.config_entry, "number")
