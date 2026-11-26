---
updatedAt: 2026-11-12T06:11:18.000Z
agentTools:
  projectIndex: https://docs.capillarytech.com/llms.txt
---

# API Reference for Event Tracking, Notifications, and User Lifecycle

The `capillary_hydra` package provides the classes below for user and account management (`HydraCore`), user identity and events (`Hydra`), push notifications (`HydraPushNotification`), the notification inbox (`HydraInbox`, `HydraInboxUI`), event callbacks (`HydraNativeEvents`), and the model classes they use.

# Quick reference

| Method                                                                                          | What it does                                                                              |
| ----------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------- |
| [`HydraCore.updateUser`](#hydracore-class-apis)                                                 | Update user details, custom data, and subscriptions.                                      |
| [`HydraCore.updateGeoConfig`](#hydracore-class-apis)                                            | Update the user's geo config.                                                             |
| [`HydraCore.updatePushPreferences`](#hydracore-class-apis)                                      | Enable/disable promotional and transactional push.                                        |
| [`HydraCore.setHydraAccountConfig`](#hydracore-class-apis)                                      | Switch Hydra account with values you provide (multi-account setup).                       |
| [`HydraCore.setFirebaseRemoteConfigKeys`](#hydracore-class-apis)                                | Switch Hydra account using custom Firebase Remote Config key names (multi-account setup). |
| [`Hydra.identify`](#hydra-class-apis)                                                           | Identify the current user.                                                                |
| [`Hydra.track`](#hydra-class-apis)                                                              | Report a custom event.                                                                    |
| [`Hydra.reset`](#hydra-class-apis)                                                              | Reset the current user.                                                                   |
| [`Hydra.getCurrentUserState`](#hydra-class-apis)                                                | Get the current user state.                                                               |
| [`Hydra.getVisitorDetails`](#hydra-class-apis)                                                  | Get the current visitor details.                                                          |
| [`Hydra.isVisitorFlowEnabled`](#hydra-class-apis)                                               | Check whether the visitor flow is enabled.                                                |
| [`Hydra.gamificationScreenAppeared` / `Hydra.gamificationScreenDisappeared`](#hydra-class-apis) | Report a gamification screen appearing/disappearing.                                      |
| [`Hydra.setCapToken`](#hydra-class-apis)                                                        | Set the cap token required by `GamificationLoyaltyView`.                                  |
| [`Hydra.setGamificationSuppressed` / `Hydra.isGamificationSuppressed`](#hydra-class-apis)       | Suppress gamification campaigns, or check the setting.                                    |
| [`Hydra.setThemeMode` / `Hydra.getThemeMode`](#hydra-class-apis)                                | Set/get the gamification theme mode.                                                      |
| [`HydraPushNotification.getFCMToken`](#hydrapushnotification-class-apis)                        | Get the current FCM token.                                                                |
| [`HydraPushNotification.requestPermission`](#hydrapushnotification-class-apis)                  | Request push notification permission.                                                     |
| [`HydraPushNotification.passFCMToken`](#hydrapushnotification-class-apis)                       | Pass an FCM token your app obtained outside Hydra to the SDK (Android only).              |
| [`HydraInbox.getInboxMessages`](#hydrainbox-class-apis)                                         | Get the list of Hydra notifications.                                                      |
| [`HydraInbox.getUnreadInboxMessagesCount`](#hydrainbox-class-apis)                              | Get the unread notification count.                                                        |
| [`HydraInbox.markInboxMessageAsRead`](#hydrainbox-class-apis)                                   | Mark a notification as read.                                                              |
| [`HydraInbox.deleteInboxMessage`](#hydrainbox-class-apis)                                       | Delete a notification.                                                                    |
| [`HydraInbox.deleteAllInboxMessages`](#hydrainbox-class-apis)                                   | Delete all notifications.                                                                 |
| [`HydraInboxUI.showNotificationCenter`](#hydrainboxui-class-apis)                               | Show the built-in notification center.                                                    |
| [`HydraInboxUI.hideNotificationCenterIfShowing`](#hydrainboxui-class-apis)                      | Hide the built-in notification center.                                                    |
| [`HydraNativeEvents.addEventHandler`](#hydranativeevent-class-apis)                             | Register an event handler.                                                                |
| [`HydraNativeEvents.removeEventHandler`](#hydranativeevent-class-apis)                          | Remove an event handler.                                                                  |
| [`HydraNativeEvents.removeAllEventHandlers`](#hydranativeevent-class-apis)                      | Remove all event handlers.                                                                |

<a id="hydracore-class-apis"></a>

# HydraCore Class APIs

`import 'package:capillary_hydra/hydra.dart';`

## 1. Update User

```dart
static Future<bool> updateUser({
  required HydraUserDetails userDetails,
  Map<String, dynamic>? customData,
  List<Map<String, dynamic>>? subscriptions,
});
```

| Parameter     | Type                                  | Required/Optional | Description                                                                              |
| ------------- | ------------------------------------- | ----------------- | ---------------------------------------------------------------------------------------- |
| userDetails   | [HydraUserDetails](#hydrauserdetails) | required          | Read more about this class [here](#hydrauserdetails).                                    |
| customData    | Map\<String, dynamic>?                | optional          | Custom attributes that can be used for analytics.                                        |
| subscriptions | List\<Map\<String, dynamic>>?         | optional          | List of subscriptions, each including channel, accountId, priority, type and sourcename. |

**Returns:** A Future which resolves to a bool indicating if the update was successfully requested.

**Usage:**

```dart
bool updateUserResult = await HydraCore.updateUser(
  userDetails: updatedUserDetails,
  customData: {"Key": "Value"},
  subscriptions: [
    {"channel": "channel1", "type": "topic1", "priority": 1},
  ],
);
```

## 2. Update Geo Config

```dart
static Future<bool> updateGeoConfig({required HydraGeoConfig config});
```

| Parameter | Type                              | Required/Optional | Description                                         |
| --------- | --------------------------------- | ----------------- | --------------------------------------------------- |
| config    | [HydraGeoConfig](#hydrageoconfig) | required          | Read more about this class [here](#hydrageoconfig). |

**Returns:** A Future which resolves to a bool indicating if the update of geo config was successfully requested.

**Usage:**

```dart
bool updateGeoConfigResult = await HydraCore.updateGeoConfig(config: config);
```

## 3. Update User Push Preferences

```dart
static Future<bool> updatePushPreferences({
  required String customerId,
  required HydraPushPreferences preferences,
});
```

| Parameter   | Type                                          | Required/Optional | Description                                               |
| ----------- | --------------------------------------------- | ----------------- | --------------------------------------------------------- |
| customerId  | String                                        | required          | Customer id of the user to update push preferences.       |
| preferences | [HydraPushPreferences](#hydrapushpreferences) | required          | Read more about this class [here](#hydrapushpreferences). |

**Returns:** A Future which resolves to a bool indicating if the user push preferences update was successfully requested.

**Usage:**

```dart
bool result = await HydraCore.updatePushPreferences(
  preferences: pushPreferences,
  customerId: "8888888888",
);
```

## 4. Set Hydra Account Configuration (multi-account setup)

```dart
static Future<bool> setHydraAccountConfig({required HydraAccountConfig hydraAccountConfig});
```

| Parameter          | Type                                      | Required/Optional | Description                                                                                                                                                                                             |
| ------------------ | ----------------------------------------- | ----------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| hydraAccountConfig | [HydraAccountConfig](#hydraaccountconfig) | required          | Read more about this class [here](#hydraaccountconfig), including the optional `orgId` (Anonymous/Visitor Flow) and `gamificationKey`/`gamificationRegion`/`gamificationBaseUrl` (Gamification) fields. |

**Returns:** A Future which resolves to a bool indicating whether the account config update was successfully requested. Use this when you're fetching Hydra account values yourself rather than via Firebase Remote Config.

**Usage:**

```dart
bool result = await HydraCore.setHydraAccountConfig(hydraAccountConfig: hydraAccountConfig);
```

## 5. Set Firebase Remote Config Keys (multi-account setup)

```dart
static Future<bool> setFirebaseRemoteConfigKeys({required HydraFirebaseRemoteConfigKeys hydraFirebaseRemoteConfigKeys});
```

| Parameter                     | Type                                                            | Required/Optional | Description                                                                                                                                                                                                                                   |
| ----------------------------- | --------------------------------------------------------------- | ----------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| hydraFirebaseRemoteConfigKeys | [HydraFirebaseRemoteConfigKeys](#hydrafirebaseremoteconfigkeys) | required          | Read more about this class [here](#hydrafirebaseremoteconfigkeys), including the optional `keyForOrgId` (Anonymous/Visitor Flow) and `keyForGamificationKey`/`keyForGamificationRegion`/`keyForGamificationBaseUrl` (Gamification) key names. |

**Returns:** A Future which resolves to a bool indicating whether the remote config keys update was successfully requested. Use this when you have multiple Hydra accounts configured under different Firebase Remote Config key names.

**Usage:**

```dart
bool result = await HydraCore.setFirebaseRemoteConfigKeys(hydraFirebaseRemoteConfigKeys: hydraFirebaseRemoteConfigKeys);
```

<a id="hydra-class-apis"></a>

# Hydra Class APIs

`import 'package:capillary_hydra/hydra.dart';`

## 1. Identify

```dart
static Future<bool> identify({
  required HydraUserDetails userDetails,
  Map<String, dynamic>? customAttributes,
});
```

| Parameter        | Type                                  | Required/Optional | Description                                       |
| ---------------- | ------------------------------------- | ----------------- | ------------------------------------------------- |
| userDetails      | [HydraUserDetails](#hydrauserdetails) | required          | Identifies the current visitor as a known user.   |
| customAttributes | Map\<String, dynamic>?                | optional          | Custom attributes that can be used for analytics. |

**Returns:** A Future which resolves to a bool indicating if identify was successfully requested.

**Usage:**

```dart
bool result = await Hydra.identify(userDetails: userDetails);
```

## 2. Track

```dart
static Future<bool> track({
  required String eventName,
  Map<String, dynamic>? attributes,
});
```

| Parameter  | Type                   | Required/Optional | Description                                         |
| ---------- | ---------------------- | ----------------- | --------------------------------------------------- |
| eventName  | String                 | required          | Name of the event you want to report.               |
| attributes | Map\<String, dynamic>? | optional          | Key value pairs for additional data with the event. |

**Returns:** A Future which resolves to a bool indicating if the event was successfully reported.

**Usage:**

```dart
bool result = await Hydra.track(eventName: 'product_viewed', attributes: {'productId': 'abc123'});
```

## 3. Reset

```dart
static Future<bool> reset({required String customerId});
```

| Parameter  | Type   | Required/Optional | Description                       |
| ---------- | ------ | ----------------- | --------------------------------- |
| customerId | String | required          | Customer id of the user to reset. |

**Returns:** A Future which resolves to a bool indicating if reset was successfully requested.

**Usage:**

```dart
bool result = await Hydra.reset(customerId: '8888888888');
```

## 4. Get Current User State

```dart
static Future<UserState?> getCurrentUserState();
```

**Returns:** A Future which resolves to the current [UserState](#userstate), or null.

**Usage:**

```dart
UserState? state = await Hydra.getCurrentUserState();
```

## 5. Get Visitor Details

```dart
static Future<HydraVisitorInfo?> getVisitorDetails();
```

**Returns:** A Future which resolves to a [HydraVisitorInfo](#hydravisitorinfo) (`visitorId`), or null.

**Usage:**

```dart
HydraVisitorInfo? info = await Hydra.getVisitorDetails();
```

## 6. Is Visitor Flow Enabled

```dart
static Future<bool> isVisitorFlowEnabled();
```

**Returns:** A Future which resolves to a bool indicating whether the anonymous visitor flow is enabled for this account.

**Usage:**

```dart
bool enabled = await Hydra.isVisitorFlowEnabled();
```

<a id="7-gamification-screen-appeared-disappeared"></a>

## 7. Gamification Screen Appeared / Disappeared

```dart
static Future<void> gamificationScreenAppeared({required String screenName});
static Future<void> gamificationScreenDisappeared({required String screenName});
```

| Parameter  | Type   | Required/Optional | Description                                                                                              |
| ---------- | ------ | ----------------- | -------------------------------------------------------------------------------------------------------- |
| screenName | String | required          | Name of the screen to track for gamification screen views. Pass the **same** `screenName` to both calls. |

**Usage:**

```dart
Hydra.gamificationScreenAppeared(screenName: 'HomeScreen');
// ... later, when the screen unmounts:
Hydra.gamificationScreenDisappeared(screenName: 'HomeScreen');
```

## 8. Set Cap Token

```dart
static Future<void> setCapToken({required String token});
```

Must be called before mounting a `GamificationLoyaltyView` — see [Gamification](https://docs.capillarytech.com/docs/gamification-flutter).

**Usage:**

```dart
Hydra.setCapToken(token: token);
```

<a id="9-gamification-suppression"></a>

## 9. Gamification Suppression

```dart
static Future<void> setGamificationSuppressed({required bool suppressed});
static Future<bool> isGamificationSuppressed();
```

| Parameter  | Type | Required/Optional | Description                                                                          |
| ---------- | ---- | ----------------- | ------------------------------------------------------------------------------------ |
| suppressed | bool | required          | `true` to stop gamification campaigns from being shown, `false` to allow them again. |

**Returns:** `setGamificationSuppressed` completes once the value is applied. `isGamificationSuppressed` resolves to the current value. Both **throw** if the Hydra SDK is not initialized yet, so an error means suppression was not applied (or the value is unknown), not that it is `false`.

**Usage:**

```dart
// e.g. while the user is in checkout
await Hydra.setGamificationSuppressed(suppressed: true);
// ... later
await Hydra.setGamificationSuppressed(suppressed: false);

bool suppressed = await Hydra.isGamificationSuppressed();
```

<a id="10-theme-mode"></a>

## 10. Theme Mode

```dart
static Future<void> setThemeMode({required HydraThemeMode mode});
static Future<HydraThemeMode> getThemeMode();
```

| Parameter | Type                              | Required/Optional | Description                     |
| --------- | --------------------------------- | ----------------- | ------------------------------- |
| mode      | [HydraThemeMode](#hydrathememode) | required          | Theme mode for gamification UI. |

**Returns:** `setThemeMode` completes once the mode is applied, and throws if the SDK is not initialized. `getThemeMode` resolves to the current [HydraThemeMode](#hydrathememode), or `HydraThemeMode.none` if the SDK is not initialized yet.

**Usage:**

```dart
await Hydra.setThemeMode(mode: HydraThemeMode.dark);

HydraThemeMode mode = await Hydra.getThemeMode();
```

# HydraPushNotification class APIs

`import 'package:capillary_hydra/hydra.dart';`

## 1. Get FCM Token

```dart
static Future<String> getFCMToken();
```

**Returns:** A Future which resolves to a String containing the FCM token. If the FCM token is not available, it throws an error.

**Usage:**

```dart
String fcmToken = await HydraPushNotification.getFCMToken();
```

## 2. Request Permission for Push Notifications

```dart
static Future<bool> requestPermission();
```

**Returns:** A Future which resolves to a bool indicating if the permission was granted. It can also throw an error.

**Usage:**

```dart
bool granted = await HydraPushNotification.requestPermission();
```

<a id="3-pass-fcm-token-android-only"></a>

## 3. Pass FCM Token (Android only)

```dart
static Future<void> passFCMToken({required String token});
```

Hands an FCM token your app obtained outside Hydra (e.g. from `firebase_messaging`) to the SDK. Call it with each new token, e.g. from `FirebaseMessaging.instance.onTokenRefresh`. On iOS it completes without doing anything, so it's safe to call on both platforms.

| Parameter | Type   | Required/Optional | Description             |
| --------- | ------ | ----------------- | ----------------------- |
| token     | String | required          | The device's FCM token. |

**Usage:**

```dart
import 'package:firebase_messaging/firebase_messaging.dart';

final token = await FirebaseMessaging.instance.getToken();
if (token != null) {
  await HydraPushNotification.passFCMToken(token: token);
}
FirebaseMessaging.instance.onTokenRefresh.listen(
  (token) => HydraPushNotification.passFCMToken(token: token),
);
```

<a id="hydrainbox-class-apis"></a>

# HydraInbox class APIs

`import 'package:capillary_hydra/hydra.dart';`

## 1. Get list of Hydra Notifications

```dart
static Future<List<HydraNotification>> getInboxMessages();
```

**Returns:** A Future which resolves to a list of [HydraNotification](#hydranotification).

**Usage:**

```dart
List<HydraNotification> notifications = await HydraInbox.getInboxMessages();
```

## 2. Get Unread Hydra Notifications Count

```dart
static Future<int> getUnreadInboxMessagesCount();
```

**Returns:** A Future which resolves to a number containing the unread count.

**Usage:**

```dart
int unreadNotificationCount = await HydraInbox.getUnreadInboxMessagesCount();
```

## 3. Mark a Hydra Notification as Read

```dart
static Future<bool> markInboxMessageAsRead({required HydraNotification notification});
```

| Parameter    | Type                                    | Required/Optional | Description                                                                                                           |
| ------------ | --------------------------------------- | ----------------- | --------------------------------------------------------------------------------------------------------------------- |
| notification | [HydraNotification](#hydranotification) | required          | Hydra Notification to mark as read from the list obtained via [getInboxMessages](#1-get-list-of-hydra-notifications). |

**Returns:** A Future which resolves to a bool if marking the notification as read is successfully requested.

**Usage:**

```dart
bool marked = await HydraInbox.markInboxMessageAsRead(notification: notification);
```

## 4. Delete a Hydra Notification

```dart
static Future<bool> deleteInboxMessage({required HydraNotification notification});
```

| Parameter    | Type                                    | Required/Optional | Description                                                                                                     |
| ------------ | --------------------------------------- | ----------------- | --------------------------------------------------------------------------------------------------------------- |
| notification | [HydraNotification](#hydranotification) | required          | Hydra Notification to delete from the list obtained via [getInboxMessages](#1-get-list-of-hydra-notifications). |

**Returns:** A Future which resolves to a bool if deleting the notification is successfully requested.

**Usage:**

```dart
bool deleted = await HydraInbox.deleteInboxMessage(notification: notification);
```

## 5. Delete all Hydra Notifications

```dart
static Future<bool> deleteAllInboxMessages();
```

**Returns:** A Future which resolves to a bool if deleting all notifications is successfully requested.

**Usage:**

```dart
bool deleted = await HydraInbox.deleteAllInboxMessages();
```

<a id="hydrainboxui-class-apis"></a>

# HydraInboxUI class APIs

`import 'package:capillary_hydra/hydra.dart';`

## 1. Show In-Built Notification Center

```dart
static Future<void> showNotificationCenter();
```

**Returns:** A Future which resolves to void.

**Usage:**

```dart
HydraInboxUI.showNotificationCenter();
```

## 2. Hide In-Built Notification Center if Showing

```dart
static Future<void> hideNotificationCenterIfShowing();
```

**Returns:** A Future which resolves to void.

**Usage:**

```dart
await HydraInboxUI.hideNotificationCenterIfShowing();
```

<a id="hydranativeevent-class-apis"></a>

# HydraNativeEvents class APIs

`import 'package:capillary_hydra/hydra.dart';`

To receive callbacks on various events from the native Hydra SDKs, register a handler using this class. There are functions for removing handlers too.

## 1. Add Event Handler

```dart
static void addEventHandler(HydraNativeEventHandler handler);
```

| Parameter | Type                                                      | Required/Optional | Description                                                                |
| --------- | --------------------------------------------------------- | ----------------- | -------------------------------------------------------------------------- |
| handler   | [HydraNativeEventHandler](#hydranativeeventhandler-class) | required          | An instance of a class that extends or implements HydraNativeEventHandler. |

**Usage:**

```dart
HydraNativeEvents.addEventHandler(handler);
```

## 2. Remove Event Handler

```dart
static void removeEventHandler(HydraNativeEventHandler handler);
```

| Parameter | Type                                                      | Required/Optional | Description                                                                |
| --------- | --------------------------------------------------------- | ----------------- | -------------------------------------------------------------------------- |
| handler   | [HydraNativeEventHandler](#hydranativeeventhandler-class) | required          | An instance of a class that extends or implements HydraNativeEventHandler. |

**Usage:**

```dart
HydraNativeEvents.removeEventHandler(handler);
```

## 3. Remove All Event Handlers

```dart
static void removeAllEventHandlers();
```

**Usage:**

```dart
HydraNativeEvents.removeAllEventHandlers();
```

<a id="hydranativeeventhandler-class"></a>

## HydraNativeEventHandler

Extend this class and override the callbacks you're interested in (all methods have empty default bodies). Prefer `extends` over `implements`: a class that `implements` it must define every callback, including any added in later releases, so it can stop compiling after an upgrade.

```dart
class HydraNativeEventHandler {
  void onTokenAvailable({required String token}) {}
  void onHydraNotificationReceived({required HydraNotification notification}) {}
  void onHydraNotificationClicked({HydraNotificationCTA? cta, HydraNotification? notification}) {}
  void onHydraNotificationDismissed({required HydraNotification notification}) {}
  void onHydraNotificationShown({required HydraNotification notification}) {}
  void onNonHydraNotificationReceived({required NonHydraNotification notification}) {}
  void onNonHydraNotificationClicked({NonHydraNotification? notification}) {}
  void onNotificationCenterDismissed() {}
  void onHydraSdkInitializationResult({required bool success, String? error}) {}
  // Anonymous / Visitor Flow:
  void onConfigFetched({required bool isVisitorFlowEnabled}) {}
  void onLegacyFlowReady() {}
  void onVisitorSessionReady() {}
  void onUserStateChanged({UserState? userState}) {}
  // Gamification:
  void onGamificationEventTrigger({required String name, required Map<String, dynamic> payload}) {}
  void onGamificationAnalyticsEvent({required String name, required Map<String, dynamic> payload}) {}
  void onGamificationDeeplink({required String url}) {}
}
```

1. **`onTokenAvailable`** — fired when a new FCM token is available; provided as a `String`.
2. **`onHydraNotificationReceived`** — fired when a Hydra notification is received; provides the [`HydraNotification`](#hydranotification).
3. **`onHydraNotificationClicked`** — fired when a Hydra notification is clicked in the system notification tray/center on either platform, when a notification is clicked in the SDK's built-in notification center, or when a click is received on an in-app message. Provides both the [`HydraNotification`](#hydranotification) and the [`HydraNotificationCTA`](#hydranotificationcta) that was clicked.
4. **`onHydraNotificationDismissed`** — fired when a Hydra notification is dismissed in the system tray/center. Provides the [`HydraNotification`](#hydranotification).
5. **`onHydraNotificationShown`** — fired when a Hydra notification is shown in the system tray/center. Provides the [`HydraNotification`](#hydranotification).
6. **`onNonHydraNotificationReceived`** / **`onNonHydraNotificationClicked`** — same as above, for non-Hydra push notifications.
7. **`onNotificationCenterDismissed`** — fired when the built-in notification center is dismissed.
8. **`onHydraSdkInitializationResult`** — since SDK initialization happens automatically, use this to check whether it succeeded or failed (with an optional error).
9. **`onConfigFetched`** / **`onLegacyFlowReady`** / **`onVisitorSessionReady`** / **`onUserStateChanged`** — see [Anonymous / Visitor Flow](https://docs.capillarytech.com/docs/flutter-setup-overview#anonymous--visitor-flow).
10. **`onGamificationDeeplink`** — fired when a gamification campaign asks the app to open a deep link. Route `url` in your app.
11. **`onGamificationEventTrigger`** — fired when a gamification campaign or game triggers a named event; provides the event `name` and its `payload`.
12. **`onGamificationAnalyticsEvent`** — fired for analytics events emitted by gamification UI, e.g. to forward them to your own analytics tool; provides the event `name` and its `payload`.

There's no dedicated "inbox updated" event — refresh your UI from `onHydraNotificationReceived` or `onNotificationCenterDismissed`, or by polling `HydraInbox` on demand.

# HydraCore Model Classes and Enumerations

`import 'package:capillary_hydra_platform_interface/capillary_hydra_platform_interface.dart';`

<a id="hydrauserdetails"></a>

## HydraUserDetails

Used across multiple `HydraCore` APIs for signing up, signing in, and updating user details.

```dart
HydraUserDetails({
  required this.customerId,
  this.email,
  this.phoneNumber,
  this.firstName,
  this.lastName,
});
```

| Parameter   | Type    | Required/Optional | Description                                                                                                                                                                                                                                            |
| ----------- | ------- | ----------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| customerId  | String  | required          | Can be mobile, email, InTouchUserId, externalId or FCMToken, depending on how your app is configured on the Capillary CRM dashboard (Organisation Settings → Omni Channel Settings → Channel Configurations → MAPP\_SDK → Account Linking Identifier). |
| firstName   | String? | optional          | First name of the user.                                                                                                                                                                                                                                |
| lastName    | String? | optional          | Last name of the user.                                                                                                                                                                                                                                 |
| email       | String? | optional          | Email of the user.                                                                                                                                                                                                                                     |
| phoneNumber | String? | optional          | Phone number of the user.                                                                                                                                                                                                                              |

**Usage:**

```dart
HydraUserDetails userDetails = HydraUserDetails(
  customerId: '8888888888',
  firstName: 'FirstName',
  lastName: 'LastName',
  email: 'test@capillarytech.com',
  phoneNumber: '918888888888',
);
```

<a id="hydrageoconfig"></a>

## HydraGeoConfig

Used in `updateGeoConfig`.

```dart
HydraGeoConfig({
  required this.city,
  required this.country,
  required this.countryCode,
  this.timezone,
});
```

| Parameter   | Type    | Required/Optional | Description                     |
| ----------- | ------- | ----------------- | ------------------------------- |
| city        | String  | required          | City of the user.               |
| country     | String  | required          | Country of the user.            |
| countryCode | String  | required          | Country code for mobile number. |
| timezone    | String? | optional          | User's timezone.                |

**Usage:**

```dart
HydraGeoConfig geoConfig = HydraGeoConfig(
  city: "Bangalore",
  country: "India",
  countryCode: "IN",
  timezone: "Asia/Kolkata",
);
```

<a id="hydrapushpreferences"></a>

## HydraPushPreferences

Used to update a user's push preferences.

```dart
HydraPushPreferences({
  required this.promPushEnabled,
  required this.transPushEnabled,
});
```

| Parameter        | Type | Required/Optional | Description                                      |
| ---------------- | ---- | ----------------- | ------------------------------------------------ |
| promPushEnabled  | bool | required          | Enable/disable promotional push notifications.   |
| transPushEnabled | bool | required          | Enable/disable transactional push notifications. |

**Usage:**

```dart
HydraPushPreferences pushPreferences = HydraPushPreferences(
  promPushEnabled: false,
  transPushEnabled: true,
);
```

## HydraLogLevel

```dart
enum HydraLogLevel {
  off(0),
  error(1),
  warn(2),
  info(3),
  debug(4),
  verbose(5);

  final int value;
}
```

<a id="hydraaccountconfig"></a>

## HydraAccountConfig

```dart
class HydraAccountConfig {
  final String accountId;
  final String baseUrl;
  final String sslPublicKey;
  final HydraLogLevel remoteLogLevel;
  final String? orgId;
  final String? gamificationKey;
  final String? gamificationRegion;
  final String? gamificationBaseUrl;
}
```

| Parameter           | Required/Optional | Description                                   |
| ------------------- | ----------------- | --------------------------------------------- |
| accountId           | required          | Account id from the apps team.                |
| baseUrl             | required          | Base Url (End Point) from the apps team.      |
| sslPublicKey        | required          | SSL public key from the apps team.            |
| remoteLogLevel      | required          | See [HydraLogLevel](#hydraloglevel).          |
| orgId               | optional          | Required only for the Anonymous/Visitor Flow. |
| gamificationKey     | optional          | Required only for Gamification.               |
| gamificationRegion  | optional          | Required only for Gamification.               |
| gamificationBaseUrl | optional          | Required only for Gamification.               |

**Usage:**

```dart
HydraAccountConfig hydraAccountConfig = HydraAccountConfig(
  accountId: accountId,
  baseUrl: baseUrl,
  sslPublicKey: sslPublicKey,
  remoteLogLevel: HydraLogLevel.debug,
  orgId: orgId,
  gamificationKey: gamificationKey,
  gamificationRegion: gamificationRegion,
  gamificationBaseUrl: gamificationBaseUrl,
);
```

<a id="hydrafirebaseremoteconfigkeys"></a>

## HydraFirebaseRemoteConfigKeys

```dart
class HydraFirebaseRemoteConfigKeys {
  final String keyForAccountId;
  final String keyForBaseUrl;
  final String keyForSsl;
  final String keyForRemoteLogLevel;
  final String? keyForOrgId;
  final String? keyForGamificationKey;
  final String? keyForGamificationRegion;
  final String? keyForGamificationBaseUrl;
}
```

**Usage:**

```dart
final hydraFirebaseRemoteConfigKeys = {
  'ind_account': HydraFirebaseRemoteConfigKeys(
    keyForAccountId: 'ind_hydra_account_id',
    keyForBaseUrl: 'ind_hydra_base_url',
    keyForSsl: 'ind_hydra_ssl_public_key',
    keyForRemoteLogLevel: 'ind_hydra_remote_log_level',
    keyForOrgId: 'ind_hydra_org_id',
    keyForGamificationKey: 'ind_hydra_gamification_key',
    keyForGamificationRegion: 'ind_hydra_gamification_region',
    keyForGamificationBaseUrl: 'ind_hydra_gamification_base_url',
  ),
};
```

<a id="userstate"></a>

## UserState

```dart
enum UserState { none, legacyRegistered, visitor, merged, signedOut }
```

<a id="hydravisitorinfo"></a>

## HydraVisitorInfo

```dart
class HydraVisitorInfo {
  final String? visitorId;
}
```

<a id="hydrathememode"></a>

## HydraThemeMode

Used with [Hydra.setThemeMode / getThemeMode](#10-theme-mode).

```dart
enum HydraThemeMode { none, auto, light, dark }
```

| Value   | Description                                |
| ------- | ------------------------------------------ |
| `none`  | Leaves the campaign's own theme untouched. |
| `auto`  | Follows the device's light/dark setting.   |
| `light` | Always uses the light theme.               |
| `dark`  | Always uses the dark theme.                |

# HydraNotification Model Classes and Enumerations

`import 'package:capillary_hydra_platform_interface/capillary_hydra_platform_interface.dart';`

<a id="hydranotification"></a>

## HydraNotification

Model class for Hydra Notification objects received from the native SDK; all fields are final.

```dart
class HydraNotification {
  final String? cuid;
  final String? scope;
  final String? campaignId;
  final String? variationId;
  final String? senderId;
  final String? senderSource;
  final String? custom;
  final Map<String, dynamic>? customData;
  final String? priority;
  final String? validity;
  final String? messageId;
  final HydraNotificationGateway? gateway;
  final HydraNotificationBody? body;
  final HydraNotificationExpandedDetails? expandableDetails;
  final bool? isRead;
  final String? imageIdentifier;
  final String? accountId;
  final String? channelId;
  final String? payload;
  final DateTime? createdAt;
  final bool? isExpanded;
  final bool? isMessageEllipsized;
  final bool? isTitleEllipsized;
  final bool? showArrow;
}
```

## HydraNotificationBody

```dart
class HydraNotificationBody {
  final String? title;
  final String? message;
  final String? image;
  final HydraNotificationCTA? cta;
}
```

<a id="hydranotificationcta"></a>

## HydraNotificationCTA

```dart
class HydraNotificationCTA {
  final HydraNotificationCTAType? type;
  final String? action;
  final String? actionText;
}
```

## HydraNotificationCTAType

```dart
enum HydraNotificationCTAType { external, deepLink, rating, feedback, appRating, unknown }
```

## HydraNotificationExpandedDetails

```dart
class HydraNotificationExpandedDetails {
  final List<HydraNotificationCTA>? ctas;
  final String? message;
  final String? image;
  final String? style;
}
```

## HydraNotificationGateway

```dart
enum HydraNotificationGateway { fcm, xiaomi, unknown }
```

## NonHydraNotification

```dart
class NonHydraNotification {
  final String? title;
  final String? body;
  final String? icon;
  final String? imageUrl;
  final Map<String, dynamic> data;
}
```