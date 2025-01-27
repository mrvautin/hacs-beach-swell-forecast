from datetime import datetime, timedelta
import logging
import voluptuous as vol # type: ignore

import aiohttp  # type: ignore[import]

from homeassistant.config_entries import ConfigEntry  # type: ignore
from homeassistant.core import HomeAssistant  # type: ignore
from homeassistant.helpers.entity import Entity  # type: ignore
from homeassistant.util import Throttle  # type: ignore

from .utils import clean_string, get_attributes, split_forecast

_LOGGER = logging.getLogger(__name__)
SCAN_INTERVAL = timedelta(hours=1)

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities):
    """Set up the integration from a config entry."""
    config_data= entry.data
    entities = [
        CurrentDaySensor(entry.data),
        DayForecastSensor(entry.data, 1),
        DayForecastSensor(entry.data, 2),
        DayForecastSensor(entry.data, 3),
        DayForecastSensor(entry.data, 4),
        DayForecastSensor(entry.data, 5)
    ]
    async_add_entities(entities)
    updater = DataUpdater(entities, config_data, hass)
    hass.loop.create_task(updater.async_update())

class DataUpdater:
    """Class to update data for the sensors."""

    def __init__(self, sensors, config, hass):
        """Initialize the data updater with sensors and configuration."""
        self.sensors = sensors
        self.config = config
        self.hass = hass

    @Throttle(SCAN_INTERVAL)
    async def async_update(self):
        """Fetch new data for the sensors and update their state."""
        _LOGGER.info("Swell sensor updating: %s", self.config["location_name"])

        latitude = self.config["location_latitude"]
        longitude = self.config["location_longitude"]
        if not self.hass.config.time_zone:
            time_zone = "auto"
        else:
            time_zone = self.hass.config.time_zone

        url = f"https://marine-api.open-meteo.com/v1/marine?latitude={latitude}4&longitude={longitude}&current=wave_height,swell_wave_height&hourly=wave_height&temporal_resolution=hourly_3&models=best_match&timezone={time_zone}"
        headers = {
            "Content-Type": "application/json",
        }
        try:
            async with aiohttp.ClientSession() as session:
                _LOGGER.info("Swell sensor updating data: %s", url)
                async with session.get(url, headers=headers) as response:
                    if response.status == 200:
                        data = await response.json()
                        for sensor in self.sensors:
                            data["forecast_data"] = split_forecast(data)
                            sensor.update_state(data)
                    else:
                        _LOGGER.info("Swell sensor - Got data: %s", response.status)
        except aiohttp.ClientConnectorError as e:
            _LOGGER.info("Error: %s", e)

class CurrentDaySensor(Entity):
    """Representation of a current day sensor."""

    def __init__(self, config_data):
        """Initialize the sensor with configuration data and the sensor day."""
        self._state = None
        self._attributes = {}
        self._config_data = config_data

    @property
    def name(self):
        """Return the name of the sensor."""
        return self._config_data["location_name"] + " current"

    @property
    def state(self):
        """Return the state of the sensor."""
        return self._state

    @property
    def extra_state_attributes(self):
        """Return the extra state attributes of the sensor."""
        return self._attributes

    @property
    def unique_id(self):
        """Return the unique ID of the sensor."""
        return clean_string(self._config_data["location_name"]) + "_current"

    def update_state(self, data):
        """Update the state of the sensor with new data."""

        # Define the schema
        current_schema = vol.Schema({
            vol.Required("time"): str,
            vol.Required("swell_wave_height"): vol.Any(int, float),
            vol.Required("wave_height"): vol.Any(int, float),
        }, extra=vol.ALLOW_EXTRA)

        current_units = vol.Schema({
            vol.Required("swell_wave_height"): str,
            vol.Required("wave_height"): str,
        }, extra=vol.ALLOW_EXTRA)

        schema = vol.Schema({
            vol.Required("current"): current_schema,
            vol.Required("current_units"): current_units
        }, extra=vol.ALLOW_EXTRA)

        current_data = {}
        try:
            schema(data)
            current_data["current_time"] = data["current"]["time"]
            current_data["swell_height"] = data["current"]["swell_wave_height"]
            current_data["swell_metric"] = data["current_units"]["swell_wave_height"]
            current_data["wave_height"] = data["current"]["wave_height"]
            current_data["wave_metric"] = data["current_units"]["wave_height"]
            self._state = data["current"]["wave_height"]

            # Set the interval
            if data["current_units"]["interval"] == "seconds":
                current_data["update_interval"] = data["current"]["interval"] / 60
            if data["current_units"]["interval"] == "minutes":
                current_data["update_interval"] = data["current"]["interval"]
            current_data["update_interval_metric"] = "mins"
        except vol.MultipleInvalid as e:
            _LOGGER.info("Current day schema is not valid: %s", e)
            self._state = "Invalid data"

        # Set the attributes
        self._attributes = current_data
        self.async_write_ha_state()

class DayForecastSensor(Entity):
    """Representation of a day forecast sensor."""

    def __init__(self, config_data, sensor_day):
        """Initialize the sensor with configuration data and the sensor day."""
        self._state = None
        self._attributes = {}
        self._config_data = config_data
        self._sensor_day = sensor_day

    @property
    def name(self):
        """Return the name of the sensor."""
        return self._config_data["location_name"] + " day" + str(self._sensor_day) + " forecast"

    @property
    def state(self):
        """Return the state of the sensor."""
        return self._state

    @property
    def extra_state_attributes(self):
        """Return the extra state attributes of the sensor."""
        return self._attributes

    @property
    def unique_id(self):
        """Return the unique ID of the sensor."""
        return clean_string(self._config_data["location_name"]) + "_day" + str(self._sensor_day) + "_forecast"

    def update_state(self, data):
        """Update the state of the sensor with new data."""

        date_obj = datetime.fromisoformat(data["current"]["time"].replace("Z", "+00:00"))
        target_date = date_obj + timedelta(days=self._sensor_day - 1)
        self._sensor_date = target_date
        self._sensor_data = data["forecast_data"]
        self._state = target_date
        self._attributes = get_attributes(self, data)
        self.async_write_ha_state()
