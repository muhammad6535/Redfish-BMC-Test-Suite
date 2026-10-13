"""Minimal Redfish client used by the test suite."""
import requests


class RedfishClientError(Exception):
    """Raised when the BMC returns an unexpected response."""


class RedfishClient:
    def __init__(self, base_url, timeout=10, auth=None, verify=True, session=None):
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.session = session or requests.Session()
        self.session.auth = auth
        self.session.verify = verify

    def _url(self, path):
        if path.startswith("http"):
            return path
        return f"{self.base_url}/{path.lstrip('/')}"

    def get(self, path):
        return self._request("GET", path)

    def patch(self, path, body):
        return self._request("PATCH", path, json=body)

    def post(self, path, body):
        return self._request("POST", path, json=body)

    def members(self, path):
        """Return the @odata.id list of a Redfish collection."""
        collection = self.get(path)
        return [member["@odata.id"] for member in collection.get("Members", [])]

    def _request(self, method, path, **kwargs):
        url = self._url(path)
        try:
            response = self.session.request(method, url, timeout=self.timeout, **kwargs)
        except requests.RequestException as exc:
            raise RedfishClientError(f"{method} {url} failed: {exc}") from exc
        if not response.ok:
            raise RedfishClientError(
                f"{method} {url} -> {response.status_code}: {response.text[:200]}"
            )
        return response.json() if response.content else None
