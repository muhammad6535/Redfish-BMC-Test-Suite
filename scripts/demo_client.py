"""Small demo of RedfishClient against the mock BMC."""
from redfish_client.client import RedfishClient, RedfishClientError

BASE = "http://127.0.0.1:8000"
client = RedfishClient(BASE)

print("RedfishVersion:", client.get("/redfish/v1")["RedfishVersion"])
print("Systems:       ", client.members("/redfish/v1/Systems"))
print("Managers:      ", client.members("/redfish/v1/Managers"))

system = client.members("/redfish/v1/Systems")[0]
print("PowerState:    ", client.get(system)["PowerState"])

original = client.get(system)["AssetTag"]
client.patch(system, {"AssetTag": "DEMO-TAG"})
print("AssetTag PATCH:", client.get(system)["AssetTag"])
client.patch(system, {"AssetTag": original})
print("AssetTag back: ", client.get(system)["AssetTag"])

try:
    client.get("/redfish/v1/Systems/NOPE")
except RedfishClientError as exc:
    print("Caught expected error:", exc)
