from __future__ import annotations

import logging
from typing import Any, Dict, List

from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.entity import DeviceInfo

from .const import DOMAIN
from .coordinator import GardenaCoordinator

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback) -> None:
    coord = GardenaCoordinator(hass, entry)
    await coord.async_setup()
    hass.data[DOMAIN][entry.entry_id]["coordinator"] = coord

    entities: List[SensorEntity] = []
    entities.append(RouteSensor(coord))
    async_add_entities(entities, True)


class RouteSensor(SensorEntity):
    _attr_name = "Sileno Route"
    _attr_icon = "mdi:map-marker-path"
    _attr_has_entity_name = True

    def __init__(self, coordinator: GardenaCoordinator) -> None:
        self._coordinator = coordinator
        self._attr_unique_id = f"{coordinator.entry.entry_id}_route"
        self._state = None
        self._attr_extra_state_attributes = {}

    @property
    def device_info(self) -> DeviceInfo | None:
        return DeviceInfo(
            identifiers={(DOMAIN, self._coordinator.entry.entry_id)},
            name="Gardena Smart",
            manufacturer="Husqvarna Group",
        )

    async def async_update(self) -> None:
        # choose first mower with track
        devices = self._coordinator.devices
        if not devices:
            return
        dev_id = next(iter(devices.keys()))
        geo = await self._coordinator.async_get_geojson(dev_id, self._coordinator.entry.options.get("route_window_hours", 12))
        self._state = geo["properties"]["generated"]
        self._attr_extra_state_attributes = {"geojson": geo}

    @property
    def native_value(self):
        return self._state
