"""Support for Velux covers."""
import logging

from homeassistant.const import SERVICE_OPEN_COVER, SERVICE_CLOSE_COVER, SERVICE_SET_COVER_POSITION
from homeassistant.helpers.entity_platform import async_get_current_platform
from pyvlx import OpeningDevice, Position
from pyvlx.opening_device import Awning, Blind, DualRollerShutter, GarageDoor, Gate, RollerShutter, Window

from homeassistant.components.cover import (
    ATTR_POSITION,
    ATTR_TILT_POSITION,
    DEVICE_CLASS_AWNING,
    DEVICE_CLASS_BLIND,
    DEVICE_CLASS_GARAGE,
    DEVICE_CLASS_GATE,
    DEVICE_CLASS_SHUTTER,
    DEVICE_CLASS_WINDOW,
    SUPPORT_CLOSE,
    SUPPORT_CLOSE_TILT,
    SUPPORT_OPEN,
    SUPPORT_OPEN_TILT,
    SUPPORT_SET_POSITION,
    SUPPORT_SET_TILT_POSITION,
    SUPPORT_STOP,
    SUPPORT_STOP_TILT,
    CoverEntity, CoverEntityFeature,
)
from homeassistant.core import callback

from .const import ATTR_VELOCITY, DOMAIN, DUAL_COVER, UPPER_COVER, LOWER_COVER

import voluptuous as vol

_LOGGER = logging.getLogger(__name__)
PARALLEL_UPDATES = 1


async def async_setup_entry(hass, entry, async_add_entities):
    """Set up cover(s) for Velux platform."""
    entities = []
    gateway = hass.data[DOMAIN][entry.entry_id]
    for node in gateway.nodes:
        if isinstance(node, DualRollerShutter):
            entities.append(VeluxCover(node, subtype=DUAL_COVER))
            _LOGGER.debug("Cover added: %s_%s", node.name, DUAL_COVER)
            entities.append(VeluxCover(node, subtype=UPPER_COVER))
            _LOGGER.debug("Cover added: %s_%s", node.name, UPPER_COVER)
            entities.append(VeluxCover(node, subtype=LOWER_COVER))
            _LOGGER.debug("Cover added: %s_%s", node.name, LOWER_COVER)
        elif isinstance(node, OpeningDevice):
            _LOGGER.debug("Cover will be added: %s", node.name)
            entities.append(VeluxCover(node))
    async_add_entities(entities)

    platform = async_get_current_platform()
    platform.async_register_entity_service(
        SERVICE_OPEN_COVER,
        {
            vol.Required(ATTR_POSITION): vol.All(
                vol.Coerce(int), vol.Range(min=0, max=100)
            ),
            vol.Optional(ATTR_VELOCITY): vol.All(
                vol.Coerce(int), vol.Range(min=0, max=100)
            )
        },
        "async_open_cover",
        [CoverEntityFeature.OPEN]
    )

    platform.async_register_entity_service(
        SERVICE_CLOSE_COVER,
        {
            vol.Required(ATTR_POSITION): vol.All(
                vol.Coerce(int), vol.Range(min=0, max=100)
            ),
            vol.Optional(ATTR_VELOCITY): vol.All(
                vol.Coerce(int), vol.Range(min=0, max=100)
            )
        },
        "async_close_cover",
        [CoverEntityFeature.CLOSE]
    )

    platform.async_register_entity_service(
        SERVICE_SET_COVER_POSITION,
        {
            vol.Required(ATTR_POSITION): vol.All(
                vol.Coerce(int), vol.Range(min=0, max=100)
            ),
            vol.Optional(ATTR_VELOCITY): vol.All(
                vol.Coerce(int), vol.Range(min=0, max=100)
            )
        },
        "async_set_cover_position",
        [CoverEntityFeature.SET_POSITION],
    )


