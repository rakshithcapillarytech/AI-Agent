---
title: "Push notifications on mobile: how it works, what must match, how to test"
sources: ["PST (Confluence): 'Mapp-SDK Related Issues' (updated 2026-10-09)", "MobileSDK (Confluence, space CAM): 'SDK Integration prerequisites' (2026-06-05) and 'Mobile SDK - PST Guidelines Document' (2026-01-15)", "Engage+ KT Sessions (Confluence, space CAM): 'Configuration steps and overview of SDK to CRM' (updated 2024-10-24)", "Engage+ KT Sessions (Confluence, space CAM): 'FCM Logs Enablement in Firebase Console' (updated 2026-02-17)"]
owner: TBD
last_verified: null
review_status: draft
---
# Push notifications on mobile (Android, iOS, React Native, Flutter)

Applies when the client wants **push** in an Android, iOS, React Native or Flutter app. It explains the server side that the platform files don't, and what to check when a push doesn't arrive. The in-app setup is in the platform file's **Push** section. Push goes through **Firebase Cloud Messaging (FCM)**.

## How a push reaches a device
1. The app, which carries the client's own Firebase config (`google-services.json` / `GoogleService-Info.plist`), gets an **FCM token** from Firebase.
2. When the user signs in, the Hydra SDK registers the user with Capillary. Capillary stores the token on the customer's profile, tied to the **Firebase project** the token came from.
3. When a push campaign runs, Capillary picks the audience, checks which users are reachable, and reads each profile's token.
4. Capillary sends the message to **FCM, using the Firebase project registered for the client's account**. FCM checks the token against that project and, if it matches, delivers it to the app.

Around this: the SDK authenticates with Capillary's Hydra backend and sends device, user and behaviour events to it; the backend creates the customer's MAPP_SDK profile in Capillary's CDP. Capillary's campaigns and journeys send through FCM (which uses APNs for iOS), and delivery receipts (message id, delivery status, device token) come back to Capillary.

**Reachability takes about a day.** A user becomes reachable for push roughly **1 day after they first sign in** in the app. Audience lists created before that need their reachability refreshed after the day has passed. Test campaigns sent immediately after the first sign-in can skip the user for this reason.

**The rule that explains most failures:** the token must belong to the same Firebase project Capillary has registered. If the app uses a different project, the send breaks.

