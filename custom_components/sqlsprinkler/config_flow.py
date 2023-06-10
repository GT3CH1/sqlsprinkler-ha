from homeassistant.config_entries import ConfigEntry, ConfigFlow
from homeassistant.data_entry_flow import FlowResult,FlowHandler
from homeassistant.const import CONF_HOST
from .const import DOMAIN
import voluptuous as vol

class SqlSprinklerConfigFlow(ConfigFlow, domain=DOMAIN):
    VERSION = 1
    async def async_step_init(self,info=None) -> FlowResult:
        await self.async_step_user()
    async def async_step_user(self, info=None) -> FlowResult:
        if info is not None:
            await self.async_set_unique_id(DOMAIN)
            return self.async_create_entry(title="SQLSprinkler",
                                           data={
                                               "host":info["host"]
                                               }
                                          )
        schema = vol.Schema(
            {
                vol.Required("host"):str,
            }
        )
        return self.async_show_form(
                step_id="user",
                data_schema=schema
                )
