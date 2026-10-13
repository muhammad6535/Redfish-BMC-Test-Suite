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


@pytest.fixture(scope="session")
def bmc_url():
    url = os.environ.get("BMC_URL")
    if url:
        yield url.rstrip("/")
        return

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
    try:
        if not _wait_until_ready(DEFAULT_URL, STARTUP_TIMEOUT):
            raise RuntimeError(f"Mock BMC not ready at {DEFAULT_URL} within {STARTUP_TIMEOUT}s")
        yield DEFAULT_URL
    finally:
        process.terminate()
        try:
            process.wait(timeout=10)
        except subprocess.TimeoutExpired:
            process.kill()


@pytest.fixture(scope="session")
def client(bmc_url):
    return RedfishClient(bmc_url)
