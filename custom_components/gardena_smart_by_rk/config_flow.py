from homeassistant import config_entries
from homeassistant.core import callback
from .const import DOMAIN

class GardenaSmartConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Gardena Smart by RK."""

    VERSION = 1

    async def async_step_user(self, user_input=None):
        if user_input is not None:
            return self.async_create_entry(title="Gardena Smart by RK", data=user_input)
        return self.async_show_form(step_id="user", data_schema=None)

    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        return GardenaSmartOptionsFlowHandler(config_entry)

class GardenaSmartOptionsFlowHandler(config_entries.OptionsFlow):
    def __init__(self, config_entry):
        self.config_entry = config_entry

    async def async_step_init(self, user_input=None):
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)
        return self.async_show_form(step_id="init", data_schema=None)
