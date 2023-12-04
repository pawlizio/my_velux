"""Generic Velux Entity."""
from typing import Optional

from pyvlx import Node

from homeassistant.core import callback
from homeassistant.helpers.entity import DeviceInfo, Entity

from .const import DOMAIN


class VeluxNodeEntity(Entity):
    """Abstraction for all pyvlx node entities."""

    _attr_should_poll = False

    def __init__(self, node: Node, subtype: Optional[str] = None) -> None:
        """Initialize the Velux device."""
        self.subtype: str = subtype
        self.node: Node = node

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
    def unique_id(self) -> str:
        """Return the unique ID of this entity."""
        # Unique IDs for double cover, subtyme is either upper or lower
        if self.subtype is not None:
            unique_id = str(self.node.node_id) + "_" + self.subtype
        # Some devices from other vendors does not provide a serial_number
        # Node_if is used instead, which is unique within velux component
        elif self.node.serial_number is None:
            unique_id = str(self.node.node_id)
        else:
            unique_id = self.node.serial_number
        return unique_id

    @property
    def name(self) -> str:
        """Return the name of the entity."""
        if not self.node.name:
            return "#" + str(self.node.node_id)
        # Name for double cover which is handled in one node within pylx,
        # but represented by 3 covers in HA (upper, lower, combined)
        if self.subtype is not None:
            return self.node.name + "_" + self.subtype
        return self.node.name

    @property
    def should_poll(self) -> bool:
        """No polling needed within Velux."""
        return False

    @property
    def device_info(self) -> DeviceInfo:
        """Return specific device attributes."""
        return {
            "identifiers": {(DOMAIN, self.node.node_id)},
            "name": self.name,
        }
