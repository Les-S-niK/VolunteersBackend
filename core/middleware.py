from collections.abc import Awaitable, Callable
from ipaddress import ip_address, ip_network
from typing import Any

Scope = dict[str, Any]
Message = dict[str, Any]
Receive = Callable[[], Awaitable[Message]]
Send = Callable[[Message], Awaitable[None]]


class TrustedProxyMiddleware:
    def __init__(self, app: Any, *, trusted_proxies: list[str]) -> None:
        self.app = app
        self.trusted_networks = [
            ip_network(proxy, strict=False) for proxy in trusted_proxies
        ]

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] == "http":
            client = scope.get("client")
            if client and self.is_trusted(client[0]):
                headers = dict(scope.get("headers", []))
                real_ip = headers.get(b"x-real-ip")
                if real_ip and self.is_ip(real_ip):
                    scope["client"] = (real_ip.decode("ascii"), client[1])
                    scope["headers"] = [
                        (name, value)
                        for name, value in scope["headers"]
                        if name.lower() != b"x-forwarded-for"
                    ]
        await self.app(scope, receive, send)

    def is_trusted(self, host: str) -> bool:
        try:
            address = ip_address(host)
        except ValueError:
            return False
        return any(address in network for network in self.trusted_networks)

    @staticmethod
    def is_ip(value: bytes) -> bool:
        try:
            ip_address(value.decode("ascii"))
        except (UnicodeDecodeError, ValueError):
            return False
        return True
