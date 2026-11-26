"""Polite HTTP access to the docs site: one request at a time, a pause between requests, back off when rate-limited."""

import time
from collections.abc import Callable
from dataclasses import dataclass
from typing import Protocol

import httpx

from app.sync.models import FetchConfig


@dataclass
class Fetched:
    status: int
    text: str


class Fetcher(Protocol):
    def get(self, url: str) -> Fetched: ...


class FetchError(Exception):
    """The page couldn't be fetched after retries (rate limit, server error, network)."""


class HttpFetcher:
    """GET with retries. 429 and 5xx are retried with the server's Retry-After (or exponential backoff)."""

    def __init__(
        self,
        config: FetchConfig,
        client: httpx.Client | None = None,
        sleep: Callable[[float], None] = time.sleep,
    ) -> None:
        self.config = config
        self._client = client or httpx.Client(
            headers={"User-Agent": config.user_agent}, timeout=config.timeout_seconds, follow_redirects=True
        )
        self._sleep = sleep
        self._last = 0.0

    def get(self, url: str) -> Fetched:
        for attempt in range(self.config.max_retries + 1):
            wait = self.config.delay_seconds - (time.monotonic() - self._last)
            if wait > 0:
                self._sleep(wait)
            try:
                response = self._client.get(url)
            except httpx.HTTPError as error:
                self._last = time.monotonic()
                if attempt == self.config.max_retries:
                    raise FetchError(f"{type(error).__name__}: {error}") from error
                self._sleep(2**attempt)
                continue
            self._last = time.monotonic()
            if response.status_code == 429 or response.status_code >= 500:
                if attempt == self.config.max_retries:
                    raise FetchError(f"HTTP {response.status_code} after {attempt + 1} tries")
                retry_after = response.headers.get("retry-after", "")
                self._sleep(float(retry_after) if retry_after.isdigit() else min(60.0, 5.0 * 2**attempt))
                continue
            return Fetched(response.status_code, response.text)
        raise FetchError("unreachable")  # pragma: no cover
