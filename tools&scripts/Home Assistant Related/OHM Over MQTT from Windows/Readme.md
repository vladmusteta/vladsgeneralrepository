# MQTT Hardware Sensors Integration

Automated system for exporting OpenHardwareMonitor data to Home Assistant via MQTT, providing real-time hardware monitoring in your smart home dashboard.

## Overview

This setup continuously monitors your Windows system's hardware (CPU, GPU, temperatures, etc.) using OpenHardwareMonitor and automatically publishes the data to MQTT for Home Assistant integration.

## Components

- `mqtt_sensors.yaml` - Home Assistant sensor configuration
- `export_ohm_to_mqtt.ps1` - PowerShell script for data export
- `OHM to MQTT Export.xml` - Pre-configured Windows Task Scheduler task

## Installation

### 1. Home Assistant Configuration

Place the `mqtt_sensors.yaml` file in your Home Assistant configuration directory:

```
/config/mqtt_sensors.yaml
```

Add the sensors to your Home Assistant configuration and restart the service.

### 2. Windows Task Scheduler Setup

#### Option A: Import Pre-configured Task

Import the included task configuration:

1. Open Windows Task Scheduler
2. Select "Import Task..."
3. Choose `OHM to MQTT Export.xml`
4. Verify the script path matches your installation

#### Option B: Manual Task Creation

Create a new scheduled task with these settings:

**General Tab:**
- Name: `OHM to MQTT Export`
- Run whether user is logged on or not

**Triggers Tab:**
- Trigger: `On a schedule`
- Settings: `Daily`
- Recur every: `1 days`
- Advanced: `Repeat task every 1 minute for a duration of 1 day`
- Enable: ✓

**Actions Tab:**
- Action: `Start a program`
- Program/script: `powershell.exe`
- Arguments: `-ExecutionPolicy Bypass -File "A:\Apps\OpenHardwareMonitor\export_ohm_to_mqtt.ps1"`

**Settings Tab:**
- ✓ Allow task to be run on demand
- ✓ If the task fails, restart every 1 minute (up to 3 times)
- ✓ Stop the task if it runs longer than 5 minutes
- ✓ If the running task does not end when requested, force it to stop

## Prerequisites

- Windows system with PowerShell
- OpenHardwareMonitor installed
- MQTT broker configured and accessible
- Home Assistant with MQTT integration enabled

## Configuration

Update the PowerShell script with your MQTT broker details:
- MQTT broker IP/hostname
- Username and password (if required)
- Topic structure preferences

## Testing

### Manual Script Execution

Test the PowerShell script directly:

```powershell
powershell.exe -ExecutionPolicy Bypass -File "A:\Apps\OpenHardwareMonitor\export_ohm_to_mqtt.ps1"
```

### Task Scheduler Verification

1. Open Task Scheduler
2. Locate your task under "Task Scheduler Library"
3. Right-click and select "Run" to test
4. Check "Last Run Result" for success status

## Monitoring

- **Home Assistant**: Check if sensors appear in your entity list
- **MQTT Explorer**: Monitor topic activity on your broker
- **Task Scheduler**: Review task history and execution logs
- **Event Viewer**: Check Windows logs for PowerShell execution errors

## Troubleshooting

**Task not running:**
- Verify PowerShell execution policy allows script execution
- Check script file path in task configuration
- Ensure user account has necessary permissions

**No data in Home Assistant:**
- Confirm MQTT broker connectivity
- Verify sensor configuration syntax in `mqtt_sensors.yaml`
- Check MQTT topic names match between script and configuration