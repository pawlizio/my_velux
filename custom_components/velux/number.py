"""Component to allow numeric input for platforms."""

from pyvlx.opening_device import Blind

from homeassistant.helpers.entity import EntityCategory
from homeassistant.components.number import NumberEntity
from homeassistant.components.number.const import DOMAIN, MODE_SLIDER


from .const import DOMAIN

PARALLEL_UPDATES = 1


async def async_setup_entry(hass, entry, async_add_entities):
    """Set up cover(s) for Velux platform."""
    entities = []
    gateway = hass.data[DOMAIN][entry.entry_id]
    for node in gateway.nodes:
        if isinstance(node, Blind):
            entities.append(VeluxOpenOrientatoion(node))
            entities.append(VeluxCloseOrientatoion(node))
    async_add_entities(entities)


class VeluxOpenOrientatoion(NumberEntity):
    """Representation of a Velux number."""
    
    def __init__(self, node):
        """Initialize the cover."""
        self.node = node
        # self.entity_description = "Configure open orientation of %s", self.node.name
    
    @property
    def device_info(self):
        return {
            "identifiers": {
                (DOMAIN, self.node.node_id)
            },
            "name": self.node.name,
        }

    def set_native_value(self, value):
        """Update the current value."""
        self.node.open_orientation_target = int(value)

    @property
    def native_value(self) -> float:
        """Return the entity value to represent the entity state."""
        return self.node.open_orientation_target

    @property
    def name(self):
        """Return the name of the Velux device."""
        name = self.node.name + "_open_orientation_target"
        return name

    @property
    def unique_id(self):
        """Return the unique ID of this number."""
        id = str(self.node.node_id) + "_open_orientation_target"
        return id
    
    @property
    def entity_category(self):
        """Return the entity_categor of this number."""
        return EntityCategory.CONFIG

    @property
    def mode(self):
        """Return the mode of this number."""
        return MODE_SLIDER

class VeluxCloseOrientatoion(NumberEntity):
    """Representation of a Velux number."""
    
    def __init__(self, node):
        """Initialize the cover."""
        self.node = node
        # self.entity_description = "Configure close orientation of %s", self.node.name
    
    @property
    def device_info(self):
        return {
            "identifiers": {
                (DOMAIN, self.node.node_id)
            },
            "name": self.node.name,
        }

    def set_native_value(self, value):
        """Update the current value."""
        self.node.close_orientation_target = int(value)

    @property
    def native_value(self) -> float:
        """Return the entity value to represent the entity state."""
        return self.node.close_orientation_target

    @property
    def name(self):
        """Return the name of the Velux device."""
        name = self.node.name + "_close_orientation_target"
        return name

    @property
    def unique_id(self):
        """Return the unique ID of this cover."""
        id = str(self.node.node_id) + "_close_orientation_target"
        return id
    
    @property
    def entity_category(self):
        """Return the entity_categor of this number."""
        return EntityCategory.CONFIG

    @property
    def mode(self):
        """Return the mode of this number."""
        return MODE_SLIDER