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
| App signature (SHA256, from the Android app signing report) | React Native, Flutter. Android: see the Gap below |
| Firebase project ID and the project's service account (email and credentials file), for push | Android, iOS, React Native, Flutter when push is used (`_shared/push.md`) |

For Web, Capillary registers the app and sends the values below (`accountId`, `baseURL`, `orgId`, and for gamification `gamificationWriteKey`, `gamificationRegion`, `gamificationBaseUrl` plus the entry-point `hookId`s and loyalty `embedId`s); the Web guides list nothing else the client sends.

> ⚠️ Gap: the native Android guides don't list the app signature as something the client sends, but the KT notes show Capillary registers an **App Signature** for the app and that a mismatch stops the SDK from starting (`Client Credentials Generation Failed … source not found`, 400). Send it for native Android too and confirm with Capillary.

> The Firebase service-account file contains a private key. Send it only through the secure channel the Capillary contact names, never in chat, email or git.

What Capillary does with these details (the MAPP_SDK channel account and the push gateways), and what must match for push to work, is in `_shared/push.md`.

**How registration is requested.** The client's Capillary contact raises a request to Capillary's support (PST) team, who create the MAPP_SDK account. It needs: the **cluster** and **org**, the Android application ID and iOS bundle ID, the Android app signature (SHA256), and the Firebase service-account credentials file. The details must match the app's own configuration exactly (`_shared/troubleshooting.md` › section 1).

## Capillary gives the client
| Item | When |
|---|---|
| Account Id | Always. It is the **Source Account Id** of the client's MAPP_SDK channel account (*Organisation Settings → Omni Channel Settings → Channel Configurations → MAPP_SDK*). |
| Base URL | Always. Specific to the client's Capillary cluster; use the one for the environment you run (UAT or production). |
| SSL Public Key | Mobile only (not Web) |
| Org Id | Web; native direct-mode init (Android, iOS, React Native). Flutter and React Native: only for the visitor flow (`hydra_org_id` in Firebase mode; the `orgId` value in the init in direct mode, React Native passes it in direct mode generally). iOS with gamification passes `orgID` in `HydraConfiguration` (see `ios/*.md`). |
| Gamification Key (write key) | Gamification |
| Gamification Region | Gamification. Values `IN`, `US`, `ME` (Android `GamificationRegion.IN/.US/.ME`); Web examples use lower case (`"us"`, `"me"`, `"in"`). |
| Gamification Base URL | Gamification. **Required together with key and region on Flutter, React Native and Web**; optional on Android; on iOS either region or base URL is enough (see the platform file) |
| Banner / Embedded / Loyalty IDs | Only for those views. Banner / Embedded IDs: Gamification dashboard entry-point settings. Loyalty ID: Capillary team. |

> ⚠️ Gap: Capillary's developer docs (2026) require the Gamification Base URL for Flutter, React Native and Web but treat it as optional for Android and as an alternative to region on iOS. Confirm with a Capillary engineer that this per-platform difference is intended.

### Base URL by cluster
The Base URL is the Hydra endpoint of the cluster the client's org lives on:

| Cluster | Base URL |
|---|---|
| IN / APAC | `https://mapp-incrm.api.capillarytech.com/` |
| SEA | `https://mapp-seacrm.api.capillarytech.com/` |
| EU | `https://mapp-eucrm.api.capillarytech.com/` |
| Asia / SG / APAC2 | `https://mapp-sgcrm.api.capillarytech.com/` |
| North America | `https://mapp-uscrm.api.capillarytech.com/` |

Use the one Capillary confirms for the org.

> ⚠️ Gap: no endpoint is listed for the `ME` region offered in the profile, and how regions map to these clusters isn't stated. Ask a Capillary engineer.

### SSL public key: it expires
The SSL public key pins the cluster endpoint's certificate and **expires about every 9 months**. When it does, the SDK fails with a `Certificate pinning failure` and stops talking to Capillary.
- **Don't hardcode it.** Keep it (with the Account Id and Base URL) in Firebase Remote Config or another remote configuration, so it can be replaced without a new App Store / Play Store release. If it's compiled into the app, an expired key needs a new release.
- **Flutter and React Native** have an `enable_ssl_pinning` flag in `hydra-config.json` (default `true`): the SDK checks the Hydra endpoint's certificate against the SSL public key; `false` turns pinning off.
- When it changes, Capillary gives the new key (Capillary also has a guide for extracting it from the endpoint's certificate). The endpoint certificate's expiry can be checked with any SSL checker, for example `https://www.sslshopper.com/ssl-checker.html`.

## SDK package access
Where the SDKs come from differs by platform, and Capillary's sources disagree in places (Gap below):

| Platform | Source |
|---|---|
| Android (native) | Capillary's private Maven repository `https://github.com/Capillary/hydra-sdk-android-maven`, with GitHub credentials (`github.properties`; `android/*.md`) |
| iOS (native) | `https://github.com/Capillary/hydra-sdk-ios-packages` (Swift Package Manager or CocoaPods; `ios/*.md`) |
| React Native | npm package `@capillarytech/react-native-hydra-lib` from the public npm registry; the Android SDK (`com.capillarytech:hydra-*`) from Maven Central; iOS through CocoaPods or `https://github.com/Capillary/hydra-ios-sdk-spm.git` (Swift Package Manager) (`react-native/*.md`) |
| Flutter | pub.dev packages `capillary_hydra` and `capillary_hydra_platform_interface`; the Android SDK from Maven Central, no extra repository or credentials (`flutter/*.md`) |

**Credentials.** Where credentials are needed, Capillary gives the client a GitHub username and a **Personal Access Token (PAT)** for its package-access account; ask your Capillary contact. The PAT **expires**: after that, installs and builds fail with access denied until Capillary issues a new one. Apps already published aren't affected.

> ⚠️ Gap: an internal Capillary runbook (June 2026) installs React Native from GitHub Packages (`@capillary/react-native-hydra-lib`, a GitHub token) and Flutter from `https://github.com/Capillary/flutter-hydra-lib`; the public developer docs (November 2026) use the public npm registry and pub.dev with no credentials for those, and the native Android docs still use GitHub credentials. Whether React Native on iOS still needs a GitHub token isn't stated. Use the public docs and ask a Capillary engineer if an install is denied.

### Older guides: access per platform
Request access from Capillary's access team.

| Platform | Private repository | Credentials |
|---|---|---|
| Android | `https://github.com/Capillary/hydra-sdk-android-maven` | GitHub username + Personal Access Token with `read:packages` scope |
| iOS | `https://github.com/Capillary/hydra-sdk-ios-packages` | GitHub account added in Xcode, or GitHub username + PAT with access to the repo |

**Tokens stay on the client's machine** (environment variables, a git-ignored `github.properties`, CI secrets). Never share them in chat, email or git.

## Capillary CRM: Account Linking Identifier
For the mobile SDKs, the `customerId` the app sends at sign-in must match the **Account Linking Identifier** configured in Capillary CRM (the Web guides don't state this for `identify()`; ask a Capillary engineer):

*Organisation Settings → Omni Channel Settings → Channel Configurations → MAPP_SDK → Account Linking Identifier*

It can be: `mobile`, `email`, `InTouchUserId`, `externalId` or `FCMToken`.

## Loyalty View: Capillary token
The Loyalty View needs a **Capillary B2B short-lived token**. The app passes it with `setCapToken` after the user logs in, before the Loyalty View is shown.

> ⚠️ Gap: how the client obtains the B2B short-lived token isn't documented. Ask a Capillary engineer.
