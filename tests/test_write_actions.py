"""State-changing tests. Every change is restored."""
import pytest

pytestmark = pytest.mark.write

NEW_TAG = "QA-TEST-TAG"


def test_asset_tag_roundtrip(client, system_path):
    original = client.get(system_path).get("AssetTag")
    try:
        client.patch(system_path, {"AssetTag": NEW_TAG})
        assert client.get(system_path)["AssetTag"] == NEW_TAG
    finally:
        if original is not None:
            client.patch(system_path, {"AssetTag": original})
    assert client.get(system_path).get("AssetTag") == original


def test_reset_action_accepted(client, system_path):
    reset = client.get(system_path)["Actions"]["#ComputerSystem.Reset"]
    target = reset["target"]
    allowed = reset.get("ResetType@Redfish.AllowableValues")
    if allowed:
        assert "On" in allowed
    client.post(target, {"ResetType": "On"})
