# https://developers.home-assistant.io/docs/config_entries_config_flow_handler#defining-your-config-flow
import logging
import voluptuous as vol

from homeassistant import config_entries
from .const import (
    DOMAIN,
    CONF_HOST,
    CONF_PASSWORD
)


DATA_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_HOST): str,
        vol.Required(CONF_PASSWORD): str,
    }
)

class ExampleConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Example config flow."""

    async def zeroconf(self, info):
        if info is not None:
            pass  # TODO: process info

        return self.async_show_form(
            step_id="user", data_schema=vol.Schema({vol.Required("password"): str})
        )