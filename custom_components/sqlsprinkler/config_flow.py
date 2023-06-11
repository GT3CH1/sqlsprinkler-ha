from homeassistant.config_entries import ConfigEntry, ConfigFlow, OptionsFlow
from homeassistant.data_entry_flow import FlowResult,FlowHandler
from homeassistant.const import CONF_HOST
from homeassistant.core import HomeAssistant, callback
from homeassistant import exceptions
from sqlsprinkler import System
from urllib.parse import urlparse
from .const import DOMAIN
from typing import Any
import voluptuous as vol


DATA_SCHEMA = vol.Schema({
        vol.Required("host",default="http://10.5.1.7:3030"):str,
        vol.Required("interval",default=30):int
    })

async def validate_input(hass: HomeAssistant, data: dict) -> dict[str, Any]:
    _host = data["host"]
    _interval = int(data["interval"])
    _res = {}
    url = urlparse(_host)
    if url.scheme != "http" or url.netloc == "" or url.path != "":
        raise InvalidHost
    sys = System(_host)
    try:
        await sys.async_update()
    except Exception:
        raise CannotConnect
    if len(sys.zones) == 0:
        raise CannotConnect
    if _interval <= 0:
        raise InvalidInterval
    _res['host'] = _host
    _res['interval'] = _interval
    return _res



class SqlSprinklerConfigFlow(ConfigFlow, domain=DOMAIN):
    VERSION = 1
    async def async_step_init(self,info=None) -> FlowResult:
        await self.async_step_user()

    async def async_step_user(self, info=None) -> FlowResult:
        errors = {}
        if info is not None:
            try:
                res = await validate_input(self.hass,info)
                await self.async_set_unique_id(DOMAIN)
                return self.async_create_entry(title="SQLSprinkler",data=res)
            except ValueError:
                errors["interval"] = "bad_interval"
            except InvalidHost:
                errors["host"] = "bad_host"
            except CannotConnect:
                errors["host"] = "cannot_connect"
         
        return self.async_show_form(
                step_id="user",
                data_schema=DATA_SCHEMA,
                errors=errors
            )

    @staticmethod
    @callback
    def async_get_options_flow(config_entry: ConfigEntry) -> OptionsFlow:
        return OptionsFlowHandler(config_entry)


class OptionsFlowHandler(OptionsFlow):
    def __init__(self,config_entry: ConfigEntry) -> None:
        self.config_entry = config_entry

    async def async_step_init(self, info=None) -> FlowResult:
        errors = {}
        if info is not None:
            try:
                res = await validate_input(self.hass,info)
                return self.async_create_entry(title="SQLSprinkler",data=res)
            except ValueError:
                errors["interval"] = "bad_interval"
            except InvalidHost:
                errors["host"] = "bad_host"
            except CannotConnect:
                errors["host"] = "cannot_connect"
         
        return self.async_show_form(
                step_id="init",
                data_schema=DATA_SCHEMA,
                errors=errors
            )


class CannotConnect(exceptions.HomeAssistantError):
    """Error saying we cannot connect to a host"""

class InvalidHost(exceptions.HomeAssistantError):
    """Error saying our host was invalid."""

class InvalidInterval(exceptions.HomeAssistantError):
    """Error saying our interval was invalid."""
