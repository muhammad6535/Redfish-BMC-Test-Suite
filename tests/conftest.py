"""Shared fixtures: start the mock BMC and provide a Redfish client."""
import os
import subprocess
import sys
import time

import pytest
import requests

from redfish_client.client import RedfishClient

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MOCK_DIR = os.environ.get(
    "MOCK_SERVER_DIR",
    os.path.abspath(os.path.join(REPO_ROOT, os.pardir, "Redfish-Mockup-Server")),
)
MOCK_SCRIPT = os.path.join(MOCK_DIR, "redfishMockupServer.py")
DEFAULT_URL = "http://127.0.0.1:8000"
STARTUP_TIMEOUT = 30

_server = {"process": None, "url": None}


def _wait_until_ready(url, timeout):
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        try:
            if requests.get(f"{url}/redfish/v1", timeout=2).ok:
                return True
        except requests.RequestException:
            pass
        time.sleep(0.5)
    return False


def _base_url():
    """Return the BMC base URL, starting the mock server on first use."""
    if _server["url"]:
        return _server["url"]
    url = os.environ.get("BMC_URL")
    if url:
        _server["url"] = url.rstrip("/")
        return _server["url"]
    if not os.path.isfile(MOCK_SCRIPT):
        pytest.exit(
            f"Mock server not found at {MOCK_SCRIPT}. "
            "Clone DMTF/Redfish-Mockup-Server, or set BMC_URL / MOCK_SERVER_DIR."
        )
    process = subprocess.Popen(
        [sys.executable, MOCK_SCRIPT],
        cwd=MOCK_DIR,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    if not _wait_until_ready(DEFAULT_URL, STARTUP_TIMEOUT):
        process.terminate()
        pytest.exit(f"Mock BMC not ready at {DEFAULT_URL} within {STARTUP_TIMEOUT}s")
    _server["process"] = process
    _server["url"] = DEFAULT_URL
    return _server["url"]


def pytest_unconfigure(config):
    process = _server.get("process")
    if process and process.poll() is None:
        process.terminate()
        try:
            process.wait(timeout=10)
        except subprocess.TimeoutExpired:
            process.kill()


def _short_id(path):
    return path.rstrip("/").rsplit("/", 1)[-1]


def pytest_generate_tests(metafunc):
    """Parametrize tests over discovered resources (one test per resource)."""
    names = set(metafunc.fixturenames)
    interesting = {
        "system_path",
        "manager_path",
        "chassis_path",
        "interface_path",
        "temperature",
        "fan",
        "voltage",
    }
    if not (names & interesting):
        return

    client = RedfishClient(_base_url())

    if "system_path" in names:
        paths = client.members("/redfish/v1/Systems")
        metafunc.parametrize("system_path", paths, ids=[_short_id(p) for p in paths])

    if "manager_path" in names:
        paths = client.members("/redfish/v1/Managers")
        metafunc.parametrize("manager_path", paths, ids=[_short_id(p) for p in paths])

    if "chassis_path" in names:
        paths = client.members("/redfish/v1/Chassis")
        metafunc.parametrize("chassis_path", paths, ids=[_short_id(p) for p in paths])

    if "interface_path" in names:
        paths = []
        for manager in client.members("/redfish/v1/Managers"):
            paths += client.members(f"{manager}/EthernetInterfaces")
        metafunc.parametrize("interface_path", paths, ids=[_short_id(p) for p in paths])

    if "temperature" in names or "fan" in names:
        temperatures, fans = [], []
        for chassis in client.members("/redfish/v1/Chassis"):
            thermal = client.get(f"{chassis}/Thermal")
            temperatures += thermal.get("Temperatures", [])
            fans += thermal.get("Fans", [])
        if "temperature" in names:
            metafunc.parametrize(
                "temperature",
                temperatures,
                ids=[t.get("Name", str(i)) for i, t in enumerate(temperatures)],
            )
        if "fan" in names:
            metafunc.parametrize(
                "fan",
                fans,
                ids=[f.get("Name", str(i)) for i, f in enumerate(fans)],
            )

    if "voltage" in names:
        voltages = []
        for chassis in client.members("/redfish/v1/Chassis"):
            power = client.get(f"{chassis}/Power")
            voltages += power.get("Voltages", [])
        metafunc.parametrize(
            "voltage",
            voltages,
            ids=[v.get("Name", str(i)) for i, v in enumerate(voltages)],
        )


@pytest.fixture(scope="session")
def bmc_url():
    return _base_url()


@pytest.fixture(scope="session")
def client(bmc_url):
    return RedfishClient(bmc_url)
