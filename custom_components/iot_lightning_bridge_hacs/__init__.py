"""IOT Lightning Bridge HACS integration."""
import logging
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.typing import ConfigType
from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)
PLATFORMS = ["switch"]

class IOTLightningManager:
    """Manager pentru a gestiona entitățile dinamice."""
    def __init__(self, hass, entry):
        self.hass = hass
        self.entry = entry

    async def add_manual_entity(self, topic, name, token):
        """Logica pentru a notifica switch.py să creeze o nouă entitate."""
        # Aici vom declanșa crearea entității în switch.py
        # Folosim un semnal sau actualizăm starea internă
        _LOGGER.info("Adăugare entitate dinamică: %s pe topicul %s", name, topic)
        # Notă: Implementarea propriu-zisă va fi în switch.py folosind discovery

async def async_setup(hass: HomeAssistant, config: ConfigType) -> bool:
    """Set up the IOT Lightning Bridge HACS component."""
    hass.data.setdefault(DOMAIN, {})
    return True

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up entry and initialize the Manager."""
    
    if "mqtt" not in hass.data:
        _LOGGER.error("MQTT integration not loaded.")
        return False

    # Inițializăm Managerul
    manager = IOTLightningManager(hass, entry)
    
    hass.data[DOMAIN][entry.entry_id] = {
        "api_token": entry.data.get("api_token"),
        "broker_prefix": entry.data.get("broker_prefix"),
        "manager": manager,
    }

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    
    # Înregistrare serviciu
    async def async_add_entity_service(call):
        topic = call.data.get("topic")
        name = call.data.get("name")
        token = call.data.get("token")
        
        # Persistență în options
        options = dict(entry.options)
        manual = list(options.get("manual_entities", []))
        manual.append({"topic": topic, "name": name, "token": token})
        options["manual_entities"] = manual
        
        hass.config_entries.async_update_entry(entry, options=options)
        await manager.add_manual_entity(topic, name, token)

    hass.services.async_register(DOMAIN, "add_entity", async_add_entity_service)
    return True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    if unload_ok := await hass.config_entries.async_unload_platforms(entry, PLATFORMS):
        hass.data[DOMAIN].pop(entry.entry_id)
    return unload_ok
