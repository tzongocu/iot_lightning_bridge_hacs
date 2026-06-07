"""Switch entity for IOT Lightning Bridge HACS."""
import asyncio
import json
import logging
from datetime import datetime, timezone
from typing import Any


from homeassistant.components.switch import SwitchEntity, SwitchDeviceClass
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import CONF_API_TOKEN, CONF_BROKER_PREFIX, DOMAIN

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the switch platform and MQTT listener that creates device switches dynamically."""
    _LOGGER.debug("Setting up switch platform for IOT Lightning Bridge HACS")

    # Get configuration data
    data = hass.data[DOMAIN][config_entry.entry_id]
    api_token = data.get(CONF_API_TOKEN)
    broker_prefix = data.get(CONF_BROKER_PREFIX)

    # Manager entity listens for device topics and creates device switches
    manager = IOTLightningBridgeManager(
        hass=hass,
        config_entry=config_entry,
        api_token=api_token,
        broker_prefix=broker_prefix,
        async_add_entities=async_add_entities,
    )

    # Keep manager in hass data so it isn't garbage collected
    hass.data[DOMAIN][config_entry.entry_id]["manager"] = manager


class IOTLightningBridgeManager:
    """Manager that listens to MQTT topics and creates per-device switches."""

    def __init__(
        self,
        hass: HomeAssistant,
        config_entry: ConfigEntry,
        api_token: str,
        broker_prefix: str,
        async_add_entities: AddEntitiesCallback,
    ) -> None:
        self.hass = hass
        self.config_entry = config_entry
        self._api_token = api_token
        self._broker_prefix = broker_prefix
        self._async_add = async_add_entities
        self._devices = {}  # device_id -> entity
        self._subscriptions = []
        # Process any manual entities stored in config entry options
        manual = list(config_entry.options.get("manual_entities", [])) if hasattr(config_entry, "options") else []
        for item in manual:
            try:
                topic = item.get("topic")
                name = item.get("name")
                # derive device id from topic last segment
                parts = topic.split("/") if isinstance(topic, str) else []
                device_id = parts[-1] if parts else None
                if device_id and device_id not in self._devices:
                    ent = IOTDeviceSwitch(
                        hass=self.hass,
                        config_entry=self.config_entry,
                        api_token=self._api_token,
                        broker_prefix=self._broker_prefix,
                        device_id=device_id,
                    )
                    if name:
                        ent._attr_name = name
                    self._devices[device_id] = ent
                    self._async_add([ent])
            except Exception:
                _LOGGER.exception("Failed to create manual entity from options: %s", item)

        # Subscribe to all topics under the broker prefix
        topic = f"{self._broker_prefix}/#"
        mqtt = hass.components.mqtt
        # Use async_subscribe to receive messages
        async def _msg_received(msg):
            try:
                topic = msg.topic
                payload = msg.payload.decode("utf-8") if isinstance(msg.payload, (bytes, bytearray)) else str(msg.payload)
            except Exception:
                _LOGGER.exception("Failed to decode MQTT message")
                return

            # Determine device id: prefer topic's last part
            parts = topic.split("/") if isinstance(topic, str) else []
            device_id = parts[-1] if parts else None
            if not device_id:
                return

            # If payload is like '<deviceid>_on' or '<deviceid>_off', handle accordingly
            if payload.endswith("_on") or payload.endswith("_off"):
                # payload form: '{id}_on'
                base = payload.rsplit("_", 1)[0]
                if base != device_id:
                    # If payload embed id, prefer payload base
                    device_id = base

            # Create device entity if needed
            if device_id not in self._devices:
                ent = IOTDeviceSwitch(
                    hass=self.hass,
                    config_entry=self.config_entry,
                    api_token=self._api_token,
                    broker_prefix=self._broker_prefix,
                    device_id=device_id,
                )
                self._devices[device_id] = ent
                # Add entity to HA
                self._async_add([ent])

            # Update device state based on payload
            device_ent = self._devices.get(device_id)
            if device_ent:
                if payload.lower().endswith("_on") or payload.upper() == "ON":
                    device_ent.set_state(True, payload=payload)
                elif payload.lower().endswith("_off") or payload.upper() == "OFF":
                    device_ent.set_state(False, payload=payload)

        # register subscription
        try:
            coro = mqtt.async_subscribe(topic, _msg_received, qos=1)
            # Schedule subscription
            hass.async_create_task(coro)
            _LOGGER.info("Subscribed to MQTT topic %s for dynamic device discovery", topic)
        except Exception:
            _LOGGER.exception("Failed to subscribe to MQTT topic for dynamic devices")

        # Perform active discovery: publish a short 'whoareyou' request so devices can respond
        # Devices should reply on their own topic (e.g. {prefix}/{device_id}) with a state payload
        # The subscription above will receive those responses and create entities.
        hass.async_create_task(self._perform_discovery())

    async def _perform_discovery(self) -> None:
        """Publish a discovery request to encourage devices to announce themselves.

        Devices MAY respond by publishing their id/state to topics under the prefix.
        The manager is already subscribed to `{prefix}/#` so responses will be handled
        by the subscription callback which creates entities.
        """
        # small delay to ensure subscription is registered
        await asyncio.sleep(0.5)
        try:
            mqtt = self.hass.components.mqtt
        except Exception:
            _LOGGER.warning("MQTT component not available; skipping active discovery")
            return

        discovery_topic = f"{self._broker_prefix}/get"
        payload = json.dumps({"cmd": "whoareyou"})

        try:
            await mqtt.async_publish(discovery_topic, payload=payload, qos=1, retain=False)
            _LOGGER.info("Published discovery request to %s", discovery_topic)
        except Exception as err:
            _LOGGER.error("Failed to publish discovery request: %s", err)

    async def add_manual_entity(self, topic: str, name: str | None = None) -> None:
        """Create and add a manual entity at runtime.

        `topic` is the full topic (e.g. prefix/device). The device id is taken as last segment.
        """
        try:
            parts = topic.split("/") if isinstance(topic, str) else []
            device_id = parts[-1] if parts else None
            if not device_id:
                _LOGGER.error("Invalid topic for manual entity: %s", topic)
                return

            if device_id in self._devices:
                _LOGGER.debug("Manual entity %s already exists", device_id)
                return

            ent = IOTDeviceSwitch(
                hass=self.hass,
                config_entry=self.config_entry,
                api_token=self._api_token,
                broker_prefix=self._broker_prefix,
                device_id=device_id,
            )
            if name:
                ent._attr_name = name

            self._devices[device_id] = ent
            self._async_add([ent])
            _LOGGER.info("Added manual entity %s for topic %s", device_id, topic)
        except Exception:
            _LOGGER.exception("Failed to add manual entity for topic %s", topic)

    


class IOTDeviceSwitch(SwitchEntity):
    """Per-device switch created dynamically when MQTT messages arrive."""

    _attr_device_class = SwitchDeviceClass.SWITCH
    _attr_has_entity_name = True
    _attr_should_poll = False

    def __init__(
        self,
        hass: HomeAssistant,
        config_entry: ConfigEntry,
        api_token: str,
        broker_prefix: str,
        device_id: str,
    ) -> None:
        self.hass = hass
        self.config_entry = config_entry
        self._api_token = api_token
        self._broker_prefix = broker_prefix
        self._device_id = device_id
        self._is_on = False

        # Unique ID per device
        self._attr_unique_id = f"{DOMAIN}_{device_id}"
        # Default name is device id; user can rename via HA
        self._attr_name = device_id

        self._attr_device_info = {
            "identifiers": {(DOMAIN, device_id)},
            "name": device_id,
            "manufacturer": "IOT Lightning",
            "model": "Device",
        }
        # Track last trigger info for UI and automations
        self._last_triggered: str | None = None
        self._last_payload: str | None = None
        self._trigger_count: int = 0

    

    def set_state(self, on: bool, payload: str | None = None) -> None:
        """Set the internal state and write it to HA registry."""
        self._is_on = bool(on)
        # record trigger info
        if payload is not None:
            self._last_payload = payload
        self._last_triggered = datetime.now(timezone.utc).isoformat()
        self._trigger_count += 1
        # Publish state to MQTT state topic for this device
        self.hass.async_create_task(self._publish_state())
        self.async_write_ha_state()

    async def async_turn_on(self, **kwargs: Any) -> None:
        self._is_on = True
        await self._publish_state()
        self.async_write_ha_state()

    async def async_turn_off(self, **kwargs: Any) -> None:
        self._is_on = False
        await self._publish_state()
        self.async_write_ha_state()

    async def _publish_state(self) -> None:
        try:
            mqtt = self.hass.components.mqtt
        except AttributeError:
            _LOGGER.warning("MQTT component not available for state publishing")
            return

        state_topic = f"{self._broker_prefix}/{self._device_id}/state"
        payload = f"{self._device_id}_on" if self._is_on else f"{self._device_id}_off"

        try:
            await mqtt.async_publish(state_topic, payload=payload, qos=1, retain=True)
            _LOGGER.debug("Published state '%s' to topic '%s'", payload, state_topic)
        except Exception as err:
            _LOGGER.error("Error publishing state to MQTT topic %s: %s", state_topic, err)

    @property
    def is_on(self) -> bool:
        return self._is_on

    @property
    def extra_state_attributes(self) -> dict:
        """Return extra state attributes for the entity."""
        attrs = {}
        if self._last_triggered:
            attrs["last_triggered"] = self._last_triggered
        if self._last_payload:
            attrs["last_payload"] = self._last_payload
        attrs["trigger_count"] = self._trigger_count
        return attrs

    async def async_added_to_hass(self) -> None:
        """When entity is added to Home Assistant: publish discovery and availability for this device."""
        _LOGGER.debug("Device switch %s added to Home Assistant", self._device_id)
        await self.async_publish_discovery()
        await self._publish_availability(online=True)

    async def async_publish_discovery(self) -> None:
        """Publish MQTT Discovery configuration for this device."""
        try:
            mqtt = self.hass.components.mqtt
        except AttributeError:
            _LOGGER.warning("MQTT component not available for discovery")
            return

        device_id = self._device_id
        object_id = device_id
        discovery_topic = f"homeassistant/switch/{DOMAIN}/{object_id}/config"

        discovery_payload = {
            "name": device_id,
            "unique_id": self._attr_unique_id,
            "device_class": "switch",
            "state_topic": f"{self._broker_prefix}/{device_id}/state",
            "command_topic": f"{self._broker_prefix}/{device_id}/set",
            "availability_topic": f"{self._broker_prefix}/availability",
            "payload_on": f"{device_id}_on",
            "payload_off": f"{device_id}_off",
            "state_on": f"{device_id}_on",
            "state_off": f"{device_id}_off",
            "device": {
                "identifiers": [self._attr_unique_id],
                "name": device_id,
                "manufacturer": "IOT Lightning",
                "model": "Device",
            },
        }

        try:
            await mqtt.async_publish(discovery_topic, payload=json.dumps(discovery_payload), qos=1, retain=True)
            _LOGGER.info("Published MQTT Discovery to %s", discovery_topic)
        except Exception as err:
            _LOGGER.error("Error publishing MQTT Discovery for device %s: %s", device_id, err)

    async def _publish_availability(self, online: bool = True) -> None:
        try:
            mqtt = self.hass.components.mqtt
        except AttributeError:
            _LOGGER.warning("MQTT component not available for availability publishing")
            return

        availability_topic = f"{self._broker_prefix}/availability"
        payload = "online" if online else "offline"

        try:
            await mqtt.async_publish(availability_topic, payload=payload, qos=1, retain=True)
        except Exception as err:
            _LOGGER.error("Error publishing availability to MQTT topic %s: %s", availability_topic, err)
