---
platform: flutter
config_mode: direct
sdk_package: capillary_hydra
sdk_version: 1.1.1-beta.6
modules_covered: [core, push, inapp, inbox_api, inbox_ui, visitor, gamification, multi_account]
modules_missing: []
sources: ["Flutter-Hydra-Integration-Guide pp.1–24 (direct init: Advanced Android Setup pp.6–8, Advanced iOS Setup pp.8–9, HydraCore.setHydraAccountConfig pp.12–13, 21)", "Integration document _ Experience+ pp.52–59 (Gamification Flutter Integration Guide)"]
owner: TBD
last_verified: null
review_status: draft   # drafted from the source docs; not yet SME-verified
---
# Flutter (without Firebase Remote Config: config passed directly)

## Coverage
**What "direct" means for Flutter.** The Hydra account values (Account Id, Base URL, SSL public key, log level, and optionally Org Id and the gamification values) are passed straight to the SDK instead of being read from Firebase Remote Config. The values can come from another CMS or be hardcoded (pp.7–8). The guide documents three ways to pass them:

| Where | API | Source |
|---|---|---|
| Android, native | `HydraRemoteConfig.Builder(...)` + `HydraInitializer.initialize(this, hydraRemoteConfig)` in a `HydraApplication` subclass | pp.6–8 |
| iOS, native | `HydraRemoteConfig(...)` + `HydraNativeAPI.shared.initApplication(..., hydraRemoteConfig:)` in `AppDelegate.swift` | pp.8–9 |
| Dart | `HydraCore.setHydraAccountConfig(hydraAccountConfig:)` with a `HydraAccountConfig` | pp.2, 12–13, 21 |

**What direct mode doesn't change: push still uses Firebase.** Direct mode only replaces Firebase *Remote Config*. The guide's Push Notification section (pp.4–5) has no mode condition, and Flutter push is built on Firebase Cloud Messaging:
- `HydraPushNotification.getFCMToken()` returns "the FCM token" (p.15);
- `onTokenAvailable` fires "when a new FCM token is available" (p.18).

So push in this mode still needs the Firebase registration files (`google-services.json`, `GoogleService-Info.plist`) and the Google Services Gradle plugin. *(Derived from pp.4–5, 15, 18.)* This is **not** the same as native Android direct mode (`android/direct.md`), where push isn't available and Firebase must not be added. Don't carry that rule over to Flutter.

> ⚠️ Gap: the guide never says outright that push works in direct mode. It also doesn't say whether an app that uses neither Remote Config nor push can leave out `google-services.json`, `GoogleService-Info.plist` and the Google Services plugin, in other words whether `capillary_hydra` needs a Firebase configuration just to start. Ask a Capillary engineer before removing Firebase from a Flutter app.

| Module | Status in this mode |
|---|---|
| Core (native or Dart init with direct values, `identify` / `track` / `reset`, user / geo / push-preference updates) | Documented |
| Push notifications (FCM; iOS rich notifications are mandatory) | Documented in a section that isn't mode-specific. Still needs the Firebase (FCM) files *(derived; see above)*. |
| In-App messaging | Documented, not mode-specific: a config flag, a placeholder image, one iOS `AppDelegate` hook (a remote-notification handler). `enable_in_app_messaging_in_flutter` isn't explained and is marked non-functional. |
| Inbox API (`HydraInbox`) / Inbox UI (`HydraInboxUI`) | Documented, not mode-specific. The inbox stores *received notifications*, so it depends on Push. |
| Visitor (anonymous) flow | Documented: pass `orgId` in the direct config |
| Gamification | Documented: pass the gamification values in the direct config. The Integration document's Flutter chapter only describes Remote Config keys; the direct path comes from the Flutter guide. |
| Multi-account | Partly documented: `HydraCore.setHydraAccountConfig` from Dart. How it interacts with native initialisation isn't described. |
| Firebase Remote Config (default keys, prefixed keys, `setFirebaseRemoteConfigKeys`) | Not used in this mode. See `flutter/firebase.md`. |

