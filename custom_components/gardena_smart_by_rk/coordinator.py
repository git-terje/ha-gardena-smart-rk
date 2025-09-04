from __future__ import annotations

import asyncio
import json
import logging
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, Optional

import aiohttp

from homeassistant.core import HomeAssistant, callback
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers import aiohttp_client
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator
from homeassistant.helpers.storage import Store
from homeassistant.helpers import config_entry_oauth2_flow

from .const import DOMAIN, API_BASE, WS_URL

_LOGGER = logging.getLogger(__name__)

class GardenaCoordinator(DataUpdateCoordinator):
    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        super().__init__(
            hass,
            _LOGGER,
            name=f"{DOMAIN}-coordinator",
            update_interval=timedelta(minutes=60),  # minimal HTTP polling; primary is WS
        )
        self.entry = entry
        self.session = aiohttp_client.async_get_clientsession(hass)
        self.devices: Dict[str, Dict[str, Any]] = {}
        self.locations: Dict[str, Any] = {}
        self.ws_task: Optional[asyncio.Task] = None
        self.store = Store(hass, 1, f"{DOMAIN}_{entry.entry_id}_route.json")

    # OAuth2 session helper
    @property
    def oauth_session(self) -> config_entry_oauth2_flow.OAuth2Session:
        return config_entry_oauth2_flow.async_get_config_entry_implementation(self.hass, self.entry).async_create_oauth2_session(self.hass, self.entry)

    async def async_setup(self) -> None:
        await self._http_bootstrap()
        await self._start_ws()

    async def async_unload(self) -> None:
        if self.ws_task:
            self.ws_task.cancel()
            self.ws_task = None

    async def _http_bootstrap(self) -> None:
        # minimal bootstrap to retrieve locations/devices once
        token = await self.oauth_session.async_ensure_token_valid()
        headers = {
            "Authorization": f"Bearer {token['access_token']}",
            "Accept": "application/json",
        }
        async with self.session.get(f"{API_BASE}/locations", headers=headers) as resp:
            if resp.status != 200:
                _LOGGER.warning("Failed to fetch locations: %s", await resp.text())
                return
            data = await resp.json()
            self.locations = {loc["id"]: loc for loc in data.get("data", [])}

    async def _start_ws(self) -> None:
        if self.ws_task and not self.ws_task.done():
            return
        self.ws_task = self.hass.async_create_task(self._ws_loop())

    async def _ws_loop(self) -> None:
        backoff = 1
        while True:
            try:
                token = await self.oauth_session.async_ensure_token_valid()
                headers = {"Authorization": f"Bearer {token['access_token']}"}
                async with self.session.ws_connect(WS_URL, headers=headers, heartbeat=30) as ws:
                    _LOGGER.info("Connected to Gardena WebSocket")
                    backoff = 1
                    async for msg in ws:
                        if msg.type == aiohttp.WSMsgType.TEXT:
                            await self._handle_ws(json.loads(msg.data))
                        elif msg.type == aiohttp.WSMsgType.ERROR:
                            _LOGGER.error("WS error: %s", msg.data)
                            break
            except asyncio.CancelledError:
                _LOGGER.info("WS task cancelled")
                return
            except Exception as err:  # noqa: BLE001
                _LOGGER.warning("WS reconnect in %s sec due to %s", backoff, err)
                await asyncio.sleep(backoff)
                backoff = min(backoff * 2, 60)

    @callback
    async def _handle_ws(self, payload: Dict[str, Any]) -> None:
        # Expect payloads with device updates; adapt mapping as needed
        # Example shape assumed:
        # {"type":"DEVICE_UPDATE","device":{"id":"...","category":"MOWER","status":{...},"position":{"latitude":..,"longitude":..,"time":"..."}}}
        dev = payload.get("device") or {}
        dev_id = dev.get("id")
        if not dev_id:
            return
        self.devices[dev_id] = dev

        # Persist GPS track if present
        pos = dev.get("position")
        if pos and "latitude" in pos and "longitude" in pos:
            await self._append_track(dev_id, pos)

        # notify platforms
        self.async_set_updated_data(self.devices)

    async def _append_track(self, dev_id: str, pos: Dict[str, Any]) -> None:
        st = await self.store.async_load() or {}
        dev_track = st.setdefault("tracks", {}).setdefault(dev_id, [])
        point = {
            "lat": pos.get("latitude"),
            "lon": pos.get("longitude"),
            "ts": pos.get("time") or datetime.now(timezone.utc).isoformat(),
        }
        # de-dup consecutive identical points
        if not dev_track or dev_track[-1]["lat"] != point["lat"] or dev_track[-1]["lon"] != point["lon"]:
            dev_track.append(point)
            await self.store.async_save(st)

    async def async_get_geojson(self, dev_id: str, hours: int = 12) -> Dict[str, Any]:
        st = await self.store.async_load() or {}
        points = st.get("tracks", {}).get(dev_id, [])
        cutoff = datetime.now(timezone.utc) - timedelta(hours=hours)
        coords = []
        for p in points:
            try:
                ts = datetime.fromisoformat(p["ts"].replace("Z","+00:00"))
            except Exception:
                continue
            if ts >= cutoff:
                coords.append([p["lon"], p["lat"], ts.isoformat()])
        return {
            "type": "Feature",
            "geometry": {
                "type": "LineString",
                "coordinates": coords
            },
            "properties": {
                "device_id": dev_id,
                "generated": datetime.now(timezone.utc).isoformat()
            }
        }
