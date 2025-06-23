# Kubernetes MQTT Monitor

A Python service that monitors Kubernetes cluster status and reports metrics over MQTT.

## Overview

This tool provides real-time monitoring of your Kubernetes cluster by publishing status updates and metrics to an MQTT broker. It runs as a system service for continuous monitoring.

## Prerequisites

- Python 3 installed
- Access to a Kubernetes cluster
- MQTT broker configured and accessible

## Installation

### 1. Install Python Package Manager

```bash
sudo dnf install python3-pip -y
```

### 2. Create Virtual Environment

Create an isolated Python environment for the project:

```bash
python3 -m venv ~/k8smon_venv
```

### 3. Activate Environment

```bash
source ~/k8smon_venv/bin/activate
```

### 4. Install Dependencies

```bash
pip install paho-mqtt kubernetes
```

### 5. Deploy Script

Copy the `k8s_mqtt_monitor.py` script to your home directory.

## Testing

Verify the monitor works correctly:

```bash
python3 ~/k8s_mqtt_monitor.py
```

## Service Setup (Optional)

To run the monitor automatically at system boot:

### 1. Create Service File

```bash
sudo vi /etc/systemd/system/k8smonitorovermqtt.service
```

### 2. Configure Service

Add your service configuration to the file (service file should be included in this project).

### 3. Enable and Start Service

```bash
sudo systemctl daemon-reload
sudo systemctl enable k8smonitorovermqtt.service
sudo systemctl start k8smonitorovermqtt.service
```

## Files Included

- `k8s_mqtt_monitor.py` - Main monitoring script
- `k8smonitorovermqtt.service` - Systemd service configuration (if included)

## Usage

Once running, the monitor will continuously publish Kubernetes cluster metrics to your configured MQTT broker. Check your MQTT client or dashboard to view the incoming data.

## Service Management

```bash
# Check service status
sudo systemctl status k8smonitorovermqtt.service

# View logs
sudo journalctl -u k8smonitorovermqtt.service -f

# Restart service
sudo systemctl restart k8smonitorovermqtt.service
```