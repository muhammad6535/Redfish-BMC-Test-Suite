"""Pure validation helpers for Redfish values."""
import ipaddress
import re

_MAC_RE = re.compile(r"^([0-9A-Fa-f]{2}[:-]){5}[0-9A-Fa-f]{2}$")


def is_valid_mac(value):
    return isinstance(value, str) and bool(_MAC_RE.match(value))


def is_valid_ipv4(value):
    if not isinstance(value, str):
        return False
    try:
        return isinstance(ipaddress.ip_address(value), ipaddress.IPv4Address)
    except ValueError:
        return False


def in_allowed_set(value, allowed):
    return value in allowed


def in_range(value, minimum=None, maximum=None):
    if not isinstance(value, (int, float)):
        return False
    if minimum is not None and value < minimum:
        return False
    if maximum is not None and value > maximum:
        return False
    return True
