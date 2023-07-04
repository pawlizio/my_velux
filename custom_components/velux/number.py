"""Component to allow numeric input for platforms."""

from homeassistant.const import PERCENTAGE
from homeassistant.helpers.restore_state import RestoreEntity
from pyvlx.opening_device import Blind, DualRollerShutter, OpeningDevice

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
        if isinstance(node, OpeningDevice) and not isinstance(node, DualRollerShutter):
            entities.append(VeluxDefaultVelocity(node))
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


class VeluxDefaultVelocity(NumberEntity, RestoreEntity):
    """Representation of a Velux number."""

    def __init__(self, node):
        """Initialize the cover."""
        self.node = node
        self._attr_unit_of_measurement = PERCENTAGE

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
        self._attr_native_value = self.node.default_velocity = int(value)

    async def async_internal_added_to_hass(self) -> None:
        await super().async_internal_added_to_hass()

        value = await self.async_get_last_state()

        if value is not None and value.state is not None and value.state != "unavailable":
            try:
                self.set_native_value(value.state)
            except:
                self.set_native_value(100)
        else:
            self.set_native_value(100)

    @property
    def name(self):
        """Return the name of the Velux device."""
        name = self.node.name + " Default Velocity"
        return name

    @property
    def unique_id(self):
        """Return the unique ID of this cover."""
        id = str(self.node.node_id) + "_default_velocity"
        return id

    @property
    def entity_category(self):
        """Return the entity_categor of this number."""
        return EntityCategory.CONFIG

    @property
    def native_max_value(self) -> int:
        """Return the max value."""
        return 100

    @property
    def native_min_value(self) -> int:
        """Return the max value."""
        return 0

    @property
    def native_step(self) -> float | None:
        """Return the native step value."""
        return 1.0

    @property
    def mode(self):
        """Return the mode of this number."""
        return MODE_SLIDER