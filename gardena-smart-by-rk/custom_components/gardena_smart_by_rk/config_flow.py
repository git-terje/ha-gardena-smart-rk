from __future__ import annotations

import logging
from typing import Any, Dict

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.core import callback
from homeassistant.data_entry_flow import FlowResult
from homeassistant.helpers import config_entry_oauth2_flow
from homeassistant.helpers.network import get_url

from .const import DOMAIN, AUTH_AUTHORIZE_URL, AUTH_TOKEN_URL, SCOPES

_LOGGER = logging.getLogger(__name__)

class GardenaOAuth2Implementation(config_entry_oauth2_flow.LocalOAuth2Implementation):
    def __init__(self, hass, client_id: str, client_secret: str):
        redirect_uri = f"{get_url(hass)}/auth/external/callback"
        super().__init__(
            hass,
            DOMAIN,
            client_id,
            client_secret,
            AUTH_AUTHORIZE_URL,
            AUTH_TOKEN_URL,
            redirect_uri,
        )

class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1

    async def async_step_user(self, user_input: Dict[str, Any] | None = None) -> FlowResult:
        if user_input is None:
            return self.async_show_form(
                step_id="user",
                data_schema=vol.Schema({
                    vol.Required("client_id"): str,
                    vol.Required("client_secret"): str,
                }),
            )

        impl = GardenaOAuth2Implementation(self.hass, user_input["client_id"], user_input["client_secret"])
        config_entry_oauth2_flow.async_register_implementation(self.hass, impl)

        return await config_entry_oauth2_flow.async_oauth2_flow_start(
            self, impl
        )

    async def async_step_import(self, user_input: Dict[str, Any] | None = None) -> FlowResult:
        return await self.async_step_user(user_input)

    @callback
    def async_get_options_flow(self, config_entry):
        return OptionsFlowHandler(config_entry)


class OptionsFlowHandler(config_entries.OptionsFlow):
    def __init__(self, config_entry: config_entries.ConfigEntry) -> None:
        self.config_entry = config_entry

    async def async_step_init(self, user_input=None) -> FlowResult:
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        data_schema = vol.Schema({
            vol.Optional("route_window_hours", default=self.config_entry.options.get("route_window_hours", 12)): int,
        })
        return self.async_show_form(step_id="init", data_schema=data_schema)
