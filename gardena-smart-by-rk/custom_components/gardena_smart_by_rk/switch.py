from __future__ import annotations

import logging
from typing import Any

from homeassistant.components.switch import SwitchEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN, API_BASE
from .coordinator import GardenaCoordinator

import aiohttp

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback) -> None:
    coord: GardenaCoordinator = hass.data[DOMAIN][entry.entry_id]["coordinator"]
    async_add_entities([MowerStartSwitch(coord), MowerParkSwitch(coord), MowerStopSwitch(coord)], True)


class _BaseMowerSwitch(SwitchEntity):
    _action = ""
    _attr_has_entity_name = True

    def __init__(self, coordinator: GardenaCoordinator) -> None:
        self._coordinator = coordinator
        self._attr_unique_id = f"{coordinator.entry.entry_id}_{self._action}"
        self._is_on = False

    @property
    def is_on(self) -> bool:
        return self._is_on

    async def async_turn_on(self, **kwargs) -> None:
        await self._send_action()
        self._is_on = True
        self.async_write_ha_state()

    async def async_turn_off(self, **kwargs) -> None:
        self._is_on = False
        self.async_write_ha_state()

    async def _send_action(self) -> None:
        # naive: select first mower device id
        dev_id = None
        for d in self._coordinator.devices.values():
            if d.get("category") == "MOWER":
                dev_id = d.get("id")
                break
        if not dev_id:
            _LOGGER.warning("No mower device found")
            return
        token = await self._coordinator.oauth_session.async_ensure_token_valid()
        headers = {"Authorization": f"Bearer {token['access_token']}", "Accept": "application/json", "Content-Type":"application/json"}
        url = f"{API_BASE}/devices/{dev_id}/actions"
        payload = {"action": self._action}
        async with self._coordinator.session.post(url, headers=headers, json=payload) as resp:
            if resp.status not in (200, 202, 204):
                _LOGGER.warning("Mower action failed: %s %s", resp.status, await resp.text())

class MowerStartSwitch(_BaseMowerSwitch):
    _action = "start_mowing"
    _attr_name = "Mower Start"

class MowerParkSwitch(_BaseMowerSwitch):
    _action = "park_mower"
    _attr_name = "Mower Park"

class MowerStopSwitch(_BaseMowerSwitch):
    _action = "stop_mower"
    _attr_name = "Mower Stop"
