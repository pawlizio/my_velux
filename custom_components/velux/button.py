"""Component to pressing a button as platforms."""

from pyvlx.opening_device import Blind

from homeassistant.helpers.entity import EntityCategory
from homeassistant.components.button import ButtonEntity, ButtonDeviceClass

from .const import DOMAIN

PARALLEL_UPDATES = 1


async def async_setup_entry(hass, entry, async_add_entities):
    """Set up sensor(s) for Velux platform."""
    entities = []
    gateway = hass.data[DOMAIN][entry.entry_id]
    entities.append(VeluxGatewayRestart(gateway))
    async_add_entities(entities)


class VeluxGatewayRestart(ButtonEntity):
    """Representation of a Velux number."""

    def __init__(self, gateway):
        """Initialize the cover."""
        self.pyvlx = gateway
        # self.entity_description = "Configure open orientation of %s", self.node.name

    @property
    def name(self):
        """Name of the entity."""
        return "KLF200 Reboot"

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
    def unique_id(self):
        """Return the unique ID of this cover."""
        return "KLF200_Reboot"

    @property
    def entity_category(self):
        """Return the entity_categor of this number."""
        return EntityCategory.CONFIG

    @property
    def device_class(self):
        """Return the entity_categor of this number."""
        return ButtonDeviceClass.RESTART

    async def async_press(self) -> None:
        """Handle the button press."""
        await self.pyvlx.klf200.reboot()
