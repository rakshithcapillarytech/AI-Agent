---
title: Firebase setup shared by every Firebase-mode platform
sources: ["Flutter-Hydra-Integration-Guide pp.1–4, p.10 (Prerequisites, Getting Started, hydra-config.json, Push Notification, Anonymous/Visitor Flow)", "Integration document _ Experience+ pp.14–15 (Hydra WEB SDK Integration Runbook: Firebase Project Setup)", "Integration document _ Experience+ gamification key lists: p.3 (React Native), pp.8–9 and p.12 (Web), pp.27–28 and p.36 (iOS), p.39 and p.50 (Android), pp.53–54 and p.58 (Flutter)"]
owner: TBD
last_verified: null
review_status: draft
---
# Firebase setup (all platforms, Firebase mode)

Use this file only when the app uses Firebase (`config_mode: firebase`). It covers the work done in the **Firebase console**: creating the project, registering apps, Remote Config parameters and the services to enable. Anything done in the app's code or build files is platform-specific (config-file placement, Gradle plugin lines, Xcode capabilities, service workers, how the SDK reads Remote Config). For those, **see the platform file** (`<platform>/firebase.md`).

The values that go into Remote Config come from Capillary. See `_shared/prerequisites.md` for that exchange.

Not using Firebase Remote Config? The Flutter guide (p.2) says the values can instead be fetched from another CMS, or passed to the SDK directly. That is direct mode: see `<platform>/direct.md`.

> ⚠️ Gap: no single source documents Firebase setup for every platform. This file combines the Flutter guide and the Web runbook. Native Android, iOS and React Native have no Firebase setup section of their own in the sources. Ask a Capillary engineer before relying on a step for a platform that isn't named next to it.

## 1. Create a Firebase project
*Source: Web runbook (Integration doc p.14). Skip this if the client already has a Firebase project.*

1. Go to the Firebase Console.
2. Click **Add project** (or **Create a project**).
3. Enter a project name.
4. Choose whether to enable Google Analytics (the runbook recommends it). If you enable it, select or create a Google Analytics account.
5. Click **Create project**.

## 2. Register each app with Firebase
**Android and iOS** (*source: Flutter guide p.4*):
1. Register the app with Firebase. The Flutter guide points to Firebase's own instructions for this.
2. Download the config files: `google-services.json` for Android and `GoogleService-Info.plist` for iOS.
3. Where each file goes in the project, and any build changes, is platform-specific. See the platform file.

> ⚠️ **Don't make the code changes Firebase suggests while generating these files.** *Source: Flutter guide p.4.* This warning is stated only in the Flutter guide. Whether it also applies to native Android and iOS apps isn't stated: ask a Capillary engineer. The only Android hint in the sources says push needs "Firebase dependencies and google-services.json" (Integration doc p.112; see `android/firebase.md`).

> ⚠️ Gap: the sources give no console click-path for registering an Android or iOS app (the fields to fill in, such as the package name or bundle ID). Ask a Capillary engineer.

**Web** (*source: Web runbook p.14*):
1. In the Firebase project dashboard, click the Web icon (`</>`) to add a web app.
2. Enter an app nickname.
3. Optionally, tick **Also set up Firebase Hosting** if you plan to use Firebase Hosting.
4. Click **Register app**.
5. Copy the Firebase configuration object. How the Web SDK uses it: see the Web platform file.

## 3. Set up Remote Config

### How to add a parameter
*Source: Web runbook p.15.*
1. In the Firebase project, go to **Remote Config** in the left sidebar.
2. Click **Create configuration**.
3. Click **Add parameter**.
4. Set **Parameter key** to the key name (see below).
5. Set **Default value** to the value from Capillary.
6. Click **Save**, then **Publish changes**.

> ⚠️ Always finish with **Publish changes**. The Web gamification checklist (Integration doc p.12) lists "Publish the updated Remote Config" as a required step.

### Two ways the sources structure Remote Config
| Style | Used by | What you add |
|---|---|---|
| One parameter per value, with fixed `hydra_*` names | Flutter (core and gamification keys, Flutter guide p.1). Android, iOS and React Native (gamification keys, Integration doc). | One parameter per key, using the exact names below |
| One parameter whose value is a JSON object | Web (runbook p.15, gamification p.8) | One parameter with a name of your choice (e.g. `hydra_sdk_config`). Its value is a JSON object with camelCase fields. Field list and SDK wiring: see the Web platform file. |

### Core keys
*Source: Flutter guide p.1 (log-level scale: pp.3, 10). The Flutter guide says to add them "with these exact names".*

| Remote Config key | Value from Capillary | When it's needed |
|---|---|---|
| `hydra_account_id` | Account Id | Mandatory |
| `hydra_base_url` | Base URL (end point) | Mandatory |
| `hydra_ssl_public_key` | SSL public key | Mandatory |
| `hydra_remote_log_level` | Remote log level, 0–5 (0 off, 1 error, 2 warn, 3 info, 4 debug, 5 verbose) | Mandatory |
| `hydra_org_id` | Org Id | Only for the Anonymous / Visitor Flow (Flutter guide pp.1, 10) |
| `hydra_gamification_*` | Gamification values | Only for gamification. See the per-platform table below. |

In the Flutter plugin, the SDK reads these keys from Firebase Remote Config by default (Flutter guide p.1). How each other platform reads Remote Config: see the platform file.

> ⚠️ Gap: these core key names come **only from the Flutter guide**. The Integration document's Android, iOS and React Native sections list only gamification keys (React Native also lists `hydra_org_id`). They don't say whether the native SDKs read `hydra_account_id`, `hydra_base_url`, `hydra_ssl_public_key` and `hydra_remote_log_level`. Ask a Capillary engineer.