class VeluxCover(CoverEntity):
    """Representation of a Velux cover."""

    def __init__(self, node, subtype=None):
        """Initialize the cover."""
        self.node = node
        self.subtype = subtype

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
        if self.subtype is None:
            unique_id = self.node.node_id
        else: 
            unique_id = str(self.node.node_id) + "_" + self.subtype
        return unique_id

    @property
    def name(self):
        """Return the name of the Velux device."""
        if self.subtype is None:
            name = self.node.name
        else: 
            name = self.node.name + "_" + self.subtype
        return name

    @property
    def should_poll(self):
        """No polling needed within Velux."""
        return False

    @property
    def supported_features(self):
        """Flag supported features."""
        supported_features = (
            SUPPORT_OPEN | SUPPORT_CLOSE | SUPPORT_SET_POSITION | SUPPORT_STOP
        )
        if self.current_cover_tilt_position is not None:
            supported_features |= (
                SUPPORT_OPEN_TILT
                | SUPPORT_CLOSE_TILT
                | SUPPORT_SET_TILT_POSITION
                | SUPPORT_STOP_TILT
            )
        return supported_features

    @property
    def current_cover_position(self):
        """Return the current position of the cover."""
        if self.subtype == UPPER_COVER:
            return 100 - self.node.position_upper_curtain.position_percent
        elif self.subtype == LOWER_COVER:
            return 100 - self.node.position_lower_curtain.position_percent
        else:
            return 100 - self.node.position.position_percent

    @property
    def current_cover_tilt_position(self):
        """Return the current position of the cover."""
        if isinstance(self.node, Blind):
            return 100 - self.node.orientation.position_percent

    @property
    def device_class(self):
        """Define this cover as either awning, blind, garage, gate, shutter or window."""
        if isinstance(self.node, Awning):
            return DEVICE_CLASS_AWNING
        if isinstance(self.node, Blind):
            return DEVICE_CLASS_BLIND
        if isinstance(self.node, GarageDoor):
            return DEVICE_CLASS_GARAGE
        if isinstance(self.node, Gate):
            return DEVICE_CLASS_GATE
        if isinstance(self.node, RollerShutter):
            return DEVICE_CLASS_SHUTTER
        if isinstance(self.node, DualRollerShutter):
            return DEVICE_CLASS_SHUTTER
        if isinstance(self.node, Window):
            return DEVICE_CLASS_WINDOW
        return DEVICE_CLASS_WINDOW

    @property
    def device_info(self):
        return {
            "identifiers": {
                (DOMAIN, self.node.node_id)
            },
            "name": self.name,
        }

    @property
    def is_closed(self):
        """Return if the cover is closed."""
        return self.node.position.closed        

    @property
    def is_opening(self):
        """Return if the cover is closing or not."""
        return self.node.is_opening

    @property
    def is_closing(self):
        """Return if the cover is opening or not."""
        return self.node.is_closing

    async def async_close_cover(self, **kwargs):
        """Close the cover."""

        if 'velocity' in kwargs:
            velocity = kwargs['velocity']
        else:
            velocity = None

        if self.subtype is None:
            await self.node.close(wait_for_completion=False, velocity=velocity)
        else: 
            await self.node.close(wait_for_completion=False, velocity=velocity, curtain=self.subtype)

    async def async_open_cover(self, **kwargs):
        """Open the cover."""

        if 'velocity' in kwargs:
            velocity = kwargs['velocity']
        else:
            velocity = None

        if self.subtype is None:
            await self.node.open(wait_for_completion=False, velocity=velocity)
        else:
            await self.node.open(wait_for_completion=False, velocity=velocity, curtain=self.subtype)

    async def async_set_cover_position(self, **kwargs):
        """Move the cover to a specific position."""
        if ATTR_POSITION in kwargs:
            position_percent = 100 - kwargs[ATTR_POSITION]
            position = Position(position_percent=position_percent)

            if 'velocity' in kwargs:
                velocity = kwargs['velocity']
            else:
                velocity = None

            if self.subtype is None:
                await self.node.set_position(position=position, velocity=velocity, wait_for_completion=False)
            else:
                await self.node.set_position(position=position, velocity=velocity, wait_for_completion=False, curtain=self.subtype)

    async def async_stop_cover(self, **kwargs):
        """Stop the cover."""
        if self.subtype is None:
            await self.node.stop(wait_for_completion=False)
        else:
            await self.node.stop(wait_for_completion=False, curtain=self.subtype)

    async def async_close_cover_tilt(self, **kwargs):
        """Close cover tilt."""
        await self.node.close_orientation(wait_for_completion=False)

    async def async_open_cover_tilt(self, **kwargs):
        """Open cover tilt."""
        await self.node.open_orientation(wait_for_completion=False)

    async def async_stop_cover_tilt(self, **kwargs):
        """Stop cover tilt."""
        await self.node.stop_orientation(wait_for_completion=False)

    async def async_set_cover_tilt_position(self, **kwargs):
        """Move the cover to a specific position."""
        if ATTR_TILT_POSITION in kwargs:
            position_percent = 100 - kwargs[ATTR_TILT_POSITION]
            orientation = Position(position_percent=position_percent)
            await self.node.set_orientation(
                orientation=orientation, wait_for_completion=False
            )
