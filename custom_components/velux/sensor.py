from homeassistant.components.sensor import SensorEntity

from .const import DOMAIN


async def async_setup_entry(hass, entry, async_add_entities):
    """Set up sensor(s) for Velux platform."""
    entities = []
    gateway = hass.data[DOMAIN][entry.entry_id]
    entities.append(VeluxConnectionCounter(gateway))
    async_add_entities(entities)


class VeluxConnectionCounter(SensorEntity):
    """Representation of a Velux number."""

    def __init__(self, gateway):
        """Initialize the cover."""
        self.pyvlx = gateway   

    @property
    def name(self):
        """Name of the entity."""
        return "KLF200 Connection Counter"

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
        return "KLF200ConnectionCounter"

    @property
    def native_value(self):
        """Return the value reported by the sensor."""
        return self.pyvlx.connection.connection_counter
