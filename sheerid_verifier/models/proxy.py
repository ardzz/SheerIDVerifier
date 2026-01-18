"""Proxy configuration model."""

from dataclasses import dataclass
from enum import Enum


class ProxyType(Enum):
    """Supported proxy types."""

    HTTP = "http"
    HTTPS = "https"
    SOCKS5 = "socks5"


@dataclass(frozen=True)
class ProxyConfig:
    """
    Proxy configuration.

    Attributes:
        type: Proxy protocol type (http, https, socks5)
        host: Proxy server hostname or IP
        port: Proxy server port
        username: Optional authentication username
        password: Optional authentication password
    """

    type: ProxyType
    host: str
    port: int
    username: str | None = None
    password: str | None = None

    @property
    def url(self) -> str:
        """
        Build proxy URL string.

        Returns:
            Full proxy URL in format: protocol://[user:pass@]host:port
        """
        auth = f"{self.username}:{self.password}@" if self.username else ""
        return f"{self.type.value}://{auth}{self.host}:{self.port}"

    @property
    def has_auth(self) -> bool:
        """Check if proxy requires authentication."""
        return self.username is not None and self.password is not None

    def __str__(self) -> str:
        """Return masked URL (hides password)."""
        if self.has_auth:
            return f"{self.type.value}://{self.username}:****@{self.host}:{self.port}"
        return self.url
