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
- Power: voltage thresholds, power consumption, power supply health
- Write actions: PATCH AssetTag (restored), POST Reset
- Negative cases: missing resource, malformed JSON, timeout, unsupported value PATCH

## Out of scope
- Real hardware, a UI, performance/load testing, authentication beyond error handling

## Test categories
| Marker | File | Focus |
| --- | --- | --- |
| smoke | test_smoke.py | service is up, root links respond, under 2s |
| functional | test_system.py, test_thermal_power.py | fields/values correct, thermal and power sensors, PSU health |
| network | test_manager_network.py | interface data valid |
| write | test_write_actions.py | changes persist and are restored |
| negative | test_negative.py | bad input fails clearly; unsupported-value PATCH |

## Test design notes
- Resources are discovered from collection `Members` and parametrized, so each interface or
  sensor appears as its own pass/fail.
- Write tests restore the original value in a `finally` block, so the suite is order-independent.
- The unsupported `PowerState` PATCH (a real BMC should answer 4xx) is marked `xfail` against
  the mock, which accepts it without validation. The test restores the state afterwards and
  XPASSes on real hardware — a known-bug case to discuss in an interview.
- A power supply reporting `Status.Health: Warning` is a valid Redfish state; the health test
  accepts the documented set rather than assuming OK.
- Cases the mock cannot exercise (e.g. LinkStatus on `ToHost`, schema validation) are skipped
  or xfailed with a reason (see docs/recon.md).

## Environment
- Python 3.13, pytest, requests, pytest-html
- DMTF Redfish Mockup Server started by the fixtures on a free local port (or a real BMC
  via BMC_URL), with optional `BMC_USER`, `BMC_PASSWORD`, `BMC_VERIFY_TLS`.

## Entry / exit criteria
- Entry: mock BMC (or real BMC via BMC_URL) reachable at /redfish/v1.
- Exit: all non-skipped, non-xfailed tests pass; the skips and the xfail are documented mock
  limitations.