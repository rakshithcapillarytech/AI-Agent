---
title: Firebase setup shared by every Firebase-mode platform
sources: ["Flutter-Hydra-Integration-Guide pp.1–4, p.10 (Prerequisites, Getting Started, hydra-config.json, Push Notification, Anonymous/Visitor Flow)", "Integration document _ Experience+ pp.14–15 (Hydra WEB SDK Integration Runbook: Firebase Project Setup)", "Integration document _ Experience+ gamification key lists: p.3 (React Native), pp.8–9 and p.12 (Web), pp.27–28 and p.36 (iOS), p.39 and p.50 (Android), pp.53–54 and p.58 (Flutter)"]
owner: TBD
last_verified: null
review_status: draft
---
# Firebase setup (Firebase console, all platforms)

Steps done in the **Firebase console**. Everything in the app's code or build files (config-file placement, Gradle, Xcode, service workers, reading Remote Config) is in the platform file. Values come from Capillary (`_shared/prerequisites.md`). Not using Remote Config? Use direct mode (`<platform>/direct.md`); Flutter and Web direct-mode apps that still use Firebase for push need sections 1, 2 and 4.

> ⚠️ Gap: Firebase console steps are documented only in the Flutter guide and the Web runbook, not for native Android, iOS or React Native. Ask a Capillary engineer before relying on them there.

## 1. Create a Firebase project (skip if one exists)
1. Firebase Console → **Add project** (or **Create a project**).
2. Enter a project name.
3. Choose whether to enable Google Analytics (recommended); if enabled, select or create an Analytics account.
4. Click **Create project**.

## 2. Register each app
**Android / iOS:** register the app in Firebase and download `google-services.json` (Android) and `GoogleService-Info.plist` (iOS). **Don't make the code changes Firebase suggests** while generating these files (Flutter guide).

> ⚠️ Gap: whether the "don't make Firebase's suggested code changes" rule also applies to native Android / iOS apps isn't stated. Ask a Capillary engineer.

**Web:**
1. Project dashboard → Web icon (`</>`).
2. Enter an app nickname. Optionally tick **Also set up Firebase Hosting**.
3. Click **Register app**, then copy the Firebase configuration object.

## 3. Remote Config
**Add a parameter:** Remote Config → **Create configuration** → **Add parameter** → set **Parameter key** and **Default value** → **Save** → **Publish changes**. Always finish with **Publish changes**.

| Platform | How values are stored |
|---|---|
| Android, iOS, React Native, Flutter | One parameter per value, with the exact `hydra_*` names below |
| Web | One parameter (any name, e.g. `hydra_sdk_config`) whose value is a JSON object with camelCase fields. Fields: see the Web platform file. |

### Core keys (Flutter)
| Key | Value | Needed |
|---|---|---|
| `hydra_account_id` | Account Id | Always |
| `hydra_base_url` | Base URL | Always |
| `hydra_ssl_public_key` | SSL public key | Always |
| `hydra_remote_log_level` | 0–5 (0 off, 1 error, 2 warn, 3 info, 4 debug, 5 verbose) | Always |
| `hydra_org_id` | Org Id | Visitor flow only |

**Multi-account (Flutter):** put the default account in the keys above; give each extra account prefixed keys, e.g. `ind_hydra_account_id`, `ind_hydra_base_url`, `ind_hydra_gamification_key`. The app then passes those key names to the SDK (see the platform file).

> ⚠️ Gap: the core keys and multi-account keys are documented only for Flutter. Whether native Android, iOS and React Native read them isn't stated. Ask a Capillary engineer.

### Gamification keys
| Platform | Write key | Region | Base URL | Required (per that platform's doc) |
|---|---|---|---|---|
| Android | `hydra_gamification_key` | `hydra_gamification_region` | `hydra_gamification_base_url` (optional) | Key and region |
| iOS | `hydra_gamification_key` | `hydra_gamification_region` | `hydra_gamification_base_url` (optional) | Key, plus region **or** base URL (base URL wins if set) |
| React Native | `hydra_gamification_key` | `hydra_gamification_region` | `hydra_gamification_base_url` | Key and base URL; also add `hydra_org_id` |
| Flutter | `hydra_gamification_key` | `hydra_gamification_region` | `hydra_gamification_base_url` (optional) | Key and region |
| Web (JSON fields) | `gamificationWriteKey` | `gamificationRegion` (`"us"`, `"me"`, `"in"`) | `gamificationBaseUrl` (optional) | Write key and region |

Gamification stays disabled if a mandatory value is missing.

> ⚠️ Correction: ✅ Use `hydra_gamification_base_url` for the gamification base-URL key on every platform, Flutter included. ❌ Don't use `hydra_gamification_url` (Integration doc, Flutter gamification chapter, pp.53–54). *Pending SME confirmation.*

> ⚠️ Gap: the mandatory rules disagree across platforms: React Native (p.3) requires the base URL; iOS (p.28) requires region or base URL; Android, Flutter and Web require region. Ask a Capillary engineer.

## 4. Web push: VAPID key
Project settings (gear icon) → **Cloud Messaging** tab → **Web configuration** → **Web Push certificates** → **Generate key pair** → copy the key. Where it goes, and the service-worker file from Capillary: see the Web platform file.

## 5. Check Firebase services are enabled
- **Remote Config:** shows your configuration.
- **Cloud Messaging:** shows its dashboard.
- **Realtime Database:** Web only, if the config uses `databaseURL`. **Create Database**, choose region and security rules (test mode for development).

> ⚠️ Gap: APNs key/certificate upload for iOS push isn't documented. Ask a Capillary engineer.
