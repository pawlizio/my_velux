"""Support for Velux covers."""
from __future__ import annotations

import asyncio
from datetime import timedelta
import inspect
import logging
from typing import Any, Optional

from pyvlx import OpeningDevice, Position, PyVLX
from pyvlx.api.get_limitation import GetLimitation
from pyvlx.exception import PyVLXException
from pyvlx.opening_device import (
    Awning,
    Blind,
    DualRollerShutter,
    GarageDoor,
    Gate,
    RollerShutter,
    Window,
)
import voluptuous as vol

from homeassistant.components.cover import (
    ATTR_POSITION,
    ATTR_TILT_POSITION,
    CoverDeviceClass,
    CoverEntity,
    CoverEntityFeature,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import (
    SERVICE_CLOSE_COVER,
    SERVICE_OPEN_COVER,
    SERVICE_SET_COVER_POSITION,
)
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity_platform import (
    AddEntitiesCallback,
    EntityPlatform,
    async_get_current_platform,
)
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

from .const import ATTR_VELOCITY, DOMAIN, DUAL_COVER, LOWER_COVER, UPPER_COVER
from .node_entity import VeluxNodeEntity

_LOGGER = logging.getLogger(__name__)
PARALLEL_UPDATES = 1
DEFAULT_SCAN_INTERVAL = timedelta(minutes=2)


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """Set up cover(s) for Velux platform."""
    entities = []
    pyvlx: PyVLX = hass.data[DOMAIN][entry.entry_id]
    for node in pyvlx.nodes:
        if isinstance(node, DualRollerShutter):
            entities.append(VeluxCover(node, subtype=DUAL_COVER))
            _LOGGER.debug("Cover added: %s_%s", node.name, DUAL_COVER)
            entities.append(VeluxCover(node, subtype=UPPER_COVER))
            _LOGGER.debug("Cover added: %s_%s", node.name, UPPER_COVER)
            entities.append(VeluxCover(node, subtype=LOWER_COVER))
            _LOGGER.debug("Cover added: %s_%s", node.name, LOWER_COVER)
        elif isinstance(node, OpeningDevice):
            if isinstance(node, Window):
                _LOGGER.debug("Window will be added: %s", node.name)
                entities.append(VeluxWindow(hass, node))
            else:
                _LOGGER.debug("Cover will be added: %s", node.name)
                entities.append(VeluxCover(node))
    async_add_entities(entities)

    platform: EntityPlatform = async_get_current_platform()
    platform.async_register_entity_service(
        SERVICE_OPEN_COVER,
        {
            vol.Optional(ATTR_VELOCITY): vol.All(
                vol.Coerce(int), vol.Range(min=0, max=100)
            )
        },
        "async_open_cover",
        [CoverEntityFeature.OPEN],
    )

    platform.async_register_entity_service(
        SERVICE_CLOSE_COVER,
        {
            vol.Optional(ATTR_VELOCITY): vol.All(
                vol.Coerce(int), vol.Range(min=0, max=100)
            )
        },
        "async_close_cover",
        [CoverEntityFeature.CLOSE],
    )

    platform.async_register_entity_service(
        SERVICE_SET_COVER_POSITION,
        {
            vol.Required(ATTR_POSITION): vol.All(
                vol.Coerce(int), vol.Range(min=0, max=100)
            ),
            vol.Optional(ATTR_VELOCITY): vol.All(
                vol.Coerce(int), vol.Range(min=0, max=100)
            ),
        },
        "async_set_cover_position",
        [CoverEntityFeature.SET_POSITION],
    )


class VeluxCover(VeluxNodeEntity, CoverEntity):
    """Representation of a Velux cover."""

    def __init__(self, node: OpeningDevice, subtyp: Optional[str] = None) -> None:
        """Initialize VeluxCover."""
        super().__init__(node, subtyp)
        self._attr_device_class = CoverDeviceClass.WINDOW
        if isinstance(node, Awning):
            self._attr_device_class = CoverDeviceClass.AWNING
        if isinstance(node, Blind):
            self._attr_device_class = CoverDeviceClass.BLIND
            self._is_blind = True
        if isinstance(node, GarageDoor):
            self._attr_device_class = CoverDeviceClass.GARAGE
        if isinstance(node, Gate):
            self._attr_device_class = CoverDeviceClass.GATE
        if isinstance(node, RollerShutter):
            self._attr_device_class = CoverDeviceClass.SHUTTER
        if isinstance(node, DualRollerShutter):
            self._attr_device_class = CoverDeviceClass.SHUTTER
        if isinstance(node, Window):
            self._attr_device_class = CoverDeviceClass.WINDOW
        self.is_looping_while_moving: bool = False

    @property
    def supported_features(self) -> CoverEntityFeature:
        """Flag supported features."""
        supported_features = (
            CoverEntityFeature.OPEN
            | CoverEntityFeature.CLOSE
            | CoverEntityFeature.SET_POSITION
            | CoverEntityFeature.STOP
        )
        if self.current_cover_tilt_position is not None:
            supported_features |= (
                CoverEntityFeature.OPEN_TILT
                | CoverEntityFeature.CLOSE_TILT
                | CoverEntityFeature.SET_TILT_POSITION
                | CoverEntityFeature.STOP_TILT
            )
        return supported_features

    @property
    def current_cover_position(self) -> int:
        """Return the current position of the cover."""
        if self.subtype == UPPER_COVER:
            return 100 - self.node.position_upper_curtain.position_percent
        if self.subtype == LOWER_COVER:
            return 100 - self.node.position_lower_curtain.position_percent
        return 100 - self.node.get_position().position_percent

    @property
    def current_cover_tilt_position(self) -> int | None:
        """Return the current position of the cover."""
        if not isinstance(self.node, Blind):
            return None
        return 100 - self.node.orientation.position_percent

    @property
    def is_closed(self) -> bool:
        """Return if the cover is closed."""
        return self.node.position.closed

    @property
    def is_opening(self) -> bool:
        """Return if the cover is closing or not."""
        return self.node.is_opening

    @property
    def is_closing(self) -> bool:
        """Return if the cover is opening or not."""
        return self.node.is_closing

    @callback
    def async_register_callbacks(self) -> None:
        """Register callbacks to update hass after device was changed."""

        async def after_update_callback(device) -> None:
            """Call after device was updated."""
            self.async_write_ha_state()
            if self.node.is_moving():
                if not self.is_looping_while_moving:
                    self.is_looping_while_moving = True
                    while self.node.is_moving():
                        await asyncio.sleep(1)
                        self.async_write_ha_state()
                    self.is_looping_while_moving = False
        self.node.register_device_updated_cb(after_update_callback)

    async def async_close_cover(self, **kwargs: Any) -> None:
        """Close the cover."""
        close_args = {"wait_for_completion": False}
        if (
            "velocity" in kwargs
            and "velocity" in inspect.getfullargspec(self.node.close).args
        ):
            close_args["velocity"] = kwargs["velocity"]
        if self.subtype is not None:
            close_args["curtain"] = self.subtype
        await self.node.close(**close_args)

    async def async_open_cover(self, **kwargs: Any) -> None:
        """Open the cover."""
        open_args = {"wait_for_completion": False}
        if (
            "velocity" in kwargs
            and "velocity" in inspect.getfullargspec(self.node.open).args
        ):
            open_args["velocity"] = kwargs["velocity"]
        if self.subtype is not None:
            open_args["curtain"] = self.subtype
        await self.node.open(**open_args)

    async def async_set_cover_position(self, **kwargs: Any) -> None:
        """Move the cover to a specific position."""
        if ATTR_POSITION in kwargs:
            position_percent: int = 100 - kwargs[ATTR_POSITION]
            position: Position = Position(position_percent=position_percent)
            set_pos_args = {"wait_for_completion": False}
            if (
                "velocity" in kwargs
                and "velocity" in inspect.getfullargspec(self.node.set_position).args
            ):
                set_pos_args["velocity"] = kwargs["velocity"]
            if self.subtype is not None:
                set_pos_args["curtain"] = self.subtype
            await self.node.set_position(position, **set_pos_args)

    async def async_stop_cover(self, **kwargs: Any) -> None:
        """Stop the cover."""
        await self.node.stop(wait_for_completion=False)

    async def async_close_cover_tilt(self, **kwargs: Any) -> None:
        """Close cover tilt."""
        await self.node.close_orientation(wait_for_completion=False)

    async def async_open_cover_tilt(self, **kwargs: Any) -> None:
        """Open cover tilt."""
        await self.node.open_orientation(wait_for_completion=False)

    async def async_stop_cover_tilt(self, **kwargs: Any) -> None:
        """Stop cover tilt."""
        await self.node.stop_orientation(wait_for_completion=False)

    async def async_set_cover_tilt_position(self, **kwargs: Any) -> None:
        """Move cover tilt to a specific position."""
        position_percent: int = 100 - kwargs[ATTR_TILT_POSITION]
        orientation: Position = Position(position_percent=position_percent)
        await self.node.set_orientation(
            orientation=orientation, wait_for_completion=False
        )


class VeluxWindow(VeluxCover):
    """Representation of a Velux window."""

    def __init__(self, hass: HomeAssistant, node: OpeningDevice) -> None:
        """Initialize Velux window."""
        super().__init__(node)
        self._hass: HomeAssistant = hass
        self._extra_attr_limitation_min: int | None = None
        self._extra_attr_limitation_max: int | None = None

        self.coordinator: DataUpdateCoordinator = DataUpdateCoordinator(
            self._hass,
            _LOGGER,
            name=self.unique_id,
            update_method=self.async_update_limitation,
            update_interval=DEFAULT_SCAN_INTERVAL,
        )

    async def async_init(self):
        """Async initialize."""
        return await self.coordinator.async_config_entry_first_refresh()

    async def async_update_limitation(self):
        """Get the updated status of the cover (limitations only)."""
        try:
            limitation: GetLimitation = await self.node.get_limitation()
            self._extra_attr_limitation_min = limitation.min_value
            self._extra_attr_limitation_max = limitation.max_value
        except PyVLXException:
            _LOGGER.error("Error fetch limitation data for cover %s", self.name)

    @property
    def extra_state_attributes(self) -> dict[str, int | None]:
        """Return the state attributes."""
        return {
            "limitation_min": self._extra_attr_limitation_min,
            "limitation_max": self._extra_attr_limitation_max,
        }

    async def async_added_to_hass(self) -> None:
        """When entity is added to hass."""
        await super().async_added_to_hass()
        self.async_on_remove(
            self.coordinator.async_add_listener(self._handle_coordinator_update)
        )

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        self.async_write_ha_state()

    async def async_update(self) -> None:
        """Update the entity.

        Only used by the generic entity update service.
        """
        await self.coordinator.async_request_refresh()
