from datetime import UTC, datetime, timedelta
import logging
import re

import aiohttp  # type: ignore  # noqa: PGH003

_LOGGER = logging.getLogger(__name__)

def epoch_to_iso(day):
    dt = datetime.fromtimestamp(day['timestamp'], tz=UTC)
    dt = dt + timedelta(hours=day['utcOffset'])
    iso_format = dt.isoformat()
    return iso_format

def get_readable_date(day):
    dt = datetime.fromtimestamp(day['timestamp'], tz=UTC)
    dt = dt + timedelta(hours=day['utcOffset'])
    readable_date = dt.strftime("%A, %B %d, %Y")
    return readable_date

def clean_string(input_string):
    input_string = input_string.lower()
    input_string = input_string.replace(" ", "_")
    input_string = re.sub(r'[^a-z0-9_]', '', input_string)
    return input_string

def is_duplicate_entity(hass, unique_id):
    """Check if an entity with the given unique ID already exists."""
    return any(
        entity.entity_id for entity in hass.states.async_all()
        if entity.attributes.get("unique_id") == unique_id
    )

async def check_location_id(location_id):
    url = f"https://services.surfline.com/kbyg/spots/forecasts/wave/?spotId={location_id}&days=5&intervalHours=24"
    headers = {
        "Content-Type": "application/json",
    }
    try:
        async with aiohttp.ClientSession() as session:
            _LOGGER.info(f"Checking location id: {location_id}")
            async with session.get(url, headers=headers) as response:
                if response.status == 200:
                   return True
                _LOGGER.info(f"Got data: {response.status}")
                return False
    except aiohttp.ClientConnectorError as e:
        _LOGGER.info(f"Error: {e!s}")
        return False
    return True

def get_attributes(self, wave):
    return {
            "locationId": self._config_data['location_id'],
            "locationName": self._config_data['location_name'],
            "probability": wave["probability"],
            "surfMinFt": wave["surf"]["min"],
            "surfMaxFt": wave["surf"]["max"],
            "surfMinM": wave["surf"]["min"] * 0.3048,
            "surfMaxM": wave["surf"]["max"] * 0.3048,
            "surfPower": wave["power"],
            "optimalScore": wave["surf"]["optimalScore"],
            "humanRelation": wave["surf"]["humanRelation"],
            "forecastDate": epoch_to_iso(wave),
            "readableDate": get_readable_date(wave)
        }
