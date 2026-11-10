"""Checks on the Firebase config files a client uploads (PLAN.md §4 ②).

`google-services.json` (Android) and `GoogleService-Info.plist` (iOS) must belong to the app the
client registered with Capillary: the package name or bundle ID inside the file has to equal the
application ID or bundle ID the client gave us. A mismatch is the classic cause of "Firebase
works but Hydra push doesn't".

Uploaded files are untrusted data and contain API keys. Nothing from them reaches the model
except package names and bundle IDs that pass the same format check as client-stated values.
"""

import json
import plistlib
from dataclasses import dataclass
from typing import Literal

from app.rules.prereq_engine import FORMATS

Kind = Literal["google_services_json", "google_service_info_plist"]
Outcome = Literal["match", "mismatch", "unchecked", "invalid", "unrecognised"]

# Which checklist rule records each file, and which identifier it has to agree with.
EXPECTED_ITEM = {"google_services_json": "android_application_id", "google_service_info_plist": "ios_bundle_id"}
ID_FORMAT = {"google_services_json": "android_application_id", "google_service_info_plist": "ios_bundle_id"}
ID_LABEL = {"google_services_json": "package name", "google_service_info_plist": "bundle ID"}
FILE_LABEL = {"google_services_json": "google-services.json", "google_service_info_plist": "GoogleService-Info.plist"}


@dataclass
class FileCheck:
    outcome: Outcome
    detail: str  # plain-English result, safe to show the client and the model
    kind: Kind | None = None


def _safe_ids(kind: Kind, values: list) -> list[str]:
    """Only well-formed identifiers survive; anything else in an untrusted file is dropped."""
    pattern = FORMATS[ID_FORMAT[kind]]
    unique = {v for v in values if isinstance(v, str) and len(v) <= 200 and pattern.fullmatch(v)}
    return sorted(unique)


def _android_package_names(data: dict) -> list:
    names = []
    for client in data.get("client") or []:
        try:
            names.append(client["client_info"]["android_client_info"]["package_name"])
        except (KeyError, TypeError):
            continue
    return names


def _parse(content: bytes) -> tuple[Kind, list[str]] | None:
    """Recognise the file by its content (not its name) and pull out its package names / bundle ID."""
    try:
        data = json.loads(content.decode("utf-8-sig"))
    except ValueError:  # includes UnicodeDecodeError and JSONDecodeError
        data = None
    if isinstance(data, dict) and "project_info" in data and "client" in data:
        return "google_services_json", _android_package_names(data)

    try:
        plist = plistlib.loads(content)
    except Exception:  # noqa: BLE001 - untrusted input: expat, plistlib and value errors all mean "not a plist"
        plist = None
    if isinstance(plist, dict) and "GOOGLE_APP_ID" in plist:
        return "google_service_info_plist", [plist.get("BUNDLE_ID")]
    return None


def _quote(items: list[str]) -> str:
    return ", ".join(f"`{i}`" for i in items)


def check_firebase_file(content: bytes, expected: dict[str, str | None]) -> FileCheck:
    """Compare an uploaded file with the identifiers the client has stated.

    `expected` maps checklist ids (android_application_id, ios_bundle_id) to the client's value,
    or None if they haven't given it yet.
    """
    parsed = _parse(content)
    if parsed is None:
        return FileCheck(
            "unrecognised",
            "This doesn't look like a Firebase `google-services.json` or `GoogleService-Info.plist`. "
            "Download the file again from Firebase Console → Project settings → Your apps.",
        )
    kind, raw = parsed
    file, label = FILE_LABEL[kind], ID_LABEL[kind]
    found = _safe_ids(kind, raw)
    if not found:
        return FileCheck(
            "invalid",
            f"`{file}` has no usable {label}. Re-download it from the Firebase app registered "
            f"for this app.",
            kind,
        )

    want = expected.get(EXPECTED_ITEM[kind])
    if not want:
        return FileCheck(
            "unchecked",
            f"`{file}` is for {label} {_quote(found)}. The client hasn't told us their "
            f"{label} yet, so it can't be compared: ask them to confirm it.",
            kind,
        )
    if want in found:
        return FileCheck("match", f"`{file}` matches the client's {label} `{want}`.", kind)

    hint = ""
    if any(f.startswith(want) or want.startswith(f) for f in found):
        hint = " One is a prefix of the other: check for a build-flavor or debug suffix."
    return FileCheck(
        "mismatch",
        f"`{file}` is for {label} {_quote(found)}, but the client's is `{want}`. "
        f"It was probably downloaded for a different app.{hint}",
        kind,
    )
