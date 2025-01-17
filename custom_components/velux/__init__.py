"""Support for VELUX KLF 200 devices."""
import logging

import homeassistant.helpers.config_validation as cv
import voluptuous as vol
from homeassistant.config_entries import SOURCE_IMPORT, ConfigEntry
from homeassistant.const import CONF_HOST, CONF_PASSWORD, EVENT_HOMEASSISTANT_STOP
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryNotReady
from homeassistant.helpers import device_registry as dr
from homeassistant.helpers.device_registry import DeviceEntry
from homeassistant.helpers.typing import ConfigType
from pyvlx import PyVLX

from .const import DOMAIN, LOGGER, PLATFORMS


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up velux component from config entry."""

    # Setup pyvlx module and connect to KLF200
    pyvlx_args = {
        "host": entry.data[CONF_HOST],
        "password": entry.data[CONF_PASSWORD],
    }
    pyvlx: PyVLX = PyVLX(**pyvlx_args)
    try:
        await pyvlx.connect()
    except OSError as ex:
        LOGGER.warning("Unable to connect to KLF200: %s", str(ex))
        raise ConfigEntryNotReady from ex

    # Store pyvlx in hass data
    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = pyvlx

    # Add bridge device to device registry
    connections = set()
    mac_address = hass.data.get(dr.CONNECTION_NETWORK_MAC)
    if mac_address is not None:
        connections = {(dr.CONNECTION_NETWORK_MAC, mac_address)}

    device_registry = dr.async_get(hass)
    device_registry.async_get_or_create(
        config_entry_id=entry.entry_id,
        identifiers={(DOMAIN, entry.unique_id)},
        connections=connections,
        manufacturer="Velux",
        name=entry.unique_id,
        model="KLF200",
        hw_version=pyvlx.klf200.version.hardwareversion,
        sw_version=pyvlx.klf200.version.softwareversion,
    )

    # Load nodes (devices) and scenes from API
    await pyvlx.load_nodes()
    await pyvlx.load_scenes()

    # Setup velux components
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    async def on_hass_stop(event):
        """Close connection when hass stops."""
        LOGGER.debug("Velux interface terminated")
        await pyvlx.disconnect()

    hass.bus.async_listen_once(EVENT_HOMEASSISTANT_STOP, on_hass_stop)

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


async def async_remove_config_entry_device(
    hass: HomeAssistant, config_entry: ConfigEntry, device_entry: DeviceEntry
) -> bool:
    """Remove a config entry from a device."""
    return True
