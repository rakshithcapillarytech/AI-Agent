"""One sync run: read the index, fetch the pages, update the snapshot, say what changed."""

import re
from datetime import UTC, datetime

from app.sync.client import Fetcher, FetchError
from app.sync.index import all_slugs, branch, branch_lines, linked_slugs, updated_at
from app.sync.models import PageRecord, SyncConfig, SyncResult
from app.sync.store import SnapshotStore, sha256


def _wanted_by_link(slug: str, config: SyncConfig) -> bool:
    return any(re.search(p, slug) for p in config.follow.slug_patterns)


def run_sync(config: SyncConfig, store: SnapshotStore, fetcher: Fetcher, now: datetime | None = None) -> SyncResult:
    """Mirror the configured branch of the docs into the snapshot.

    Never loses data: a page that can't be fetched keeps its old snapshot, and if the index itself can't be read
    nothing changes. A run never marks pages as reviewed; that is a person's decision (`accept`)."""
    started = now or datetime.now(UTC)
    result = SyncResult(started_at=started)
    manifest = store.load()
    manifest.source, manifest.base_url = config.source, config.base_url

    try:
        index = fetcher.get(config.base_url + config.index_path)
    except FetchError as error:
        result.index_ok = False
        result.failed["(index)"] = str(error)
        result.finished_at = datetime.now(UTC)
        return result
    entries = branch(index.text, config.root_title) if index.status == 200 else []
    if not entries:
        result.index_ok = False
        result.failed["(index)"] = f"no '{config.root_title}' branch found (HTTP {index.status})"
        result.finished_at = datetime.now(UTC)
        return result

    store.write_text("index.txt", "\n".join(branch_lines(index.text, config.root_title)) + "\n")  # what the site's index listed
    in_index = all_slugs(index.text)
    queue: list[tuple[str, str, str | None, str]] = [(e.slug, e.title, e.parent, "index") for e in entries]
    seen: set[str] = set()
    queued: set[str] = {e.slug for e in entries}
    extra = 0
    while queue:
        slug, title, parent, found_via = queue.pop(0)
        if slug in seen:
            continue
        seen.add(slug)
        url = f"{config.base_url}/docs/{slug}.md"
        try:
            page = fetcher.get(url)
        except FetchError as error:
            result.failed[slug] = str(error)
            continue
        if page.status != 200 or not page.text.lstrip().startswith("---"):
            result.failed[slug] = f"HTTP {page.status}" if page.status != 200 else "not a Markdown page"
            continue
        result.fetched += 1
        digest = sha256(page.text)
        previous = manifest.pages.get(slug)
        record = PageRecord(
            slug=slug,
            url=url,
            title=title,
            parent=parent,
            found_via=found_via,
            updated_at=updated_at(page.text),
            sha256=digest,
            size=len(page.text),
            fetched_at=started,
            reviewed_sha256=previous.reviewed_sha256 if previous else None,
            reviewed_updated_at=previous.reviewed_updated_at if previous else None,
        )
        if previous is None:
            result.added.append(slug)
        elif previous.sha256 != digest:
            result.changed.append(slug)
        else:
            result.unchanged += 1
            record.fetched_at = previous.fetched_at  # an unchanged page stays byte-identical in git
        if previous is None or previous.sha256 != digest or store.read_page(slug) is None:
            store.write_page(record, page.text, previous)
        manifest.pages[slug] = record
        # pages the index leaves out: follow links from the pages we mirror (not from followed pages: depth 1)
        if found_via == "index":
            for linked in sorted(linked_slugs(page.text)):
                if linked in queued or linked in in_index or not _wanted_by_link(linked, config):
                    continue
                if extra >= config.follow.max_extra_pages:
                    break
                extra += 1
                queued.add(linked)
                queue.append((linked, linked, slug, f"link:{slug}"))
                result.followed.append(linked)

    for slug, record in manifest.pages.items():
        if slug not in seen and not record.removed:
            record.removed = True
            result.removed.append(slug)
        elif slug in seen and record.removed:
            record.removed = False
    if result.added or result.changed or result.removed or manifest.synced_at is None:
        manifest.synced_at = started  # the snapshot's own date moves only when its content does, so git stays quiet
    store.save(manifest)
    result.finished_at = datetime.now(UTC)
    store.write_json("last-run.json", result.model_dump(mode="json"))
    return result
