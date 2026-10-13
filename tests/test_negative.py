"""Negative and edge-case tests: bad input and clear failures."""
import pytest
import requests

from redfish_client.client import RedfishClient, RedfishClientError

pytestmark = pytest.mark.negative


def test_missing_resource_raises_404(client):
    with pytest.raises(RedfishClientError) as exc:
        client.get("/redfish/v1/Systems/DOES-NOT-EXIST")
    assert "404" in str(exc.value)


def test_invalid_value_patch(client, system_path):
    pytest.skip(
        "Mock accepts invalid values (returns 204); a real BMC should return 4xx "
        "(see docs/recon.md)"
    )


def test_malformed_json_body(client, system_path):
    url = f"{client.base_url}{system_path}"
    response = requests.patch(
        url,
        data="{ this is not json",
        headers={"Content-Type": "application/json"},
        timeout=5,
    )
    assert response.status_code == 400


def test_timeout_raises_clear_error():
    unreachable = RedfishClient("http://10.255.255.1", timeout=1)
    with pytest.raises(RedfishClientError):
        unreachable.get("/redfish/v1")
