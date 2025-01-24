import logging  # noqa: D104

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryNotReady

from .const import DOMAIN
from .utils import check_location_id

_LOGGER = logging.getLogger(__name__)

async def async_setup(hass, config):
    """Set up the integration."""
    return True

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up the integration from a config entry."""
    _LOGGER.info("Setting up custom integration from config entry: %s", entry.data['location_id'])

    location_id_check = await check_location_id(entry.data['location_id'])
    if location_id_check is False:
        raise ConfigEntryNotReady(f"Invalid location id: {entry.data['location_id']}")

    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = entry

    # Load sensors
    await hass.config_entries.async_forward_entry_setup(entry, "sensor")
    return True

async def async_unload_entry(hass, config_entry):
    """Unload a config entry."""
    return await hass.config_entries.async_forward_entry_unload(config_entry, "sensor")
