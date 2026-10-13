# Test Plan — Redfish BMC Test Suite

## Purpose
Validate a server BMC through its Redfish API, the way a QA engineer would test real
hardware. The BMC is exercised through a single `RedfishClient`; resources are discovered by
following links, never hard-coded, so the same suite runs against the DMTF mock BMC or real
hardware (set `BMC_URL`).

## In scope
- Service root and top-level collections (Systems, Chassis, Managers)
- ComputerSystem fields: PowerState, Status.Health, Model, SerialNumber
- Manager Ethernet interfaces: MAC, IPv4, LinkStatus, SpeedMbps, VLAN
- Thermal: temperature thresholds, fan readings
- Power: voltage thresholds, power consumption
- Write actions: PATCH AssetTag (restored), POST Reset
- Negative cases: missing resource, malformed JSON, timeout

## Out of scope
- Real hardware, a UI, performance/load testing, authentication beyond error handling

## Test categories
| Marker | File | Focus |
| --- | --- | --- |
| smoke | test_smoke.py | service is up, root links respond, under 2s |
| functional | test_system.py, test_thermal_power.py | fields and values correct |
| network | test_manager_network.py | interface data valid |
| write | test_write_actions.py | changes persist and are restored |
| negative | test_negative.py | bad input fails clearly |

## Test design notes
- Resources are discovered from collection `Members` and parametrized, so each interface or
  sensor appears as its own pass/fail.
- Write tests restore the original value in a `finally` block, so the suite is order-independent.
- Cases that cannot work on the mock are skipped with a reason (see docs/recon.md).

## Environment
- Python 3.13, pytest, requests, pytest-html
- DMTF Redfish Mockup Server on 127.0.0.1:8000 (or a real BMC via BMC_URL)

## Entry / exit criteria
- Entry: mock BMC reachable at /redfish/v1.
- Exit: all non-skipped tests pass; skips are documented mock limitations.
