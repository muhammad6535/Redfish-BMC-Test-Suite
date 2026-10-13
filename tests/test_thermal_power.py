"""Thermal and power functional checks."""
import pytest

from redfish_client.validators import in_range

pytestmark = pytest.mark.functional


def test_temperature_within_thresholds(temperature):
    reading = temperature.get("ReadingCelsius")
    if reading is None:
        pytest.skip("sensor has no reading")
    assert in_range(
        reading,
        minimum=temperature.get("LowerThresholdNonCritical"),
        maximum=temperature.get("UpperThresholdNonCritical"),
    )


def test_fan_reading_positive_when_healthy(fan):
    if fan.get("Status", {}).get("Health") != "OK":
        pytest.skip("fan is not healthy")
    assert fan.get("Reading", 0) > 0


def test_voltage_within_critical_range(voltage):
    reading = voltage.get("ReadingVolts")
    if reading is None:
        pytest.skip("voltage sensor has no reading")
    assert in_range(
        reading,
        minimum=voltage.get("LowerThresholdCritical"),
        maximum=voltage.get("UpperThresholdCritical"),
    )
