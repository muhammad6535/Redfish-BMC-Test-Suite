"""Network checks on BMC Ethernet interfaces."""
import pytest

from redfish_client.validators import is_valid_ipv4, is_valid_mac

pytestmark = pytest.mark.network

KNOWN_LINK_STATUS = {"LinkUp", "LinkDown", "NoLink"}


def test_mac_is_valid(client, interface_path):
    mac = client.get(interface_path).get("MACAddress")
    assert mac and is_valid_mac(mac)


def test_ipv4_addresses_are_valid(client, interface_path):
    for entry in client.get(interface_path).get("IPv4Addresses", []):
        assert is_valid_ipv4(entry.get("Address")), entry


def test_link_status_is_known(client, interface_path):
    shown = client.get(interface_path).get("LinkStatus")
    if shown is None:
        pytest.skip("interface does not report LinkStatus (see docs/recon.md)")
    assert shown in KNOWN_LINK_STATUS


def test_speed_positive_when_link_up(client, interface_path):
    data = client.get(interface_path)
    if data.get("LinkStatus") != "LinkUp":
        pytest.skip("link is not up")
    assert data["SpeedMbps"] > 0


def test_vlan_consistent(client, interface_path):
    vlan = client.get(interface_path).get("VLAN")
    if vlan is None:
        pytest.skip("no VLAN configured")
    if vlan.get("VLANEnable"):
        assert isinstance(vlan.get("VLANId"), int) and 0 <= vlan["VLANId"] <= 4094


def test_macs_are_unique(client):
    seen = {}
    for manager in client.members("/redfish/v1/Managers"):
        for path in client.members(f"{manager}/EthernetInterfaces"):
            mac = client.get(path).get("MACAddress")
            assert mac not in seen, f"duplicate MAC {mac}: {path} and {seen[mac]}"
            seen[mac] = path
