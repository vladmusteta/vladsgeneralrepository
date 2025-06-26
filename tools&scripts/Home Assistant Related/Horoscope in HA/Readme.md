# Home Assistant - Horoscope Integration

This integration adds a custom horoscope card to your Home Assistant dashboard, pulling daily predictions from a Romanian horoscope API.

## Features

- Daily horoscope updates for all zodiac signs
- Zodiac sign emoji display
- Romanian language support
- Clean, minimalist card design
- Automatic hourly updates

## Installation

### Step 1: Configure Sensors

Add the following configuration to your `configuration.yaml` file:

```yaml
rest:
  - scan_interval: 3600 # Updates every hour
    resource: https://hass-forum.ro/api/horoscop.php?zodiac=leu
    sensor:
      - name: "Horoscop API Data"
        value_template: "{{ value_json.success }}"
        json_attributes:
          - sign
          - date
          - horoscope
```

**Note:** Replace `zodiac=leu` with your desired zodiac sign:
- `berbec` (Aries)
- `taur` (Taurus)
- `gemeni` (Gemini)
- `rac` (Cancer)
- `leu` (Leo)
- `fecioara` (Virgo)
- `balanta` (Libra)
- `scorpion` (Scorpio)
- `sagetator` (Sagittarius)
- `capricorn` (Capricorn)
- `varsator` (Aquarius)
- `pesti` (Pisces)

### Step 2: Add Template Sensor

Add this template sensor configuration to your `configuration.yaml`:

```yaml
template:
  - sensor:
      - name: "Zodie Emoji"
        state: >
          {% set sign = state_attr('sensor.horoscop_api_data', 'sign') %}
          {{
            {
              'berbec': '♈', 'taur': '♉', 'gemeni': '♊', 'rac': '♋',
              'leu': '♌', 'fecioara': '♍', 'balanta': '♎', 'scorpion': '♏',
              'sagetator': '♐', 'capricorn': '♑', 'varsator': '♒', 'pesti': '♓'
            }[sign] if sign in ['berbec','taur','gemeni','rac','leu','fecioara',
            'balanta','scorpion','sagetator','capricorn',
            'varsator','pesti'] else '♋'
          }}
        attributes:
          sign: "{{ state_attr('sensor.horoscop_api_data', 'sign') }}"
          date: "{{ state_attr('sensor.horoscop_api_data', 'date') }}"
          horoscope: "{{ state_attr('sensor.horoscop_api_data', 'horoscope') }}"
```

### Step 3: Restart Home Assistant

Save the configuration and restart Home Assistant to apply the changes.

## Dashboard Card

Add a new Markdown card to your dashboard with the following configuration:

```yaml
type: markdown
content: >
  ## {{ states('sensor.zodie_emoji') }} Zodia {{
  state_attr('sensor.zodie_emoji', 'sign')|capitalize }} - {{
  state_attr('sensor.zodie_emoji', 'date') }}

  {{ state_attr('sensor.zodie_emoji', 'horoscope') }}
```

## Troubleshooting

If something doesn't work as expected:

1. Check your `configuration.yaml` syntax
2. Verify that the API endpoint is accessible
3. Check Home Assistant logs for any errors
4. Visit the [HASS Forum](http://hass-forum.ro/showthread.php?tid=12) for support

## API Information

This integration uses the Romanian horoscope API provided by HASS Forum:
- **Endpoint:** `https://hass-forum.ro/api/horoscop.php`
- **Update Frequency:** Every hour
- **Language:** Romanian

## Credits

- Original article and implementation by [AndreiDima.ro](https://andreidima.ro)
- API provided by [HASS Forum](http://hass-forum.ro)