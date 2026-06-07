"""Config flow for IOT Lightning Bridge HACS."""
import logging
from typing import Any
import voluptuous as vol

from homeassistant import config_entries
from homeassistant.data_entry_flow import FlowResult
from .const import DOMAIN, CONF_API_TOKEN, CONF_BROKER_PREFIX, DEFAULT_BROKER_PREFIX

_LOGGER = logging.getLogger(__name__)

class IOTLightningBridgeConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for IOT Lightning Bridge."""
    VERSION = 1

    async def async_step_user(self, user_input: dict[str, Any] | None = None) -> FlowResult:
        """Handle the initial step."""
        errors = {}

        if user_input is not None:
            # Validare simplă pentru campurile obligatorii
            if len(user_input.get(CONF_API_TOKEN, "")) < 3:
                errors[CONF_API_TOKEN] = "invalid_api_token"
            
            if not errors:
                # Folosim username-ul ca unique_id
                await self.async_set_unique_id(user_input.get("username", "default"))
                self._abort_if_unique_id_configured()

                return self.async_create_entry(
                    title="IOT Lightning Bridge",
                    data=user_input
                )

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema({
                vol.Required("username", default="analog"): str,
                vol.Required(CONF_API_TOKEN): str,
                vol.Required(CONF_BROKER_PREFIX, default=DEFAULT_BROKER_PREFIX): str,
            }),
            errors=errors
        )

    @staticmethod
    def async_get_options_flow(config_entry: config_entries.ConfigEntry):
        return IOTLightningBridgeOptionsFlow(config_entry)

class IOTLightningBridgeOptionsFlow(config_entries.OptionsFlow):
    """Handle options flow for adding manual entities."""
    def __init__(self, config_entry: config_entries.ConfigEntry) -> None:
        self.config_entry = config_entry

    async def async_step_init(self, user_input: dict[str, Any] | None = None) -> FlowResult:
        """Primul pas din Options: Adăugare entitate."""
        if user_input is not None:
            return await self.async_step_add_entity(user_input)

        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema({
                vol.Required("topic"): str,
                vol.Optional("name"): str,
                vol.Optional("token"): str,
            })
        )

    async def async_step_add_entity(self, user_input: dict[str, Any]) -> FlowResult:
        """Salvează entitatea în options."""
        options = dict(self.config_entry.options)
        manual_entities = list(options.get("manual_entities", []))
        manual_entities.append(user_input)
        options["manual_entities"] = manual_entities
        
        self.hass.config_entries.async_update_entry(self.config_entry, options=options)
        return self.async_create_entry(title="Entitate adăugată", data={})
