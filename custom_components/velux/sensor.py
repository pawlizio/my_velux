"""Support for VELUX sensors."""
from homeassistant.components.binary_sensor import BinarySensorEntity, BinarySensorDeviceClass
from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import callback, HomeAssistant
from homeassistant.helpers.entity import DeviceInfo, EntityCategory
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from pyvlx import PyVLX

from .const import DOMAIN


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """Set up sensor(s) for Velux platform."""
    entities = []
    pyvlx: PyVLX = hass.data[DOMAIN][entry.entry_id]
    entities.append(VeluxConnectionCounter(pyvlx, entry))
    entities.append(VeluxConnectionState(pyvlx, entry))
    async_add_entities(entities)


class VeluxConnectionCounter(SensorEntity):
    """Representation of a Velux number."""

    def __init__(self, pyvlx: PyVLX, entry: ConfigEntry) -> None:
        """Initialize the cover."""
        self.pyvlx: PyVLX = pyvlx
        self._attr_unique_id = f"{entry.unique_id}_connection_counter"
        self._attr_name = "Connection Counter"
        self._attr_native_value = self.pyvlx.connection.connection_counter
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, entry.unique_id)},
        )


class VeluxConnectionState(BinarySensorEntity):
    """Representation of a Velux state."""

    def __init__(self, pyvlx: PyVLX, entry: ConfigEntry):
        """Initialize the cover."""
        self.pyvlx: PyVLX = pyvlx
        self._attr_unique_id = f"{entry.unique_id}_connection_state"
        self._attr_device_class = BinarySensorDeviceClass.CONNECTIVITY
        self._attr_name = "Connection State"
        self._attr_is_on = self.pyvlx.connection.connected
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, entry.unique_id)},
        )

    @callback
    async def after_update_callback(self):
        """Call after device was updated."""
        self.async_write_ha_state()

    async def async_added_to_hass(self) -> None:
        """Register callbacks to update hass after device was changed."""
        self.pyvlx.connection.register_connection_opened_cb(self.after_update_callback)
        self.pyvlx.connection.register_connection_closed_cb(self.after_update_callback)

    async def async_will_remove_from_hass(self) -> None:
        """Unregister callbacks to update hass after device was changed."""
        self.pyvlx.connection.unregister_connection_opened_cb(self.after_update_callback)
        self.pyvlx.connection.unregister_connection_closed_cb(self.after_update_callback)
