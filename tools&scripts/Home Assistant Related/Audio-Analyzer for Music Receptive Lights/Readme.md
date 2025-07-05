# 🎵 Audio Analyzer for Home Assistant

Real-time audio frequency analysis for audio-reactive lighting and automation in Home Assistant. This project analyzes bass, mids, treble, energy levels, and beat detection from audio streams and sends the data via MQTT for use in Home Assistant automations.

![Audio Reactive Lighting Demo](https://img.shields.io/badge/Home%20Assistant-Compatible-blue)
![Kubernetes](https://img.shields.io/badge/Kubernetes-Ready-green)
![MQTT](https://img.shields.io/badge/MQTT-Enabled-orange)

## ✨ Features

- **Real-time frequency analysis** (Bass, Mids, Treble)
- **Beat detection** for flash effects
- **Energy level monitoring**
- **MQTT integration** with Home Assistant
- **Kubernetes deployment ready**
- **Multiple lighting modes** (Party, Ambient, Study, Adaptive)
- **Genre detection** (Electronic/EDM, Classical, Rock)
- **Fallback test data** when audio source unavailable

## 🏠 Home Assistant Integration

### MQTT Sensors Created:
- `sensor.audio_analyzer_over_mqtt_audio_bass`
- `sensor.audio_analyzer_over_mqtt_audio_mids` 
- `sensor.audio_analyzer_over_mqtt_audio_treble`
- `sensor.audio_analyzer_over_mqtt_audio_energy`
- `sensor.audio_analyzer_over_mqtt_audio_beat`

### Lighting Modes:
- **🎉 Party Mode**: Fast, bright, colorful effects
- **🕯️ Ambient Mode**: Slow, warm, relaxing colors
- **📚 Study Mode**: Cool white light for concentration
- **🌅 Adaptive Mode**: Circadian rhythm + audio response
- **🎵 Auto Genre**: Automatic music genre detection

## 🚀 Quick Start

### Prerequisites
- Kubernetes cluster
- Home Assistant
- MQTT broker (Mosquitto)
- Audio source (Snapcast, Music Assistant, etc.)

### Installation

1. **Clone this repository**
```bash
git clone https://github.com/yourusername/audio-analyzer-ha
cd audio-analyzer-ha
```

2. **Deploy to Kubernetes**
```bash
# Update the MQTT IP in the deployment file
kubectl apply -f audio-analyzer-deployment.yaml
```

3. **Add MQTT sensors to Home Assistant**

Add to your `audio_sensors.yaml`:
```yaml
- name: "Audio Bass"
  state_topic: "audio/analysis"
  value_template: "{{ value_json.bass | round(2) }}"
  unit_of_measurement: "dB"
  
- name: "Audio Mids"
  state_topic: "audio/analysis" 
  value_template: "{{ value_json.mids | round(2) }}"
  unit_of_measurement: "dB"
  
- name: "Audio Treble"
  state_topic: "audio/analysis"
  value_template: "{{ value_json.treble | round(2) }}"
  unit_of_measurement: "dB"
  
- name: "Audio Beat"
  state_topic: "audio/analysis"
  value_template: "{{ value_json.beat }}"
  
- name: "Audio Energy"
  state_topic: "audio/analysis"
  value_template: "{{ value_json.energy | round(2) }}"
  unit_of_measurement: "dB"
```

4. **Configure input selects**

Add to your `input_selects.yaml`:
```yaml
audio_lighting_mode:
  name: "Audio Lighting Mode"
  options:
    - "Party Mode"
    - "Ambient Mode" 
    - "Study Mode"
    - "Adaptive Light"
    - "Auto Genre"
    - "Off"
  initial: "Auto Genre"
```

5. **Import automations**
- Copy the automation examples to your Home Assistant
- Update light entity names to match your setup

## ⚙️ Configuration

### Environment Variables
- `MQTT_HOST`: MQTT broker hostname/IP
- `MQTT_PORT`: MQTT broker port (default: 1883)

### Audio Source Configuration
The analyzer attempts to read from:
1. `/tmp/snapfifo/music_assistant` (Snapcast integration)
2. System audio devices
3. Fallback to enhanced test data

### Update Frequency
- Default: 5 Hz (200ms intervals)
- Adjustable in deployment configuration
- Optimized for smart bulb response times

## 🎛️ Dashboard Integration

Add this card to your Home Assistant dashboard:

```yaml
type: vertical-stack
cards:
  - type: entities
    title: "🎵 Audio Lighting Control"
    entities:
      - entity: input_select.audio_lighting_mode
      - entity: sensor.music_energy_level
      - entity: light.your_light_entity
  
  - type: glance
    title: "🎛️ Audio Analysis"
    entities:
      - entity: sensor.audio_analyzer_over_mqtt_audio_bass
      - entity: sensor.audio_analyzer_over_mqtt_audio_mids
      - entity: sensor.audio_analyzer_over_mqtt_audio_treble
      - entity: sensor.audio_analyzer_over_mqtt_audio_energy
```

## 🔧 Troubleshooting

### Common Issues

**No audio data:**
- Check if audio source exists: `kubectl exec -it deployment/audio-analyzer -- ls -la /tmp/snapfifo/`
- Verify MQTT connection: Check Home Assistant logs
- Audio analyzer will use test data if no real audio found

**MQTT not connecting:**
- Update MQTT_HOST in deployment
- Verify MQTT broker is running: `kubectl get pods | grep mosquitto`
- Check logs: `kubectl logs deployment/audio-analyzer`

**Lights not responding:**
- Verify light entity names in automations
- Check automation triggers in Home Assistant
- Some lights may have rate limits (enable music mode for Yeelight)

### Performance Tuning

**For high-end setups:**
```python
time.sleep(0.05)  # 20 Hz updates
```

**For rate-limited lights:**
```python
time.sleep(0.5)   # 2 Hz updates
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Submit a pull request

## 📄 License

MIT License - see LICENSE file for details.

## 🙏 Acknowledgments

- Home Assistant community
- Music Assistant project
- Snapcast audio streaming
- MQTT protocol developers

## 📞 Support

- 🐛 **Issues**: GitHub Issues
- 💬 **Discussions**: GitHub Discussions  
- 📖 **Wiki**: Check the Wiki for advanced configurations

---

**⭐ If this project helped you create amazing audio-reactive lighting, please star the repository!**