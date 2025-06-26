# Home Assistant - Romanian Weather Alerts (ANM)

![Weather Alerts Card Example](https://andreidima.ro/wp-content/uploads/2025/06/Untitled-2-1024x722.png)

## Overview

If you're using Home Assistant and want to stay one step ahead of the weather, integrating weather alerts is a smart move. This integration pulls official weather warning data directly from meteoromania.ro (Romania's National Meteorological Administration) through an easy-to-use intermediate API.

You'll be able to display weather alerts directly in your dashboard or trigger automations when yellow, orange, or red weather codes appear.

## Features

- Official weather alerts from ANM (Administrația Națională de Meteorologie)
- Automatic data updates every 6 hours
- Support for all alert levels (yellow, orange, red codes)
- Weather alert images display
- Romanian language support
- Perfect for triggering automations based on weather conditions

## Prerequisites

- Functional Home Assistant installation
- Access to `configuration.yaml` file
- File Editor add-on or SSH access

## Installation

### Step 1: Access Configuration File

1. Go to Home Assistant
2. Open File Editor (or connect via SSH if you're old school)
3. Locate the `configuration.yaml` file
4. Scroll to find the `sensor:` section or add it at the end of the file if it doesn't exist

### Step 2: Add Weather Alert Sensor

Add the following code to your `configuration.yaml`:

```yaml
sensor:
  - platform: rest
    name: Avertizare Meteo
    resource: https://hass-forum.ro/api/meteoro.php
    value_template: "{{ value_json.status }}"
    json_attributes:
      - mesaj
      - imagine
    scan_interval: 21600  # Updates every 6 hours
```

### Step 3: Restart Home Assistant

1. Go to **Settings** → **System** → **Restart**
2. Or run in terminal: `ha core restart`

### Step 4: Verify the Sensor

After restart:

1. Go to **Developer Tools** → **States**
2. Search for `sensor.avertizare_meteo`

You should see something like this when alerts are active:

```
mesaj: Cod galben 24 – 26 iunie: val de căldură, caniculă și disconfort termic
imagine: *image link*
friendly_name: Avertizare Meteo
```

When no alerts are active, you'll see a message indicating no current warnings.

## Dashboard Card

Add a Markdown card to your dashboard with the following configuration:

```yaml
type: markdown
content: >
  ## 🌤️ Avertizare Meteo
  
  **{{ state_attr('sensor.avertizare_meteo', 'mesaj') }}**
  
  <br><center><img src="{{ state_attr('sensor.avertizare_meteo', 'imagine') }}"
  class="imagine-meteo">
  
style: |
  ha-card {
    text-align: center;
  }
  img.imagine-meteo {
    display: block;
    margin: 16px auto 0 auto;
    max-width: 100%;
    height: auto;
    border: 1px solid #ccc;
    box-shadow: 0 2px 6px rgba(0,0,0,0.2);
  }
```

## Automation Examples

### Basic Alert Notification

```yaml
automation:
  - alias: "Weather Alert Notification"
    trigger:
      - platform: state
        entity_id: sensor.avertizare_meteo
    condition:
      - condition: template
        value_template: "{{ trigger.to_state.state != 'No alerts' }}"
    action:
      - service: notify.mobile_app_your_phone
        data:
          title: "⚠️ Avertizare Meteo"
          message: "{{ state_attr('sensor.avertizare_meteo', 'mesaj') }}"
```

### Weather-Based Device Control

```yaml
automation:
  - alias: "Close Blinds on High Wind Alert"
    trigger:
      - platform: state
        entity_id: sensor.avertizare_meteo
    condition:
      - condition: template
        value_template: "{{ 'vânt' in state_attr('sensor.avertizare_meteo', 'mesaj')|lower }}"
    action:
      - service: cover.close_cover
        target:
          entity_id: cover.living_room_blinds
```

## Alert Color Codes

Romanian weather alerts follow a standard color coding system:

- **🟡 Yellow (Galben)**: Be aware - weather conditions may cause disruption
- **🟠 Orange (Portocaliu)**: Be prepared - dangerous weather is expected
- **🔴 Red (Roșu)**: Take action - dangerous weather is expected with high impact

## API Information

- **Endpoint**: `https://hass-forum.ro/api/meteoro.php`
- **Data Source**: meteoromania.ro (official ANM data)
- **Update Frequency**: Every 6 hours
- **Response Format**: JSON with status, message, and image URL

## Troubleshooting

### Common Issues

1. **Sensor shows "Unknown"**
   - Check internet connectivity
   - Verify API endpoint is accessible
   - Check Home Assistant logs for errors

2. **Image not displaying**
   - Ensure the image URL is valid
   - Check if your Home Assistant can access external images

3. **Configuration errors**
   - Validate YAML syntax
   - Check indentation (use spaces, not tabs)
   - Restart Home Assistant after changes

### Getting Help

If you have suggestions or something isn't working, you can ask for help here: [Weather Alerts ANM Forum](https://hass-forum.ro/showthread.php?tid=9)

## Advanced Usage

### Multiple Location Support

You can create multiple sensors for different Romanian counties by modifying the API endpoint (if supported) or creating separate REST sensors.

### Integration with Weather Stations

Combine this alert system with local weather station data for comprehensive weather monitoring and more sophisticated automations.

## Credits

- Original article and implementation by [AndreiDima.ro](https://andreidima.ro)
- Weather data provided by ANM (Administrația Națională de Meteorologie)
- API intermediary by [HASS Forum](http://hass-forum.ro)