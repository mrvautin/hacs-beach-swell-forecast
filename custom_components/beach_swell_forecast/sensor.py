from datetime import timedelta, datetime  # noqa: D100
import logging

import aiohttp  # type: ignore[import]

from homeassistant.config_entries import ConfigEntry # type: ignore
from homeassistant.core import HomeAssistant # type: ignore
from homeassistant.helpers.entity import Entity # type: ignore
from homeassistant.util import Throttle # type: ignore

from .utils import clean_string, get_attributes

_LOGGER = logging.getLogger(__name__)
SCAN_INTERVAL = timedelta(hours=1)

SENSORS = [
    {"name": "Temperature Sensor 1", "unit_of_measurement": "°C"},
    {"name": "Temperature Sensor 2", "unit_of_measurement": "°C"},
    {"name": "Humidity Sensor", "unit_of_measurement": "%"},
]

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities):
    """Set up the integration from a config entry."""
    config_data= entry.data
    entities = [
        DayForecastSensor(entry.data, 1),
        DayForecastSensor(entry.data, 2),
        DayForecastSensor(entry.data, 3),
        DayForecastSensor(entry.data, 4),
        DayForecastSensor(entry.data, 5)
    ]
    async_add_entities(entities)
    updater = DataUpdater(entities, config_data)
    hass.loop.create_task(updater.async_update())


class DataUpdater:
    """Class to update data for the sensors."""

    def __init__(self, sensors, config):
        """Initialize the data updater with sensors and configuration."""
        self.sensors = sensors
        self.config = config

    @Throttle(SCAN_INTERVAL)
    async def async_update(self):
        """Fetch new data for the sensors and update their state."""
        _LOGGER.info("Swell sensor updating: %s", self.config['location_id'])

        url = f"https://services.surfline.com/kbyg/spots/forecasts/wave/?spotId={self.config['location_id']}&days=5&intervalHours=24"
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
                            sensor.update_state(data)
                    else:
                        _LOGGER.info("Swell sensor - Got data: %s", response.status)
        except aiohttp.ClientConnectorError as e:
            _LOGGER.info("Error: %s", e)


class DayForecastSensor(Entity):
    """Representation of a day forecast sensor."""

    def __init__(self, config_data, SensorDay):
        """Initialize the sensor with configuration data and the sensor day."""
        self._state = None
        self._attributes = {}
        self._config_data = config_data
        self._sensor_day = SensorDay

    @property
    def name(self):
        """Return the name of the sensor."""
        return self._config_data['location_name'] + " day" + str(self._sensor_day) + " forecast"

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
        return clean_string(self._config_data['location_name']) + "_day" + str(self._sensor_day) + "_forecast"

    def update_state(self, data):
        """Update the state of the sensor with new data."""
        index = self._sensor_day - 1
        wave = data["data"]["wave"][index]
        self._state = datetime.now().isoformat()
        self._attributes = get_attributes(self, wave)
        self.async_write_ha_state()
