"""IOT Lightning Bridge HACS integration."""
import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.typing import ConfigType

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

PLATFORMS = ["switch"]


async def async_setup(hass: HomeAssistant, config: ConfigType) -> bool:
    """Set up the IOT Lightning Bridge HACS component."""
    _LOGGER.debug("Setting up IOT Lightning Bridge HACS")
    hass.data[DOMAIN] = {}
    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up IOT Lightning Bridge HACS from a config entry."""
    _LOGGER.debug("Setting up IOT Lightning Bridge HACS entry: %s", entry.entry_id)

    # Verify MQTT is loaded
    if "mqtt" not in hass.data:
        _LOGGER.error(
            "MQTT integration not loaded. Please ensure MQTT integration is configured in Home Assistant."
        )
        return False

    # Store the config data
    hass.data[DOMAIN][entry.entry_id] = {
        "api_token": entry.data.get("api_token"),
        "broker_prefix": entry.data.get("broker_prefix"),
    }

    _LOGGER.info(
        "IOT Lightning Bridge HACS initialized with broker prefix: %s",
        entry.data.get("broker_prefix"),
    )

    # Forward the setup to platforms
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    # Listen for changes
    entry.async_on_unload(entry.add_update_listener(async_update_listener))

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    _LOGGER.debug("Unloading IOT Lightning Bridge HACS entry: %s", entry.entry_id)

    # Unload platforms
    if unload_ok := await hass.config_entries.async_unload_platforms(entry, PLATFORMS):
        hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok


async def async_update_listener(
    hass: HomeAssistant, config_entry: ConfigEntry
) -> None:
    """Handle options update."""
    _LOGGER.debug("Reloading IOT Lightning Bridge HACS entry due to options change")
    await hass.config_entries.async_reload(config_entry.entry_id)
