---
platform: android            # flutter | react-native | ios | android | web
config_mode: direct          # firebase | direct
sdk_package: com.capillary:hydra-core
sdk_version: 0.0.0           # code blocks use {{sdk_version}}, so a version bump is this one line
modules_covered: [core]      # core, push, inapp, inbox_api, inbox_ui, visitor, gamification, multi_account
modules_missing: []          # documented gaps: the agent escalates instead of guessing
sources: ["<source doc> pp.X–Y"]
owner: <SME name>
last_verified: YYYY-MM-DD
review_status: draft         # draft → verified once an SME has checked it
---
# <Platform> (<with Firebase | without Firebase>)

## Coverage
What this file covers and what it doesn't, for each module. Be explicit about gaps.

## Requirements
Minimum OS and tooling versions (minSdk / iOS deployment target / Flutter / RN / Node / Xcode / Gradle …).

## Prerequisites
Items specific to this platform and mode. Link to `_shared/prerequisites.md` for the common exchange
(bundle ID / applicationId / SHA256 ↔ accountId / baseURL / SSL key / orgId / gamification values).

## Steps
Numbered and in order. Each step says what to do, where, and why. For code blocks:
- use placeholders for client- and Capillary-specific values: `{{account_id}}`, `{{base_url}}`,
  `{{ssl_public_key}}`, `{{org_id}}`, `{{application_id}}`, `{{bundle_id}}`,
  `{{gamification_key}}`, `{{gamification_region}}`, `{{gamification_base_url}}`, `{{sdk_version}}`
- add `file=<path>` to the fence info when the block is a whole file or a named snippet, e.g. an
  opening fence of ```` ```kotlin file=app/src/main/java/<pkg>/MyApplication.kt ````

1. Install the SDK
2. Initialise
3. …

## Modules
### Push
### In-App
### Inbox
### Visitor
### Gamification

## Verification
How to confirm each step or module works: expected log lines, callbacks (e.g. the SDK initialisation
result), and dashboard checks.

## Known Issues
Symptom → cause → fix. Promoted from `issues/` once a problem recurs.

## API Reference
Public methods and config keys for this platform and mode.

<!-- Corrections to the source docs go inline as callouts:
> ⚠️ Source doc says X; confirmed Y — <SME>, <date>
and are logged in CHANGELOG.md. -->
