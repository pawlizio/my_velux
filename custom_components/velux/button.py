"""Component to pressing a button as platforms."""

from homeassistant.components.button import ButtonDeviceClass, ButtonEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import DeviceInfo, EntityCategory
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from pyvlx import PyVLX

from .const import DOMAIN

PARALLEL_UPDATES = 1


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """Set up sensor(s) for Velux platform."""
    entities = []
    pyvlx: PyVLX = hass.data[DOMAIN][entry.entry_id]
    entities.append(VeluxGatewayRestart(pyvlx, entry))
    async_add_entities(entities)


class VeluxGatewayRestart(ButtonEntity):
    """Representation of a KLF200 restart button entity."""

    def __init__(self, pyvlx: PyVLX, entry: ConfigEntry) -> None:
        """Initialize the button entity."""
        self.pyvlx: PyVLX = pyvlx
        self._attr_unique_id = f"reboot_{entry.unique_id}"
        self._attr_entity_category = EntityCategory.CONFIG
        self._attr_device_class = ButtonDeviceClass.RESTART
        self._attr_name = f"Reboot {entry.unique_id}"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, entry.unique_id)},
        )

    async def async_press(self) -> None:
        """Handle the button press."""
        await self.pyvlx.klf200.reboot()
