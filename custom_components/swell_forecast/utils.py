from datetime import datetime, timedelta
import logging
import re

import aiohttp  # type: ignore  # noqa: PGH003

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

def get_wave_score(height):
    scores = [
        {
            "score": 1,
            "height_min": 0,
            "height_max": 0.10,
            "desc": "Calm"
        },
        {
            "score": 2,
            "height_min": 0.10,
            "height_max": 0.50,
            "desc": "Smooth"
        },
        {
            "score": 3,
            "height_min": 0.5,
            "height_max": 1.25,
            "desc": "Slight"
        },
        {
            "score": 4,
            "height_min": 1.25,
            "height_max": 2.50,
            "desc": "Moderate"
        },
        {
            "score": 5,
            "height_min": 2.50,
            "height_max": 4.00,
            "desc": "Rough"
        },
        {
            "score": 6,
            "height_min": 4.00,
            "height_max": 6.00,
            "desc": "Very Rough"
        },
        {
            "score": 7,
            "height_min": 6.00,
            "height_max": 9.00,
            "desc": "High"
        },
        {
            "score": 8,
            "height_min": 6.00,
            "height_max": 9.00,
            "desc": "Very high"
        },
        {
            "score": 9,
            "height_min": 14.00,
            "height_max": 200.00,
            "desc": "Phenomenal"
        }
    ]
    for score in scores:
        if height > score["height_min"] and height < score["height_max"]:
            return score


def optimal_wave(forecast):
    """Check if an entity with the given unique ID already exists."""

    max_wave = None
    max_wave_height = 0
    for hourly in forecast:
        wave_height = hourly["wave_height"]
        if wave_height > max_wave_height:
            max_wave_height = wave_height
            max_wave = str(wave_height) + "m @ " + hourly["time_value"]
    return {
        "max_wave_height": max_wave_height,
        "max_wave": max_wave,
        "wave_score": get_wave_score(max_wave_height)
    }

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

        date_key = str(date_obj.year) + str(date_obj.month) + str(date_obj.day)
        if date_key not in dates_forecast:
            dates_forecast[date_key] = []
        day_data = {}
        day_data["time_value"] = time_value
        day_data["wave_height"] = forecast["hourly"]["wave_height"][index]

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
    return str(date_obj.year) + str(date_obj.month) + str(date_obj.day)

async def check_location(location_lat, location_long):
    """Check if the given location ID is valid.

    Args:
        location_lat (str): The location latitude to check.
        location_long (str): The location longitude to check.

    Returns:
        bool: True if the location ID is valid, False otherwise.

    """

    url = f"https://marine-api.open-meteo.com/v1/marine?latitude={location_lat}4&longitude={location_long}&current=wave_height&hourly=wave_height&temporal_resolution=hourly_3&models=best_match"
    headers = {
        "Content-Type": "application/json",
    }
    try:
        async with aiohttp.ClientSession() as session:
            _LOGGER.info("Checking location: %s / %s", location_lat, location_long)
            async with session.get(url, headers=headers) as response:
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

    target_date = self._sensor_date + timedelta(days=1)
    target_date = get_date_key(target_date.isoformat())
    response = {}
    response["forecast"] = wave["forecast_data"][target_date]
    response["height_metric"] = wave["current_units"]["wave_height"]
    response["optimal_wave"] = optimal_wave(response["forecast"])
    response["updated"] = self._state
    return response
