from sqlsprinkler import Zone, System
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, CoordinatorEntity
import logging
from .const import DOMAIN
from datetime import timedelta
_LOGGER= logging.getLogger(__name__)

class MyCoordinator(DataUpdateCoordinator):
    def __init__(self, hass: HomeAssistant, system: System) -> None:
        super().__init__(
                hass,
                _LOGGER,
                name=DOMAIN,
                update_interval=timedelta(seconds=5),
        )
        self.sqlsprinklersystem = system

    async def _async_update_data(self) -> None:
        info = {}
        await self.sqlsprinklersystem.async_update()
        info["system_state"] = self.sqlsprinklersystem.system_state
        info["zones"] = self.sqlsprinklersystem.zones
        return info

class SqlSprinklerZoneEntity(CoordinatorEntity):
    zone: Zone
    def __init__(self, coordinator, zone):
        super().__init__(coordinator)
        self.zone = zone

    def get_time() -> int:
        return self.zone.time

    def is_enabled() -> bool:
        return self.zone.enabled

    def is_on() -> bool:
        return self.zone.state

    def is_auto_off() -> bool:
        return self.zone.auto_off


