# Home Assistant Nemy Integration

This is a custom integration for Home Assistant that integrates with the Nemy API to provide real-time electricity pricing and renewable energy information for the Australian National Electricity Market (NEM).

## Features

- Real-time household electricity prices
- Wholesale dispatch prices
- Renewable energy percentage
- Price and renewables categories
- Support for all NEM regions (NSW1, QLD1, SA1, TAS1, VIC1, and NEM)

## Installation

1. Copy this integration to your `custom_components` directory
2. Restart Home Assistant
3. Go to Configuration > Integrations
4. Click the + button and search for "Nemy"
5. Enter your API key and select your state
6. Click Submit

## Configuration

The integration requires:
- Nemy API Key (from RapidAPI)
- State selection (NSW1, QLD1, SA1, TAS1, VIC1, or NEM)

## Available Sensors

- Household Price (c/kWh)
- Dispatch Price ($/MWh)
- Renewables Percentage (%)
- Renewables Category (extremely green, green, typical, polluting, extremely polluting)
- Price Category (free, cheap, typical, expensive, spike)