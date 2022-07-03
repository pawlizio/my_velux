"""Component to interface with switches that can be controlled remotely."""

from pyvlx.opening_device import Blind

from homeassistant.helpers.entity import EntityCategory
from homeassistant.components.switch import SwitchEntity, SwitchDeviceClass

from .const import DOMAIN

PARALLEL_UPDATES = 1


async def async_setup_entry(hass, entry, async_add_entities):
    """Set up sensor(s) for Velux platform."""
    entities = []
    gateway = hass.data[DOMAIN][entry.entry_id]
    entities.append(VeluxHouseStatusMonitor(gateway))
    entities.append(VeluxHeartbeat(gateway))
    async_add_entities(entities)


class VeluxHouseStatusMonitor(SwitchEntity):
    """Representation of a Velux number."""

    def __init__(self, gateway):
        """Initialize the cover."""
        self.pyvlx = gateway

    @property
    def name(self):
        """Name of the entity."""
        return "KLF200 House Status Monitor"

    @property
    def device_info(self):
        return {
            "identifiers": {
                (DOMAIN, self.unique_id)
            },
            "connections": {
                ("Host", self.pyvlx.config.host)
            },
            "name": "KLF200 Gateway",
            "manufacturer": "Velux",
            "sw_version": self.pyvlx.version,
        }

    @property
    def entity_category(self):
        """Return the entity_categor of this number."""
        return EntityCategory.CONFIG

    @property
    def device_class(self):
        """Return the entity_categor of this number."""
        return SwitchDeviceClass.SWITCH

    @property
    def unique_id(self):
        """Return the unique ID of this cover."""
        return "KLF200_House_Status_Monitor"

    @property
    def is_on(self):
        """Return if the switch state"""
        return self.pyvlx.klf200.house_status_monitor_enabled

    async def async_turn_on(self, **kwargs):
        """Turn the entity on."""
        await self.pyvlx.klf200.house_status_monitor_enable(pyvlx=self.pyvlx)

    async def async_turn_off(self, **kwargs):
        """Turn the entity off."""
        await self.pyvlx.klf200.house_status_monitor_disable(pyvlx=self.pyvlx)

class VeluxHeartbeat(SwitchEntity):
    """Representation of a Velux number."""

    def __init__(self, gateway):
        """Initialize the cover."""
        self.pyvlx = gateway

    @property
    def name(self):
        """Name of the entity."""
        return "PyVLX Heartbeat"

    @property
    def device_info(self):
        return {
            "identifiers": {
                (DOMAIN, self.unique_id)
            },
            "connections": {
                ("Host", self.pyvlx.config.host)
            },
            "name": "KLF200 Gateway",
            "manufacturer": "Velux",
            "sw_version": self.pyvlx.version,
        }

    @property
    def entity_category(self):
        """Return the entity_categor of this number."""
        return EntityCategory.CONFIG

    @property
    def device_class(self):
        """Return the entity_categor of this number."""
        return SwitchDeviceClass.SWITCH

    @property
    def unique_id(self):
        """Return the unique ID of this cover."""
        return "PyVLX_Heartbeat"

    @property
    def is_on(self):
        """Return if the switch state"""
        return (not self.pyvlx.heartbeat.stopped)

    def async_turn_on(self, **kwargs):
        """Turn the entity on."""
        self.pyvlx.heartbeat.start()

    async def async_turn_off(self, **kwargs):
        """Turn the entity off."""
        await self.pyvlx.heartbeat.stop()