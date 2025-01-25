"""Config flow for Beach Swell Forecast integration."""

import voluptuous as vol  # type: ignore[attr-defined]

from homeassistant import config_entries

from .const import DOMAIN


@config_entries.HANDLERS.register(DOMAIN)
class BeachSwellForecastConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Beach Swell Forecast."""

    VERSION = 1
    CONNECTION_CLASS = config_entries.CONN_CLASS_CLOUD_POLL

    async def async_step_user(self, user_input=None):
        """Handle the initial step of the config flow."""
        if user_input is not None:
            return self.async_create_entry(title="Beach Swell Sensor", data=user_input)

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema({
                vol.Required("location_name", default="Kirra Qld Australia"): str,
                vol.Required("location_latitude", default="-35.160006845204165"): str,
                vol.Required("location_longitude", default="138.46987943548"): str,
            }),
            description_placeholders={
                "location_name": "Swell location name",
                "location_latitude": "Swell latitude - Can grab from Google Maps.",
                "location_longitude": "Swell longitude - Can grab from Google Maps.",
            }
        )