### Several Hydra accounts in one app (prefixed keys)
*Source: Flutter guide p.1.*
- Put the most-default account's values in the standard keys above.
- For each additional Hydra account, define new keys with a prefix. The guide's example for an India account:
  - `ind_hydra_account_id`, `ind_hydra_base_url`, `ind_hydra_ssl_public_key`, `ind_hydra_remote_log_level`
  - and, if applicable, `ind_hydra_org_id`, `ind_hydra_gamification_key`, `ind_hydra_gamification_region`, `ind_hydra_gamification_base_url`
- The app then tells the SDK which key names to use. That API is platform-specific: see the platform file.

> ⚠️ Gap: multi-account setup is documented only in the Flutter guide. Ask a Capillary engineer for other platforms.

### Gamification keys per platform
The sources name the gamification keys differently per platform, and disagree on which ones are mandatory. Use the row for the client's platform, exactly as written.

| Platform (source) | Write key | Region | Base URL | Also listed | What the source says is mandatory |
|---|---|---|---|---|---|
| Android (Integration doc p.39; checklist p.50) | `hydra_gamification_key` | `hydra_gamification_region` | `hydra_gamification_base_url` | — | The checklist lists key and region as Required, and base URL as "(Optional)". No explicit mandatory statement. |
| iOS (Integration doc pp.27–28; checklist p.36) | `hydra_gamification_key` | `hydra_gamification_region` | `hydra_gamification_base_url` | — | "`hydra_gamification_key` is mandatory. Either `hydra_gamification_region` or `hydra_gamification_base_url` must be provided." If the base URL is set it's used; otherwise the URL is resolved from the region. The checklist marks the base URL "(Optional)". |
| React Native (Integration doc p.3) | `hydra_gamification_key` | `hydra_gamification_region` | `hydra_gamification_base_url` | `hydra_org_id` | "Key and url values are mandatory. HydraGamification will remain disabled if either value is missing." |
| Flutter (Integration doc pp.53–54; checklist p.58) | `hydra_gamification_key` | `hydra_gamification_region` | **`hydra_gamification_url`** | — | "`hydra_gamification_region` and `hydra_gamification_key` are mandatory. `hydra_gamification_url` is optional." |
| Flutter (Flutter guide p.1) | `hydra_gamification_key` | `hydra_gamification_region` | `hydra_gamification_base_url` | — | Only says "if you also want to use Gamification, add these 3 parameters". |
| Web (Integration doc pp.8–9; checklist p.12) | `gamificationWriteKey` (JSON field) | `gamificationRegion` (JSON field; examples `"us"`, `"me"`, `"in"`) | `gamificationBaseUrl` (JSON field, optional) | Fields go inside the existing SDK config JSON | "Both Remote Config values are mandatory" (write key and region); the base URL is "an optional param". |

The Android, iOS and Flutter sections of the Integration document print the base-URL key followed by empty parentheses, e.g. `hydra_gamification_base_url ()`. Their checklists mark it optional.

> ⚠️ Source doc correction: the Integration document's Flutter gamification section (pp.53–54) names the base-URL key `hydra_gamification_url` vs `hydra_gamification_base_url` in the Flutter guide (p.1, including its multi-account example `ind_hydra_gamification_base_url`) and in the Android, iOS and React Native sections. Don't guess the name: ask a Capillary engineer which key the client's `capillary_hydra` version reads. *Pending SME confirmation.*

> ⚠️ Source doc correction: the mandatory rules disagree. React Native (p.3) says the key **and the URL** are mandatory vs Android, Flutter and Web, which make the base URL optional and require key and region, and iOS (p.28), which requires the key plus **either** region **or** base URL. *Pending SME confirmation.*

Region values: Capillary gives `IN`, `US` or `ME` (see `_shared/prerequisites.md`). The Web examples use lower case (`"us"`). Whether case matters is platform-specific: see the platform file.

## 4. Cloud Messaging (push)
- **Android and iOS:** push uses the config files from section 2. Everything else is platform-specific (build setup, capabilities, notification service extension, icons): see the platform file.
- **Web: generate a VAPID key** (*source: Web runbook p.15*):
  1. In the Firebase project, go to **Project settings** (the gear icon in the sidebar).
  2. Open the **Cloud Messaging** tab.
  3. Scroll down to **Web configuration**.
  4. Under **Web Push certificates**, click **Generate key pair**.
  5. Copy the generated VAPID key.

  Where the key goes, and the service-worker file that Web push also needs (obtained from the Capillary team): see the Web platform file.

## 5. Enable the required Firebase services
*Source: Web runbook p.15. Check that these are enabled in the Firebase project:*

| Service | Check |
|---|---|
| Remote Config | Remote Config shows your configuration |
| Cloud Messaging | Cloud Messaging shows its dashboard |
| Realtime Database | Only if the Web Firebase config uses `databaseURL`. Go to Realtime Database → **Create Database**, then choose the region and security rules. The runbook says to start in test mode for development. |

> ⚠️ Gap: the sources don't say which Firebase services native Android, iOS, React Native or Flutter apps need beyond Remote Config and Cloud Messaging. They also give no APNs key or certificate upload steps for iOS push. Ask a Capillary engineer.

## Checklist
- [ ] Firebase project created (section 1)
- [ ] Each app registered. `google-services.json` / `GoogleService-Info.plist` downloaded, or the Web config object copied (section 2).
- [ ] Remote Config parameters added with the exact key names for the client's platform (section 3)
- [ ] **Publish changes** clicked in Remote Config
- [ ] Web only: VAPID key generated (section 4)
- [ ] Remote Config and Cloud Messaging enabled (section 5)
- [ ] Platform-specific steps completed: see the platform file
