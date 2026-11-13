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
| `firebase` | The SDK's settings come from **Firebase Remote Config**. Which values depends on the platform: Flutter and React Native read the core values (Account Id, Base URL, SSL key, log level) and the gamification keys; on Android and iOS the documented Remote Config keys are the gamification ones (see the platform file). |
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

## How an integration is set up (order)
1. **Firebase and the push gateway:** the client's mobile app team sets up Firebase; Capillary's team configures the gateway (`_shared/push.md`).
2. **Source account:** the client's Capillary contact (CSM or project manager) configures the MAPP_SDK source account in Capillary CRM (`_shared/prerequisites.md`).
3. Then in the app: install the SDK, initialise it, sign users in, then push, in-app, inbox and gamification, as the platform file describes.

Behavioural events must exist in Capillary before the app sends them (*Organisation settings → Master Data Management → Data Model → Behavioural events*), and they only count after a sign-in or sign-up.

## Versions
UAT / POC uses the beta SDK builds where a platform file names one; most platforms install the latest release.

> ⚠️ Gap: production SDK versions aren't documented. Ask a Capillary engineer.
