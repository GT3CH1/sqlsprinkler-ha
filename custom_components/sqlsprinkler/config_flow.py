from homeassistant import config_entries
from .const import DOMAIN
import voluptuous as vol

class SqlSprinklerConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1
    async def async_step_user(self, info):
        if info is not None:
            pass
        return self.async_show_form(
                step_id="host",
                data_schema=vol.Schema({vol.Required("host"): str}))

