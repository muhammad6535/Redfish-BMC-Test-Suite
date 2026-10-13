# Redfish BMC Test Suite

[![CI](https://github.com/muhammad6535/Redfish-BMC-Test-Suite/actions/workflows/ci.yml/badge.svg)](https://github.com/muhammad6535/Redfish-BMC-Test-Suite/actions/workflows/ci.yml)

Automated Pytest suite that validates a server BMC through the DMTF Redfish API.

## Why it matters

A BMC (Baseboard Management Controller) is the small computer inside a server that manages
the hardware out-of-band: power, cooling, sensors and network. Hardware teams test it
constantly, because a BMC that reports wrong data or ignores commands can take down a whole
rack. This project tests one the way a QA engineer would, against a free mock BMC, so
everything runs on a laptop.

## Architecture

```mermaid
flowchart LR
    T[Pytest tests] --> C[RedfishClient]
    C -->|HTTP GET/PATCH/POST| B[BMC Redfish API]
    T --> V[Validators]
```

Tests never call the BMC directly; they go through one `RedfishClient`, so changing `BMC_URL`
points the same suite at real hardware. The client handles HTTP, timeouts and link-following;
the validators hold the checks (MAC, IP, ranges); the tests only describe what should be true.

## What is tested

- **Smoke** - the service root responds and advertises Systems, Chassis, Managers.
- **Functional (system)** - power state, health and identity fields are present and valid.
- **Network** - each BMC Ethernet interface has a valid, unique MAC, valid IPv4, a known link
  status, positive speed when up, and consistent VLAN settings.
- **Thermal and power** - temperatures within thresholds, fans spinning when healthy,
  voltages within range.
- **Write and actions** - PATCH the system AssetTag and restore it; POST a Reset action.
- **Negative** - missing resources, malformed JSON and timeouts fail clearly, never hang.

## How to run

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
git clone --depth 1 https://github.com/DMTF/Redfish-Mockup-Server.git ../Redfish-Mockup-Server
pytest
```

Point it at a real BMC by setting the base URL:

```bash
BMC_URL=https://my-bmc.example.com pytest
```

Run one category with markers: `pytest -m smoke`, `pytest -m network`, etc.

## Sample report

`pytest` writes an HTML report to `reports/report.html`. A copy from a local run (47 passed,
5 skipped - the skips are documented mock limitations):

![Sample pytest report](docs/report-screenshot.png)

CI uploads the same report as a downloadable artifact on every run.

## Repository layout

```
src/redfish_client/   client.py, validators.py
tests/                conftest.py, test_*.py, unit/
docs/                 test_plan.md, bug_report_template.md, recon.md, report-screenshot.png
.github/workflows/    ci.yml
```
