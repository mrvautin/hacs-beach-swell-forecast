from datetime import datetime
import logging
import re

import aiohttp  # type: ignore  # noqa: PGH003
from .scoring import get_wave_score

_LOGGER = logging.getLogger(__name__)

def clean_string(input_string):
    """Clean the input string by converting it to lowercase, replacing spaces with underscores, and removing non-alphanumeric characters.

    Args:
        input_string (str): The string to be cleaned.

    Returns:
        str: The cleaned string.

    """

    input_string = input_string.lower()
    input_string = input_string.replace(" ", "_")
    return re.sub(r"[^a-z0-9_]", "", input_string)

def optimal_wave(forecast, wave):
    """Clean the input string by converting it to lowercase, replacing spaces with underscores, and removing non-alphanumeric characters.

    Args:
        forecast (obj): Forecast object
        wave (obj): Wave object

    Returns:
        obj: An object of the optimal wave.

    """

    try:
        max_wave = None
        max_swell = None
        max_wave_height = 0
        max_wave_time = 0
        max_swell_height = 0
        max_swell_time = 0
        wave_height_metric = wave["hourly_units"]["wave_height"]
        swell_height_metric = wave["hourly_units"]["swell_wave_height"]
        for hourly in forecast:
            wave_height = hourly["wave_height"]
            swell_height = hourly["swell_height"]
            if wave_height > max_wave_height:
                max_wave_height = wave_height
                max_wave_time = hourly["time"]
                max_wave = str(wave_height) +  wave_height_metric + " @ " + hourly["time"]
            if swell_height > max_swell_height:
                max_swell_height = swell_height
                max_swell_time = hourly["time"]
                max_swell = str(swell_height) +  swell_height_metric + " @ " + hourly["time"]
        return {
            "wave": {
                "max_height": max_wave_height,
                "max_time": max_wave_time,
                "max": max_wave,
                "score": get_wave_score(max_wave_height, wave_height_metric)
            },
            "swell": {
                "max_height": max_swell_height,
                "max_time": max_swell_time,
                "max": max_swell,
                "score": get_wave_score(max_swell_height, swell_height_metric)
            }
        }
    except aiohttp.ClientConnectorError as e:
        _LOGGER.error("Error getting the optimal wave: %s", e)

def split_forecast(forecast):
    """Check if an entity with the given unique ID already exists."""

    dates_forecast = {}
    for index, hourly in enumerate(forecast["hourly"]["time"]):
        date_obj = datetime.fromisoformat(hourly.replace("Z", "+00:00"))
        time_value = str(date_obj.hour) + "am"
        if date_obj.hour == 12:
            time_value = "12pm"
        if date_obj.hour > 12:
            time_value = str(date_obj.hour - 12) + "pm"
        if date_obj.hour == 0:
            time_value = "12am"

        date_key = date_obj.strftime("%Y%m%d")
        if date_key not in dates_forecast:
            dates_forecast[date_key] = []
        day_data = {}
        day_data["time"] = time_value
        day_data["wave_height"] = round(forecast["hourly"]["wave_height"][index], 2)
        day_data["swell_height"] = round(forecast["hourly"]["swell_wave_height"][index], 2)

        dates_forecast[date_key].append(day_data)

    return dates_forecast

def get_date_key(iso_date):
    """Get a date key from an ISO formatted date string.

    Args:
        iso_date (str): The ISO formatted date string.

    Returns:
        str: The date key in the format 'YYYYMMDD'.

    """

    date_obj = datetime.fromisoformat(iso_date.replace("Z", "+00:00"))
    return date_obj.strftime("%Y%m%d")

async def check_location(location_lat, location_long):
    """Check if the given location ID is valid.

    Args:
        location_lat (str): The location latitude to check.
        location_long (str): The location longitude to check.

    Returns:
        bool: True if the location ID is valid, False otherwise.

    """

    params = {
            "latitude": location_lat,
            "longitude": location_long,
            "hourly": ["wave_height", "wave_period", "swell_wave_height"],
            "daily": ["wave_height_max", "swell_wave_height_max"],
            "temporal_resolution": "hourly_3",
            "models": "best_match"
        }
    url = "https://marine-api.open-meteo.com/v1/marine"
    headers = {
        "Content-Type": "application/json",
    }
    try:
        async with aiohttp.ClientSession() as session:
            _LOGGER.info("Checking location: %s / %s", location_lat, location_long)
            async with session.get(url, headers=headers, params=params) as response:
                if response.status == 200:
                   return True
                _LOGGER.info("Got data: %s", response.status)
                return False
    except aiohttp.ClientConnectorError as e:
        _LOGGER.info("Error: %s", e)
        return False
    return True

def get_attributes(self, wave):
    """Get attributes from the wave data.

    Args:
        self: The instance of the class.
        wave (dict): The wave data containing hourly and current wave information.

    Returns:
        dict: A dictionary containing wave height, forecast, and other attributes.

    """

    target_date = get_date_key(self._sensor_date.isoformat())
    response = {}
    response["forecast"] = wave["forecast_data"][target_date]
    response["height_metric"] = wave["current_units"]["wave_height"]
    response["optimal_wave"] = optimal_wave(response["forecast"], wave)
    response["updated"] = self._state
    return response
