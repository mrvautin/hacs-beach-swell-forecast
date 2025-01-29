import logging  # noqa: D104

from homeassistant.config_entries import ConfigEntry # type: ignore
from homeassistant.const import Platform # type: ignore
from homeassistant.core import HomeAssistant # type: ignore
from homeassistant.exceptions import ConfigEntryNotReady # type: ignore

from .const import DOMAIN
from .utils import check_location

_LOGGER = logging.getLogger(__name__)

async def async_setup(hass, config):
    """Set up the integration."""
    return True

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up the integration from a config entry."""
    _LOGGER.info("Setting up custom integration from config entry: %s", entry.data['location_name'])

    location_check = await check_location(entry.data['location_latitude'], entry.data['location_longitude'])
    if location_check is False:
        raise ConfigEntryNotReady(f"Invalid location: {entry.data['location_latitude']} / {entry.data['location_longitude']}")

    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = entry

    # Load sensors
    await hass.config_entries.async_forward_entry_setups(entry, [Platform.SENSOR])
    return True

async def async_unload_entry(hass, config_entry):
    """Unload a config entry."""
    return await hass.config_entries.async_forward_entry_unload(config_entry, "sensor")
