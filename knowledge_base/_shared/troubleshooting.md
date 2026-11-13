---
title: "Troubleshooting on every platform: what to check before asking Capillary"
sources: ["PST (Confluence): 'Mapp-SDK Related Issues' (updated 2026-10-09)", "MobileSDK (Confluence, space CAM): 'Mobile SDK - PST Guidelines Document' (updated 2026-01-15)", "'Hydra SDK - Authentication flow with Hydra BE' (2025-10-08)", "'Debugging using Remote logs on Grafana' (2025-04-22)", "'SDK Integration prerequisites' (2026-06-05)", "'Hydra API endPoint and SSL Key for various clusters' (2026-09-18)"]
owner: TBD
last_verified: null
review_status: draft
---
# Troubleshooting (all platforms)

These checks come from the playbook Capillary's support team uses (written for the **mobile** SDKs: Android, iOS, React Native and Flutter; for **Web**, whose init errors log `Failed to initialize SDK:` and which has no app signature or GitHub package token, use the Web file's Known Issues and Verification) before involving the Mobile SDK team. Work through the ones that fit the symptom; most problems are a mismatch between the app and Capillary's registration, an expired key or token, or push setup. Push-specific checks are in `_shared/push.md`.

## 1. The app and Capillary's registration must match
Capillary's MAPP_SDK account must hold exactly what the app uses. Check these first for almost any problem:

| In the app | At Capillary (MAPP_SDK account) |
|---|---|
| Account Id passed to the SDK | **Source Account Id** |
| Android application ID / iOS bundle ID of the build you're running | **Bundle Name** |
| SHA256 of the key the Android build is signed with | **App Signature** |
| Firebase project in `google-services.json` / `GoogleService-Info.plist` | **FCM Project ID** |
| Base URL and SSL key | The cluster the org lives on (`_shared/prerequisites.md`) |

## 2. The SDK can't start or authenticate
How the SDK authenticates: on first start it requests **client credentials** from Capillary using the **Account Id** and the app's **bundle identifier** (which the SDK reads itself), plus the **app signature on Android** (not sent on iOS). It then uses those credentials to get short-lived access tokens for every call.

| Symptom | Cause | Fix |
|---|---|---|
| SDK log `Client Credentials Generation Failed` with `{"error":"source not found","status":400}` | Documented cause: the Android **app signature** registered at Capillary doesn't match the build. The SDK's authentication request also carries the Account Id and the bundle identifier, so a mismatch there is a likely cause too, but Capillary's notes only confirm the signature case | Compare all three with section 1; ask Capillary to correct the registration. A build variant with a different application or bundle ID (for example a `.dev` suffix) is a different app to Capillary |
| Auth calls fail with **400** | Invalid request payload | Usually the same mismatch; collect the SDK log |
| Auth calls fail with **401** | Wrong credentials | Check the Account Id and the environment (UAT vs production) |
| `Certificate pinning failure`, or the SDK stops connecting after months of working | The SSL public key expired (about every 9 months) or belongs to another cluster | Get the current key from Capillary and update it (`_shared/prerequisites.md` › SSL public key) |

**Sign-in or start-up problems: check these five against Capillary's configuration** — the bundle ID, the Firebase project ID, the SSL key, the Base URL the app actually uses (for example the value in Firebase Remote Config), and the Android app signature. Capillary stores the signature as `SHA256 - ` followed by the 64-character hex fingerprint without colons (for example `SHA256 - C9F2936D37CF7B97FF3A474D0F24F0866B78D6D4217BBEB6877739603BBA968D`); the signing report prints the same value as colon-separated pairs. If the configuration matches, Capillary can check whether the SDK's calls reach its backend.

SDK log lines are prefixed `HYDRA CAPILLARY SDK:`.

## 3. The project can't download the SDK
| Symptom | Check |
|---|---|
| Access denied / 401 when fetching Capillary's private packages | The GitHub token has expired or has no access. Ask your Capillary contact for a new token and replace it where it's stored. An expired token doesn't affect apps already in the App Store or Play Store |
| Android build can't resolve the SDK | `github.properties` exists in the project root (next to `settings.gradle`) and is git-ignored; its `token=` line holds a classic token starting `ghp_`; CI generates the file from secrets |
| React Native or Flutter install fails | Check the package name (`@capillarytech/react-native-hydra-lib` from the public npm registry; `capillary_hydra` and `capillary_hydra_platform_interface` from pub.dev). If you still use the older GitHub Packages setup, `.npmrc` / `.yarnrc.yml` must point the `@capillary` scope at GitHub Packages and `HYDRA_GITHUB_PAT` must be set (`react-native/*.md`, `_shared/prerequisites.md`) |

## 4. Let Capillary see the SDK's logs in production
The SDK can send its own logs to Capillary's backend, where Capillary can trace end-to-end failures in production. It's **off by default** and is turned on per app with a **remote log level**. The setting and its scale differ by platform: **React Native and Flutter** use 0–5 (0 Off, 1 Error, 2 Warn, 3 Info, 4 Debug, 5 Verbose) through `hydra_remote_log_level` in Firebase Remote Config or the initialiser's remote level; **Android** uses `.remoteDebugLevel(LogType…)` with OFF(-1), INFO(0), DEBUG(1); **iOS** uses `updateRemoteLogLevel(level:)` with `error`, `warning`, `info`, `debug`, `none` (default `none`). Details are in the platform file. If an issue only happens in production, raise the remote level (through Remote Config where the platform reads it, so no release is needed) and ask Capillary to check the remote logs.

## 5. Ask Capillary for a test request or a walkthrough
After a fresh integration, Capillary's team can share a test request to check the setup end to end, and a recording of a full end-to-end test from the platform. Ask your Capillary contact.

## 6. What to send when you escalate
Escalate only after the checks above. Include:
- a short summary of the problem and what you expected,
- the platform (Android, iOS, React Native, Flutter or Web) and the **Hydra SDK version**,
- the exact error and the SDK logs (lines prefixed `HYDRA CAPILLARY SDK:`), plus screenshots,
- what you have already checked and tried.

For **delivery problems** (low delivery rate, messages stuck as sent), also include: the app stack (native, React Native, Flutter), whether it's Android or iOS, the SSL key and its expiry, the account configuration (bundle ID, Firebase project ID, Android app signature) and the relevant Firebase configuration.

> ⚠️ Gap: changing a user's identifiers later (customer id, phone number, name) through Capillary's platform or APIs is a known source of problems, but the guidance isn't in the knowledge base. Ask a Capillary engineer before doing it.

Capillary's public developer documentation for the SDKs: `https://docs.capillarytech.com/docs/sdks`.
