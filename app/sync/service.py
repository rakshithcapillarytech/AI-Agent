"""The entry points the CLI, the API and the scheduler share."""

import asyncio
import logging
from pathlib import Path

from app.sync.client import Fetcher, HttpFetcher
from app.sync.impact import store_for
from app.sync.models import SyncResult, load_config
from app.sync.report import write_report
from app.sync.run import run_sync

log = logging.getLogger(__name__)
_lock = asyncio.Lock()


def run_and_report(kb_dir: Path, fetcher: Fetcher | None = None) -> SyncResult:
    """Fetch, update the snapshot and write the reviewer's report."""
    config = load_config(kb_dir)
    store = store_for(config, kb_dir)
    result = run_sync(config, store, fetcher or HttpFetcher(config.fetch))
    if result.index_ok:
        write_report(kb_dir)
    return result


async def run_in_background(kb_dir: Path) -> SyncResult | None:
    """Run a sync without blocking the server; returns None if one is already running."""
    if _lock.locked():
        return None
    async with _lock:
        return await asyncio.to_thread(run_and_report, kb_dir)


async def run_periodically(kb_dir: Path, hours: float) -> None:
    """Sync every `hours` hours (the first run after one interval). Errors are logged, never raised."""
    while True:
        await asyncio.sleep(hours * 3600)
        try:
            result = await run_in_background(kb_dir)
            if result is not None:
                log.info("docs sync: %s changed, %s added, %s failed", len(result.changed), len(result.added), len(result.failed))
        except Exception:
            log.exception("docs sync failed")
