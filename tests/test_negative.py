"""Negative and edge-case tests: bad input and clear failures."""
import pytest

from redfish_client.client import RedfishClient, RedfishClientError

pytestmark = pytest.mark.negative

POWER_STATES = {"On", "Off", "PoweringOn", "PoweringOff"}


def test_missing_resource_raises_404(client):
    with pytest.raises(RedfishClientError) as exc:
        client.get("/redfish/v1/Systems/DOES-NOT-EXIST")
    assert "404" in str(exc.value)


@pytest.mark.xfail(
    reason="mock accepts invalid values (returns 204); a real BMC should return 4xx "
    "(see docs/recon.md)",
    strict=False,
)
def test_invalid_value_patch(client, system_path):
    """PATCH PowerState with an unsupported value. XPASSes on a real BMC.

    Sent through client.session so the login and TLS settings apply. If the invalid
    value sticks (as the mock does), the saved state is restored afterwards.
    """
    url = f"{client.base_url}{system_path}"
    original = client.get(system_path).get("PowerState")
    response = client.session.patch(
        url, json={"PowerState": "Banana"}, timeout=client.timeout
    )
    try:
        assert 400 <= response.status_code < 500
    finally:
        current = client.get(system_path).get("PowerState")
        if current not in POWER_STATES:
            restore = original if original in POWER_STATES else "On"
            client.patch(system_path, {"PowerState": restore})


def test_malformed_json_body(client, system_path):
    response = client.session.patch(
        f"{client.base_url}{system_path}",
        data="{ this is not json",
        headers={"Content-Type": "application/json"},
        timeout=client.timeout,
    )
    assert response.status_code == 400


def test_timeout_raises_clear_error():
    unreachable = RedfishClient("http://10.255.255.1", timeout=1)
    with pytest.raises(RedfishClientError):
        unreachable.get("/redfish/v1")