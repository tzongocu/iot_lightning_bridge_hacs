# IOT Lightning Bridge HACS

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-41BDF5.svg?style=for-the-badge)](https://github.com/hacs/integration)
[![GitHub Release](https://img.shields.io/github/release/tzongocu/iot_lightning_bridge_hacs?style=for-the-badge)](https://github.com/tzongocu/iot_lightning_bridge_hacs/releases)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg?style=for-the-badge)](https://opensource.org/licenses/MIT)

**Bridge oficial pentru integrarea dispozitivelor IOT Lightning în Home Assistant via MQTT.**

## 🎯 Funcționalități

- 🔌 **MQTT Discovery** - Detectare automată în Home Assistant
- 🔐 **Autentificare Token** - Protecție prin API token
- ⚡ **Lightning Network** - Integrare completă cu rețele Lightning
- 📊 **Control Real-time** - Comande instantanee prin MQTT
- 🎨 **Config Flow UI** - Interfață de configurare grafică
- 🏥 **Availability Status** - Raportare automată a statusului online/offline
- 📝 **Logging Complet** - Debug messages detailate

## 📥 Instalare

### Metoda 1: Instalare prin HACS (Recomandat)

1. Deschide **HACS** → **Integrations**
2. Click pe **⋮** (colț dreapta sus) → **Custom repositories**
3. Adaugă URL-ul: `https://github.com/yourusername/iot_lightning_bridge_hacs`
4. Selectează categoria: **Integration**
5. Click **Install**
6. **Restart Home Assistant**
7. Mergi la **Settings** → **Devices & Services** → **Add Integration**
8. Caută "IOT Lightning Bridge HACS"

### Metoda 2: Instalare Manuală (Development)

```bash
# Clone repository-ul
git clone https://github.com/tzongocu/iot_lightning_bridge_hacs.git

# Copiază în Home Assistant
cp -r iot_lightning_bridge_hacs /config/custom_components/

# Restart Home Assistant
# Settings → System → Restart
```

### Metoda 3: Docker/HA OS

Dacă folosești **Docker** sau **Home Assistant OS**:
1. Deschide **File Editor** addon (din Add-on Store)
2. Navigează la `/config/custom_components/`
3. Creează folder: `iot_lightning_bridge_hacs`
4. Upload fișierele din repository

## ⚙️ Configurare

### Prin UI (Recomandat)

După instalare:
1. **Settings** → **Devices & Services**
2. Click **Create Integration** (sau caută "IOT Lightning Bridge")
3. Completează formularul:
   - **API Token**: Token-ul tău de autentificare
   - **MQTT Broker Prefix**: Prefixul pentru topicuri (ex: `iot/lightning`)

### Prin YAML (Opțional)

```yaml
# configuration.yaml
iot_lightning_bridge_hacs:
  api_token: "your_token_here"
  broker_prefix: "iot/lightning"
```

## 📡 MQTT Topics

### Discovery (Home Assistant Detect)

```
homeassistant/switch/iot_lightning_bridge_hacs/bridge/config
```

**Payload:**
```json
{
  "name": "IOT Lightning Bridge",
  "unique_id": "iot_lightning_bridge_hacs_...",
  "state_topic": "iot/lightning/switch/bridge/state",
  "command_topic": "iot/lightning/switch/bridge/set",
  "availability_topic": "iot/lightning/availability",
  "device": {
    "identifiers": ["iot_lightning_bridge_hacs_..."],
    "name": "IOT Lightning Bridge",
    "manufacturer": "IOT Lightning",
    "model": "Bridge v1.0"
  }
}
```

### State (Status Update)

```
Topic: iot/lightning/switch/bridge/state
Payload: ON / OFF
QoS: 1, Retain: True
```

### Command (Control)

```
Topic: iot/lightning/switch/bridge/set
Payload: ON / OFF
QoS: 1
```

### Availability (Online/Offline)

```
Topic: iot/lightning/availability
Payload: online / offline
QoS: 1, Retain: True
```

## 🔍 Depanare

### Integrarea nu apare în UI?

```
1. Verifică loguri: Settings → System → Logs
2. Cauta: "iot_lightning_bridge_hacs"
3. Verifica dacă MQTT integration este încărcată
```

Erori comune:
- ❌ `MQTT integration not loaded` → Configureaza MQTT în HA mai întâi
- ❌ `invalid_api_token` → Token prea scurt (min. 3 caractere)
- ❌ `invalid_broker_prefix` → Prefixul nu poate fi gol

### MQTT nu funcționează?

```bash
# Verifică conexiunea MQTT
mosquitto_sub -h <mqtt_broker> -t "homeassistant/switch/iot_lightning_bridge_hacs/#"

# Poți vedea payload-ul discovery
mosquitto_sub -h <mqtt_broker> -t "iot/lightning/#"
```

### Verifică Log-urile Home Assistant

```
Settings → System → Logs
Filtrează: iot_lightning_bridge_hacs
```

Caut pe liniile cu:
- `✓` `Published MQTT Discovery`
- `✓` `Published availability 'online'`
- `⚠️` `MQTT component not available`
- `❌` `Error publishing`

## 📋 Cerințe

- **Home Assistant:** 2026.1.0+
- **MQTT Integration:** Configurată și funcțională
- **Python:** 3.11+
- **Librării:** Doar componente native Home Assistant (zero dependențe externe)

## 📁 Structura Proiect

```
iot_lightning_bridge_hacs/
├── __init__.py              # Setup și lifecycle
├── config_flow.py           # Formular configurare
├── const.py                 # Constante domeniu
├── switch.py                # Entitate switch cu MQTT
├── manifest.json            # Metadata integrare
├── strings.json             # Traduceri UI
├── README.md                # Documentație
└── LICENSE                  # MIT License
```

## 🚀 Development

### Setup Local Environment

```bash
# Clone repo
git clone https://github.com/yourusername/iot_lightning_bridge_hacs.git
cd iot_lightning_bridge_hacs

# Check Python syntax
python -m py_compile *.py

# Run tests (if added)
pytest tests/
```

### Workflow pentru Contribuții

1. Fork repository-ul
2. Creează branch: `git checkout -b feature/my-feature`
3. Commit: `git commit -am 'Add my feature'`
4. Push: `git push origin feature/my-feature`
5. Deschide Pull Request

## 📝 Jurnal Schimbări

### v1.0.0 (2026-06-07)
- 🎉 Prima versiune publică
- ✅ MQTT Discovery complet
- ✅ Config Flow UI
- ✅ Availability status tracking
- ✅ Full async/await pattern

## 🆘 Support & Issues

- **Bugs:** [GitHub Issues](https://github.com/tzongocu/iot_lightning_bridge_hacs/issues)
- **Discuții:** [GitHub Discussions](https://github.com/tzongocu/iot_lightning_bridge_hacs/discussions)
- **Home Assistant Forum:** Menționează `@tzongocu`

## 📄 Licență

[MIT License](LICENSE) - Liber de folosit în proiecte comerciale și personale

---

**Made with ❤️ for Home Assistant**

Dacă a fost util, dă un ⭐ pe GitHub!
