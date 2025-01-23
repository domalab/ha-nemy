# Home Assistant Nemy Integration

[![HACS Integration][hacsbadge]][hacs]
[![GitHub Last Commit](https://img.shields.io/github/last-commit/domalab/ha-nemy?style=for-the-badge)](https://github.com/domalab/ha-nemy/commits/main)
[![License](https://img.shields.io/github/license/domalab/ha-nemy?style=for-the-badge)](./LICENSE)

This custom integration for Home Assistant connects with the Nemy API to provide real-time electricity pricing and renewable energy information for the Australian National Electricity Market (NEM). Monitor electricity prices and renewable energy percentages to optimize your energy usage and reduce costs.

## Overview

Nemy tracks the National Electricity Market (NEM) in Australia and provides simple endpoints designed to help people align their electricity usage with times of abundant renewable energy. This integration brings that functionality directly into your Home Assistant instance.

## Features

- **Real-time Price Monitoring**
  - Household electricity prices (c/kWh)
  - Wholesale dispatch prices ($/MWh)
  - Price categorization (free, cheap, typical, expensive, spike)
  - Price percentile tracking

- **Renewable Energy Tracking**
  - Current renewable energy percentage
  - Renewable energy without rooftop solar
  - Renewable energy percentile
  - Status categorization (extremely green, green, typical, polluting, extremely polluting)

- **Regional Support**
  - NSW1 (New South Wales)
  - QLD1 (Queensland)
  - SA1 (South Australia)
  - TAS1 (Tasmania)
  - VIC1 (Victoria)
  - NEM (National Market)

## Installation

### HACS Installation (Recommended)

[![Open your Home Assistant instance and open a repository inside the Home Assistant Community Store.](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=domalab&repository=ha-nemy&category=integration)

### Manual Installation

1. Download the latest release from the releases page
2. Copy the `custom_components/nemy` directory to your Home Assistant's `custom_components` directory
3. Restart Home Assistant

## Configuration

### Prerequisites

- A RapidAPI account with API key (available at [RapidAPI - Nemy](https://rapidapi.com/nemy-nemy-default/api/nemy))
- nemy on RapidAPI is a freemium service. There is a limited free tier available and a selection of recurring monthly subscription plans.
- Your NEM region code (NSW1, QLD1, SA1, TAS1, VIC1, or NEM)

### Setup Steps

1. In Home Assistant, go to **Configuration** → **Integrations**
2. Click the **+ ADD INTEGRATION** button
3. Search for "Nemy"
4. Enter your:
   - RapidAPI key
   - State/Region code
5. Click "Submit"

## Available Sensors

| Sensor | Description | Unit |
|--------|-------------|------|
| `sensor.nemy_household_price` | Current household electricity price | c/kWh |
| `sensor.nemy_dispatch_price` | Current wholesale dispatch price | $/MWh |
| `sensor.nemy_renewables_percentage` | Current renewable energy percentage | % |
| `sensor.nemy_renewables_category` | Current renewables status | text |
| `sensor.nemy_price_category` | Current price status | text |

### Sensor Details

#### Price Categories

- **Free**: Extremely low or negative prices
- **Cheap**: Below average prices
- **Typical**: Average price range
- **Expensive**: Above average prices
- **Spike**: Significantly high prices

#### Renewable Categories

- **Extremely Green**: Very high renewable percentage
- **Green**: Above average renewable percentage
- **Typical**: Average renewable percentage
- **Polluting**: Below average renewable percentage
- **Extremely Polluting**: Very low renewable percentage

## Usage Examples

### Automations

```yaml
# Turn on pool pump when electricity is cheap
automation:
  - alias: "Pool Pump - Cheap Power"
    trigger:
      - platform: state
        entity_id: sensor.nemy_price_category
        to: 'cheap'
    action:
      - service: switch.turn_on
        target:
          entity_id: switch.pool_pump

# Charge EV during high renewable periods
automation:
  - alias: "EV Charging - Green Power"
    trigger:
      - platform: state
        entity_id: sensor.nemy_renewables_category
        to: 'extremely green'
    condition:
      - condition: numeric_state
        entity_id: sensor.ev_battery_level
        below: 80
    action:
      - service: switch.turn_on
        target:
          entity_id: switch.ev_charger
```

## Error Handling

The integration includes robust error handling for:

- API connection issues
- Data validation
- Rate limiting
- Network timeouts

## Advanced Configuration

### Update Frequency

The integration polls the Nemy API every 5 minutes by default. This can be adjusted in `const.py` if needed.

### Rate Limiting

The integration respects RapidAPI's rate limits and includes automatic handling of rate limit responses.

## Troubleshooting

### Common Issues

1. **Cannot Connect Error**
   - Verify your API key is correct
   - Check your internet connection
   - Ensure RapidAPI service is available

2. **Invalid State Error**
   - Verify you're using a valid state code (NSW1, QLD1, SA1, TAS1, VIC1, or NEM)

3. **No Data Updated**
   - Check the Home Assistant logs for any error messages
   - Verify your API key hasn't expired
   - Check your rate limit usage in RapidAPI dashboard

## License

This project is licensed under the Apache License - see the [LICENSE](LICENSE) file for details.

[hacs]: https://github.com/custom-components/hacs
[hacsbadge]: https://img.shields.io/badge/HACS-Default-orange.svg?style=for-the-badge
