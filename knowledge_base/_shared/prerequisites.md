---
title: Prerequisites shared by every platform
sources: ["Integration document _ Experience+", "Flutter-Hydra-Integration-Guide"]
owner: TBD
last_verified: null
review_status: draft
---
# Prerequisites (all platforms)

Exchanged before any code is written. The platform file's **Prerequisites** section says which apply.

## The client gives Capillary (to register the app)
| Item | Platforms |
|---|---|
| Android application ID (package name) | Android, React Native, Flutter |
| iOS bundle ID | iOS, React Native, Flutter |
| App signature (SHA256, from the Android app signing report) | React Native, Flutter |

The Web guides list nothing the client provides; Capillary registers the app and sends the values below.

## Capillary gives the client
| Item | When |
|---|---|
| Account Id | Always |
| Base URL | Always |
| SSL Public Key | Mobile only (not Web) |
| Org Id | Web; native direct-mode init (Android, iOS, React Native). Flutter: only for the visitor flow. |
| Gamification Key (write key) | Gamification |
| Gamification Region | Gamification. Values `IN`, `US`, `ME` (Android `GamificationRegion.IN/.US/.ME`); Web examples use lower case (`"us"`, `"me"`, `"in"`). |
| Gamification Base URL | Gamification; optional on most platforms (see the platform file) |
| Banner / Embedded / Loyalty IDs | Only for those views. Banner / Embedded IDs: Gamification dashboard entry-point settings. Loyalty ID: Capillary team. |

> ⚠️ Gap: the docs disagree on whether the Gamification Base URL is optional (required in the React Native gamification guide p.3 and the Web direct config reference p.69). Ask a Capillary engineer.

## SDK repository access (native direct mode)
Request access from Capillary's access team.

| Platform | Private repository | Credentials |
|---|---|---|
| Android | `https://github.com/Capillary/hydra-sdk-android-maven` | GitHub username + Personal Access Token with `read:packages` scope |
| iOS | `https://github.com/Capillary/hydra-sdk-ios-packages` | GitHub account added in Xcode, or GitHub username + PAT with access to the repo |

**Tokens stay on the client's machine.** Never share them in chat.

## Capillary CRM: Account Linking Identifier
The `customerId` the app sends at sign-in must match the **Account Linking Identifier** configured in Capillary CRM:

*Organisation Settings → Omni Channel Settings → Channel Configurations → MAPP_SDK → Account Linking Identifier*

It can be: `mobile`, `email`, `InTouchUserId`, `externalId` or `FCMToken`.

## Loyalty View: Capillary token
The Loyalty View needs a **Capillary B2B short-lived token**. The app passes it with `setCapToken` after the user logs in, before the Loyalty View is shown.

> ⚠️ Gap: how the client obtains the B2B short-lived token isn't documented. Ask a Capillary engineer.
