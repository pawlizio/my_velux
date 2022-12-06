"""Component to interface with switches that can be controlled remotely."""
import logging

from pyvlx import OnOffSwitch

from homeassistant.helpers.entity import EntityCategory
from homeassistant.components.switch import SwitchEntity, SwitchDeviceClass
from homeassistant.core import callback

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)
PARALLEL_UPDATES = 1


async def async_setup_entry(hass, entry, async_add_entities):
    """Set up sensor(s) for Velux platform."""
    entities = []
    gateway = hass.data[DOMAIN][entry.entry_id]
    entities.append(VeluxHouseStatusMonitor(gateway))
    entities.append(VeluxHeartbeat(gateway))
    for node in gateway.nodes:
        if isinstance(node, OnOffSwitch):
            _LOGGER.debug("Switch will be added: %s", node.name)
            entities.append(VeluxSwitch(node))
    async_add_entities(entities)


class VeluxHouseStatusMonitor(SwitchEntity):
    """Representation of a Velux HouseStatusMonitor switch."""

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
    """Representation of a Velux Heartbeat switch."""

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

class VeluxSwitch(SwitchEntity):
    """Representation of a Velux physical switch."""

    def __init__(self, node):
        """Initialize the cover."""
        self.node = node

    @callback
    def async_register_callbacks(self):
        """Register callbacks to update hass after device was changed."""

        async def after_update_callback(device):
            """Call after device was updated."""
            self.async_write_ha_state()

        self.node.register_device_updated_cb(after_update_callback)

    async def async_added_to_hass(self):
        """Store register state change callback."""
        self.async_register_callbacks()

    @property
    def unique_id(self):
        """Return the unique ID of this cover."""
        return self.node.node_id

    @property
    def device_info(self):
        return {
            "identifiers": {
                (DOMAIN, self.unique_id)
            },
            "name": self.name,
        }

    @property
    def name(self):
        """Return the name of the Velux switch."""
        return self.node.name

    @property
    def should_poll(self):
        """No polling needed within Velux."""
        return False

    @property
    def device_class(self):
        """Return the device class of this node."""
        return SwitchDeviceClass.SWITCH

    @property
    def is_on(self):
        """Return the state of the switch"""
        return self.node.is_on()

    async def async_turn_on(self, **kwargs):
        """Turn the switch on."""
        await self.node.set_on()

    async def async_turn_off(self, **kwargs):
        """Turn the switch off."""
        await self.node.set_off()