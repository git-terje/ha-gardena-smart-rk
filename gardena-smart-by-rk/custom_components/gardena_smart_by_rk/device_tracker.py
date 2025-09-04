from __future__ import annotations

import logging
from typing import Any

from homeassistant.components.device_tracker.config_entry import TrackerEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN
from .coordinator import GardenaCoordinator

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback) -> None:
    coord: GardenaCoordinator = hass.data[DOMAIN][entry.entry_id]["coordinator"]
    async_add_entities([SilenoTracker(coord)], True)


class SilenoTracker(TrackerEntity):
    _attr_name = "Sileno"
    _attr_icon = "mdi:robot-mower-outline"
    _attr_has_entity_name = True

    def __init__(self, coordinator: GardenaCoordinator) -> None:
        self._coordinator = coordinator
        self._attr_unique_id = f"{coordinator.entry.entry_id}_tracker"
        self._lat = None
        self._lon = None

    @property
    def should_poll(self) -> bool:
        return False

    @property
    def latitude(self):
        return self._lat

    @property
    def longitude(self):
        return self._lon

    async def async_update(self) -> None:
        # naive: pick first device with position
        for dev in self._coordinator.devices.values():
            pos = dev.get("position")
            if pos and "latitude" in pos and "longitude" in pos:
                self._lat = pos["latitude"]
                self._lon = pos["longitude"]
                break
