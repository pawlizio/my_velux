"""Support for VELUX KLF 200 devices."""
import logging

from pyvlx import PyVLX

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_HOST, CONF_PASSWORD
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryNotReady
from homeassistant.helpers.typing import ConfigType

from .const import (
    CONF_HEARTBEAT_INTERVAL,
    CONF_HEARTBEAT_LOAD_ALL_STATES,
    DOMAIN,
    PLATFORMS,
)

_LOGGER = logging.getLogger(__name__)


async def async_setup(hass: HomeAssistant, config: ConfigType) -> bool:
    """Set up velux component via configuration.yaml."""
    if DOMAIN in config:
        _LOGGER.warning(
            "Please note that configuration of integrations which communicate to external devices should no longer use configuration.yaml setup. Your configuration data has been transferred to integration flow used on the GUI Integration page. You can safely remove your velux entry from configuration.yaml"
        )
        hass.async_create_task(
            hass.config_entries.flow.async_init(
                DOMAIN, context={"source": "import"}, data=config[DOMAIN]
            )
        )
    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up velux component from config entry."""
    # Setup pyvlx module and connect to KLF200
    pyvlx_args = {
        "host": entry.data[CONF_HOST],
        "password": entry.data[CONF_PASSWORD],
        "heartbeat_interval": entry.data.get(CONF_HEARTBEAT_INTERVAL, 30),
        "heartbeat_load_all_states": entry.data.get(
            CONF_HEARTBEAT_LOAD_ALL_STATES, True
        ),
    }
    pyvlx: PyVLX = PyVLX(**pyvlx_args)
    try:
        await pyvlx.connect()
    except OSError as ex:
        _LOGGER.warning("Unable to connect to KLF200: %s", str(ex))
        raise ConfigEntryNotReady from ex

    # Store pyvlx in hass data
    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = pyvlx

    # Setup velux components
    await pyvlx.load_nodes()
    await pyvlx.load_scenes()
    for component in PLATFORMS:
        hass.async_create_task(
            hass.config_entries.async_forward_entry_setup(entry, component)
        )

    # Register velux services
    async def async_reboot_gateway(service_call):
        await pyvlx.reboot_gateway()

    hass.services.async_register(DOMAIN, "reboot_gateway", async_reboot_gateway)

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unloading the Velux platform."""
    pyvlx: PyVLX = hass.data[DOMAIN][entry.entry_id]
    # Disconnect from KLF200
    await pyvlx.disconnect()

    # Unload velux platform components
    for component in PLATFORMS:
        await hass.config_entries.async_forward_entry_unload(entry, component)

    return True
