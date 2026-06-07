"""Switch entity for IOT Lightning Bridge HACS."""
import json
import logging
from typing import Any

from homeassistant.components import mqtt
from homeassistant.components.switch import SwitchEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.restore_state import RestoreEntity

from .const import DOMAIN, CONF_BROKER_PREFIX

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the switch platform."""
    broker_prefix = hass.data[DOMAIN][config_entry.entry_id].get(CONF_BROKER_PREFIX)
    
    # Managerul gestionează ciclul de viață al entităților
    manager = IOTLightningBridgeManager(hass, config_entry, broker_prefix, async_add_entities)
    hass.data[DOMAIN][config_entry.entry_id]["manager"] = manager

class IOTLightningBridgeManager:
    """Manager pentru entități dinamice."""
    def __init__(self, hass, config_entry, broker_prefix, async_add_entities):
        self.hass = hass
        self.config_entry = config_entry
        self.broker_prefix = broker_prefix
        self.async_add = async_add_entities
        self.devices = {}

    async def add_manual_entity(self, topic: str, name: str, token: str | None = None):
        """Creează o entitate nouă dacă nu există deja."""
        device_id = topic.split("/")[-1]
        if device_id in self.devices:
            return

        entity = IOTDeviceSwitch(self.hass, self.broker_prefix, device_id, name, token)
        self.devices[device_id] = entity
        self.async_add([entity])

class IOTDeviceSwitch(SwitchEntity, RestoreEntity):
    """Reprezentarea unui switch IOT Lightning."""
    
    def __init__(self, hass, broker_prefix, device_id, name, token):
        self.hass = hass
        self._broker_prefix = broker_prefix
        self._device_id = device_id
        self._attr_name = name or device_id
        self._attr_unique_id = f"{DOMAIN}_{device_id}"
        self._state = False
        self._token = token

    @property
    def is_on(self) -> bool:
        return self._state

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Trimite comanda ON."""
        await self._publish_command("ON")

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Trimite comanda OFF."""
        await self._publish_command("OFF")

    async def _publish_command(self, state: str) -> None:
        """Publică pe topicul de set."""
        topic = f"{self._broker_prefix}/{self._device_id}/set"
        payload = f"{self._device_id}_{state.lower()}"
        await mqtt.async_publish(self.hass, topic, payload, qos=1)
        self._state = (state == "ON")
        self.async_write_ha_state()

    async def async_added_to_hass(self) -> None:
        """Subscriere la starea dispozitivului."""
        state_topic = f"{self._broker_prefix}/{self._device_id}/state"
        
        async def message_received(msg):
            payload = msg.payload.decode()
            if "_on" in payload:
                self._state = True
            elif "_off" in payload:
                self._state = False
            self.async_write_ha_state()

        await mqtt.async_subscribe(self.hass, state_topic, message_received)
        
        # Restaurare stare anterioară
        last_state = await self.async_get_last_state()
        if last_state:
            self._state = (last_state.state == "on")
