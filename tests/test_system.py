"""Functional checks on ComputerSystem resources."""
import pytest

pytestmark = pytest.mark.functional

POWER_STATES = {"On", "Off", "PoweringOn", "PoweringOff"}
HEALTH_VALUES = {"OK", "Warning", "Critical"}


def test_power_state_is_known(client, system_path):
    assert client.get(system_path)["PowerState"] in POWER_STATES


def test_status_health_is_known(client, system_path):
    assert client.get(system_path)["Status"]["Health"] in HEALTH_VALUES


@pytest.mark.parametrize("field", ["Model", "SerialNumber"])
def test_identity_fields_present(client, system_path, field):
    assert client.get(system_path).get(field)
