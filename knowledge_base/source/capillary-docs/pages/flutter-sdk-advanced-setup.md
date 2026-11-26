---
updatedAt: 2026-11-12T06:11:18.000Z
agentTools:
  projectIndex: https://docs.capillarytech.com/llms.txt
---

# Advanced Platform Setup

# Advanced setup

The standard integration pages cover the standard setup. Use the sections below only if your app needs something outside that flow:

* [Other initializers](#other-initializers): custom Firebase Remote Config key names, or passing the account values directly.
* [Multi-Hydra account setup](#multi-hydra-account-setup): one app talking to more than one Hydra account.

<a id="other-initializers"></a>

# Other initializers

[Setting up iOS](https://docs.capillarytech.com/docs/flutter-sdk-install#setting-up-ios) and [Setting up Android](https://docs.capillarytech.com/docs/flutter-sdk-install#setting-up-android) use the default initialization, which reads the account values from Firebase Remote Config under the default key names. Use one of the variants below instead if that doesn't fit your app.

**Where to call the initializer:**

* **iOS:** in `AppDelegate.swift`, **after** `GeneratedPluginRegistrant.register(...)`. Hydra reads `capillary/hydra-config.json` through the plugin registrar, so plugins must already be registered.
  * **App-delegate lifecycle:** in `application(_:didFinishLaunchingWithOptions:)`, after `GeneratedPluginRegistrant.register(with: self)` and before `super.application(...)`, as in the samples below.
  * **UIScene lifecycle:** plugins register in `didInitializeImplicitFlutterEngine(_:)`, after launch, so call the initializer there, right after `GeneratedPluginRegistrant.register(with: engineBridge.pluginRegistry)`. Pass `UIApplication.shared` and `nil` launch options:

    ```swift
    import capillary_hydra_ios

    func didInitializeImplicitFlutterEngine(_ engineBridge: FlutterImplicitEngineBridge) {
      GeneratedPluginRegistrant.register(with: engineBridge.pluginRegistry)
      // keys / remoteConfig built as in the samples below
      HydraNativeAPI.shared.initApplicationWithFirebaseRemoteConfig(UIApplication.shared, didFinishLaunchingWithOptions: nil, firebaseRemoteConfigKeys: keys)
    }
    ```

* **Android:** in your own Application class that extends `HydraApplication`, immediately after `super.onCreate()` (see step 3 of [Setting up Android](https://docs.capillarytech.com/docs/flutter-sdk-install#setting-up-android)).

## 1. Custom Firebase Remote Config key names

Use this when the account values are in Firebase Remote Config under different key names, e.g. to start a [multi-Hydra account setup](#multi-hydra-account-setup) on a non-default account.

### iOS

Build a `HydraFirebaseRemoteConfigKeys` and pass it to `initApplicationWithFirebaseRemoteConfig`. `keyForAccountId`, `keyForBaseUrl`, `keyForSsl`, and `keyForRemoteLogLevel` are required; the org id and gamification keys are optional:

```swift
import capillary_hydra_ios

override func application(
  _ application: UIApplication,
  didFinishLaunchingWithOptions launchOptions: [UIApplication.LaunchOptionsKey: Any]?
) -> Bool {
  GeneratedPluginRegistrant.register(with: self)
  let keys = HydraFirebaseRemoteConfigKeys(
      keyForAccountId: "ind_hydra_account_id",
      keyForBaseUrl: "ind_hydra_base_url",
      keyForSsl: "ind_hydra_ssl_public_key",
      keyForRemoteLogLevel: "ind_hydra_remote_log_level",
      keyForOrgId: "ind_hydra_org_id",
      keyForGamificationKey: "ind_hydra_gamification_key",
      keyForGamificationRegion: "ind_hydra_gamification_region",
      keyForGamificationBaseUrl: "ind_hydra_gamification_base_url"
  )
  HydraNativeAPI.shared.initApplicationWithFirebaseRemoteConfig(application, didFinishLaunchingWithOptions: launchOptions, firebaseRemoteConfigKeys: keys)
  return super.application(application, didFinishLaunchingWithOptions: launchOptions)
}
```

### Android

Build a `HydraFirebaseRemoteConfigKeys` and pass it to `HydraInitializer.initializeUsingFirebaseRemoteConfig`:

```kotlin
import com.capillary.plugins.hydra.HydraApplication
import com.capillary.plugins.hydra.nativeapis.HydraInitializer
import com.capillary.plugins.hydra.nativeapis.HydraFirebaseRemoteConfigKeys

class ExampleApplication : HydraApplication() {
    override fun onCreate() {
        super.onCreate()
        val keys = HydraFirebaseRemoteConfigKeys(
            "ind_hydra_account_id",
            "ind_hydra_base_url",
            "ind_hydra_ssl_public_key",
            "ind_hydra_remote_log_level",
            "ind_hydra_org_id",
            "ind_hydra_gamification_key",
            "ind_hydra_gamification_region",
            "ind_hydra_gamification_base_url"
        )
        HydraInitializer.initializeUsingFirebaseRemoteConfig(this, keys)
        // ...
    }
}
```

## 2. Pass the account values directly

Use this when you get the account values from somewhere other than Firebase Remote Config (your own backend, another CMS, or hardcoded values).

### iOS

Build a `HydraRemoteConfig` and pass it to `initApplication`:

```swift
import capillary_hydra_ios

override func application(
  _ application: UIApplication,
  didFinishLaunchingWithOptions launchOptions: [UIApplication.LaunchOptionsKey: Any]?
) -> Bool {
  GeneratedPluginRegistrant.register(with: self)
  let remoteConfig = HydraRemoteConfig(
      accountId: "your_account_id",
      baseUrl: "your_base_url",
      sslPublicKey: "your_ssl_public_key",
      remoteLogLevel: 4, // Debug level
      orgId: "your_org_id",
      gamificationKey: "your_gamification_key",
      gamificationRegion: "your_gamification_region",
      gamificationBaseUrl: "your_gamification_base_url"
  )
  HydraNativeAPI.shared.initApplication(application, didFinishLaunchingWithOptions: launchOptions, hydraRemoteConfig: remoteConfig!)
  return super.application(application, didFinishLaunchingWithOptions: launchOptions)
}
```

| Parameter           | Required/Optional | Description                                                                                                                                                       |
| ------------------- | ----------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| accountId           | required          | Account Id from the apps team (see [Prerequisites](https://docs.capillarytech.com/docs/flutter-sdk-getting-started#prerequisites)).                               |
| baseUrl             | required          | Base Url (End Point) from the apps team.                                                                                                                          |
| sslPublicKey        | required          | SSL public key from the apps team.                                                                                                                                |
| remoteLogLevel      | required          | Remote log level, 0–5 (see [HydraLogLevel](https://docs.capillarytech.com/docs/flutter-sdk-api-reference#hydraloglevel)).                                         |
| orgId               | optional          | Org Id, required only for the [Anonymous/Visitor Flow](https://docs.capillarytech.com/docs/flutter-setup-overview#anonymous--visitor-flow). Pass `nil` if unused. |
| gamificationKey     | optional          | Gamification Key, required only for [Gamification](https://docs.capillarytech.com/docs/gamification-flutter). Pass `nil` if unused.                               |
| gamificationRegion  | optional          | Gamification Region, required only for [Gamification](https://docs.capillarytech.com/docs/gamification-flutter). Pass `nil` if unused.                            |
| gamificationBaseUrl | optional          | Gamification Base Url, required only for [Gamification](https://docs.capillarytech.com/docs/gamification-flutter). Pass `nil` if unused.                          |

### Android

Build a `HydraRemoteConfig` via its `Builder` and pass it to `HydraInitializer.initialize`:

```kotlin
import com.capillary.plugins.hydra.HydraApplication
import com.capillary.plugins.hydra.nativeapis.HydraInitializer
import com.capillary.plugins.hydra.nativeapis.HydraRemoteConfig

class ExampleApplication : HydraApplication() {
    override fun onCreate() {
        super.onCreate()
        val hydraRemoteConfig = HydraRemoteConfig.Builder(
            "your_account_id", "your_base_url", "your_ssl_public_key", 4 // LogType.DEBUG
        )
            .orgId("your_org_id")
            .gamificationKey("your_gamification_key")
            .gamificationRegion("your_gamification_region")
            .gamificationBaseUrl("your_gamification_base_url")
            .build()
        HydraInitializer.initialize(this, hydraRemoteConfig)
        // ...
    }
}
```

| Parameter (Builder)                   | Required/Optional | Description                                                                                                                                                 |
| ------------------------------------- | ----------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------- |
| accountId (1st positional arg)        | required          | Account Id from the apps team (see [Prerequisites](https://docs.capillarytech.com/docs/flutter-sdk-getting-started#prerequisites)).                         |
| baseURL (2nd positional arg)          | required          | Base Url (End Point) from the apps team.                                                                                                                    |
| sslPublicKey (3rd positional arg)     | required          | SSL public key from the apps team.                                                                                                                          |
| remoteDebugLevel (4th positional arg) | optional          | Remote log level, 0–5 (see [HydraLogLevel](https://docs.capillarytech.com/docs/flutter-sdk-api-reference#hydraloglevel)). Defaults to `0`.                  |
| `.orgId(...)`                         | optional          | Org Id, required only for the [Anonymous/Visitor Flow](https://docs.capillarytech.com/docs/flutter-setup-overview#anonymous--visitor-flow). Omit if unused. |
| `.gamificationKey(...)`               | optional          | Gamification Key, required only for [Gamification](https://docs.capillarytech.com/docs/gamification-flutter). Omit if unused.                               |
| `.gamificationRegion(...)`            | optional          | Gamification Region, required only for [Gamification](https://docs.capillarytech.com/docs/gamification-flutter). Omit if unused.                            |
| `.gamificationBaseUrl(...)`           | optional          | Gamification Base Url, required only for [Gamification](https://docs.capillarytech.com/docs/gamification-flutter). Omit if unused.                          |

<a id="multi-hydra-account-setup"></a>

# Multi-Hydra account setup

Use this when one app talks to more than one Hydra account, e.g. separate accounts for India, the USA and Europe. You need the account details (Account Id, Base Url, SSL public key, and Org Id / Gamification values if you use those features) for **each** account from the apps team.

The native initialization sets the **default** account. From Dart you then switch to another account with one of two `HydraCore` methods, depending on where the account values come from.

## 1. Choose where the account values come from

**Option A: Firebase Remote Config.** Keep the default account's values in the standard keys (`hydra_account_id`, `hydra_base_url`, …; see [Getting Started](https://docs.capillarytech.com/docs/flutter-sdk-getting-started#getting-started)), and publish one extra set of keys per additional account with a prefix of your choice. For example, for India:

* `ind_hydra_account_id`
* `ind_hydra_base_url`
* `ind_hydra_ssl_public_key`
* `ind_hydra_remote_log_level`
* `ind_hydra_org_id` *(if using the Anonymous/Visitor Flow)*
* `ind_hydra_gamification_key` *(if using Gamification)*
* `ind_hydra_gamification_region` *(if using Gamification)*
* `ind_hydra_gamification_base_url` *(if using Gamification)*

Then switch with [HydraCore.setFirebaseRemoteConfigKeys](https://docs.capillarytech.com/docs/flutter-sdk-api-reference#5-set-firebase-remote-config-keys-multi-account-setup), passing a [HydraFirebaseRemoteConfigKeys](https://docs.capillarytech.com/docs/flutter-sdk-api-reference#hydrafirebaseremoteconfigkeys) with that account's key names:

```dart
await HydraCore.setFirebaseRemoteConfigKeys(
  hydraFirebaseRemoteConfigKeys: HydraFirebaseRemoteConfigKeys(
    keyForAccountId: 'ind_hydra_account_id',
    keyForBaseUrl: 'ind_hydra_base_url',
    keyForSsl: 'ind_hydra_ssl_public_key',
    keyForRemoteLogLevel: 'ind_hydra_remote_log_level',
    keyForOrgId: 'ind_hydra_org_id',
    keyForGamificationKey: 'ind_hydra_gamification_key',
    keyForGamificationRegion: 'ind_hydra_gamification_region',
    keyForGamificationBaseUrl: 'ind_hydra_gamification_base_url',
  ),
);
```

This reads the values Firebase Remote Config has **already fetched**. It doesn't fetch them itself, so the prefixed keys must be published in Remote Config. If they aren't, the account isn't switched: on iOS the call returns `false`, but on Android it still returns `true` and only logs "Failed to get values for these keys from Firebase remote config".

**Option B: values you fetch yourself** (your own backend or another CMS). Switch with [HydraCore.setHydraAccountConfig](https://docs.capillarytech.com/docs/flutter-sdk-api-reference#4-set-hydra-account-configuration-multi-account-setup), passing a [HydraAccountConfig](https://docs.capillarytech.com/docs/flutter-sdk-api-reference#hydraaccountconfig):

```dart
await HydraCore.setHydraAccountConfig(
  hydraAccountConfig: HydraAccountConfig(
    accountId: accountId,
    baseUrl: baseUrl,
    sslPublicKey: sslPublicKey,
    remoteLogLevel: HydraLogLevel.off,
    orgId: orgId, // optional, Anonymous/Visitor Flow
    gamificationKey: gamificationKey, // optional, Gamification
    gamificationRegion: gamificationRegion, // optional, Gamification
    gamificationBaseUrl: gamificationBaseUrl, // optional, Gamification
  ),
);
```

## 2. Set the account before identifying the user

In a multi-account setup, call `setHydraAccountConfig` / `setFirebaseRemoteConfigKeys` **before** [Hydra.identify](https://docs.capillarytech.com/docs/flutter-sdk-api-reference#1-identify). Don't call `identify` before the account is set.

The order is:

1. Wait for the SDK to initialize (`onHydraSdkInitializationResult` on your [HydraNativeEventHandler](https://docs.capillarytech.com/docs/flutter-sdk-api-reference#hydranativeeventhandler-class)). With Option A, this also means Firebase Remote Config has fetched its values.
2. Set the user's account with `setHydraAccountConfig` or `setFirebaseRemoteConfigKeys`, and wait for the `Future` to complete.
3. Call `Hydra.identify(...)`.

```dart
await HydraCore.setHydraAccountConfig(hydraAccountConfig: accountConfigForUser);
await Hydra.identify(userDetails: HydraUserDetails(customerId: customerId));
```

## 3. How switching behaves

* **The SDK switches straight away.** The set methods re-initialize Hydra with the new account. Setting the account that's already active changes nothing.
* **The chosen account persists.** The account you set (or its key names, for Option A) is saved on the device and used on every later launch, in place of what the native initialization passes. The native initialization only decides the account for a fresh install.