## Requirements
- Packages (from pub.dev): `capillary_hydra` and `capillary_hydra_platform_interface`, both at `^{{sdk_version}}`. Package page: `https://pub.dev/packages/capillary_hydra`.
- Android:
  - an Application class of your own that extends `HydraApplication` (the guide's sample is Kotlin only),
  - the application theme must derive from AppCompat (step 8),
  - Gradle with Kotlin DSL or Groovy.
- iOS:
  - CocoaPods with `use_frameworks!`, or Swift Package Manager,
  - Xcode, for `AppDelegate.swift` and, for push, the capabilities and Notification Service Extension.
- For push only (see Coverage):
  - a Firebase project with this app registered,
  - the Google Services Gradle plugin at the version the guide shows, `4.4.2`,
  - access to `developer.apple.com`.

> ⚠️ Gap: the guide doesn't state the minimum Flutter / Dart SDK, Android minSdk / compileSdk, AGP / Gradle / Kotlin, iOS deployment target, Xcode or CocoaPods versions. Ask a Capillary engineer before giving numbers.

## Prerequisites
See `_shared/prerequisites.md` for the common exchange. For Flutter in this mode:
- **Client gives Capillary's apps team:**
  - the iOS bundle ID (`{{bundle_id}}`),
  - the Android applicationId (`{{application_id}}`),
  - the app signature (SHA256) from the Android app signing report.
- **Capillary gives the client:**
  - Account Id: **required**
  - Base URL (end point): **required**
  - SSL public key: **required**
  - Org Id: optional, only for the visitor flow
  - Gamification Key, Gamification Region and Gamification Base URL: only for gamification
- **Where the app gets these values:** from a CMS other than Firebase Remote Config, or hardcoded (pp.7–8).
- **CRM:** the `customerId` the app sends must match the **Account Linking Identifier** configured in Capillary CRM (see `_shared/prerequisites.md`).
- **Loyalty View only:** the client's backend must supply a Capillary B2B short-lived token after login (see `_shared/prerequisites.md`).
- **Banner / Embed / Loyalty IDs:** the Flutter sources don't say where these come from. `_shared/prerequisites.md` says they're configured in the gamification dashboard.
- **Push only:** a Firebase project with the app registered, and access to `developer.apple.com` (Modules → Push).
- **Example app:** the guide points to an example app on the package's pub.dev page: `https://pub.dev/packages/capillary_hydra/example`.
- The Flutter guide doesn't ask for access to the private native SDK repositories listed in `_shared/prerequisites.md`.

`_shared/prerequisites.md` lists Org Id as "required … in direct mode". That comes from the native platform guides. In the Flutter guide's direct initialisers, `orgId` is optional and only needed for the visitor flow (pp.7, 8–9, 21).

> ⚠️ Source doc correction: Getting Started (p.1) says it's "mandatory" to get Account Id, SSL public key, Base URL and remote log level "from a remote configuration tool (CMS tool)". The direct-init sections (pp.7, 8) say the values can come from "a CMS other than Firebase Remote Config, **or hardcoded values**". Hardcoding is allowed by the samples. Whether it's acceptable for production is unconfirmed. *Pending SME confirmation.*

## Steps

### 1. Add the packages to `pubspec.yaml`
Capillary announces when a new version is available.

```yaml file=pubspec.yaml
dependencies:
  capillary_hydra: ^{{sdk_version}}
  capillary_hydra_platform_interface: ^{{sdk_version}}
```

Or run:

```bash
flutter pub add capillary_hydra:^{{sdk_version}} capillary_hydra_platform_interface:^{{sdk_version}}
```

### 2. Create `capillary/hydra-config.json`
Create a folder named `capillary` at the root of the Flutter project. Inside it, create `hydra-config.json` with these contents:

```json file=capillary/hydra-config.json
{
  "console_log_level": 4,
  "enable_in_app_messaging": false,
  "enable_inbox_api": false,
  "enable_inbox_ui": false,
  "use_default_inbox_ui_config": true,
  "max_notification_count": 200,
  "hydra_notification_color": "#FF03DAC5",
  "enable_in_app_messaging_in_flutter": false
}
```

Set the values as needed:

| Key | Type | Default | Platform | Meaning |
|---|---|---|---|---|
| `console_log_level` | number | `4` | Android & iOS | Console log level, 0–5: 0=off, 1=error, 2=warn, 3=info, 4=debug, 5=verbose |
| `enable_in_app_messaging` | boolean | `false` | Android & iOS | `true` enables in-app messaging. Needs the in-app placeholder image (Modules → In-App). |
| `enable_in_app_messaging_in_flutter` | boolean | `false` | Android only | **Currently non-functional. Don't enable it in production.** |
| `enable_inbox_api` | boolean | `false` | Android & iOS | `true` enables the Inbox API (Modules → Inbox) |
| `enable_inbox_ui` | boolean | `false` | Android & iOS | `true` enables the built-in notification center (Modules → Inbox) |
| `use_default_inbox_ui_config` | boolean | `true` | iOS only | Use the SDK's default notification center layout |
| `max_notification_count` | number | `200` | Android & iOS | Maximum number of notifications kept in the inbox / notification center |
| `hydra_notification_color` | string | – | Android only | Notification tint colour, e.g. `"#FF03DAC5"` (Modules → Push) |

The console log level is set here. In this mode the **remote** log level isn't a Remote Config key. Pass it in the direct config instead:
- the 4th argument of the Android `Builder` (step 6),
- `remoteLogLevel` on iOS (step 11),
- `remoteLogLevel` in `HydraAccountConfig` (step 12).

*(Derived: the guide describes `hydra_remote_log_level` only for Remote Config, p.10.)*

### 3. Declare the config folder as assets
In `pubspec.yaml`, declare the `capillary/` folder as assets. Add its `icons` subfolder once you add the icon images described in Modules (Push, In-App, Inbox UI).

```yaml file=pubspec.yaml
flutter:
  assets:
    - capillary/
    - capillary/icons/
```

### 4. Fetch the packages
```bash
flutter pub get
```

### 5. Call `HydraInitializer.initialize()` in `main()`, before `runApp`
The guide gives this step for every app, in Setup for Flutter, before any choice of config source.

```dart file=lib/main.dart
import 'package:capillary_hydra/hydra.dart';
import 'package:flutter/material.dart';

void main() {
  WidgetsFlutterBinding.ensureInitialized();
  HydraInitializer.initialize();
  runApp(const MyApp());
}
```

This Dart `HydraInitializer` (from `package:capillary_hydra/hydra.dart`) is a different class from the native Android `com.capillary.plugins.hydra.nativeapis.HydraInitializer` in step 6. *(Derived from the imports.)*

### 6. Android: create an Application class that passes the values directly
Flutter doesn't use a custom Application class by default, but the Hydra SDK needs one to run its initialisation.
1. Create a class that **extends `HydraApplication`** (if you already have an Application class, change it to extend `HydraApplication`).
2. In `onCreate()`, build a `HydraRemoteConfig` with its `Builder`.
3. Pass it to `HydraInitializer.initialize`, **immediately after `super.onCreate()`**.

Builder arguments:
- **Required:** `accountId`, `baseURL`, `sslPublicKey`.
- **Remote debug level:** the 4th argument. It defaults to `0`; the sample passes `4` (debug).
- **Optional:** `orgId` (visitor flow); `gamificationKey` / `gamificationRegion` / `gamificationBaseUrl` (gamification).

```kotlin file=android/app/src/main/kotlin/<your-package>/ExampleApplication.kt
import com.capillary.plugins.hydra.HydraApplication
import com.capillary.plugins.hydra.nativeapis.HydraInitializer
import com.capillary.plugins.hydra.nativeapis.HydraRemoteConfig

class ExampleApplication : HydraApplication() {
    override fun onCreate() {
        super.onCreate()
        val hydraRemoteConfig = HydraRemoteConfig.Builder(
            "{{account_id}}", "{{base_url}}", "{{ssl_public_key}}", 4 // LogType.DEBUG
        )
            .orgId("{{org_id}}")
            .gamificationKey("{{gamification_key}}")
            .gamificationRegion("{{gamification_region}}")
            .gamificationBaseUrl("{{gamification_base_url}}")
            .build()
        HydraInitializer.initialize(this, hydraRemoteConfig)
        // ...
    }
}
```

The guide shows this in Kotlin only.

> ⚠️ Gap: the samples use hardcoded strings. The guide doesn't show how to fetch values from another CMS before this call in `Application.onCreate()`, for example if the fetch is asynchronous. Ask a Capillary engineer.

### 7. Android: register your Application class
In `AndroidManifest.xml`, point `android:name` at your class's **fully qualified name** (package + class name):

```xml file=android/app/src/main/AndroidManifest.xml
<application
    android:name="<your.package>.ExampleApplication"
    ...>
```

Don't point the manifest straight at `com.capillary.plugins.hydra.HydraApplication` in this mode. When the class is exactly `HydraApplication`, the SDK initialises automatically from the **default Firebase Remote Config keys**. *(Derived from pp.3 and 6.)*

### 8. Android: set an AppCompat theme
The Hydra plugin requires the application theme to derive from AppCompat:

```xml file=android/app/src/main/AndroidManifest.xml
<application
    ...
    android:theme="@style/Theme.AppCompat.DayNight.NoActionBar">
```

### 9. iOS: add Hydra to the Podfile (CocoaPods only)
**If Swift Package Manager is enabled in the project, skip this step.**

At the top of `ios/Podfile`, add:

```ruby file=ios/Podfile
require_relative './.symlinks/plugins/capillary_hydra_ios/script/HydraPods.rb'
```

In the `Runner` target, add `hydra_pods`:

```ruby file=ios/Podfile
target 'Runner' do
  use_frameworks!

  hydra_pods
  flutter_install_all_ios_pods File.dirname(File.realpath(__FILE__))
  target 'RunnerTests' do
    inherit! :search_paths
  end
end
```

> ⚠️ Gap: for Swift Package Manager projects, the guide only says to skip the Podfile steps. It gives no SPM-specific steps. Ask a Capillary engineer.

### 10. iOS: install pods
In the `ios` folder, run:

```bash
pod install
```

### 11. iOS: initialise the SDK in `AppDelegate.swift` with the values
By default the plugin initialises the SDK automatically from the default Firebase Remote Config keys. To pass values directly, initialise it yourself in `AppDelegate.swift`, **after `GeneratedPluginRegistrant.register(with:)` and before `super.application(...)`**.

`HydraRemoteConfig` arguments:
- **Required:** `accountId`, `baseUrl`, `sslPublicKey`.
- **Optional:** `orgId` (visitor flow) and the gamification values.

```swift file=ios/Runner/AppDelegate.swift
import capillary_hydra_ios

override func application(
  _ application: UIApplication,
  didFinishLaunchingWithOptions launchOptions: [UIApplication.LaunchOptionsKey: Any]?
) -> Bool {
  GeneratedPluginRegistrant.register(with: self)
  let remoteConfig = HydraRemoteConfig(
      accountId: "{{account_id}}",
      baseUrl: "{{base_url}}",
      sslPublicKey: "{{ssl_public_key}}",
      remoteLogLevel: 4, // Debug level
      orgId: "{{org_id}}",
      gamificationKey: "{{gamification_key}}",
      gamificationRegion: "{{gamification_region}}",
      gamificationBaseUrl: "{{gamification_base_url}}"
  )
  HydraNativeAPI.shared.initApplication(application, didFinishLaunchingWithOptions: launchOptions, hydraRemoteConfig: remoteConfig!)
  return super.application(application, didFinishLaunchingWithOptions: launchOptions)
}
```

> ⚠️ Gap: the guide says `orgId` and the gamification values are optional but doesn't show the call without them. It doesn't say whether to leave the arguments out or pass `nil`. The sample also force-unwraps `remoteConfig!`, so `HydraRemoteConfig(...)` appears to be failable, but the guide doesn't say when it returns `nil`. Ask a Capillary engineer.

### 12. (Alternative) Pass the values from Dart with `HydraCore.setHydraAccountConfig`
The guide also lets you pass the values from Dart instead of natively (p.2). Use this "when you're fetching Hydra account values yourself rather than via Firebase Remote Config" (p.12).

`HydraAccountConfig` fields:
- **Required:** `accountId`, `baseUrl`, `sslPublicKey`, `remoteLogLevel` (a `HydraLogLevel`).
- **Optional:** `orgId` (visitor flow); `gamificationKey`, `gamificationRegion`, `gamificationBaseUrl` (gamification).

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

bool result = await HydraCore.setHydraAccountConfig(hydraAccountConfig: hydraAccountConfig);
```

The call returns whether the account config update was requested successfully. Fill the variables with `{{account_id}}`, `{{base_url}}`, `{{ssl_public_key}}`, `{{org_id}}`, `{{gamification_key}}`, `{{gamification_region}}` and `{{gamification_base_url}}` from your CMS.

> ⚠️ Gap: the guide doesn't describe the native setup to pair with the Dart-only path. For example: should Android still use a `HydraApplication` subclass, and with which initialiser? Exactly `HydraApplication` would auto-initialise from the default Remote Config keys. It also doesn't say what happens before `setHydraAccountConfig` is called, or whether the values persist across launches. Until a Capillary engineer confirms, prefer the native initialisers in steps 6 and 11.

### 13. Register a native event handler and wait for initialisation
Before using any `capillary_hydra` API, make sure the Hydra SDK has initialised successfully.
1. Write a class that extends or implements `HydraNativeEventHandler`. Override only the callbacks you need; all of them have empty default bodies.
2. Register it:

```dart
HydraNativeEvents.addEventHandler(handler);
```

The initialisation result arrives through:

```dart
void onHydraSdkInitializationResult({required bool success, String? error})
```

The full callback list is in the API Reference.

### 14. Identify, track and reset the user
**Identify.** Call `Hydra.identify` with a `HydraUserDetails`. `customerId` is required and **must match the Account Linking Identifier configured in Capillary CRM**: mobile, email, InTouchUserId, externalId or FCMToken. The setting is at *Organisation Settings → Omni Channel Settings → Channel Configurations → MAPP_SDK → Account Linking Identifier*.

```dart
import 'package:capillary_hydra/hydra.dart';
import 'package:capillary_hydra_platform_interface/capillary_hydra_platform_interface.dart';

HydraUserDetails userDetails = HydraUserDetails(
  customerId: '8888888888',
  firstName: 'FirstName',
  lastName: 'LastName',
  email: 'test@capillarytech.com',
  phoneNumber: '918888888888',
);

bool result = await Hydra.identify(userDetails: userDetails);
```

`identify` also takes an optional `customAttributes` (`Map<String, dynamic>?`), for custom attributes used in analytics.

**Track** a custom event:

```dart
bool result = await Hydra.track(eventName: 'product_viewed', attributes: {'productId': 'abc123'});
```

**Reset** (sign out) the current user:

```dart
bool result = await Hydra.reset(customerId: '8888888888');
```

Each call returns a `Future<bool>` that says whether the request was **made** successfully.

### 15. (Optional) Update the user, geo config and push preferences
These are static functions on `HydraCore`, from `import 'package:capillary_hydra/hydra.dart';`.

```dart
bool updateUserResult = await HydraCore.updateUser(
  userDetails: updatedUserDetails,
  customData: {"Key": "Value"},
  subscriptions: [
    {"channel": "channel1", "type": "topic1", "priority": 1},
  ],
);
```
`subscriptions` is a list of subscriptions. According to the guide, each one includes `channel`, `accountId`, `priority`, `type` and `sourcename`.

```dart
HydraGeoConfig geoConfig = HydraGeoConfig(
  city: "Bangalore",
  country: "India",
  countryCode: "IN",
  timezone: "Asia/Kolkata",
);

bool updateGeoConfigResult = await HydraCore.updateGeoConfig(config: config);
```
In the guide, the geo-config usage passes `config: config` while the model sample names its variable `geoConfig`. Pass your `HydraGeoConfig` instance.

```dart
HydraPushPreferences pushPreferences = HydraPushPreferences(
  promPushEnabled: false,
  transPushEnabled: true,
);

bool result = await HydraCore.updatePushPreferences(
  preferences: pushPreferences,
  customerId: "8888888888",
);
```

## Modules

### Push
Direct mode only replaces Remote Config. Flutter push runs on Firebase Cloud Messaging, so the Firebase steps below still apply. *(Derived; see the Coverage callout.)*

**1. Register the app with Firebase and add the config files**
1. Register the app on Firebase. The guide links to `https://support.google.com/appsheet/answer/10104995?hl=en`.
2. Download `google-services.json` and `GoogleService-Info.plist`. **Don't make any code changes the Firebase console suggests while you generate these files.**
3. **iOS:** add `GoogleService-Info.plist` to the iOS project using Xcode.
4. **Android:** add `google-services.json` to the `android/app` folder.
5. **Android:** declare the Google Services plugin in the root `plugins` block.

   Kotlin DSL:

   ```kotlin file=android/settings.gradle.kts
   id("com.google.gms.google-services") version "4.4.2" apply false
   ```

   Groovy:

   ```groovy file=android/settings.gradle
   id 'com.google.gms.google-services' version '4.4.2' apply false
   ```
6. **Android:** apply the plugin in the app's `plugins` block.

   Kotlin DSL:

   ```kotlin file=android/app/build.gradle.kts
   id("com.google.gms.google-services")
   ```

   Groovy:

   ```groovy file=android/app/build.gradle
   id 'com.google.gms.google-services'
   ```

> ⚠️ Gap: the guide's "this link" for registering the app on Firebase goes to a Google AppSheet help article (`https://support.google.com/appsheet/answer/10104995?hl=en`), not to Firebase's own documentation. Check with a Capillary engineer which registration guide is intended.

**2. iOS: capabilities**
- On `developer.apple.com`, make sure the **Push Notification** capability is added to the app identifier.
- In Xcode, open the app target's **Signing & Capabilities** and add:
  - **Push Notification**,
  - **Background Modes**, with **Background fetch** and **Remote notifications** enabled.

**3. iOS: Notification Service Extension (rich notifications are mandatory)**
1. In Xcode, add a new **Notification Service Extension** target in the project settings. Xcode derives the extension's bundle ID by appending the extension's product name to the main target's bundle ID. Register that new bundle ID on `developer.apple.com`.
2. Add the **App Groups** capability in Signing & Capabilities to **both** the main target and the extension target. Use the same group in both, in the form `group.<runner_target_bundle_id>.hydra`, for example `group.{{bundle_id}}.hydra`. Create this App Group on `developer.apple.com` for both identifiers.
3. **CocoaPods only (skip if Swift Package Manager is enabled):** in `ios/Podfile`, add `extension_pods` inside the new extension target (for example `HydraRichNotification`). Then run `pod install` again, as in step 10.

   ```ruby file=ios/Podfile
   target "HydraRichNotification" do
     use_frameworks!
     extension_pods
   end
   ```
4. Replace the **entire** contents of the extension's `NotificationService.swift` with:

   ```swift file=ios/HydraRichNotification/NotificationService.swift
   import UserNotifications
   import HydraPushNotificationServiceExtension

   class NotificationService: UNNotificationServiceExtension {
       let service: HydraRemoteNotificationService = .init()

       override func didReceive(_ request: UNNotificationRequest, withContentHandler contentHandler: @escaping (UNNotificationContent) -> Void) {
           service.didReceive(request, withContentHandler: contentHandler)
       }

       override func serviceExtensionTimeWillExpire() {
           service.serviceExtensionTimeWillExpire()
       }
   }
   ```

   The folder is named after your extension target. `HydraRichNotification` is the guide's example name.

> ⚠️ Gap: with Swift Package Manager, the guide says to skip the `extension_pods` step but doesn't say how the extension target gets `HydraPushNotificationServiceExtension`. Ask a Capillary engineer.

**4. Android: notification colour.** Set `hydra_notification_color` in `capillary/hydra-config.json` (step 2), for example `"#FF03DAC5"`.

**5. Notification small icon.** If `capillary/icons/` doesn't exist yet, create it. Add an image named `hydra_notification_small_icon` (png, jpg or jpeg; png recommended). This is the small icon shown in the notification drawer. Make sure `capillary/icons/` is declared in assets (step 3).

**6. Ask for permission and get the token (Dart).** Call `requestPermission` before you can receive push:

```dart
bool granted = await HydraPushNotification.requestPermission();
```
It returns whether permission was granted. It can also throw.

To get the FCM token on demand:

```dart
String fcmToken = await HydraPushNotification.getFCMToken();
```
**If no FCM token is available, it throws an error.** You can also get the token from the `onTokenAvailable({required String token})` callback on your `HydraNativeEventHandler`, which fires whenever a new FCM token is available.

**7. Notification callbacks** on `HydraNativeEventHandler`:
- `onHydraNotificationReceived`, `onHydraNotificationShown`, `onHydraNotificationDismissed`: fired when a Hydra notification is received, or is shown / dismissed in the system tray.
- `onHydraNotificationClicked({HydraNotificationCTA? cta, HydraNotification? notification})`: fired when a Hydra notification is clicked in the system tray, in the SDK's built-in notification center, or in an in-app message.
- `onNonHydraNotificationReceived` / `onNonHydraNotificationClicked`: the same, for push notifications that don't come from Hydra.

### In-App
1. Set `enable_in_app_messaging` to `true` in `hydra-config.json`.
2. Add an image named `hydra_in_app_placeholder` to `capillary/icons` (png, jpg or jpeg).
3. **iOS:** in `AppDelegate.swift`, add `import capillary_hydra_ios` at the top. You already have it if you did step 11. Then add this function:

   ```swift file=ios/Runner/AppDelegate.swift
   override func application(_ application: UIApplication, didReceiveRemoteNotification userInfo: [AnyHashable: Any], fetchCompletionHandler completionHandler: @escaping (UIBackgroundFetchResult) -> Void) {
       HydraNativeAPI.shared.application(application, didReceiveRemoteNotification: userInfo, fetchCompletionHandler: completionHandler)
   }
   ```

Clicks on in-app messages arrive in `onHydraNotificationClicked`.

> ⚠️ Gap: the iOS in-app hook is a remote-notification handler. The guide doesn't say whether in-app messaging works in direct mode without the Push / Firebase setup (Modules → Push). Ask a Capillary engineer.

> ⚠️ Gap: the `hydra-config.json` table says to "see InApp Messaging" for `enable_in_app_messaging_in_flutter`, but the InApp Messaging section never mentions that key. What it does is undocumented. The table marks it as currently non-functional, so keep it `false`. Ask a Capillary engineer.

### Inbox
The SDK stores **received notifications** in a local database, so the inbox depends on the Push setup (Modules → Push). *(Derived from p.9.)*

**Inbox API**
1. Set `enable_inbox_api` to `true` in `hydra-config.json`.
2. **iOS:** the Notification Service Extension must be set up (Modules → Push, item 3).

`max_notification_count` (default 200) caps how many notifications are kept. Use `HydraInbox`:

```dart
List<HydraNotification> notifications = await HydraInbox.getInboxMessages();
int unreadNotificationCount = await HydraInbox.getUnreadInboxMessagesCount();
bool marked = await HydraInbox.markInboxMessageAsRead(notification: notification);
bool deleted = await HydraInbox.deleteInboxMessage(notification: notification);
bool deleted = await HydraInbox.deleteAllInboxMessages();
```
These lines are the guide's individual usage samples, gathered here. Rename the variables if you use more than one in the same scope. `notification` must be an item from the list returned by `getInboxMessages`.

There is no dedicated "inbox updated" event. To refresh your UI, use `onHydraNotificationReceived` or `onNotificationCenterDismissed`, or poll `HydraInbox` on demand.

**Inbox UI** (the SDK's built-in notification center)
1. Enable the Inbox API (above).
2. Set `enable_inbox_ui` to `true` in `hydra-config.json`.
3. Add an image named `hydra_inbox_ui_placeholder` to `capillary/icons` (png, jpg or jpeg).

```dart
HydraInboxUI.showNotificationCenter();
await HydraInboxUI.hideNotificationCenterIfShowing();
```
`onNotificationCenterDismissed()` fires when the built-in notification center is dismissed. On iOS, `use_default_inbox_ui_config` (default `true`) selects the SDK's default layout.

> ⚠️ Gap: the guide doesn't say what happens when `use_default_inbox_ui_config` is `false`, or how to customise the notification center. Ask a Capillary engineer.

### Visitor
The SDK supports an anonymous visitor flow. A user moves through these states: `none` → `visitor` (anonymous) → `merged` / `legacyRegistered` (identified) → `signedOut`. The flow needs the Org Id, passed the same way as Account Id / Base URL / SSL public key. In this mode, use:
- **Android:** `.orgId("{{org_id}}")` on `HydraRemoteConfig.Builder` (step 6);
- **iOS:** `orgId: "{{org_id}}"` in `HydraRemoteConfig` (step 11);
- **Dart:** `orgId` in `HydraAccountConfig` (step 12).

Then:
1. Check whether the visitor flow is enabled for the account:

   ```dart
   bool enabled = await Hydra.isVisitorFlowEnabled();
   ```
2. Get the current state:

   ```dart
   UserState? state = await Hydra.getCurrentUserState();
   ```
3. Get the visitor details (`visitorId`):

   ```dart
   HydraVisitorInfo? info = await Hydra.getVisitorDetails();
   ```
4. Subscribe to the visitor-flow lifecycle callbacks on your `HydraNativeEventHandler`:
   - `onConfigFetched({required bool isVisitorFlowEnabled})`
   - `onLegacyFlowReady()`
   - `onVisitorSessionReady()`
   - `onUserStateChanged({UserState? userState})`

`Hydra.identify` / `track` / `reset` (step 14) are also part of this flow.

> ⚠️ Gap: the guide doesn't explain the difference between `legacyRegistered` and `merged`, when `onLegacyFlowReady` fires rather than `onVisitorSessionReady`, or what the app should do in each state. Ask a Capillary engineer.

### Gamification
Gamification adds Floating Button, Popup and Bottom Sheet campaigns, plus Banner, Embed and Loyalty widgets placed directly as Flutter widgets. It's part of the `capillary_hydra` package; no extra package is needed.

> ⚠️ Source doc correction: the Integration document (p.53) gives the minimum version for gamification as "1.1.0 (To be released)", and its checklist (p.58) says "1.1.0 (next release) or later". The Flutter guide (p.2), which documents gamification, pins `^1.1.1-beta.6`. Use the Flutter guide's version (`{{sdk_version}}`). Whether a stable 1.1.0 with gamification has shipped isn't confirmed. *Pending SME confirmation.*

**1. Configure.** Pass the gamification values in the direct config, "configured the same way as the base account details" (Flutter guide p.10):
- **Android:** `.gamificationKey("{{gamification_key}}")`, `.gamificationRegion("{{gamification_region}}")`, `.gamificationBaseUrl("{{gamification_base_url}}")` on `HydraRemoteConfig.Builder` (step 6);
- **iOS:** the `gamificationKey:`, `gamificationRegion:` and `gamificationBaseUrl:` arguments of `HydraRemoteConfig` (step 11);
- **Dart:** `gamificationKey`, `gamificationRegion`, `gamificationBaseUrl` in `HydraAccountConfig` (step 12).

The Integration document's Flutter chapter (pp.53–54) only describes the Remote Config keys. It says the key and region are mandatory, the URL is optional, and "HydraGamification will remain disabled if either mandatory value is missing". *(Derived: the same values are needed when passed directly.)*

> ⚠️ Source doc correction: the Integration document (p.54) says the gamification URL is **optional** and only key and region are mandatory. The Flutter guide (p.1) lists Gamification Base Url among the values gamification needs, and its `HydraAccountConfig` table (p.21) marks `gamificationBaseUrl` "Required only for Gamification". Treat key and region as mandatory. Whether the base URL can be left out is unconfirmed. *Pending SME confirmation.*

**2. Report the current screen (mandatory for screen-targeted campaigns).** Campaign visibility and eligibility depend on the screen that's currently reported.
- When a gamification-related screen appears, call `Hydra.gamificationScreenAppeared(screenName: ...)`.
- When it disappears, call `Hydra.gamificationScreenDisappeared(screenName: ...)`.
- **Pass the same `screenName` to both calls.**

```dart
Hydra.gamificationScreenAppeared(screenName: 'HomeScreen');
// ... later, when the screen unmounts:
Hydra.gamificationScreenDisappeared(screenName: 'HomeScreen');
```

For a normal screen, report it from `initState` / `dispose`:

```dart
@override
void initState() {
    super.initState();
    Hydra.gamificationScreenAppeared(screenName: 'SampleScreenName');
}

@override
void dispose() {
    Hydra.gamificationScreenDisappeared(screenName: 'SampleScreenName');
    super.dispose();
}
```

Some screens stay mounted underneath pushed routes, for example a persistent Home tab. For those, `initState` / `dispose` don't fire when the screen regains focus. Use a `RouteObserver` with `RouteAware`, and also observe the app lifecycle, so the campaign is re-evaluated when the app goes to the background or foreground while that screen is still current:

```dart
final RouteObserver<PageRoute<dynamic>> routeObserver =
        RouteObserver<PageRoute<dynamic>>();

// Register once on MaterialApp:
MaterialApp(navigatorObservers: [routeObserver], ...);

class _HomePageState extends State<HomePage>
        with RouteAware, WidgetsBindingObserver {
    bool _isCurrentRoute = true;

    @override
    void didChangeAppLifecycleState(AppLifecycleState state) {
        if (!_isCurrentRoute) return;
        if (state == AppLifecycleState.resumed) {
            Hydra.gamificationScreenAppeared(screenName: 'SampleScreenName');
        } else if (state == AppLifecycleState.paused) {
            Hydra.gamificationScreenDisappeared(screenName: 'SampleScreenName');
        }
    }

    @override
    void didPopNext() {
        _isCurrentRoute = true;
        Hydra.gamificationScreenAppeared(screenName: 'SampleScreenName');
    }

    @override
    void didPushNext() {
        _isCurrentRoute = false;
        Hydra.gamificationScreenDisappeared(screenName: 'SampleScreenName');
    }
}
```

> ⚠️ Source doc correction: the Integration document's samples (pp.54–55) call `Hydra.gamificationScreenDisappeared()` with **no argument**. The Flutter guide declares `gamificationScreenDisappeared({required String screenName})` (p.15) and says to pass the same `screenName` to both calls (pp.10, 15). The samples above pass `screenName`, following the Flutter guide. *Pending SME confirmation.*

> ⚠️ Gap: the `RouteAware` sample doesn't show where the State subscribes to `routeObserver` or registers itself as a `WidgetsBindingObserver`, or where it unsubscribes. Flutter only calls those callbacks once the State is subscribed and registered. Ask a Capillary engineer for the complete sample.

**3. Set the Capillary token (required for Loyalty View).** Set the Capillary B2B short-lived token **before** rendering the Loyalty View. Without a valid token, loyalty content may not be shown.

```dart
Hydra.setCapToken(token: 'token');
```

**4. Automatic experiences.** Once a screen is reported, `capillary_hydra` shows campaigns targeted at it, with no further code:
- Floating Button campaigns
- Popup campaigns
- Bottom Sheet campaigns

**5. Optional widgets.** These Flutter widgets are backed by native `PlatformView`s:
- `GamificationBannerView({ required String bannerId, void Function(double height)? onHeightChanged })`
- `GamificationEmbedView({ required String embedId, void Function(double height)? onHeightChanged })`
- `GamificationLoyaltyView({ required String loyaltyId })`

*Banner View.* Pass a unique ID. Register `onHeightChanged` to update the height as the content loads:

```dart file=lib/gamification_section.dart
import 'package:capillary_hydra/hydra.dart';
import 'package:flutter/material.dart';

class GamificationSection extends StatefulWidget {
  const GamificationSection({super.key});
  @override
  State<GamificationSection> createState() => _GamificationSectionState();
}

class _GamificationSectionState extends State<GamificationSection> {
  double _bannerHeight = 300;

  @override
  Widget build(BuildContext context) {
    return SizedBox(
      height: _bannerHeight,
      child: GamificationBannerView(
        bannerId: '{{banner_id}}',
        onHeightChanged: (height) {
          if (height > 0) setState(() => _bannerHeight = height);
        },
      ),
    );
  }
}
```
The Integration document's version of this snippet (p.57) also checks `mounted` before `setState`: `if (height > 0 && mounted) { setState(() => bannerHeight = height); }`.

*Embed View.* The same pattern, using `GamificationEmbedView` and `embedId`. `embedHeight` is a state field, like `bannerHeight`:

```dart
SizedBox(
    height: embedHeight,
    child: GamificationEmbedView(
        embedId: '{{embed_id}}',
        onHeightChanged: (height) {
            if (height > 0 && mounted) {
                setState(() => embedHeight = height);
            }
        },
    ),
)
```

*Loyalty View.* Unlike Banner and Embed, `GamificationLoyaltyView` fills whatever size it's given and **never reports a height change**. Give it an explicit size: a fixed-height parent such as `SizedBox`, or `Expanded`. **Call `Hydra.setCapToken(token: ...)` before mounting it.** The native SDK can't bind the Loyalty view unless a cap token is already set.

```dart
SizedBox(
    height: 611,
    child: GamificationLoyaltyView(loyaltyId: '{{loyalty_id}}'),
)
```

### Multi-account
In this mode, the documented way to use another Hydra account is to pass that account's values from Dart with `HydraCore.setHydraAccountConfig`, using the code in step 12 with the other account's values. The guide labels this API "(multi-account setup)" and says to use it "when you're fetching Hydra account values yourself rather than via Firebase Remote Config" (p.12).

The prefixed-key approach (`ind_hydra_*` keys, `HydraFirebaseRemoteConfigKeys`, `HydraCore.setFirebaseRemoteConfigKeys`) is for Remote Config only. See `flutter/firebase.md`.

> ⚠️ Gap: the guide doesn't say how `setHydraAccountConfig` interacts with an SDK already initialised natively (steps 6 and 11), when to call it relative to `identify`, or whether the current user must be reset before switching account. Ask a Capillary engineer.

## Verification
What the sources support:
- **SDK initialised:** `onHydraSdkInitializationResult` on your registered `HydraNativeEventHandler` reports `success: true`. On failure it reports `success: false` with an optional `error`. With the Dart path (step 12), `setHydraAccountConfig` also returns whether the update was requested successfully.
- **Push** (needs the Firebase setup in Modules → Push):
  - `HydraPushNotification.requestPermission()` returns `true` when permission is granted.
  - `onTokenAvailable(token:)` fires, or `HydraPushNotification.getFCMToken()` returns a token. It throws if no token is available.
  - When a Hydra push arrives, `onHydraNotificationReceived` / `onHydraNotificationShown` fire.
- **Core calls:** `identify`, `track`, `reset`, `updateUser`, `updateGeoConfig` and `updatePushPreferences` return `true` when the request was made successfully. That isn't confirmation that Capillary processed it.
- **Inbox:** after a Hydra push is received, `HydraInbox.getInboxMessages()` returns it and `getUnreadInboxMessagesCount()` counts it.
- **Inbox UI:** `HydraInboxUI.showNotificationCenter()` shows the built-in notification center. `onNotificationCenterDismissed()` fires when it's closed.
- **Visitor flow:**
  - `Hydra.isVisitorFlowEnabled()` or `onConfigFetched(isVisitorFlowEnabled:)` says whether the account has the visitor flow enabled;
  - `getCurrentUserState()` and `getVisitorDetails()` show the state and `visitorId`.
- **Gamification:**
  - after the required steps, Floating Button, Bottom Sheet and Popup campaigns appear automatically on reported screens that have campaigns configured;
  - Banner, Embed and Loyalty content appears where you placed the widgets.
- **Logs:**
  - set `console_log_level` to `4` (debug) or `5` (verbose) in `hydra-config.json` for console logs;
  - set the remote log level in the direct config: Builder 4th argument, `remoteLogLevel`, or `HydraLogLevel`.

**Direct-mode checklist** (assembled from the steps above):
- `capillary_hydra` and `capillary_hydra_platform_interface` at `^{{sdk_version}}`.
- `capillary/hydra-config.json` created, and `capillary/` (plus `capillary/icons/` when used) declared in assets.
- `HydraInitializer.initialize()` called in `main()`.
- Android:
  - an Application class extending `HydraApplication` calls `HydraInitializer.initialize(this, hydraRemoteConfig)` right after `super.onCreate()`;
  - it's registered by fully qualified name in the manifest;
  - the theme is AppCompat.
- iOS: `HydraNativeAPI.shared.initApplication(..., hydraRemoteConfig:)` is called after `GeneratedPluginRegistrant.register(with:)` and before `super.application(...)`.
- Gamification: key and region (and the base URL if confirmed) passed in the direct config; screens reported; `Hydra.setCapToken(...)` called before any Loyalty View.

> ⚠️ Gap: there's no formal verification procedure. No expected log lines and no Capillary dashboard checks are documented, for example to confirm that a user or event reached Capillary, or how to send a test push or in-app message. Ask a Capillary engineer.

> ⚠️ Gap: initialisation runs natively at app start. The guide doesn't say when the Dart handler must be registered to receive `onHydraSdkInitializationResult`, or whether a handler registered after initialisation finished still gets the result. Ask a Capillary engineer.

## Known Issues

**Android: the SDK reads Firebase Remote Config instead of your values**
- Cause: the manifest points straight at `com.capillary.plugins.hydra.HydraApplication`. That class auto-initialises from the default Remote Config keys.
- Fix:
  1. Use your own subclass of `HydraApplication`.
  2. Register it by fully qualified name.
  3. Call `HydraInitializer.initialize(this, hydraRemoteConfig)`.

*Derived from the source doc (Flutter guide pp.3, 6).*

**Android: a custom Application class doesn't initialise Hydra**
- Cause: a subclass of `HydraApplication` doesn't initialise automatically.
- Fix: call the initialiser yourself, **immediately after `super.onCreate()`**. An existing Application class must be changed to extend `HydraApplication`.

*From the source doc (Flutter guide p.6).*

**Android: the Hydra plugin needs an AppCompat theme**
- Symptom: not described in the source.
- Cause: the application theme doesn't derive from AppCompat.
- Fix: set an AppCompat theme, for example `@style/Theme.AppCompat.DayNight.NoActionBar` (step 8).

*From the source doc (Flutter guide p.3).*

**iOS: manual initialisation in the wrong place**
- `HydraNativeAPI.shared.initApplication(...)` must come **after** `GeneratedPluginRegistrant.register(with:)` and **before** `super.application(...)` in `AppDelegate.swift`.

*From the source doc (Flutter guide p.8).*

**iOS: crash on `remoteConfig!`**
- The guide's sample force-unwraps the result of `HydraRemoteConfig(...)`, so if it returns `nil` the app crashes at launch.
- The guide doesn't say when it returns `nil` (see the gap in step 11).

*Derived from the sample code (Flutter guide p.9).*

**iOS: Swift Package Manager projects**
- With SPM enabled, skip the Podfile steps: `require_relative`, `hydra_pods` and `extension_pods`.
- The guide gives no SPM replacement for them.

*From the source doc (Flutter guide pp.4–5).*

**Firebase config file generation (push)**
- Don't make the code changes the Firebase console suggests while generating `google-services.json` / `GoogleService-Info.plist`.

*From the source doc (Flutter guide p.4).*

**Applying native Android "without Firebase" rules to Flutter**
- `android/direct.md` says not to add Firebase, and that push isn't available. The Flutter guide says neither.
- In Flutter direct mode, push still uses FCM (Modules → Push).

*Derived from the source docs (Flutter guide pp.4–5, 15, 18 vs Integration document pp.100–112).*

**iOS: rich notifications and the Inbox API need the Notification Service Extension**
- Rich notifications are mandatory.
- The Inbox API on iOS needs the extension set up, with the same App Group `group.<runner_target_bundle_id>.hydra` on both the main target and the extension target.

*From the source doc (Flutter guide pp.4, 6).*

**`enable_in_app_messaging_in_flutter`**
- Currently non-functional. Don't enable it in production.

*From the source doc (Flutter guide p.3).*

**`getFCMToken()` throws**
- Cause: no FCM token is available yet.
- Fix: catch the error, or wait for the token in `onTokenAvailable`.

*From the source doc (Flutter guide p.15); the fix is derived from the same page and p.9.*

**Inbox UI doesn't refresh**
- Cause: there's no "inbox updated" event.
- Fix: refresh from `onHydraNotificationReceived` or `onNotificationCenterDismissed`, or poll `HydraInbox`.

*From the source doc (Flutter guide p.19).*

**Gamification campaigns never appear**
- Causes:
  - the gamification key or region wasn't passed in the direct config;
  - the screen isn't reported.
- Fix: pass both values (Modules → Gamification) and report screens.

*Derived from the source doc (Integration document pp.54–55, which states this for the Remote Config keys).*

**Campaigns don't re-evaluate when a persistent screen regains focus**
- Cause: `initState` / `dispose` don't fire for a screen that stays mounted under pushed routes.
- Fix: use `RouteObserver` + `RouteAware` together with app-lifecycle observation.

*From the source doc (Integration document pp.54–55).*

**Screen tracking mismatch**
- Pass the same `screenName` to `gamificationScreenAppeared` and `gamificationScreenDisappeared`.

*From the source doc (Flutter guide pp.10, 15).*

**Loyalty View is blank or collapsed**
- Causes:
  - `GamificationLoyaltyView` never reports a height, so give it a fixed-height parent;
  - `Hydra.setCapToken` wasn't called before the view was mounted, so the native SDK can't bind it.

*From the source doc (Flutter guide p.10; Integration document pp.56–58).*

**Identified user isn't linked in CRM**
- Cause: `customerId` doesn't match the Account Linking Identifier configured in Capillary CRM.

*From the source doc (Flutter guide pp.9, 19).*

**SDK calls made too early**
- Make sure the SDK has initialised successfully (`onHydraSdkInitializationResult`) before using any `capillary_hydra` API.

*From the source doc (Flutter guide p.9).*

## API Reference

**Native direct-init APIs**

| API | Purpose |
|---|---|
| Android `com.capillary.plugins.hydra.HydraApplication` | Base class your Application class must extend |
| Android `HydraRemoteConfig.Builder(accountId, baseURL, sslPublicKey, remoteDebugLevel)` (`com.capillary.plugins.hydra.nativeapis.HydraRemoteConfig`) | Builds the direct config. The first three are required. `remoteDebugLevel` defaults to `0`; the sample passes `4` (`LogType.DEBUG`). Methods: `.orgId()`, `.gamificationKey()`, `.gamificationRegion()`, `.gamificationBaseUrl()` (all optional), `.build()` |
| Android `HydraInitializer.initialize(this, hydraRemoteConfig)` (`com.capillary.plugins.hydra.nativeapis.HydraInitializer`) | Initialises with the direct config. Call immediately after `super.onCreate()`. |
| iOS `HydraRemoteConfig(accountId:baseUrl:sslPublicKey:remoteLogLevel:orgId:gamificationKey:gamificationRegion:gamificationBaseUrl:)` (`import capillary_hydra_ios`) | Direct config. `accountId`, `baseUrl` and `sslPublicKey` are required; `orgId` and the gamification values are optional. The sample force-unwraps the result. |
| iOS `HydraNativeAPI.shared.initApplication(_:didFinishLaunchingWithOptions:hydraRemoteConfig:)` | Initialises with the direct config. Call after `GeneratedPluginRegistrant.register(with:)` and before `super.application(...)`. |
| iOS `HydraNativeAPI.shared.application(_:didReceiveRemoteNotification:fetchCompletionHandler:)` | Forwards remote notifications (In-App setup) |
| iOS `HydraRemoteNotificationService` (`import HydraPushNotificationServiceExtension`) | Used in the Notification Service Extension: `didReceive(_:withContentHandler:)`, `serviceExtensionTimeWillExpire()` |

**`capillary/hydra-config.json` keys** (step 2): `console_log_level`, `enable_in_app_messaging`, `enable_in_app_messaging_in_flutter`, `enable_inbox_api`, `enable_inbox_ui`, `use_default_inbox_ui_config`, `max_notification_count`, `hydra_notification_color`

**Asset images in `capillary/icons/`:** `hydra_notification_small_icon`, `hydra_in_app_placeholder`, `hydra_inbox_ui_placeholder` (png, jpg or jpeg)

**Dart APIs.** Import `package:capillary_hydra/hydra.dart`. Model classes come from `package:capillary_hydra_platform_interface/capillary_hydra_platform_interface.dart`.

| API | Purpose |
|---|---|
| `HydraInitializer.initialize()` | Call in `main()` before `runApp` |
| `HydraCore.setHydraAccountConfig({required HydraAccountConfig hydraAccountConfig})` → `Future<bool>` | Passes the account values from Dart (direct values / multi-account) |
| `Hydra.identify({required HydraUserDetails userDetails, Map<String, dynamic>? customAttributes})` → `Future<bool>` | Identifies the current visitor as a known user |
| `Hydra.track({required String eventName, Map<String, dynamic>? attributes})` → `Future<bool>` | Reports a custom event |
| `Hydra.reset({required String customerId})` → `Future<bool>` | Resets / signs out the user |
| `Hydra.getCurrentUserState()` → `Future<UserState?>` | Visitor flow: current state |
| `Hydra.getVisitorDetails()` → `Future<HydraVisitorInfo?>` | Visitor flow: `visitorId` |
| `Hydra.isVisitorFlowEnabled()` → `Future<bool>` | Visitor flow: enabled for this account? |
| `Hydra.gamificationScreenAppeared({required String screenName})` → `Future<void>` | Gamification screen tracking |
| `Hydra.gamificationScreenDisappeared({required String screenName})` → `Future<void>` | Gamification screen tracking; same `screenName` as `...Appeared` |
| `Hydra.setCapToken({required String token})` → `Future<void>` | Capillary B2B token; call before mounting `GamificationLoyaltyView` |
| `HydraCore.updateUser({required HydraUserDetails userDetails, Map<String, dynamic>? customData, List<Map<String, dynamic>>? subscriptions})` → `Future<bool>` | Updates user details |
| `HydraCore.updateGeoConfig({required HydraGeoConfig config})` → `Future<bool>` | Updates geo config |
| `HydraCore.updatePushPreferences({required String customerId, required HydraPushPreferences preferences})` → `Future<bool>` | Updates push preferences |
| `HydraPushNotification.requestPermission()` → `Future<bool>` | Asks for push permission; can throw |
| `HydraPushNotification.getFCMToken()` → `Future<String>` | FCM token; throws if not available |
| `HydraInbox.getInboxMessages()` → `Future<List<HydraNotification>>` | Stored notifications |
| `HydraInbox.getUnreadInboxMessagesCount()` → `Future<int>` | Unread count |
| `HydraInbox.markInboxMessageAsRead({required HydraNotification notification})` → `Future<bool>` | Marks one as read |
| `HydraInbox.deleteInboxMessage({required HydraNotification notification})` → `Future<bool>` | Deletes one |
| `HydraInbox.deleteAllInboxMessages()` → `Future<bool>` | Deletes all |
| `HydraInboxUI.showNotificationCenter()` → `Future<void>` | Shows the built-in notification center |
| `HydraInboxUI.hideNotificationCenterIfShowing()` → `Future<void>` | Hides it if it's showing |
| `HydraNativeEvents.addEventHandler(HydraNativeEventHandler handler)` | Registers a callback handler |
| `HydraNativeEvents.removeEventHandler(HydraNativeEventHandler handler)` | Removes one handler |
| `HydraNativeEvents.removeAllEventHandlers()` | Removes all handlers |

Not used in this mode: `HydraCore.setFirebaseRemoteConfigKeys`, `HydraFirebaseRemoteConfigKeys`, Android `HydraInitializer.initializeUsingFirebaseRemoteConfig`, iOS `HydraNativeAPI.shared.initApplicationWithFirebaseRemoteConfig`. See `flutter/firebase.md`.

**`HydraNativeEventHandler` callbacks.** Extend or implement the class; every method has an empty default body.

| Callback | Fires when |
|---|---|
| `onTokenAvailable({required String token})` | A new FCM token is available |
| `onHydraNotificationReceived({required HydraNotification notification})` | A Hydra notification is received |
| `onHydraNotificationClicked({HydraNotificationCTA? cta, HydraNotification? notification})` | A Hydra notification is clicked: system tray, built-in notification center, or in-app message |
| `onHydraNotificationDismissed({required HydraNotification notification})` | A Hydra notification is dismissed in the system tray |
| `onHydraNotificationShown({required HydraNotification notification})` | A Hydra notification is shown in the system tray |
| `onNonHydraNotificationReceived({required NonHydraNotification notification})` / `onNonHydraNotificationClicked({NonHydraNotification? notification})` | The same, for non-Hydra push |
| `onNotificationCenterDismissed()` | The built-in notification center is dismissed |
| `onHydraSdkInitializationResult({required bool success, String? error})` | SDK initialisation succeeds or fails |
| `onConfigFetched({required bool isVisitorFlowEnabled})`, `onLegacyFlowReady()`, `onVisitorSessionReady()`, `onUserStateChanged({UserState? userState})` | Visitor-flow lifecycle |

**Widgets**
- `GamificationBannerView({ required String bannerId, void Function(double height)? onHeightChanged })`
- `GamificationEmbedView({ required String embedId, void Function(double height)? onHeightChanged })`
- `GamificationLoyaltyView({ required String loyaltyId })`

**Model classes and enums**

| Type | Fields / values |
|---|---|
| `HydraAccountConfig` | `accountId`, `baseUrl`, `sslPublicKey` (`String`, required); `remoteLogLevel` (`HydraLogLevel`, required); `orgId`, `gamificationKey`, `gamificationRegion`, `gamificationBaseUrl` (`String?`, optional) |
| `HydraLogLevel` | `off(0)`, `error(1)`, `warn(2)`, `info(3)`, `debug(4)`, `verbose(5)`; `final int value` |
| `HydraUserDetails` | `customerId` (required), `email`, `phoneNumber`, `firstName`, `lastName` |
| `HydraGeoConfig` | `city`, `country`, `countryCode` (required), `timezone` (optional) |
| `HydraPushPreferences` | `promPushEnabled`, `transPushEnabled` (both required `bool`) |
| `UserState` | `none`, `legacyRegistered`, `visitor`, `merged`, `signedOut` |
| `HydraVisitorInfo` | `String? visitorId` |
| `HydraNotification` (all fields final and nullable) | `cuid`, `scope`, `campaignId`, `variationId`, `senderId`, `senderSource`, `custom`, `customData` (`Map<String, dynamic>?`), `priority`, `validity`, `messageId`, `gateway` (`HydraNotificationGateway?`), `body` (`HydraNotificationBody?`), `expandableDetails` (`HydraNotificationExpandedDetails?`), `isRead`, `imageIdentifier`, `accountId`, `channelId`, `payload`, `createdAt` (`DateTime?`), `isExpanded`, `isMessageEllipsized`, `isTitleEllipsized`, `showArrow` |
| `HydraNotificationBody` | `title`, `message`, `image`, `cta` (`HydraNotificationCTA?`) |
| `HydraNotificationCTA` | `type` (`HydraNotificationCTAType?`), `action`, `actionText` |
| `HydraNotificationCTAType` | `external`, `deepLink`, `rating`, `feedback`, `appRating`, `unknown` |
| `HydraNotificationExpandedDetails` | `ctas` (`List<HydraNotificationCTA>?`), `message`, `image`, `style` |
| `HydraNotificationGateway` | `fcm`, `xiaomi`, `unknown` |
| `NonHydraNotification` | `title`, `body`, `icon`, `imageUrl` (`String?`); `data` (`Map<String, dynamic>`) |