## What must match
| In the app | Registered at Capillary | If they differ |
|---|---|---|
| Firebase project (the app's `google-services.json` / `GoogleService-Info.plist`) | **FCM Project ID** and that project's service account | FCM can't validate the token for the registered project and the send fails. Capillary's outbound message log shows errors such as `Requested entity was not found`. |
| Android app signature (SHA256 of the key the build is signed with) | **App Signature** | The SDK can't get its credentials. Its log shows `Client Credentials Generation Failed` and `{"error":"source not found","status":400}`. |
| Android package name / iOS bundle ID | **Bundle Name**, written as `android:<applicationId>;ios:<bundleId>` | See the Gap below. |
| `customerId` sent at sign-in | **Account Linking Identifier** | The user isn't linked to the right CRM customer (`_shared/prerequisites.md`). |
| Account Id, Base URL and SSL key in the SDK | The account and environment they belong to | Map them to the environment you're running (UAT or production). The Base URL is specific to the client's Capillary cluster. |

A build with a different application or bundle ID (for example a `.dev` or flavor variant) is a different app to Capillary: the SDK sends its own bundle identifier when it authenticates (`_shared/troubleshooting.md` › section 2). Register every ID you build with.

> ⚠️ Gap: the KT notes tie the signature error to the App Signature not matching the app, but don't list which keys count (debug, release, CI, Play App Signing). Check the SHA256 of the **exact build you are running** against the registered one, and ask Capillary to update it if it differs.

## What Capillary sets up after the client sends their details
Capillary's team registers one **MAPP_SDK** channel account (*Organisation Settings → Omni Channel Settings → Channel Configurations → MAPP_SDK*) with:

| Field | Comes from |
|---|---|
| Account Linking Identifier | The identifier the app uses as `customerId` (`mobile`, `email`, …) |
| Android / iOS | Which platforms the app runs on |
| Bundle Name | The Android application ID and/or iOS bundle ID |
| App Signature | The Android signing-report SHA256 |
| FCM Project ID | `project_id` in the Firebase service-account file |
| FCM Email | `client_email` in the Firebase service-account file |
| Source Account Id | Generated automatically. **This is the Account Id the client puts in the SDK.** |
| Valid Till Name | A till in the org (needed by the form); **Enable Mirror** isn't required |
| Deep links | Optional; offered in Engage+ push creatives |

Capillary also sets up the push gateways for Android and iOS (bulk and transactional) from the service-account file, and restarts its messaging services so the change takes effect. Until that is done, push won't send even when the app is correct.

> **Never put the Firebase service-account file in chat, email, a ticket or git.** It contains a private key. Share it only through the secure channel the Capillary contact names.

> ⚠️ Gap: the channel for sharing the service-account file, and how long the gateway setup takes, aren't documented. Ask a Capillary engineer.

**iOS:** the app's APNs certificate must be added to the Firebase project's Cloud Messaging configuration, so FCM can deliver to iOS (Capillary's SDK prerequisites; steps in Capillary's developer docs, `https://docs.capillarytech.com/docs/configure-push-notifications`).

One source account can serve **both Android and iOS** when everything except the bundle ID (FCM Project ID, identifier type, …) is the same: enter both IDs in Bundle Name separated by a semicolon (`android:<applicationId>;ios:<bundleId>`). A brand that already has separate accounts and wants to merge them asks the app developer to make the change, enters both IDs in one account and deprecates the other; subscription status responses don't change.

**Late pushes (campaign TTL).** A push that can't be delivered in real time is pulled when the user next opens the app, as long as it is within the campaign TTL (15 days by default, configurable per organisation, for promotional and transactional messages). After the TTL the message is discarded. A user who receives a notification days later when opening the app is therefore normal, not a bug.

**Apps that own their `FirebaseMessagingService`** (Android) must hand tokens and payloads to the SDK: see the platform file (`passFCMToken` in React Native and Flutter, `FcmConfig(false)` with `passPushToken` / `passPushPayload` in native Android).

## Test the push flow end to end
1. Confirm the registration above is done, and that the SDK in the build uses the right Account Id, Base URL and SSL key for the environment.
2. Install the build on a device (or an emulator if the device build misbehaves). SDK log lines are prefixed `HYDRA CAPILLARY SDK:` and carry a request id.
3. **Sign in with a customer's mobile number** (or the identifier you chose). The FCM token appears in the logs.
4. Check that the token is on the customer's profile (Capillary's Member Care shows it under the device channel for `MAPP_SDK`). The SDK normally registers it at sign-in; if it isn't there, ask the Capillary contact to add it to a test customer through the customer API (device channel, source `MAPP_SDK`, the Account Id).
5. Trigger a push campaign to that customer. The notification should appear on the device.
6. **To tell whether the problem is the app/Firebase or Capillary:** send a test message from the Firebase console (Cloud Messaging) to the same token. If it arrives, the app and Firebase are fine and the fault is in the registration at Capillary (project, service account, gateway). If it doesn't, check the app's Firebase config and permissions first.

## What the SDK receives
The sample request Capillary sends to FCM has only a `data` object (no `notification` object), with these fields:

| Field | Meaning |
|---|---|
| `cuid` | The customer's identifier (for example their mobile number) |
| `accountId` | The Capillary account (Source Account Id) |
| `campaignId`, `variationId` | The campaign and variant that sent it |
| `senderId`, `senderSource` | Sender details; `senderSource` is `capillary-engage` |
| `custom` | A list of key / value pairs from the campaign |
| `body` | JSON with `title`, `message` and a `cta` (`action`, `type` such as `EXTERNAL_URL`) |
| `expandableDetails` | JSON for the expanded notification: `image`, `style` (for example `BIG_TEXT`), `message` and a list of `ctas` (`actionText`, `action`, `type`) |
| `scope` | Message scope; it must be unique |

Apps that handle FCM themselves: **native Android** is documented in `android/firebase.md` (the own-FCM-service steps, including the manifest entry); **React Native and Flutter** pass tokens with `passFCMToken` (`react-native/*.md`, `flutter/*.md`).

> ⚠️ Gap: how the SDK displays these data messages isn't documented, and neither is the `HydraFirebaseMessagingService` manifest entry for React Native and Flutter apps. Ask a Capillary engineer.

## Confirm delivery with FCM reports (BigQuery)
Firebase can export delivery data to BigQuery, which shows whether FCM accepted and delivered each message.

1. **Firebase Console** → choose the project → **Project settings** (gear icon) → **Integrations** → **BigQuery** → **Link**.
2. Enable **Cloud Messaging**, choose the region, and link the apps. Click **View in BigQuery**.
3. In the BigQuery console, select the project's resource, open **Data Transfers**, **Create Transfer**, set the source type to **Firebase FCM** and the data source to `firebase_messaging`. Schedule it.
4. Once it runs, a table appears under `firebase_messaging`. Its `message_id` is the **FCM message id**.

