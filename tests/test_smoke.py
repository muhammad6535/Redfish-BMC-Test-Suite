"""Smoke tests: the service is up and advertising the main collections."""
import time

import pytest

pytestmark = pytest.mark.smoke

EXPECTED_LINKS = ["Systems", "Chassis", "Managers"]


def test_service_root_responds(client):
    root = client.get("/redfish/v1")
    assert root["@odata.id"] == "/redfish/v1/"
    assert "RedfishVersion" in root


@pytest.mark.parametrize("link", EXPECTED_LINKS)
def test_service_root_links(client, link):
    root = client.get("/redfish/v1")
    assert link in root
    client.get(root[link]["@odata.id"])


def test_service_root_response_time(client):
    start = time.monotonic()
    client.get("/redfish/v1")
    elapsed = time.monotonic() - start
    assert elapsed < 2.0, f"service root took {elapsed:.2f}s"
