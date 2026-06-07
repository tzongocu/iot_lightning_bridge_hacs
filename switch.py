"""Switch entity for IOT Lightning Bridge HACS."""
import json
import logging
from typing import Any

from homeassistant.components.mqtt import MQTT_DISCOVERY_NEW, MqttServiceInfo
from homeassistant.components.switch import SwitchEntity, SwitchDeviceClass
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import CONF_API_TOKEN, CONF_BROKER_PREFIX, DEFAULT_NAME, DOMAIN

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the switch platform."""
    _LOGGER.debug("Setting up switch platform for IOT Lightning Bridge HACS")

    # Get configuration data
    data = hass.data[DOMAIN][config_entry.entry_id]
    api_token = data.get(CONF_API_TOKEN)
    broker_prefix = data.get(CONF_BROKER_PREFIX)

    # Create and add the switch entity
    switch = IOTLightningBridgeSwitch(
        hass=hass,
        config_entry=config_entry,
        api_token=api_token,
        broker_prefix=broker_prefix,
    )

    async_add_entities([switch])


class IOTLightningBridgeSwitch(SwitchEntity):
    """Representation of the IOT Lightning Bridge switch."""

    _attr_device_class = SwitchDeviceClass.SWITCH
    _attr_has_entity_name = True
    _attr_should_poll = False

    def __init__(
        self,
        hass: HomeAssistant,
        config_entry: ConfigEntry,
        api_token: str,
        broker_prefix: str,
    ) -> None:
        """Initialize the switch."""
        self.hass = hass
        self.config_entry = config_entry
        self._api_token = api_token
        self._broker_prefix = broker_prefix
        self._is_on = False

        # Generate unique ID
        self._attr_unique_id = f"{DOMAIN}_{api_token}_switch"
        self._attr_name = "Lightning Bridge"

        # Entity data
        self._attr_device_info = {
            "identifiers": {(DOMAIN, api_token)},
            "name": DEFAULT_NAME,
            "manufacturer": "IOT Lightning",
            "model": "Bridge v1.0",
        }

    async def async_added_to_hass(self) -> None:
        """When entity is added to Home Assistant."""
        _LOGGER.debug("Switch added to Home Assistant")

        # Publish MQTT Discovery and availability status
        await self.async_publish_discovery()
        await self._publish_availability(online=True)

        # Subscribe to MQTT Discovery updates if available
        self.async_on_remove(
            self.hass.bus.async_listen(MQTT_DISCOVERY_NEW, self._discovery_update)
        )

    @callback
    def _discovery_update(self, msg: MqttServiceInfo) -> None:
        """Handle MQTT Discovery updates."""
        _LOGGER.debug("MQTT Discovery update received: %s", msg)

    async def async_publish_discovery(self) -> None:
        """Publish MQTT Discovery configuration using Home Assistant format."""
        try:
            mqtt = self.hass.components.mqtt
        except AttributeError:
            _LOGGER.warning("MQTT component not available for discovery")
            return

        # Home Assistant MQTT Discovery format:
        # Topic: homeassistant/{component}/{device_id}/{object_id}/config
        device_id = DOMAIN
        object_id = "bridge"
        discovery_topic = f"homeassistant/switch/{device_id}/{object_id}/config"

        # Build the discovery payload according to Home Assistant MQTT spec
        discovery_payload = {
            "name": "IOT Lightning Bridge",
            "unique_id": self._attr_unique_id,
            "device_class": "switch",
            "state_topic": f"{self._broker_prefix}/switch/bridge/state",
            "command_topic": f"{self._broker_prefix}/switch/bridge/set",
            "availability_topic": f"{self._broker_prefix}/availability",
            "payload_on": "ON",
            "payload_off": "OFF",
            "state_on": "ON",
            "state_off": "OFF",
            "device": {
                "identifiers": [self._attr_unique_id],
                "name": DEFAULT_NAME,
                "manufacturer": "IOT Lightning",
                "model": "Bridge v1.0",
                "sw_version": "1.0.0",
            },
            "origin": {
                "name": DOMAIN,
                "sw": "1.0.0",
            },
        }

        # Publish the discovery message using Home Assistant MQTT format
        try:
            await mqtt.async_publish(
                discovery_topic,
                payload=json.dumps(discovery_payload),
                qos=1,
                retain=True,
            )
            _LOGGER.info(
                "Published MQTT Discovery to %s with payload: %s",
                discovery_topic,
                discovery_payload,
            )
        except Exception as err:
            _LOGGER.error("Error publishing MQTT Discovery: %s", err)

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Turn the switch on."""
        _LOGGER.debug("Turning on IOT Lightning Bridge switch")
        self._is_on = True

        # Publish state to MQTT
        await self._publish_state()

        self.async_write_ha_state()

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Turn the switch off."""
        _LOGGER.debug("Turning off IOT Lightning Bridge switch")
        self._is_on = False

        # Publish state to MQTT
        await self._publish_state()

        self.async_write_ha_state()

    async def _publish_state(self) -> None:
        """Publish current state to MQTT."""
        try:
            mqtt = self.hass.components.mqtt
        except AttributeError:
            _LOGGER.warning("MQTT component not available for state publishing")
            return

        state_topic = f"{self._broker_prefix}/switch/bridge/state"
        payload = "ON" if self._is_on else "OFF"

        try:
            await mqtt.async_publish(
                state_topic,
                payload=payload,
                qos=1,
                retain=True,
            )
            _LOGGER.debug("Published state '%s' to topic '%s'", payload, state_topic)
        except Exception as err:
            _LOGGER.error(
                "Error publishing state to MQTT topic %s: %s", state_topic, err
            )

    async def _publish_availability(self, online: bool = True) -> None:
        """Publish availability status to MQTT."""
        try:
            mqtt = self.hass.components.mqtt
        except AttributeError:
            _LOGGER.warning("MQTT component not available for availability publishing")
            return

        availability_topic = f"{self._broker_prefix}/availability"
        payload = "online" if online else "offline"

        try:
            await mqtt.async_publish(
                availability_topic,
                payload=payload,
                qos=1,
                retain=True,
            )
            _LOGGER.debug(
                "Published availability '%s' to topic '%s'",
                payload,
                availability_topic,
            )
        except Exception as err:
            _LOGGER.error(
                "Error publishing availability to MQTT topic %s: %s",
                availability_topic,
                err,
            )

    async def async_will_remove_from_hass(self) -> None:
        """When entity is removed from Home Assistant."""
        _LOGGER.debug("Switch will be removed from Home Assistant")
        # Publish offline status
        await self._publish_availability(online=False)

    @property
    def is_on(self) -> bool:
        """Return True if switch is on."""
        return self._is_on
