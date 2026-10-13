---
title: Hydra SDK (Experience+) overview
sources: ["Integration document _ Experience+", "Flutter-Hydra-Integration-Guide"]
owner: TBD
last_verified: null
review_status: draft
---
# Hydra SDK (Experience+): overview

The Hydra SDK is Capillary's client SDK, sold as **Experience+**. It connects a brand's apps and websites to Capillary for user identification, behavioural event tracking, messaging and gamification.

## Platforms
Android (native), iOS (native), React Native, Flutter and Web. Each one has its own knowledge file per config mode, for example `android/direct.md`.

## Config modes
| Mode | Meaning |
|---|---|
| `firebase` | The app uses Firebase. The SDK reads its settings (account ID, base URL, keys …) from **Firebase Remote Config**, and push notifications go through Firebase Cloud Messaging. |
| `direct` | The app doesn't use Firebase. Settings are passed straight into the SDK's init call. Push notifications are **not available** in this mode on native Android. |

## Modules
| Module | What it does |
|---|---|
| Core | Identify users (sign-in / sign-out) and track custom events |
| Push | Push notifications (Firebase mode) |
| In-App | In-app messages |
| Inbox API / Inbox UI | A stored notification inbox, and a ready-made notification-centre UI |
| Visitor flow | Anonymous users before sign-in |
| Gamification | Automatic campaigns (Floating Button, Popup, Bottom Sheet), plus optional Banner, Embed and Loyalty views |
| Multi-account | Several Hydra accounts in one app |

Which modules are documented for each platform and mode is listed in that file's **Coverage** section.

## Environments and regions
- **UAT / POC** uses the beta SDK builds named in each platform file. Production versions come from Capillary.
- **Gamification region:** `IN`, `US` or `ME`.