| `event` value | Meaning |
|---|---|
| `MESSAGE_ACCEPTED` | FCM received the message and the request is valid |
| `MESSAGE_DELIVERED` | The message reached the app's FCM SDK on the device |
| `MISSING_REGISTRATIONS` | FCM rejected the request because the registration (token) is missing |

Count messages by event:
```sql
SELECT event, COUNT(*) AS count
FROM `<project>.firebase_messaging.data`
WHERE message_id != ''
  AND TIMESTAMP_TRUNC(_PARTITIONTIME, DAY) >= TIMESTAMP("<start date>")
GROUP BY event
```
Delivered percentage = distinct `message_id` + `instance_id` with `MESSAGE_DELIVERED` (that also have `MESSAGE_ACCEPTED`) divided by those with `MESSAGE_ACCEPTED`.

> ⚠️ Gap: the KT notes' sample queries filter `message_type = 'DISPLAY_NOTIFICATION'`, but Capillary's sample message is a data message. If the counts are empty, remove that filter or check the values in `message_type`. Ask a Capillary engineer.

## Why Capillary skipped a message
When Capillary doesn't send a push to a user, its campaign report records a **skipped reason**:

| Skipped reason | Meaning | What to do |
|---|---|---|
| `Profile Not Found` | The user is reachable through another MAPP_SDK (or WebEngage) profile that isn't tied to this account's Firebase **Project ID** | Check the app's Firebase project and the account's FCM Project ID match (above) |
| `Unsubscribe` | The user is unsubscribed from push | Check the customer's profile (Capillary: *Intouch → MultiProfile → Profile V2*) |
| `Request Entity Not Found` | The FCM token expired | The user logs out and logs in again |
| `NotRegistered` | The token is no longer registered with the SDK | The user needs to register again (sign in on the current build) |
| `HTTP 401` | The Firebase credentials Capillary holds for the project have expired | Send Capillary a renewed Firebase service-account credential (securely) to update |
| `Gateway Not Found` | Capillary's push gateway or onboarding configuration is incomplete | Capillary checks the onboarding configuration and the Firebase service-account email in its UI and backend |

## Common problems
| Symptom | Likely cause | What to check |
|---|---|---|
| Token is on the profile but no push arrives | The app's Firebase project isn't the one registered at Capillary | Compare the project in `google-services.json` / `GoogleService-Info.plist` with Capillary's **FCM Project ID**. Then run the Firebase console test (step 6 above) |
| `Client Credentials Generation Failed … source not found (400)` at SDK start | The App Signature registered at Capillary doesn't match the build's signature | Compare the build's SHA256 with the registered **App Signature**; ask Capillary to update it |
| `Requested entity was not found` in Capillary's message log | The user's FCM token has expired | Ask the user to log out and log in again in the app, so a fresh token is registered |
| No token in the logs | Sign-in not completed, or Firebase isn't set up in the app | Sign in first; check the Firebase config and the platform file's Push section |
| No customer match for the token | `customerId` isn't the CRM Account Linking Identifier | See `_shared/prerequisites.md` |
| Capillary shows the message as processed, FCM accepted it, but the device never shows it | App-side push setup | `google-services.json` has the right package name; **Native Android:** `HydraFirebaseMessagingService` is registered in the app manifest (`android/firebase.md`); **iOS:** the notification delegates are registered in code. Then ask Capillary's Mobile SDK team |
| Low delivery rate, or messages stuck in the SENT state | FCM didn't accept or deliver them, the SSL key expired, or the registration doesn't match the app | Check FCM delivery reports (above), the SSL key expiry (`_shared/prerequisites.md`) and section 1 of `_shared/troubleshooting.md`, including the signature |
| Capillary's gateway couldn't process the message | Capillary-side | Capillary's backend team checks it |
| Message processed but the user isn't reached | The user isn't reachable on the device channel, or wasn't in the audience | Capillary checks the customer's profile (Member Care) |
| Delivery report shows `MISSING_REGISTRATIONS` | FCM had no valid registration for the token | Re-register by signing in again on the current build |

> ⚠️ Gap: after the app moves to a **different Firebase project**, tokens already stored belong to the old one. The data flow implies they stop working until users register again from the new build, but the KT notes don't say so directly. Ask a Capillary engineer.
