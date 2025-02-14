"""Component to allow numeric input for platforms."""

from homeassistant.components.number import (
    NumberExtraStoredData,
    NumberMode,
    RestoreNumber,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import PERCENTAGE, EntityCategory
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from pyvlx import PyVLX
from pyvlx.opening_device import Blind, DualRollerShutter, OpeningDevice

from .const import DOMAIN

PARALLEL_UPDATES = 1


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """Set up cover(s) for Velux platform."""
    entities: list = []
    pyvlx: PyVLX = hass.data[DOMAIN][entry.entry_id]
    entities.append(VeluxHeartbeatInterval(pyvlx, entry))
    for node in pyvlx.nodes:
        if isinstance(node, Blind):
            entities.append(VeluxOpenOrientation(node, entry))
            entities.append(VeluxCloseOrientation(node, entry))
        if isinstance(node, OpeningDevice) and not isinstance(node, DualRollerShutter):
            entities.append(VeluxDefaultVelocity(node, entry))
    async_add_entities(entities)


class VeluxOpenOrientation(RestoreNumber):
    """Representation of a VeluxOpenOrientation number."""

    _attr_entity_category = EntityCategory.CONFIG
    _attr_native_max_value = 100
    _attr_native_min_value = 0
    _attr_native_step = 1.0
    _attr_mode = NumberMode.SLIDER
    _number_option_unit_of_measurement = PERCENTAGE

    def __init__(self, node: Blind, entry: ConfigEntry) -> None:
        """Initialize the number."""
        self.node: Blind = node
        self._attr_name = self.node.name + "_open_orientation_target"
        self._attr_unique_id = f"{self.node.node_id}_open_orientation_target"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, str(self.node.node_id))},
            name=self.node.name,
            via_device=(DOMAIN, str(entry.unique_id)),
        )

    async def async_set_native_value(self, value: float) -> None:
        """Update the current value."""
        LOGGER.debug("Trying to set open_orientation_target of node: %s to %s", self.node, int(value))
        self.node.open_orientation_target = int(value)
        self._attr_native_value = self.node.open_orientation_target
        self.async_write_ha_state()
        LOGGER.debug("Resulting open_orientation_target of node: %s to %s", self.node, self.node.open_orientation_target)
        LOGGER.debug("Attribute value is: %s", self._attr_native_value)
        
    async def async_internal_added_to_hass(self) -> None:
        """Restore number from last number data."""
        await super().async_internal_added_to_hass()

        value: NumberExtraStoredData | None = await self.async_get_last_number_data()
        if value is not None and value.native_value is not None:
            try:
                LOGGER.debug("Restored open_orientation_target for node: %s with value %s", self.node, value.native_value)
                await self.async_set_native_value(value.native_value)
            except (TypeError, ValueError):
                LOGGER.debug("Could not restore open_orientation_target for node: %s", self.node)
                await self.async_set_native_value(self.node.open_orientation_target)


class VeluxCloseOrientation(RestoreNumber):
    """Representation of a VeluxCloseOrientation number."""

    _attr_entity_category = EntityCategory.CONFIG
    _attr_native_max_value = 100
    _attr_native_min_value = 0
    _attr_native_step = 1.0
    _attr_mode = NumberMode.SLIDER
    _number_option_unit_of_measurement = PERCENTAGE

    def __init__(self, node: Blind, entry: ConfigEntry) -> None:
        """Initialize the number."""
        self.node: Blind = node
        self._attr_name = self.node.name + "_close_orientation_target"
        self._attr_unique_id = f"{self.node.node_id}_close_orientation_target"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, str(self.node.node_id))},
            name=self.node.name,
            via_device=(DOMAIN, str(entry.unique_id)),
        )

    async def async_set_native_value(self, value: float) -> None:
        """Update the current value."""
        self.node.close_orientation_target = int(value)
        self._attr_native_value = self.node.close_orientation_target
        self.async_write_ha_state()

    async def async_internal_added_to_hass(self) -> None:
        """Restore number from last number data."""
        await super().async_internal_added_to_hass()

        value: NumberExtraStoredData | None = await self.async_get_last_number_data()
        if value is not None and value.native_value is not None:
            try:
                await self.async_set_native_value(value.native_value)
            except (TypeError, ValueError):
                await self.async_set_native_value(self.node.close_orientation_target)


class VeluxDefaultVelocity(RestoreNumber):
    """Representation of a VeluxDefaultVelocity number."""

    _attr_entity_category = EntityCategory.CONFIG
    _attr_native_max_value = 100
    _attr_native_min_value = 0
    _attr_native_step = 1.0
    _attr_mode = NumberMode.SLIDER
    _number_option_unit_of_measurement = PERCENTAGE

    def __init__(self, node: OpeningDevice, entry: ConfigEntry) -> None:
        """Initialize the number."""
        self.node: OpeningDevice = node
        self._attr_name = self.node.name + " Default Velocity"
        self._attr_unique_id = f"{self.node.node_id}_default_velocity"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, str(self.node.node_id))},
            name=self.node.name,
            via_device=(DOMAIN, str(entry.unique_id)),
        )

    async def async_set_native_value(self, value: float) -> None:
        """Update the current value."""
        self.node.default_velocity = int(value)  # type: ignore[assignment]
        self._attr_native_value = self.node.default_velocity
        self.async_write_ha_state()

    async def async_added_to_hass(self) -> None:
        """Restore number from last number data."""
        await super().async_internal_added_to_hass()

        value: NumberExtraStoredData | None = await self.async_get_last_number_data()
        if value is not None and value.native_value is not None:
            try:
                await self.async_set_native_value(value.native_value)
            except (TypeError, ValueError):
                await self.async_set_native_value(self.node.default_velocity)


class VeluxHeartbeatInterval(RestoreNumber):
    """Representation of a VeluxHeartbeatInterval number."""

    def __init__(self, pyvlx: PyVLX, entry: ConfigEntry) -> None:
        """Initialize the number entity."""
        self.pyvlx = pyvlx
        self._attr_entity_category = EntityCategory.CONFIG
        self._attr_name = "Heartbeat interval (Default=30)"
        self._attr_native_max_value = 600
        self._attr_native_min_value = 30
        self._attr_native_step = 10
        self._attr_mode = NumberMode.SLIDER
        self._attr_unique_id = f"{entry.unique_id}_velux_heartbeat_interval"
        self._number_option_unit_of_measurement = PERCENTAGE
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, str(entry.unique_id))},
        )

    async def async_set_native_value(self, value: float) -> None:
        """Update the current value."""
        self.pyvlx.heartbeat.interval = int(value)
        self._attr_native_value = self.pyvlx.heartbeat.interval
        self.async_write_ha_state()

    async def async_internal_added_to_hass(self) -> None:
        """Restore number from last number data."""
        await super().async_internal_added_to_hass()

        value: NumberExtraStoredData | None = await self.async_get_last_number_data()
        if value is not None and value.native_value is not None:
            try:
                await self.async_set_native_value(value.native_value)
            except (TypeError, ValueError):
                await self.async_set_native_value(self.pyvlx.heartbeat.interval)
