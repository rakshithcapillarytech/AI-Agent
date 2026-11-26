---
updatedAt: 2026-11-12T06:11:18.000Z
agentTools:
  projectIndex: https://docs.capillarytech.com/llms.txt
---

# Flutter Setup Overview

<a id="flutter-implementation"></a>

# Flutter Implementation

1. Before using any APIs from `capillary_hydra`, make sure the Hydra SDK has initialized successfully. Implement a [HydraNativeEventHandler](https://docs.capillarytech.com/docs/flutter-sdk-api-reference#hydranativeeventhandler-class) and register it:

   ```dart
   HydraNativeEvents.addEventHandler(handler);
   ```

   You'll receive the initialization result via:

   ```dart
   void onHydraSdkInitializationResult({required bool success, String? error})
   ```

2. If you have a single-Hydra account setup, you don't have to do anything. If you use more than one Hydra account, set the account with [setHydraAccountConfig](https://docs.capillarytech.com/docs/flutter-sdk-api-reference#4-set-hydra-account-configuration-multi-account-setup) or [setFirebaseRemoteConfigKeys](https://docs.capillarytech.com/docs/flutter-sdk-api-reference#5-set-firebase-remote-config-keys-multi-account-setup) **before** calling [Hydra.identify](https://docs.capillarytech.com/docs/flutter-sdk-api-reference#1-identify) (see [Multi-Hydra account setup](https://docs.capillarytech.com/docs/flutter-sdk-advanced-setup#multi-hydra-account-setup)).

3. Use [Hydra.identify](https://docs.capillarytech.com/docs/flutter-sdk-api-reference#1-identify) to register/identify the user — pass a [HydraUserDetails](https://docs.capillarytech.com/docs/flutter-sdk-api-reference#hydrauserdetails) with a required `customerId`, which must match how it's configured on the Capillary CRM dashboard. Use [Hydra.track](https://docs.capillarytech.com/docs/flutter-sdk-api-reference#2-track) to report custom user events, and [Hydra.reset](https://docs.capillarytech.com/docs/flutter-sdk-api-reference#3-reset) to reset/sign out the current user. `HydraCore` also has static functions for [updateUser](https://docs.capillarytech.com/docs/flutter-sdk-api-reference#1-update-user), [updateGeoConfig](https://docs.capillarytech.com/docs/flutter-sdk-api-reference#2-update-geo-config), and [updatePushPreferences](https://docs.capillarytech.com/docs/flutter-sdk-api-reference#3-update-user-push-preferences).

4. Console log level is set via `console_log_level` in `hydra-config.json` (0–5). Remote log level is set separately via `hydra_remote_log_level` in Firebase Remote Config (same 0–5 scale), as covered in [Getting Started](https://docs.capillarytech.com/docs/flutter-sdk-getting-started#getting-started).

<a id="anonymous--visitor-flow"></a>

## Anonymous / Visitor Flow

The SDK supports an anonymous "visitor" flow. A user can move through states: `none` → `visitor` (anonymous) → `merged`/`legacyRegistered` (identified) → `signedOut`. This flow requires the Org Id mentioned in [Prerequisites](https://docs.capillarytech.com/docs/flutter-sdk-getting-started#prerequisites), configured the same way as Account Id/Base Url/SSL public key (via Firebase Remote Config key `hydra_org_id`, or passed directly — see [Other initializers](https://docs.capillarytech.com/docs/flutter-sdk-advanced-setup#other-initializers) and [HydraAccountConfig](https://docs.capillarytech.com/docs/flutter-sdk-api-reference#hydraaccountconfig)/[HydraFirebaseRemoteConfigKeys](https://docs.capillarytech.com/docs/flutter-sdk-api-reference#hydrafirebaseremoteconfigkeys) for the Dart-side equivalents).

1. Use [Hydra.isVisitorFlowEnabled()](https://docs.capillarytech.com/docs/flutter-sdk-api-reference#6-is-visitor-flow-enabled) to check whether the visitor flow is enabled for your account.
2. Use [Hydra.getCurrentUserState()](https://docs.capillarytech.com/docs/flutter-sdk-api-reference#4-get-current-user-state) to get the current [UserState](https://docs.capillarytech.com/docs/flutter-sdk-api-reference#userstate).
3. Use [Hydra.getVisitorDetails()](https://docs.capillarytech.com/docs/flutter-sdk-api-reference#5-get-visitor-details) to get the current [HydraVisitorInfo](https://docs.capillarytech.com/docs/flutter-sdk-api-reference#hydravisitorinfo) (`visitorId`).
4. Subscribe to visitor-flow lifecycle events on your [HydraNativeEventHandler](https://docs.capillarytech.com/docs/flutter-sdk-api-reference#hydranativeeventhandler-class): `onConfigFetched`, `onLegacyFlowReady`, `onVisitorSessionReady`, and `onUserStateChanged`.

[Hydra.identify](https://docs.capillarytech.com/docs/flutter-sdk-api-reference#1-identify)/[track](https://docs.capillarytech.com/docs/flutter-sdk-api-reference#2-track)/[reset](https://docs.capillarytech.com/docs/flutter-sdk-api-reference#3-reset) (see [Flutter Implementation](#flutter-implementation)) are also used as part of this flow.

The [HydraNativeEventHandler](https://docs.capillarytech.com/docs/flutter-sdk-api-reference#hydranativeeventhandler-class) includes callbacks for notifications, initialization, the visitor flow, and gamification: `onTokenAvailable`, `onHydraNotificationReceived`, `onHydraNotificationShown`, `onHydraNotificationClicked`, `onHydraNotificationDismissed`, `onNonHydraNotificationReceived`, `onNonHydraNotificationClicked`, `onNotificationCenterDismissed`, `onHydraSdkInitializationResult`, `onConfigFetched`, `onLegacyFlowReady`, `onVisitorSessionReady`, `onUserStateChanged`, `onGamificationEventTrigger`, `onGamificationAnalyticsEvent`, and `onGamificationDeeplink`.