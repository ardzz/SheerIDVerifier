"""Proxy URL parsing utilities."""

import re
from urllib.parse import urlparse

from sheerid_verifier.models.proxy import ProxyConfig, ProxyType


class ProxyParseError(ValueError):
    """Raised when proxy URL cannot be parsed."""

    pass


def parse_proxy_url(url: str) -> ProxyConfig:
    """
    Parse a proxy URL string into a ProxyConfig object.

    Supports formats:
        - socks5://host:port
        - socks5://user:pass@host:port
        - http://host:port
        - http://user:pass@host:port
        - https://host:port
        - https://user:pass@host:port

    Args:
        url: Proxy URL string

    Returns:
        ProxyConfig object

    Raises:
        ProxyParseError: If URL is invalid or unsupported
    """
    if not url:
        raise ProxyParseError("Empty proxy URL")

    # Normalize URL
    url = url.strip()

    # Parse URL
    try:
        parsed = urlparse(url)
    except Exception as e:
        raise ProxyParseError(f"Invalid URL format: {e}") from e

    # Validate scheme
    scheme = parsed.scheme.lower()
    try:
        proxy_type = ProxyType(scheme)
    except ValueError:
        valid_schemes = ", ".join(t.value for t in ProxyType)
        raise ProxyParseError(f"Unsupported proxy type: {scheme}. Valid types: {valid_schemes}")

    # Extract host
    host = parsed.hostname
    if not host:
        raise ProxyParseError("Missing host in proxy URL")

    # Extract port
    port = parsed.port
    if not port:
        # Default ports
        default_ports = {
            ProxyType.HTTP: 80,
            ProxyType.HTTPS: 443,
            ProxyType.SOCKS5: 1080,
        }
        port = default_ports.get(proxy_type, 1080)

    # Extract credentials (optional)
    username = parsed.username
    password = parsed.password

    # Validate: if username provided, password should also be provided
    if username and not password:
        raise ProxyParseError("Password required when username is provided")

    return ProxyConfig(
        type=proxy_type,
        host=host,
        port=port,
        username=username,
        password=password,
    )


def validate_proxy_url(url: str) -> bool:
    """
    Validate a proxy URL string.

    Args:
        url: Proxy URL string

    Returns:
        True if valid, False otherwise
    """
    try:
        parse_proxy_url(url)
        return True
    except ProxyParseError:
        return False


def mask_proxy_url(url: str) -> str:
    """
    Mask password in proxy URL for safe logging.

    Args:
        url: Proxy URL string

    Returns:
        URL with password replaced by ****
    """
    # Pattern to match user:pass@ in URL
    pattern = r"(://[^:]+:)([^@]+)(@)"
    return re.sub(pattern, r"\1****\3", url)
