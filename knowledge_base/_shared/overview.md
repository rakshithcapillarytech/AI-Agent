---
title: Hydra SDK (Experience+) overview
sources: ["Integration document _ Experience+", "Flutter-Hydra-Integration-Guide"]
owner: TBD
last_verified: null
review_status: draft
---
# Hydra SDK (Experience+): overview

The Hydra SDK (Experience+) is Capillary's client SDK. It connects a brand's apps and websites to Capillary for user identification, event tracking, push / in-app / inbox messaging and gamification.

## Platforms
Android (native), iOS (native), React Native, Flutter and Web. Each has one knowledge file per config mode, e.g. `android/direct.md`.

## Config modes
| Mode | Meaning |
|---|---|
| `firebase` | The SDK reads its settings (Account Id, Base URL, keys …) from **Firebase Remote Config**. |
| `direct` | The settings are passed straight into the SDK's init call instead of Remote Config. |

Push uses Firebase Cloud Messaging. On native Android, push is **not available** in direct mode. Flutter and Web direct mode can still use Firebase for push: see the platform file.

## Modules
| Module | What it does |
|---|---|
| Core | Identify users (sign-in / sign-out) and track custom events |
| Push | Push notifications |
| In-App | In-app messages |
| Inbox API / Inbox UI | A stored notification inbox, and a ready-made notification-centre UI |
| Visitor flow | Anonymous users before sign-in |
| Gamification | Automatic campaigns (Floating Button, Popup, Bottom Sheet), plus optional Banner, Embedded and Loyalty views |
| Multi-account | Several Hydra accounts in one app |

Which modules are documented for a platform and mode is listed in that file's **Coverage** section.

## Versions
UAT / POC uses the beta SDK builds named in each platform file.

> ⚠️ Gap: production SDK versions aren't documented. Ask a Capillary engineer.
