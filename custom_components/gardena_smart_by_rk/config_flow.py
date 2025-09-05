import voluptuous as vol
from homeassistant import config_entries
from homeassistant.core import HomeAssistant
from homeassistant.helpers import config_validation as cv
from .const import DOMAIN

DATA_SCHEMA = vol.Schema(
    {
        vol.Required("client_id"): cv.string,
        vol.Required("client_secret"): cv.string,
        vol.Required("username"): cv.string,
        vol.Required("password"): cv.string,
    }
)

class GardenaConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle config flow for Gardena Smart by RK."""

    VERSION = 1

    async def async_step_user(self, user_input=None):
        """UI setup."""
        errors = {}

        if user_input is not None:
            # TODO: validate credentials against Gardena API v2 here
            return self.async_create_entry(
                title="Gardena Smart by RK",
                data=user_input,
            )

        return self.async_show_form(
            step_id="user", data_schema=DATA_SCHEMA, errors=errors
        )
