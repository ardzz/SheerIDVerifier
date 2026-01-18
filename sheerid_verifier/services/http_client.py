"""HTTP client protocol and implementations."""

from dataclasses import dataclass
from typing import Any, Protocol, runtime_checkable

import httpx

from sheerid_verifier.config import DEFAULT_TIMEOUT


@dataclass
class Response:
    """HTTP response wrapper."""

    status_code: int
    text: str
    _json: dict[str, Any] | None = None

    def json(self) -> dict[str, Any]:
        """Parse response as JSON."""
        if self._json is not None:
            return self._json
        import json

        try:
            parsed = json.loads(self.text) if self.text else {}
            self._json = parsed if isinstance(parsed, dict) else {"_data": parsed}
        except json.JSONDecodeError:
            self._json = {"_text": self.text}
        return self._json


@runtime_checkable
class HttpClient(Protocol):
    """Protocol for HTTP client implementations (Dependency Inversion)."""

    def get(self, url: str, *, headers: dict[str, str] | None = None) -> Response:
        """Send GET request."""
        ...

    def post(
        self,
        url: str,
        *,
        json: dict[str, Any] | None = None,
        headers: dict[str, str] | None = None,
    ) -> Response:
        """Send POST request."""
        ...

    def put(
        self,
        url: str,
        *,
        content: bytes | None = None,
        headers: dict[str, str] | None = None,
        timeout: float | None = None,
    ) -> Response:
        """Send PUT request."""
        ...

    def delete(self, url: str, *, headers: dict[str, str] | None = None) -> Response:
        """Send DELETE request."""
        ...

    def close(self) -> None:
        """Close the client and release resources."""
        ...


class HttpxClient:
    """HTTP client implementation using httpx with SOCKS5 support."""

    def __init__(
        self,
        *,
        proxy: str | None = None,
        timeout: float = DEFAULT_TIMEOUT,
    ) -> None:
        """
        Initialize httpx client.

        Args:
            proxy: Proxy URL (supports http://, socks5://)
            timeout: Default request timeout in seconds
        """
        self._timeout = timeout
        self._client = httpx.Client(
            timeout=timeout,
            proxy=proxy,
            follow_redirects=True,
        )

    def get(self, url: str, *, headers: dict[str, str] | None = None) -> Response:
        """Send GET request."""
        resp = self._client.get(url, headers=headers)
        return Response(status_code=resp.status_code, text=resp.text)

    def post(
        self,
        url: str,
        *,
        json: dict[str, Any] | None = None,
        headers: dict[str, str] | None = None,
    ) -> Response:
        """Send POST request."""
        resp = self._client.post(url, json=json, headers=headers)
        return Response(status_code=resp.status_code, text=resp.text)

    def put(
        self,
        url: str,
        *,
        content: bytes | None = None,
        headers: dict[str, str] | None = None,
        timeout: float | None = None,
    ) -> Response:
        """Send PUT request."""
        resp = self._client.put(
            url,
            content=content,
            headers=headers,
            timeout=timeout or self._timeout,
        )
        return Response(status_code=resp.status_code, text=resp.text)

    def delete(self, url: str, *, headers: dict[str, str] | None = None) -> Response:
        """Send DELETE request."""
        resp = self._client.delete(url, headers=headers)
        return Response(status_code=resp.status_code, text=resp.text)

    def close(self) -> None:
        """Close the client and release resources."""
        self._client.close()

    def __enter__(self) -> "HttpxClient":
        return self

    def __exit__(self, *args: Any) -> None:
        self.close()
