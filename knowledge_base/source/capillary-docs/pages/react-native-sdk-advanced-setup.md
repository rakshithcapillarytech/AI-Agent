---
updatedAt: 2026-11-12T06:08:47.000Z
agentTools:
  projectIndex: https://docs.capillarytech.com/llms.txt
---

# Advanced Setup

Use custom initialisers, run Hydra without Firebase, or connect one app to more than one Hydra account.

The standard integration is covered in [Install React Native SDK](https://docs.capillarytech.com/docs/react-native-sdk-install). Use the following sections only if your app needs something outside that flow:

* [Other initializers](#other-initializers): Custom Firebase Remote Config key names, or passing the account values directly.
* [Using Hydra without Firebase](#using-hydra-without-firebase): Running Hydra with no Firebase project, when you don't need push notifications.
* [Multi-Hydra account setup](#multi-hydra-account-setup): One app talking to more than one Hydra account.

# Other initializers

[Installing iOS SDK](https://docs.capillarytech.com/docs/react-native-sdk-install#installing-ios-sdk) and [Installing Android SDK](https://docs.capillarytech.com/docs/react-native-sdk-install#installing-android-sdk) use the default initialiser, which reads the account values from Firebase Remote Config under the default key names. If that doesn't fit your app, use one of the following variants instead. Call it in the same place as the default initialiser. On iOS, still call it after `super application:didFinishLaunchingWithOptions:`.

## 1. Custom Firebase Remote Config key names

Use this when the account values are in Firebase Remote Config under different key names, for example to start a [multi-Hydra account setup](#multi-hydra-account-setup) on a non-default account.

### iOS

Build a `HydraNativeFirebaseRemoteConfigKeys` and pass it as the keys parameter.

**Objective-C:**

```objectivec
HydraNativeFirebaseRemoteConfigKeys *keys = [[HydraNativeFirebaseRemoteConfigKeys alloc]
    initWithKeyForAccountId:@"ind_hydra_account_id"
    keyForBaseUrl:@"ind_hydra_base_url"
    keyForSsl:@"ind_hydra_ssl_public_key"
    keyForRemoteLogLevel:@"ind_hydra_remote_log_level"
    keyForOrgId:@"ind_hydra_org_id"
    keyForGamificationKey:@"ind_hydra_gamification_key"
    keyForGamificationRegion:@"ind_hydra_gamification_region"
    keyForGamificationBaseUrl:@"ind_hydra_gamification_base_url"];

[[Hydra sharedInstance] initialize:application
      didFinishLaunchingWithOptions:launchOptions
                           withKeys:keys
              withHydraRemoteConfig:NULL];
```

**Swift:**

```swift
let keys = HydraNativeFirebaseRemoteConfigKeys(
    keyForAccountId: "ind_hydra_account_id",
    keyForBaseUrl: "ind_hydra_base_url",
    keyForSsl: "ind_hydra_ssl_public_key",
    keyForRemoteLogLevel: "ind_hydra_remote_log_level",
    keyForOrgId: "ind_hydra_org_id",
    keyForGamificationKey: "ind_hydra_gamification_key",
    keyForGamificationRegion: "ind_hydra_gamification_region",
    keyForGamificationBaseUrl: "ind_hydra_gamification_base_url"
)

Hydra.sharedInstance().initialize(application, didFinishLaunchingWithOptions: launchOptions ?? [:], with: keys, withHydraRemoteConfig: nil)
```

### Android

Build a `HydraFirebaseRemoteConfigKeys` and pass it to `Hydra.initialize`.

```kotlin
import com.hydralib.nativeapis.Hydra
import com.hydralib.nativeapis.HydraFirebaseRemoteConfigKeys

val hydraFirebaseRemoteConfigKeys = HydraFirebaseRemoteConfigKeys(
    "ind_hydra_account_id",
    "ind_hydra_base_url",
    "ind_hydra_ssl_public_key",
    "ind_hydra_remote_log_level",
    "ind_hydra_org_id",
    "ind_hydra_gamification_key",
    "ind_hydra_gamification_region",
    "ind_hydra_gamification_base_url"
)
Hydra.initialize(this, hydraFirebaseRemoteConfigKeys)
```

## 2. Pass the account values directly

Use this when you get the account values from somewhere other than Firebase Remote Config, such as your own backend, another CMS, or hardcoded values. Use it also when you are [using Hydra without Firebase](#using-hydra-without-firebase).

### iOS

Build a `HydraNativeRemoteConfig` and pass it as the remote-config parameter instead of the keys parameter.

**Objective-C:**

```objectivec
HydraNativeRemoteConfig *remoteConfig = [[HydraNativeRemoteConfig alloc]
    initWithAccountId:@"<YOUR_ACCOUNT_ID>"
    baseUrl:@"<YOUR_BASE_URL>"
    sslPublicKey:@"<YOUR_SSL_PUBLIC_KEY>"
    remoteLogLevel:0
    orgId:@"<YOUR_ORG_ID>"
    gamificationKey:@"<YOUR_GAMIFICATION_KEY>"
    gamificationRegion:@"<YOUR_GAMIFICATION_REGION>"
    gamificationBaseUrl:@"<YOUR_GAMIFICATION_BASE_URL>"];

[[Hydra sharedInstance] initialize:application
      didFinishLaunchingWithOptions:launchOptions
                           withKeys:NULL
              withHydraRemoteConfig:remoteConfig];
```

**Swift:**

```swift
let remoteConfig = HydraNativeRemoteConfig(
    accountId: "<YOUR_ACCOUNT_ID>",
    baseUrl: "<YOUR_BASE_URL>",
    sslPublicKey: "<YOUR_SSL_PUBLIC_KEY>",
    remoteLogLevel: 0,
    orgId: "<YOUR_ORG_ID>",
    gamificationKey: "<YOUR_GAMIFICATION_KEY>",
    gamificationRegion: "<YOUR_GAMIFICATION_REGION>",
    gamificationBaseUrl: "<YOUR_GAMIFICATION_BASE_URL>"
)

Hydra.sharedInstance().initialize(application, didFinishLaunchingWithOptions: launchOptions ?? [:], with: nil, withHydraRemoteConfig: remoteConfig)
```

| Parameter           | Required/Optional | Description                                                                                                                                                |
| ------------------- | ----------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------- |
| accountId           | required          | Account Id from the apps team. For details, see [Getting Started](https://docs.capillarytech.com/docs/react-native-sdk-getting-started).                   |
| baseUrl             | required          | Base Url (End Point) from the apps team.                                                                                                                   |
| sslPublicKey        | required          | SSL public key from the apps team.                                                                                                                         |
| remoteLogLevel      | required          | Remote log level, 0 to 5. For details, see [HydraLogLevel](https://docs.capillarytech.com/docs/react-native-sdk-api-reference#hydraloglevel).              |
| orgId               | optional          | Org Id, required only for the [Anonymous/Visitor Flow](https://docs.capillarytech.com/docs/react-native-sdk-anonymous-visitor-flow). Pass `nil` if unused. |
| gamificationKey     | optional          | Gamification Key, required only for [Gamification](https://docs.capillarytech.com/docs/gamification-react-native). Pass `nil` if unused.                   |
| gamificationRegion  | optional          | Gamification Region, required only for [Gamification](https://docs.capillarytech.com/docs/gamification-react-native). Pass `nil` if unused.                |
| gamificationBaseUrl | optional          | Gamification Base Url, required only for [Gamification](https://docs.capillarytech.com/docs/gamification-react-native). Pass `nil` if unused.              |

### Android

Build a `HydraRemoteConfig` and pass it as the `remoteConfig` parameter.

```kotlin
import com.hydralib.nativeapis.Hydra
import com.hydralib.nativeapis.HydraRemoteConfig

val remoteConfig = HydraRemoteConfig.Builder(
    "your_account_id", "your_base_url", "your_ssl_public_key", 0
)
    .orgId("your_org_id")
    .gamificationKey("your_gamification_key")
    .gamificationRegion("your_gamification_region")
    .gamificationBaseUrl("your_gamification_base_url")
    .build()
Hydra.initialize(this, remoteConfig = remoteConfig)
```

| Parameter (Builder)                        | Required/Optional | Description                                                                                                                                          |
| ------------------------------------------ | ----------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------- |
| accountId (1st positional argument)        | required          | Account Id from the apps team. For details, see [Getting Started](https://docs.capillarytech.com/docs/react-native-sdk-getting-started).             |
| baseURL (2nd positional argument)          | required          | Base Url (End Point) from the apps team.                                                                                                             |
| sslPublicKey (3rd positional argument)     | required          | SSL public key from the apps team.                                                                                                                   |
| remoteDebugLevel (4th positional argument) | required          | Remote log level, 0 to 5. For details, see [HydraLogLevel](https://docs.capillarytech.com/docs/react-native-sdk-api-reference#hydraloglevel).        |
| `.orgId(...)`                              | optional          | Org Id, required only for the [Anonymous/Visitor Flow](https://docs.capillarytech.com/docs/react-native-sdk-anonymous-visitor-flow). Omit if unused. |
| `.gamificationKey(...)`                    | optional          | Gamification Key, required only for [Gamification](https://docs.capillarytech.com/docs/gamification-react-native). Omit if unused.                   |
| `.gamificationRegion(...)`                 | optional          | Gamification Region, required only for [Gamification](https://docs.capillarytech.com/docs/gamification-react-native). Omit if unused.                |
| `.gamificationBaseUrl(...)`                | optional          | Gamification Base Url, required only for [Gamification](https://docs.capillarytech.com/docs/gamification-react-native). Omit if unused.              |

# Using Hydra without Firebase

Hydra doesn't need Firebase as long as you don't need push notifications. In this mode, you pass the account values to the initialiser yourself, and the SDK never calls Firebase on either platform.

**What still works:** User identity (`identify`, `reset`, `updateUser`), event tracking (`track`), the [Anonymous/Visitor Flow](https://docs.capillarytech.com/docs/react-native-sdk-anonymous-visitor-flow), and [Gamification](https://docs.capillarytech.com/docs/gamification-react-native). Gamification includes Floating Button, Popup, and Bottom Sheet campaigns, banner, embed, and loyalty views, theme mode, and suppression.

**What doesn't work:** Push notifications, and the [In-App Messaging](https://docs.capillarytech.com/docs/react-native-sdk-in-app-messaging) and [Inbox](https://docs.capillarytech.com/docs/react-native-sdk-notification-center) features that the SDK delivers through them. Leave those turned off.

1. **Turn push off** in `PROJECT_ROOT/capillary/hydra-config.json`:

   ```json
   {
     "console_log_level": 4,
     "enable_push_notification": false,
     "enable_hydra_sdk_firebase_registration": false,
     "enable_in_app_messaging": false,
     "enable_inbox_api": false,
     "enable_inbox_ui": false
   }
   ```

   With push off, Android uses a manifest without the Firebase messaging service of Hydra, and iOS doesn't configure Firebase.

2. **Skip these Firebase steps:**
   * The Firebase setup item in the [Prerequisites of Getting Started](https://docs.capillarytech.com/docs/react-native-sdk-getting-started) (registering the app on Firebase), and the Firebase Remote Config parameters in the same section.
   * The `GoogleService-Info.plist` step in [Installing iOS SDK](https://docs.capillarytech.com/docs/react-native-sdk-install#installing-ios-sdk).
   * The `google-services.json` step in [Installing Android SDK](https://docs.capillarytech.com/docs/react-native-sdk-install#installing-android-sdk).
   * All of [Configure Push Notifications](https://docs.capillarytech.com/docs/react-native-sdk-push-notifications), including the `com.google.gms.google-services` Gradle plugin, the Notification Service Extension, and the `hydra_notification_small_icon` asset.

3. **Initialise with the values directly.** Instead of the default initialiser, pass a `HydraNativeRemoteConfig` on iOS and a `HydraRemoteConfig` on Android. For details, see [Pass the account values directly](#2-pass-the-account-values-directly). For example:

   **iOS (Swift):**

   ```swift
   let result = super.application(application, didFinishLaunchingWithOptions: launchOptions)

   let remoteConfig = HydraNativeRemoteConfig(
       accountId: "<YOUR_ACCOUNT_ID>",
       baseUrl: "<YOUR_BASE_URL>",
       sslPublicKey: "<YOUR_SSL_PUBLIC_KEY>",
       remoteLogLevel: 0,
       orgId: "<YOUR_ORG_ID>",
       gamificationKey: "<YOUR_GAMIFICATION_KEY>",
       gamificationRegion: "<YOUR_GAMIFICATION_REGION>",
       gamificationBaseUrl: "<YOUR_GAMIFICATION_BASE_URL>"
   )
   Hydra.sharedInstance().initialize(application, didFinishLaunchingWithOptions: launchOptions ?? [:], with: nil, withHydraRemoteConfig: remoteConfig)

   return result
   ```

   **Android (Kotlin, in `MainApplication.onCreate`):**

   ```kotlin
   val remoteConfig = HydraRemoteConfig.Builder(
       "<YOUR_ACCOUNT_ID>", "<YOUR_BASE_URL>", "<YOUR_SSL_PUBLIC_KEY>", 0
   )
       .orgId("<YOUR_ORG_ID>")
       .gamificationKey("<YOUR_GAMIFICATION_KEY>")
       .gamificationRegion("<YOUR_GAMIFICATION_REGION>")
       .gamificationBaseUrl("<YOUR_GAMIFICATION_BASE_URL>")
       .build()
   Hydra.initialize(this, remoteConfig = remoteConfig)
   ```

   Don't call the no-argument `Hydra.initialize(this)`, and don't pass `withKeys` or `HydraFirebaseRemoteConfigKeys`. Those read the values from Firebase Remote Config.

4. **In React Native, avoid the Firebase-only APIs:**
   * To switch accounts, use [HydraCore.setHydraAccountConfig](https://docs.capillarytech.com/docs/react-native-sdk-api-reference#configure-hydra-account-settings). Never use [HydraCore.setFirebaseRemoteConfigKeys](https://docs.capillarytech.com/docs/react-native-sdk-api-reference#configure-firebase-remote-configuration-keys). That method saves the Firebase key names. On later launches, the SDK tries to read them from Firebase Remote Config, which fails without a configured Firebase app.
   * Do call [HydraPushNotification.passFCMToken](https://docs.capillarytech.com/docs/react-native-sdk-api-reference#pass-fcm-token-android-only) with a dummy token once the SDK initializes. On Android, Gamification doesn't work properly without a token, and without Firebase there's no real one to pass. On iOS, the call does nothing, so it's safe to call on both platforms.
   * Don't call `HydraPushNotification.requestPermission` or `getFCMToken`. Don't register the push listeners (`addTokenAvailableListener`, `addHydraNotification…Listener`, `addNonHydraNotification…Listener`).

> 📘 Note
>
> The Firebase native libraries are still linked into your app because Hydra depends on them, but they stay unused.

# Multi-Hydra account setup

Use this when one app talks to more than one Hydra account, for example separate accounts for India, the USA, and Europe. You need the account details for each account from the apps team: Account Id, Base Url, SSL public key, and the Org Id and Gamification values if you use those features.

The native initialiser sets the **default** account. From React Native, you then switch to another account with one of two `HydraCore` methods, depending on where the account values come from.

## 1. Choose where the account values come from

**Option A: Firebase Remote Config.** Keep the values of the default account in the standard keys (`hydra_account_id`, `hydra_base_url`, and so on). For details, see [Getting Started](https://docs.capillarytech.com/docs/react-native-sdk-getting-started). Publish one extra set of keys for each additional account, with a prefix of your choice. For example, for India:

* `ind_hydra_account_id`
* `ind_hydra_base_url`
* `ind_hydra_ssl_public_key`
* `ind_hydra_remote_log_level`
* `ind_hydra_org_id` (if you use the Anonymous/Visitor Flow)
* `ind_hydra_gamification_key` (if you use Gamification)
* `ind_hydra_gamification_region` (if you use Gamification)
* `ind_hydra_gamification_base_url` (if you use Gamification)

Then switch with [HydraCore.setFirebaseRemoteConfigKeys](https://docs.capillarytech.com/docs/react-native-sdk-api-reference#configure-firebase-remote-configuration-keys), passing a [HydraFirebaseRemoteConfigKeys](https://docs.capillarytech.com/docs/react-native-sdk-api-reference#hydrafirebaseremoteconfigkeys) object with the key names of that account:

```typescript
await HydraCore.setFirebaseRemoteConfigKeys(
  new HydraFirebaseRemoteConfigKeys(
    'ind_hydra_account_id',
    'ind_hydra_base_url',
    'ind_hydra_ssl_public_key',
    'ind_hydra_remote_log_level',
    'ind_hydra_org_id',
    'ind_hydra_gamification_key',
    'ind_hydra_gamification_region',
    'ind_hydra_gamification_base_url'
  )
);
```

This call reads the values that Firebase Remote Config has **already fetched**. It doesn't fetch them itself, so you must publish the prefixed keys in Remote Config. Otherwise, the call rejects with "Failed to get values for these keys from Firebase remote config".

**Option B: Values you fetch yourself** (your own backend or another CMS). Switch with [HydraCore.setHydraAccountConfig](https://docs.capillarytech.com/docs/react-native-sdk-api-reference#configure-hydra-account-settings), passing a [HydraAccountConfig](https://docs.capillarytech.com/docs/react-native-sdk-api-reference#hydraaccountconfig) object:

```typescript
await HydraCore.setHydraAccountConfig(
  new HydraAccountConfig(
    accountId,
    baseUrl,
    sslPublicKey,
    HydraLogLevel.off,
    orgId, // optional, Anonymous/Visitor Flow
    gamificationKey, // optional, Gamification
    gamificationRegion, // optional, Gamification
    gamificationBaseUrl // optional, Gamification
  )
);
```

This is the only option if you are [using Hydra without Firebase](#using-hydra-without-firebase).

## 2. Set the account before identifying the user

In a multi-account setup, call `setHydraAccountConfig` or `setFirebaseRemoteConfigKeys` **before** [Hydra.identify](https://docs.capillarytech.com/docs/react-native-sdk-api-reference#identify). Don't call `identify` before you set the account.

Follow this order:

1. Wait for the SDK to initialise. Use [HydraCore.isSdkInitialized()](https://docs.capillarytech.com/docs/react-native-sdk-api-reference#check-if-hydra-sdk-is-initialized-or-not-on-demand) or [addHydraSdkInitializationResultListener](https://docs.capillarytech.com/docs/react-native-sdk-api-reference#get-callback-for-hydra-sdk-initialization-result). Both set methods reject if you call them before that.
2. Set the account of the user with `setHydraAccountConfig` or `setFirebaseRemoteConfigKeys`, and wait for the promise to resolve.
3. Call `Hydra.identify(...)`.

```typescript
await HydraCore.setHydraAccountConfig(accountConfigForUser);
await Hydra.identify(new HydraUserDetails(customerId));
```

## 3. How switching behaves

* **The SDK switches straight away.** The set methods re-initialise Hydra with the new account and resolve `true`. Setting the account that's already active changes nothing.
* **The chosen account persists.** The SDK saves the account you set (or its key names, for Option A) on the device and uses it on every later launch, in place of what the native initialiser passes. The native initialiser only decides the account for a fresh install.