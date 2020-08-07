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
        vol.Required(CONF_HOST, default=""): str,
        vol.Required(CONF_PASSWORD, default=""): str,
    }
)


def host_valid(host):
    """Return True if hostname or IP address is valid."""
    try:
        if ipaddress.ip_address(host).version == (4 or 6):
            return True
    except ValueError:
        disallowed = re.compile(r"[^a-zA-Z\d\-]")
        return all(x and not disallowed.search(x) for x in host.split("."))


class VeluxConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Velux config flow."""

    def __init__(self):
        """Initialize."""
        self.pyvlx = None
        self.host = None
        self.password = None

    async def async_step_zeroconf(self, info):
        _LOGGER.debug("Received from zeroconf %s", info)

        if info is None:
            return self.async_abort(reason="connection_error")

        if not info.get("name") or not info["name"].startswith(
            "VELUX_KLF_LAN"
        ):
            return self.async_abort(reason="not_velux_klf200")
        self.host = info["hostname"].rstrip(".")

        return self.async_show_form(
            step_id="zeroconf", data_schema=vol.Schema({
                vol.Required("host", default=self.host): str,
                vol.Required("password", default=""): str})
        )

    async def async_step_user(self, user_input=None):
        """Handle the initial step."""
        errors = {}

        if user_input is not None:
            try:
                if not host_valid(user_input[CONF_HOST]):
                    raise InvalidHost()
            except InvalidHost:
                errors[CONF_HOST] = "wrong_host"
            except ConnectionError:
                errors["base"] = "connection_error"
            except SnmpError:
                errors["base"] = "snmp_error"

        return self.async_show_form(
            step_id="user", data_schema=DATA_SCHEMA, errors=errors
        )
