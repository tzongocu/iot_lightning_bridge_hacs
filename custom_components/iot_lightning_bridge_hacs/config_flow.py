"""Config flow for IOT Lightning Bridge HACS."""
import logging
from typing import Any, Dict, Optional

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResult

from .const import CONF_API_TOKEN, CONF_BROKER_PREFIX, DEFAULT_BROKER_PREFIX, DOMAIN

_LOGGER = logging.getLogger(__name__)


async def validate_api_token(hass: HomeAssistant, api_token: str) -> bool:
    """Validate the API token asynchronously."""
    try:
        # Basic validation
        if not api_token or len(api_token) < 3:
            _LOGGER.warning("API token validation failed: token too short")
            return False

        # Token format: should not contain spaces, should be alphanumeric or similar
        if api_token != api_token.strip():
            _LOGGER.warning("API token validation failed: contains leading/trailing whitespace")
            return False

        # You can add actual API validation here:
        # Example:
        # session = async_get_clientsession(hass)
        # try:
        #     async with session.get(
        #         f"https://api.example.com/validate",
        #         headers={"Authorization": f"Bearer {api_token}"},
        #         timeout=10
        #     ) as resp:
        #         if resp.status != 200:
        #             _LOGGER.error("API validation failed with status %d", resp.status)
        #             return False
        # except asyncio.TimeoutError:
        #     _LOGGER.error("API validation timeout - broker may be unreachable")
        #     return False

        _LOGGER.debug("API token validation passed (basic check)")
        return True
    except Exception as err:
        _LOGGER.error("Error validating API token: %s", err)
        return False


class IOTLightningBridgeConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for IOT Lightning Bridge HACS."""

    VERSION = 1

    async def async_step_user(
        self, user_input: Optional[Dict[str, Any]] = None
    ) -> FlowResult:
        """Handle the initial step."""
        errors: Dict[str, str] = {}

        if user_input is not None:
            # Validate API token
            api_token = user_input.get(CONF_API_TOKEN, "").strip()
            if not await validate_api_token(self.hass, api_token):
                errors[CONF_API_TOKEN] = "invalid_api_token"

            # Validate broker prefix
            broker_prefix = user_input.get(CONF_BROKER_PREFIX, "").strip()
            if not broker_prefix:
                errors[CONF_BROKER_PREFIX] = "invalid_broker_prefix"

            if not errors:
                # Check if entry already exists
                await self.async_set_unique_id(f"{DOMAIN}_{api_token}")
                self._abort_if_unique_id_configured()

                options: Dict[str, Any] = {}
                topic = user_input.get("topic", "").strip()
                if topic:
                    manual = []
                    name = user_input.get("name", "").strip() or None
                    token = user_input.get("token", "").strip() or None
                    manual.append({"topic": topic, "name": name, "token": token})
                    options["manual_entities"] = manual

                return self.async_create_entry(
                    title="IOT Lightning Bridge",
                    data={
                        CONF_API_TOKEN: api_token,
                        CONF_BROKER_PREFIX: broker_prefix,
                    },
                    options=options,
                )

        # Create the form schema
        schema = vol.Schema(
            {
                vol.Required(
                    CONF_API_TOKEN,
                    description={"suggested_value": ""},
                ): str,
                vol.Required(
                    CONF_BROKER_PREFIX,
                    description={"suggested_value": DEFAULT_BROKER_PREFIX},
                ): str,
                vol.Optional("topic", default=""): str,
                vol.Optional("name", default=""): str,
                vol.Optional("token", default=""): str,
            }
        )

        return self.async_show_form(
            step_id="user",
            data_schema=schema,
            errors=errors,
            description_placeholders={
                "info": "Enter your IOT Lightning Bridge credentials and optional entity details"
            },
        )

    async def async_step_import(self, import_data: Dict[str, Any]) -> FlowResult:
        """Handle import from configuration.yaml."""
        _LOGGER.debug("Importing IOT Lightning Bridge HACS from YAML config")
        return await self.async_step_user(import_data)

    @staticmethod
    def async_get_options_flow(config_entry: config_entries.ConfigEntry):
        return IOTLightningBridgeOptionsFlow(config_entry)


class IOTLightningBridgeOptionsFlow(config_entries.OptionsFlow):
    """Options flow to add manual entities (topics + friendly names)."""

    def __init__(self, config_entry: config_entries.ConfigEntry) -> None:
        self._config_entry = config_entry

    async def async_step_init(self, user_input: Optional[Dict[str, Any]] = None) -> FlowResult:
        """Show initial options form: choose Add or Remove."""
        if user_input is not None:
            action = user_input.get("action")
            if action == "add":
                return await self.async_step_add_form()
            if action == "remove":
                return await self.async_step_remove()

        schema = vol.Schema({vol.Required("action", default="add"): vol.In(["add", "remove"])})
        return self.async_show_form(step_id="init", data_schema=schema)

    async def async_step_add_form(self, user_input: Optional[Dict[str, Any]] = None) -> FlowResult:
        """Show form to input topic, token and optional name for adding an entity."""
        if user_input is not None:
            return await self.async_step_add(user_input)

        schema = vol.Schema(
            {
                vol.Required("topic"): str,
                vol.Optional("name", default=""): str,
                vol.Optional("token", default=""): str,
            }
        )
        return self.async_show_form(step_id="add_form", data_schema=schema)

    async def async_step_remove(self, user_input: Optional[Dict[str, Any]] = None) -> FlowResult:
        """Show list of manual entities to remove."""
        manual = list(self._config_entry.options.get("manual_entities", [])) if self._config_entry.options else []
        topics = [m.get("topic") for m in manual if m.get("topic")]

        if not topics:
            return self.async_show_form(
                step_id="remove",
                description_placeholders={"info": "No manual entities configured."},
                data_schema=vol.Schema({}),
            )

        if user_input is not None:
            # user_input["topic"] contains the topic to remove
            topic_to_remove = user_input.get("topic")
            options = dict(self._config_entry.options) if self._config_entry.options else {}
            manual_list = list(options.get("manual_entities", []))
            manual_list = [m for m in manual_list if m.get("topic") != topic_to_remove]
            options["manual_entities"] = manual_list
            return self.async_create_entry(title="manual_entities", data=options)

        schema = vol.Schema({vol.Required("topic"): vol.In(topics)})
        return self.async_show_form(step_id="remove", data_schema=schema)

    async def async_step_add(self, user_input: Dict[str, Any]) -> FlowResult:
        """Add the manual entity to the config entry options."""
        options = dict(self._config_entry.options) if self._config_entry.options else {}
        manual = list(options.get("manual_entities", []))
        topic = user_input.get("topic").strip()
        name = user_input.get("name", "").strip() or None
        token = user_input.get("token", "").strip() or None
        manual.append({"topic": topic, "name": name, "token": token})
        options["manual_entities"] = manual

        return self.async_create_entry(title="manual_entities", data=options)
