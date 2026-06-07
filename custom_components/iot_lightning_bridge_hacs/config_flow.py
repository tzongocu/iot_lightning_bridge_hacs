"""Config flow for IOT Lightning Bridge HACS."""
import logging
import voluptuous as vol
from homeassistant import config_entries
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResult
from .const import DOMAIN, CONF_API_TOKEN, CONF_BROKER_PREFIX, DEFAULT_BROKER_PREFIX

_LOGGER = logging.getLogger(__name__)

class IOTLightningBridgeConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for IOT Lightning Bridge HACS."""
    VERSION = 1

    async def async_step_user(self, user_input: dict[str, Any] | None = None) -> FlowResult:
        """Handle the initial step of configuration."""
        errors = {}

        if user_input is not None:
            # Validare simplă
            if len(user_input[CONF_API_TOKEN]) < 3:
                errors[CONF_API_TOKEN] = "invalid_api_token"
            
            if not errors:
                # Verificăm dacă avem deja o instanță configurată
                await self.async_set_unique_id(user_input[CONF_API_TOKEN])
                self._abort_if_unique_id_configured()

                return self.async_create_entry(
                    title="IOT Lightning Bridge",
                    data=user_input
                )

        # Schema formularului
        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema({
                vol.Required(CONF_API_TOKEN): str,
                vol.Required(CONF_BROKER_PREFIX, default=DEFAULT_BROKER_PREFIX): str,
            }),
            errors=errors
        )

    @staticmethod
    @config_entries.callback
    def async_get_options_flow(config_entry: config_entries.ConfigEntry):
        return IOTLightningBridgeOptionsFlow(config_entry)

class IOTLightningBridgeOptionsFlow(config_entries.OptionsFlow):
    """Handle options flow for adding manual entities."""
    def __init__(self, config_entry: config_entries.ConfigEntry) -> None:
        self.config_entry = config_entry

    async def async_step_init(self, user_input: dict | None = None) -> FlowResult:
        if user_input is not None:
            return await self.async_step_add_entity()

        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema({vol.Required("action", default="add"): vol.In(["add"])})
        )

    async def async_step_add_entity(self, user_input: dict | None = None) -> FlowResult:
        if user_input is not None:
            # Salvăm entitatea în options
            options = dict(self.config_entry.options)
            manual_entities = list(options.get("manual_entities", []))
            manual_entities.append(user_input)
            options["manual_entities"] = manual_entities
            
            # Update entry
            self.hass.config_entries.async_update_entry(self.config_entry, options=options)
            return self.async_create_entry(title="", data={})

        return self.async_show_form(
            step_id="add_entity",
            data_schema=vol.Schema({
                vol.Required("topic"): str,
                vol.Optional("name"): str,
            })
        )
