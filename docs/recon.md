# Recon — DMTF Redfish Mockup Server

Manual exploration of the mock BMC before writing any tests, so the suite matches the
real data shapes. Server: `redfishMockupServer.py` (DMTF Redfish-Mockup-Server), mockup
`public-rackmount1`, `http://127.0.0.1:8000`. RedfishVersion `1.15.0`.

## Resource tree (discovered by following links from `/redfish/v1`)

```
/redfish/v1
├── Systems            -> /redfish/v1/Systems/437XR1138R2        (Contoso 3500, PowerState On)
├── Chassis            -> /redfish/v1/Chassis/1U                 (RackMount)
│     ├── Thermal      -> .../Thermal   (2 fans, 3 temp sensors)
│     └── Power        -> .../Power     (PowerControl, 1 supply, 2 voltages)
├── Managers           -> /redfish/v1/Managers/BMC               (ManagerType BMC)
│     └── EthernetInterfaces -> .../EthernetInterfaces/{eth0, ToHost}
├── AccountService, CertificateService, EventService, UpdateService, ...
```

Resource IDs are **not** hard-coded in tests: they are discovered from the collection
`Members` arrays so the same tests can run against real hardware.

## Key fields per resource (used by the tests)

**System `/redfish/v1/Systems/437XR1138R2`**
- `PowerState`: `"On"`. Per the Redfish spec `PowerState` can be `On`, `Off`,
  `PoweringOn`, or `PoweringOff`; the test asserts membership in exactly that set.
- Reset action allowable values from `Actions.#ComputerSystem.Reset`:
  On, ForceOff, GracefulShutdown, GracefulRestart, ForceRestart, Nmi, ForceOn,
  PushPowerButton
- `Status.Health`: `"OK"`, `Status.State`: `"Enabled"`
- `Model`: `"3500"`, `SerialNumber`: `"437XR1138R2"`, `Manufacturer`: `"Contoso"`
- `AssetTag`: `"Chicago-45Z-2381"` (writable — see write check)
- Reset action target: `/redfish/v1/Systems/437XR1138R2/Actions/ComputerSystem.Reset`

**Manager `/redfish/v1/Managers/BMC`**
- `ManagerType`: `"BMC"`, `FirmwareVersion`: `"1.45.455b66-rev4"`
- `Status.Health`: `"OK"`, `PowerState`: `"On"`

**Manager Ethernet interfaces**

| Field | eth0 | ToHost |
| --- | --- | --- |
| `MACAddress` | `23:11:8A:33:CF:EA` | `AA:BB:CC:DD:EE:FF` |
| `IPv4Addresses[0].Address` | `192.168.0.10` | `192.168.20.55` |
| `LinkStatus` | `LinkUp` | **(absent)** |
| `SpeedMbps` | `100` | `100` |
| `VLAN` | `{VLANEnable:true, VLANId:101}` | *(absent)* |
| `Status.Health` | `OK` | `OK` |

**Thermal `/redfish/v1/Chassis/1U/Thermal`**
- `Fans`: 2 entries, `Reading` 2100/2050 RPM, `ReadingUnits` `RPM`, `Status.Health` OK
- `Temperatures`: 3 entries — CPU1 (ReadingCelsius 41, health OK), CPU2
  (`Status.State: Disabled`, no reading), Chassis Intake (25, OK)
- Thresholds present: `UpperThresholdCritical`/`Fatal`/`NonCritical`, `LowerThreshold*`

**Power `/redfish/v1/Chassis/1U/Power`**
- `PowerControl[0]`: `PowerConsumedWatts` 344, capacity 800
- `PowerSupplies[0]`: `Status.Health` **`"Warning"`** (not OK), 800W
- `Voltages`: 2 entries, `ReadingVolts` 12 and 5, health OK

## Write check (PATCH / POST) — done in recon, not deferred

| Operation | Request | Result |
| --- | --- | --- |
| PATCH AssetTag | `{"AssetTag":"QA-TEST-TAG"}` | **204**, value persisted (read back confirmed), then restored to original |
| PATCH value validation | `{"PowerState":"Banana"}` | **204** — mock accepts invalid values, does **not** schema-validate |
| POST Reset action | `{"ResetType":"On"}` | **204** |
| GET missing resource | `/redfish/v1/Systems/DOES-NOT-EXIST` | **404** |
| Malformed JSON body | `{bad json` | **400** |

### Consequences for the test plan
- `write` tests are viable: PATCH persists and can be restored; POST Reset returns 204.
- Negative "PATCH invalid value returns 4xx" does **not** fail on the mock (returns 204).
  A real BMC would reject it, so that case is marked `xfail` with the documented mock
  limitation and will XPASS on hardware.
- `ToHost` has no `LinkStatus` field. A test requiring `LinkStatus` on *every* interface
  must handle the absent field (conditional / documented), not assume it.
- `PowerSupplies[0].Status.Health` is `"Warning"` in the mock data. Assertions about
  "health is OK" must be scoped (e.g. fans, not power supplies) or aware of this value,
  which is a valid Redfish health state.

## Reproduction

```powershell
# from the Redfish-Mockup-Server clone
python redfishMockupServer.py -H 127.0.0.1 -p 8000
```

The test suite itself starts the mock on a **random free port** (`-p` picked at runtime),
so a stale or dirty server left on port 8000 can never be mistaken for a fresh one.

The mock supports PATCH/POST "to a limited extent" (its README). Findings above reflect
the `public-rackmount1` mockup shipped in the cloned revision.