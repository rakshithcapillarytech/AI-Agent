"""Command line for the docs sync.

    uv run python -m app.sync run              fetch the online docs, update the snapshot, write the reviewer's report
    uv run python -m app.sync status           what is fresh, what changed, which facts fail
    uv run python -m app.sync check            check the key facts only (exit 1 if any fail): good for CI
    uv run python -m app.sync report           print the reviewer's report from the current snapshot
    uv run python -m app.sync accept --all     mark pages as reviewed (after updating the guides)
    uv run python -m app.sync accept SLUG...   mark some pages as reviewed
    uv run python -m app.sync draft            AI-drafted suggestions for the changed pages (needs an API key)
    uv run python -m app.sync propose          fetch, then prepare the update on git branches (nothing reaches your branch)
    uv run python -m app.sync update           propose, and merge it when the checks pass: values update by themselves,
                                               other changes stay flagged for a person
"""

import argparse
import sys

from app.config import get_settings
from app.sync.anchors import check_anchors, failing
from app.sync.impact import store_for
from app.sync.models import load_config
from app.sync.report import build_report, write_report
from app.sync.service import run_and_report
from app.sync.status import sync_status


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="python -m app.sync", description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = parser.add_subparsers(dest="command", required=True)
    run = sub.add_parser("run")
    run.add_argument("--fail-on-changes", action="store_true", help="exit 1 if pages changed or a key fact fails")
    sub.add_parser("status")
    sub.add_parser("check")
    sub.add_parser("report")
    accept = sub.add_parser("accept")
    accept.add_argument("slugs", nargs="*")
    accept.add_argument("--all", action="store_true")
    sub.add_parser("draft")
    for name in ("propose", "update"):
        p = sub.add_parser(name)
        p.add_argument("--no-fetch", action="store_true", help="use the snapshot as it is")
        p.add_argument("--draft", action="store_true", help="also write AI-drafted suggestions for changes a person must handle")
    args = parser.parse_args(argv)

    kb = get_settings().knowledge_base_dir
    config = load_config(kb)
    store = store_for(config, kb)

    if args.command == "run":
        result = run_and_report(kb)
        print(
            f"fetched {result.fetched} pages: {len(result.added)} new, {len(result.changed)} changed, {result.unchanged} unchanged, "
            f"{len(result.removed)} removed, {len(result.followed)} found through links, {len(result.failed)} failed"
        )
        for slug, why in result.failed.items():
            print(f"  failed {slug}: {why}")
        if not result.index_ok:
            return 2
        status = sync_status(kb)
        print(f"{len(status['changed'])} pages to review, {len(status['anchors']['failing'])} key facts failing; report: {store.root / 'CHANGES.md'}")
        if args.fail_on_changes and (status["changed"] or status["anchors"]["failing"]):
            return 1
        return 0

    if args.command == "status":
        status = sync_status(kb)
        if not status["synced"]:
            print(status.get("reason", "not synced"))
            return 1
        print(f"synced {status['synced_at']}: {status['pages']} pages, {len(status['changed'])} changed since review, "
              f"{len(status['stale_guides'])} guides need review, {len(status['anchors']['failing'])}/{status['anchors']['total']} key facts failing")
        for c in status["changed"]:
            print(f"  changed: {c['slug']} ({c['reviewed_updated_at']} -> {c['updated_at']}) -> {', '.join(c['guides']) or 'no guide'}")
        for a in status["anchors"]["failing"]:
            print(f"  fact: {a['fact']} [{a['problem']}]")
        return 0

    if args.command == "check":
        bad = failing(check_anchors(kb, store))
        for r in bad:
            where = "online page" if r.online is not True else "guides"
            print(f"FAIL {r.anchor.id}: {r.anchor.fact} ({where})")
        print(f"{len(bad)} of {len(check_anchors(kb, store))} key facts failing")
        return 1 if bad else 0

    if args.command == "report":
        print(build_report(kb))
        return 0

    if args.command == "accept":
        if not args.all and not args.slugs:
            parser.error("give page slugs or --all")
        manifest = store.load()
        done = store.accept(manifest, None if args.all else args.slugs)
        store.save(manifest)
        write_report(kb)
        print(f"marked {len(done)} pages as reviewed")
        return 0

    if args.command in ("propose", "update"):
        from app.sync.propose import ProposalError, propose

        drafter = None
        if args.draft:
            from app.llm import helper_model
            from app.sync.draft import draft_proposals

            drafter = lambda kb_dir: draft_proposals(kb_dir, helper_model())
        try:
            result = propose(kb.parent, kb, fetch=not args.no_fetch, merge=args.command == "update", drafter=drafter)
        except ProposalError as error:
            print(f"couldn't prepare the update: {error}")
            return 3
        print(f"{result.status}: {result.detail}".rstrip(": "))
        for item in result.applied:
            print(f"  updated {item['slug']}: {', '.join(item['values'])}")
        for edit in result.edits:
            print(f"  edited {edit.path} ({edit.replacements})")
        for check in result.gate:
            print(f"  check {'ok' if check.ok else 'FAILED'}: {check.name}")
        for slug, why in result.needs_person.items():
            print(f"  needs a person: {slug} ({why})")
        if result.branch:
            print(f"  branch: {result.branch}")
        return 0 if result.status in ("nothing", "merged", "ready") else 1

    if args.command == "draft":
        from app.llm import helper_model
        from app.sync.draft import draft_proposals

        path = draft_proposals(kb, helper_model())
        print(path or "nothing changed, no draft written")
        return 0
    return 1


if __name__ == "__main__":
    sys.exit(main())
