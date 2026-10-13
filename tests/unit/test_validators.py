import pytest

from redfish_client.validators import (
    in_allowed_set,
    in_range,
    is_valid_ipv4,
    is_valid_mac,
)


@pytest.mark.parametrize("mac", ["23:11:8A:33:CF:EA", "aa:bb:cc:dd:ee:ff", "AA-BB-CC-DD-EE-FF"])
def test_valid_macs(mac):
    assert is_valid_mac(mac) is True


@pytest.mark.parametrize("mac", ["23:11:8A:33:CF", "23:11:8A:33:CF:EA:11", "not-a-mac", "", None, 12345])
def test_invalid_macs(mac):
    assert is_valid_mac(mac) is False


@pytest.mark.parametrize("ip", ["192.168.0.10", "0.0.0.0", "255.255.255.255"])
def test_valid_ipv4(ip):
    assert is_valid_ipv4(ip) is True


@pytest.mark.parametrize("ip", ["256.1.1.1", "1.2.3", "abc", "", None])
def test_invalid_ipv4(ip):
    assert is_valid_ipv4(ip) is False


def test_in_allowed_set():
    assert in_allowed_set("On", ["On", "Off"]) is True
    assert in_allowed_set("Banana", ["On", "Off"]) is False


def test_in_range():
    assert in_range(41, minimum=0, maximum=60) is True
    assert in_range(61, minimum=0, maximum=60) is False
    assert in_range(None) is False
    assert in_range("41") is False
