#!/usr/bin/env python3
"""
Simple FastAPI backend exposing Homematic IP temperature/humidity sensors.

The script uses the official `homematicip` library (by eQ-3) to talk to the
cloud API and publishes a couple of read-only endpoints that your tablet or
any frontend can poll.

Prerequisite: create a config.ini with `hmip_generate_auth_token` and point
HMIP_CONFIG (or place the file next to this script).
"""

from __future__ import annotations

import asyncio
import configparser
import logging
import os
from datetime import datetime, timezone
from numbers import Number
from pathlib import Path
from typing import List, Optional

from fastapi import FastAPI, HTTPException
from homematicip.async_home import AsyncHome
from pydantic import BaseModel

LOGGER = logging.getLogger("hmip.fastapi")


def load_credentials() -> tuple[str, str]:
    """Load access point ID + auth token from the hmip config file."""
    config_path = Path(os.getenv("HMIP_CONFIG", "config.ini")).expanduser()
    parser = configparser.ConfigParser()
    if not parser.read(config_path):
        raise RuntimeError(
            f"Cannot read HomematicIP credentials at '{config_path}'. "
            "Generate one with hmip_generate_auth_token."
        )

    try:
        token = parser["AUTH"]["AuthToken"].strip()
        access_point = parser["AUTH"]["AccessPoint"].strip()
    except KeyError as exc:
        raise RuntimeError(
            "config.ini is missing the [AUTH] section with AuthToken/AccessPoint"
        ) from exc

    if not token or not access_point:
        raise RuntimeError("AuthToken or AccessPoint is empty in config.ini")

    return access_point, token


ACCESS_POINT_ID, AUTH_TOKEN = load_credentials()
hm_home: Optional[AsyncHome] = None
home_lock = asyncio.Lock()

app = FastAPI(
    title="Homematic IP Sensors API",
    description="Expose Homematic IP temperature & humidity sensors via FastAPI",
    version="0.1.0",
)


class DeviceResponse(BaseModel):
    id: str
    label: str
    device_type: str
    firmware_version: Optional[str]
    reachable: bool
    battery_low: Optional[bool]
    last_update: Optional[datetime]
    seconds_since_update: Optional[int]
    model_type: Optional[str]
    archetype: Optional[str]
    connection_type: Optional[str]
    functional_channel_types: List[str]


class SensorResponse(DeviceResponse):
    temperature: Optional[float]
    humidity: Optional[float]
    battery_low: Optional[bool]
    last_update: Optional[datetime]
    seconds_since_update: Optional[int]
    setpoint_temperature: Optional[float]
    regulation_status: Optional[str]


async def ensure_home(refresh: bool = True) -> AsyncHome:
    """Create the AsyncHome connection once and optionally refresh the state."""
    global hm_home
    async with home_lock:
        if hm_home is None:
            hm_home = AsyncHome()
            await hm_home.init_async(ACCESS_POINT_ID, AUTH_TOKEN)
        if refresh:
            await hm_home.get_current_state_async(clear_config=True)
        return hm_home


def _numeric_value(value: object) -> Optional[float]:
    if isinstance(value, Number):
        return float(value)
    return None


def _is_environment_sensor(device) -> bool:
    return any(
        getattr(device, attr, None) is not None
        for attr in ("actualTemperature", "measuredTemperature", "humidity")
    )


def _sensor_payload(device) -> SensorResponse:
    base_payload = _device_payload_data(device)
    temperature = (
        _numeric_value(getattr(device, "actualTemperature", None))
        or _numeric_value(getattr(device, "measuredTemperature", None))
    )
    humidity = _numeric_value(getattr(device, "humidity", None))
    setpoint = _numeric_value(
        getattr(device, "setPointTemperature", None)
        or getattr(device, "setTemperature", None)
    )
    regulation_status = _regulation_status(temperature, setpoint)
    return SensorResponse(
        **base_payload,
        temperature=temperature,
        humidity=humidity,
        setpoint_temperature=setpoint,
        regulation_status=regulation_status,
    )


def _device_payload(device) -> DeviceResponse:
    return DeviceResponse(**_device_payload_data(device))


def _device_payload_data(device) -> dict:
    last_update = _device_last_update(device)
    return {
        "id": device.id,
        "label": device.label or device.id,
        "device_type": getattr(device, "deviceType", "UNKNOWN"),
        "firmware_version": getattr(device, "firmwareVersion", None),
        "reachable": bool(getattr(device, "permanentlyReachable", False)),
        "battery_low": _battery_state(device),
        "last_update": last_update,
        "seconds_since_update": _seconds_since(last_update),
        "model_type": getattr(device, "modelType", None),
        "archetype": _enum_name(getattr(device, "deviceArchetype", None)),
        "connection_type": _enum_name(getattr(device, "connectionType", None)),
        "functional_channel_types": [
            name
            for ch in getattr(device, "functionalChannels", []) or []
            for name in [_enum_name(getattr(ch, "functionalChannelType", None))]
            if name
        ],
    }


def _battery_state(device) -> Optional[bool]:
    """Try to resolve a battery indicator from the device or its channels."""
    for source in (device, *getattr(device, "functionalChannels", [])):
        if source is None:
            continue
        for attr in ("lowBat", "lowBattery", "batteryLow", "badBatteryHealth"):
            value = getattr(source, attr, None)
            if isinstance(value, bool):
                return value
    return None


def _device_last_update(device) -> Optional[datetime]:
    ts = getattr(device, "lastStatusUpdate", None)
    if isinstance(ts, datetime):
        return ts if ts.tzinfo else ts.replace(tzinfo=timezone.utc)
    return None


def _seconds_since(ts: Optional[datetime]) -> Optional[int]:
    if ts is None:
        return None
    delta = datetime.now(timezone.utc) - ts
    return max(int(delta.total_seconds()), 0)


def _enum_name(value) -> Optional[str]:
    if value is None:
        return None
    if hasattr(value, "value"):
        return value.value
    return str(value)


def _regulation_status(
    current_temperature: Optional[float], setpoint_temperature: Optional[float]
) -> Optional[str]:
    if current_temperature is None or setpoint_temperature is None:
        return None
    return "cold" if setpoint_temperature > current_temperature else "hot"


@app.on_event("startup")
async def startup_event():
    await ensure_home(refresh=True)


@app.get("/health")
async def health():
    return {"status": "ok", "accessPoint": ACCESS_POINT_ID}


@app.get("/sensors", response_model=List[SensorResponse])
async def list_sensors():
    home = await ensure_home(refresh=True)
    sensors = [
        _sensor_payload(device)
        for device in home.devices
        if _is_environment_sensor(device)
    ]
    return sensors


@app.get("/sensors/{device_id}", response_model=SensorResponse)
async def sensor_detail(device_id: str):
    home = await ensure_home(refresh=True)
    for device in home.devices:
        if device.id == device_id and _is_environment_sensor(device):
            return _sensor_payload(device)
    raise HTTPException(status_code=404, detail="Sensor not found")


@app.get("/devices", response_model=List[DeviceResponse])
async def list_devices():
    home = await ensure_home(refresh=True)
    return [_device_payload(device) for device in home.devices]
