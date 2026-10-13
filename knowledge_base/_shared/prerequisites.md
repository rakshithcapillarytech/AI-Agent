---
title: Prerequisites shared by every platform
sources: ["Integration document _ Experience+", "Flutter-Hydra-Integration-Guide"]
owner: TBD
last_verified: null
review_status: draft
---
# Prerequisites (all platforms)

Before writing any code, the client and Capillary exchange the values below. Each platform file's **Prerequisites** section lists exactly which ones apply to it.

## The client gives Capillary
| Item | Needed for |
|---|---|
| Android application ID (package name) | Android, React Native, Flutter |
| iOS bundle ID | iOS, React Native, Flutter |
| App signature (SHA256, from the Android signing report) | React Native and Flutter guides |

Capillary's apps team uses these to register the app.

## Capillary gives the client
| Item | Notes |
|---|---|
| Account Id | Always |
| Base URL | Always |
| SSL Public Key | Mobile platforms only (not Web) |
| Org Id | Required on Web and passed into the native direct-mode init (Android, iOS, React Native). Optional in Flutter, where only the visitor flow uses it. The platform file says which applies. |
| Gamification Key (write key) | Only if using gamification |
| Gamification Region | Only if using gamification: `IN`, `US` or `ME`. Native SDKs use these uppercase forms (e.g. Android `GamificationRegion.IN`); the Web docs write them lowercase (`in`, `us`, `me`). Follow the platform file. |
| Gamification Base URL | Optional |
| Banner / Embed / Loyalty entry-point IDs | Only if using those gamification views; configured in the gamification dashboard |

## Access to private SDK repositories (native apps in direct mode)
| Platform | Repository | Credentials |
|---|---|---|
| Android | `https://github.com/Capillary/hydra-sdk-android-maven` | GitHub username + Personal Access Token with `read:packages` |
| iOS | `https://github.com/Capillary/hydra-sdk-ios-packages` | GitHub account in Xcode, or username + PAT |

Request access from Capillary's access team. **Tokens stay on the client's machine.** Never share them in chat.

## Capillary CRM: Account Linking Identifier
The `customerId` the app sends at sign-in must match the **Account Linking Identifier** configured in Capillary CRM. The setting is at:

*Organisation Settings → Omni Channel Settings → Channel Configurations → MAPP_SDK → Account Linking Identifier*

Allowed values: mobile, email, InTouchUserId, externalId, FCMToken.

## Loyalty View
To use the Loyalty View, the client's backend must provide a **Capillary B2B short-lived token** after login. The app passes it to the SDK with `setCapToken` before the Loyalty View is shown.
