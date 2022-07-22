"""Support for VELUX KLF 200 devices."""
import logging

from pyvlx import PyVLX

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_HOST, CONF_PASSWORD
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryNotReady

from .const import DOMAIN, PLATFORMS

_LOGGER = logging.getLogger(__name__)


async def async_setup(hass, config):
    """Set up the Velux KLF platform via configuration.yaml."""
    if DOMAIN in config:
        _LOGGER.debug("Please note that configuration of integrations which communicate to external devices should no longer use configuration.yaml setup. Your configuration data has been transferred to integration flow used on the GUI Integration page. You can safely remove your velux entry from configuration.yaml")
        hass.async_create_task(
            hass.config_entries.flow.async_init(
                DOMAIN, context={"source": "import"}, data=config[DOMAIN]
            )
        )
    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Set up the Velux KLF platforms via Config Flow."""
    _LOGGER.debug("Setting up velux entry via config flow")
    host = entry.data[CONF_HOST]
    password = entry.data[CONF_PASSWORD]
    gateway = PyVLX(host=host, password=password)

    try: 
        await gateway.connect()
    except OSError as ex:
        _LOGGER.warning("Unable to connect to KLF200: %s", str(ex))
        raise ConfigEntryNotReady from ex

    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = gateway

    await gateway.load_nodes()
    await gateway.load_scenes()

    for component in PLATFORMS:
        hass.async_create_task(
            hass.config_entries.async_forward_entry_setup(entry, component)
        )

    async def async_reboot_gateway(service_call):
        await gateway.reboot_gateway()

    hass.services.async_register(DOMAIN, "reboot_gateway", async_reboot_gateway)

    return True


async def async_unload_entry(hass, entry):
    """Unloading the Velux platform."""
    gateway = hass.data[DOMAIN][entry.entry_id]
    await gateway.reboot_gateway()
    await gateway.disconnect()

    for component in PLATFORMS:
        await hass.config_entries.async_forward_entry_unload(entry, component)

    return True
