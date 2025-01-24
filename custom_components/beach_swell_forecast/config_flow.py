"""Config flow for Swell Forecast integration."""

import voluptuous as vol  # type: ignore[attr-defined]

from homeassistant import config_entries

from .const import DOMAIN


@config_entries.HANDLERS.register(DOMAIN)
class SwellForecastConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Swell Forecast."""

    VERSION = 1
    CONNECTION_CLASS = config_entries.CONN_CLASS_CLOUD_POLL

    async def async_step_user(self, user_input=None):
        """Handle the initial step of the config flow."""
        if user_input is not None:
            return self.async_create_entry(title="Swell Sensor", data=user_input)

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema({
                vol.Required("location_name", default="Kirra Qld Australia"): str,
                vol.Required("location_id", default="5842041f4e65fad6a7708be9"): str,
            }),
            description_placeholders={
                "location_name": "Swell location name",
                "location_id": "Swell Id of the location. More info <a href='https://github.com/mrvautin/hacs-beach-swell-forecast'>here</a>.",
            }
        )
