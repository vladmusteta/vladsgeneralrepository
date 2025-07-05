# 🎵 Snapcast Server for Kubernetes

Kubernetes deployment for Snapcast Server - multi-room audio streaming solution. Stream audio from your media center to multiple devices with perfect synchronization. Ideal for whole-home audio, audio-reactive lighting, and multi-zone music systems.

![Snapcast](https://img.shields.io/badge/Snapcast-Server-blue)
![Kubernetes](https://img.shields.io/badge/Kubernetes-Ready-green)
![Multi-Room Audio](https://img.shields.io/badge/Multi--Room-Audio-orange)

## ✨ Features

- **Multi-room audio streaming** with perfect sync
- **Low latency** real-time audio
- **Multiple client support** (Windows, Linux, Android, iOS)
- **Web interface** for easy control
- **Kubernetes ready** deployment
- **Music Assistant integration**
- **Audio analysis support** for reactive lighting
- **Named pipe audio sources**

## 🏗️ Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Music Source  │───▶│  Snapcast Server │───▶│  Snapcast Client│
│ (Music Assistant│    │   (Kubernetes)   │    │    (Your PC)   │
│  Spotify, etc.) │    │                  │    │                 │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                              │
                              ▼
                       ┌──────────────────┐
                       │  Audio Analysis  │
                       │ (Home Assistant) │
                       └──────────────────┘
```

## 🚀 Quick Start

### Prerequisites
- Kubernetes cluster
- Music source (Music Assistant, MPD, etc.)
- Audio clients (Windows PC, mobile devices, etc.)

### Installation

1. **Clone this repository**
```bash
git clone https://github.com/yourusername/snapcast-kubernetes
cd snapcast-kubernetes
```

2. **Deploy Snapcast Server**
```bash
kubectl apply -f snapcast-server-deployment.yaml
```

3. **Verify deployment**
```bash
kubectl get pods -n home-automation
kubectl logs -f deployment/snapcast-server -n home-automation
```

4. **Access Web Interface**
- Open browser to: `http://[your-node-ip]:[nodeport]`
- Default ports: 1704 (audio), 1705 (control), 1780 (web)

## 📱 Client Setup

### Windows Client
1. **Download Snapcast Client** from [GitHub releases](https://github.com/badaix/snapcast/releases)
2. **Extract to folder** (e.g., `A:\Apps\Snapclient`)
3. **Connect to server**:
```cmd
snapclient.exe -h [your-server-ip]
```

### Automatic Windows Startup
Create `Start-Snapclient.bat`:
```batch
@echo off
cd /d "A:\Apps\Snapclient"
start "" .\snapclient.exe -h 192.168.100.50
timeout /t 3 /nobreak >nul
start "" "http://192.168.100.50:1780"
```

Place in Windows Startup folder: `Win+R` → `shell:startup`

### Android/iOS
- Install **Snapclient** from app store
- Configure server IP in app settings

## ⚙️ Configuration

### Audio Sources

The deployment supports multiple audio input methods:

**Named Pipe (Music Assistant)**:
```yaml
source = pipe:///tmp/snapfifo/music_assistant?name=MusicAssistant&sampleformat=48000:16:2&codec=pcm
```

**ALSA Input**:
```yaml
source = alsa://hw:0,0?name=AlsaInput&sampleformat=48000:16:2
```

**File Input**:
```yaml
source = file:///tmp/audio.wav?name=FileInput
```

### Server Configuration

Customize in `snapserver.conf`:
```ini
[server]
threads = -1
datadir = /var/lib/snapserver

[http]
enabled = true
port = 1780

[tcp]
enabled = true
port = 1704

[stream]
port = 1705
source = pipe:///tmp/snapfifo/music_assistant?name=MusicAssistant
```

### Network Configuration

**NodePort Service** (default):
- Accessible from any cluster node
- Ports automatically assigned (30000-32767 range)

**LoadBalancer Service** (cloud environments):
```yaml
spec:
  type: LoadBalancer
```

**HostNetwork** (direct host access):
```yaml
spec:
  hostNetwork: true
```

## 🎛️ Web Interface

Access the Snapcast web interface at `http://[server-ip]:1780`

Features:
- **Volume control** per client
- **Mute/unmute** clients
- **Latency adjustment**
- **Stream selection**
- **Client management**

## 🔧 Integration Examples

### Music Assistant Integration
```yaml
# Music Assistant configuration
snapcast:
  enabled: true
  host: snapcast-server.home-automation.svc.cluster.local
  port: 1704
```

### Home Assistant Media Player
```yaml
# configuration.yaml
media_player:
  - platform: snapcast
    host: [snapcast-server-ip]
    port: 1705
```

### Audio Analysis Pipeline
1. **Music Assistant** → **Snapcast Server** (audio streaming)
2. **Audio Analyzer** → reads from same audio pipe
3. **MQTT** → sends frequency data to Home Assistant
4. **Home Assistant** → controls reactive lighting

## 🚀 Advanced Deployment

### High Availability
```yaml
spec:
  replicas: 2
  strategy:
    type: RollingUpdate
```

### Resource Limits
```yaml
resources:
  requests:
    memory: "128Mi"
    cpu: "100m"
  limits:
    memory: "512Mi"
    cpu: "500m"
```

### Persistent Storage
```yaml
volumeMounts:
  - name: snapcast-data
    mountPath: /var/lib/snapserver
volumes:
  - name: snapcast-data
    persistentVolumeClaim:
      claimName: snapcast-pvc
```

## 🔧 Troubleshooting

### Common Issues

**Clients can't connect:**
```bash
# Check server is running
kubectl get pods -n home-automation | grep snapcast

# Check logs
kubectl logs deployment/snapcast-server -n home-automation

# Test port connectivity
telnet [server-ip] 1704
```

**No audio output:**
```bash
# Check audio source
kubectl exec -it deployment/snapcast-server -- ls -la /tmp/snapfifo/

# Verify audio format
kubectl logs deployment/snapcast-server | grep -i audio
```

**Client disconnections:**
- Check network stability
- Adjust buffer settings in client
- Verify firewall settings

### Performance Tuning

**Low Latency Setup:**
```ini
[stream]
buffer = 1000
codec = pcm
```

**Network Optimization:**
```ini
[tcp]
keep_alive = true
```

## 📊 Monitoring

### Health Checks
```yaml
livenessProbe:
  tcpSocket:
    port: 1704
  initialDelaySeconds: 30
  periodSeconds: 10

readinessProbe:
  tcpSocket:
    port: 1704
  initialDelaySeconds: 5
  periodSeconds: 5
```

### Metrics Collection
- Monitor client connections
- Track audio latency
- Monitor resource usage

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Submit a pull request

### Development Setup
```bash
# Local testing
docker build -t snapcast-server .
docker run -p 1704:1704 -p 1705:1705 -p 1780:1780 snapcast-server
```

## 📄 License

MIT License - see LICENSE file for details.

## 🙏 Acknowledgments

- [Snapcast project](https://github.com/badaix/snapcast) by Johannes Pohl
- Kubernetes community
- Home Assistant community

## 📞 Support

- 🐛 **Issues**: GitHub Issues
- 💬 **Discussions**: GitHub Discussions
- 📖 **Documentation**: [Official Snapcast Docs](https://github.com/badaix/snapcast/blob/develop/doc/configuration.md)

## 🔗 Related Projects

- [Music Assistant](https://github.com/music-assistant/hass-music-assistant)
- [Home Assistant](https://github.com/home-assistant/core)
- [Audio Analyzer for HA](https://github.com/yourusername/audio-analyzer-ha)

---

**⭐ If this project helped you build an awesome multi-room audio system, please star the repository!**