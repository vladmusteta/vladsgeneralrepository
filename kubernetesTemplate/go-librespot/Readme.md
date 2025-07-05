# Go-Librespot Kubernetes Deployment

A complete Kubernetes deployment for [go-librespot](https://github.com/devgianlu/go-librespot), enabling Spotify Connect functionality in your Kubernetes cluster.

## Overview

This deployment creates a Spotify Connect device called "Kubernetes-GoLibrespot" that appears in your Spotify app's device list, allowing you to stream music directly to your Kubernetes cluster.

## Features

- 🎵 **Spotify Connect Device** - Stream music from any Spotify app
- 🌐 **Web Interface** - Monitor device status and control playback
- 🔗 **HTTP API** - Programmatic control and monitoring
- 💾 **Persistent Storage** - Configuration and credentials persist across restarts
- 🎛️ **High Quality Audio** - 320kbps bitrate with volume normalization
- 🔊 **PulseAudio Integration** - Proper audio routing with PulseAudio support

## Prerequisites

- Kubernetes cluster
- **Spotify Premium account** (required for Spotify Connect)
- Local storage paths prepared on your node
- Network connectivity for mDNS discovery

## Quick Start

### 1. Prepare Storage Directories

```bash
# Create required directories
sudo mkdir -p /home/k8svolumes/go-librespot/mounted_volume/.config/go-librespot
sudo mkdir -p /home/k8svolumes/go-librespot/mounted_volume/.config/pulse/cookie
sudo mkdir -p /home/k8svolumes/go-librespot/mounted_volume/run/user/1000/pulse/native

# Set permissions
sudo chown -R root:root /home/k8svolumes/go-librespot/mounted_volume
sudo chmod -R 755 /home/k8svolumes/go-librespot/mounted_volume

# Create initial config
sudo tee /home/k8svolumes/go-librespot/mounted_volume/.config/go-librespot/config.yml > /dev/null << 'EOF'
device_name: "Kubernetes-GoLibrespot"
device_type: "speaker"
log_level: "info"

audio:
  format: "S16LE"
  bitrate: 320
  volume_steps: 64
  initial_volume: 50
  normalisation: true
  normalisation_pregain: 0.0

discovery:
  port: 57621
  disable_audio: false

server:
  enabled: true
  port: 24879
  address: "0.0.0.0"

credentials:
  type: zeroconf

zeroconf:
  persist_credentials: true
EOF
```

### 2. Deploy to Kubernetes

```bash
# Deploy in order
kubectl apply -f go-librespot-configmap.yaml
kubectl apply -f go-librespot-web-configmap.yaml
kubectl apply -f go-librespot-pv.yaml
kubectl apply -f go-librespot-pvc.yaml
kubectl apply -f go-librespot-deployment.yaml
kubectl apply -f go-librespot-web-deployment.yaml
kubectl apply -f go-librespot-service.yaml
kubectl apply -f go-librespot-web-service.yaml
```

### 3. Verify Deployment

```bash
kubectl get pods -n home-automation -l app=go-librespot
kubectl logs -n home-automation -l app=go-librespot -f
```

## Access Points

### 🎵 Spotify Connect Device
- **Device Name**: `Kubernetes-GoLibrespot`
- **Discovery Method**: mDNS/Bonjour (automatic)
- **Usage**: Appears in Spotify app device list

### 🌐 Web Interface
- **URL**: `http://192.168.100.50:30423`
- **Features**: Device status, embedded Spotify player, troubleshooting info

### 🔗 HTTP API
- **URL**: `http://192.168.100.50:30879`
- **Usage**: Direct API access for monitoring and control

## Network Ports

| Port | Type | Service | Description |
|------|------|---------|-------------|
| `57621` | UDP | Discovery | mDNS/Spotify Connect discovery |
| `24879` | TCP | HTTP API | Go-librespot HTTP API |
| `30423` | TCP | Web UI | NodePort for web interface |
| `30879` | TCP | API External | NodePort for external API access |

## File Structure

```
YAML Files:
├── go-librespot-configmap.yaml      # Configuration for go-librespot
├── go-librespot-deployment.yaml     # Main deployment with host networking
├── go-librespot-service.yaml        # NodePort service for API
├── go-librespot-pv.yaml             # Persistent volumes for storage
├── go-librespot-pvc.yaml            # Persistent volume claims
├── go-librespot-web-configmap.yaml  # Web interface content
├── go-librespot-web-deployment.yaml # Web interface deployment
└── go-librespot-web-service.yaml    # Web interface service

Storage Paths:
├── /home/k8svolumes/go-librespot/mounted_volume/
│   ├── .config/go-librespot/         # Go-librespot configuration
│   ├── .config/pulse/cookie/         # PulseAudio cookie
│   └── run/user/1000/pulse/native/   # PulseAudio native socket
```

## Usage

### Connect via Spotify App

1. **Open any Spotify app** (mobile, desktop, web)
2. **Start playing music**
3. **Tap the Connect/Devices icon** (speaker/cast icon)
4. **Select "Kubernetes-GoLibrespot"** from device list
5. **Music streams** to your Kubernetes deployment

### Monitor via Web Interface

Visit `http://192.168.100.50:30423` to:
- View device status and configuration
- Access embedded Spotify web player
- Check troubleshooting information
- Access quick links to Spotify services

### API Usage Examples

```bash
# Check device status
curl http://192.168.100.50:30879/

# Test API connectivity
curl -I http://192.168.100.50:30879
```

## Configuration

### Device Settings
- **Device Name**: `Kubernetes-GoLibrespot`
- **Audio Quality**: 320kbps
- **Volume Normalization**: Enabled
- **Initial Volume**: 50%

### Audio Backend
- **Format**: S16LE (16-bit signed little-endian)
- **PulseAudio Integration**: Configured with cookie and native socket
- **Backend**: PulseAudio via Unix socket

### Authentication
- **Method**: Zeroconf (Spotify Connect standard)
- **Credentials**: Automatically managed and persisted

## Troubleshooting

### Device Not Appearing in Spotify

1. **Check pod status**:
   ```bash
   kubectl get pods -n home-automation -l app=go-librespot
   kubectl logs -n home-automation -l app=go-librespot
   ```

2. **Verify network discovery**:
   ```bash
   nmap -p 57621 192.168.100.50
   ```

3. **Check API accessibility**:
   ```bash
   curl http://192.168.100.50:30879
   ```

### Connection Issues

- Ensure **Spotify Premium** account
- Verify devices are on **same network**
- Check **mDNS/Bonjour** is working
- Confirm **host networking** is enabled

### Audio Problems

- This deployment uses **pipe backend** (no direct audio output)
- Audio routing depends on **PulseAudio configuration**
- Check **volume levels** and **audio device** settings

### Storage Issues

- Verify **PV/PVC** are bound correctly
- Check **directory permissions** on host
- Ensure **storage paths** exist and are accessible

## Advanced Configuration

### Custom Device Name

Edit `go-librespot-configmap.yaml`:
```yaml
device_name: "Your-Custom-Name"
```

### Audio Quality

Modify bitrate in configuration:
```yaml
audio:
  bitrate: 320  # Options: 96, 160, 320
```

### API Settings

Configure server binding:
```yaml
server:
  enabled: true
  port: 24879
  address: "0.0.0.0"  # Bind to all interfaces
```

## Links and References

- **Go-Librespot Repository**: https://github.com/devgianlu/go-librespot
- **Original Librespot**: https://github.com/librespot-org/librespot
- **Spotify Web Player**: https://open.spotify.com
- **Spotify Connect Info**: https://support.spotify.com/article/spotify-connect/

## Requirements Summary

- ✅ **Kubernetes cluster** with local storage support
- ✅ **Spotify Premium** subscription
- ✅ **Network connectivity** for mDNS discovery
- ✅ **Storage directories** prepared on host node
- ✅ **NodePort access** for web interface and API

## Security Notes

- Deployment uses **host networking** for proper mDNS discovery
- **No privileged containers** required
- **Read-only** PulseAudio cookie mount
- **Persistent credentials** stored securely in PVC

---

**Enjoy streaming Spotify to your Kubernetes cluster!** 🎵

For issues or questions, check the logs and troubleshooting section above.