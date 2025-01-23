"""Diagnostics support for Nemy."""
from __future__ import annotations

from typing import Any
from datetime import datetime

from homeassistant.components.diagnostics import async_redact_data
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import UpdateFailed

from .const import DOMAIN, DEFAULT_SCAN_INTERVAL
from .coordinator import NemyDataUpdateCoordinator

TO_REDACT = {"api_key", "x-rapidapi-key"}

async def async_get_config_entry_diagnostics(
    hass: HomeAssistant, entry: ConfigEntry
) -> dict[str, Any]:
    """Return diagnostics for a config entry."""
    coordinator: NemyDataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id]
    
    # Get current time for timing calculations
    current_time = datetime.now()
    
    try:
        # Basic configuration diagnostics
        diagnostics = {
            "entry": async_redact_data(entry.as_dict(), TO_REDACT),
            "data": coordinator.data,
            "configuration": {
                "state": coordinator.api._state,
                "update_interval": coordinator.update_interval.total_seconds(),
                "default_update_interval": DEFAULT_SCAN_INTERVAL,
                "last_update_success": coordinator.last_update_success,
                "last_update": coordinator.last_update.isoformat() if coordinator.last_update else None,
            },
            "rate_limiting": {
                "requests_per_minute": coordinator.api._requests_per_minute,
                "requests_per_day": coordinator.api._requests_per_day,
                "current_minute_requests": len(coordinator.api._minute_requests),
                "current_daily_requests": len(coordinator.api._daily_requests),
                "minute_requests_remaining": coordinator.api._requests_per_minute - len(coordinator.api._minute_requests),
                "daily_requests_remaining": coordinator.api._requests_per_day - len(coordinator.api._daily_requests),
            },
            "timing": {
                "current_time": current_time.isoformat(),
                "next_update_due": (
                    coordinator.last_update + coordinator.update_interval
                ).isoformat() if coordinator.last_update else None,
            },
            "error_tracking": {
                "last_update_success": coordinator.last_update_success,
                "last_exception": str(coordinator.last_exception) if coordinator.last_exception else None,
                "last_exception_type": type(coordinator.last_exception).__name__ if coordinator.last_exception else None,
            },
        }

        # Add data validation status
        if coordinator.data:
            try:
                coordinator.api._validate_data(coordinator.data)
                diagnostics["validation"] = {
                    "status": "valid",
                    "data_fields_present": sorted(list(coordinator.data.keys())),
                }
            except Exception as validation_err:
                diagnostics["validation"] = {
                    "status": "invalid",
                    "error": str(validation_err),
                    "data_fields_present": sorted(list(coordinator.data.keys())),
                }
        else:
            diagnostics["validation"] = {
                "status": "no_data",
                "message": "No data available for validation",
            }

        # Add sensor health status
        sensor_health = {}
        for entity_id, entity in hass.data.get("entity_registry", {}).items():
            if entity_id.startswith(f"{DOMAIN}."):
                state = hass.states.get(entity_id)
                if state:
                    sensor_health[entity_id] = {
                        "state": state.state,
                        "last_updated": state.last_updated.isoformat(),
                        "attributes": state.attributes,
                    }
        diagnostics["sensor_health"] = sensor_health

        # Add update history if available
        if hasattr(coordinator, "_async_update_data"):
            update_history = []
            if hasattr(coordinator, "_update_history"):
                for update in coordinator._update_history[-10:]:  # Last 10 updates
                    update_history.append({
                        "timestamp": update["timestamp"].isoformat(),
                        "success": update["success"],
                        "duration": update["duration"],
                        "error": str(update["error"]) if update.get("error") else None,
                    })
            diagnostics["update_history"] = update_history

        return diagnostics

    except Exception as err:
        # Return basic diagnostics if full diagnostics collection fails
        return {
            "error": f"Error collecting diagnostics: {str(err)}",
            "entry": async_redact_data(entry.as_dict(), TO_REDACT),
            "basic_data": coordinator.data if coordinator.data else None,
        }