---
platform: flutter
config_mode: firebase
sdk_package: capillary_hydra
sdk_version: null            # the public docs install the latest release (`flutter pub add`); no version is pinned
modules_covered: [core, push, inapp, inbox_api, inbox_ui, visitor, gamification, multi_account]
modules_missing: []
sources: ["Flutter-Hydra-Integration-Guide pp.1–24", "Integration document _ Experience+ pp.52–59 (Gamification Flutter Integration Guide)", "Capillary developer docs (docs.capillarytech.com): flutter-sdk, flutter-sdk-getting-started, flutter-sdk-install, flutter-sdk-advanced-setup, flutter-setup-overview, flutter-sdk-push-notifications, configuring-notification-center, gamification-flutter, flutter-sdk-api-reference (updated 2026-11-12)"]
owner: TBD
last_verified: null
review_status: draft   # drafted from the source docs; not yet SME-verified
---
# Flutter (with Firebase Remote Config)

## Coverage
The SDK reads its account values from **Firebase Remote Config** under default key names (the docs' default path); the native SDKs start automatically on both platforms. Custom key names and several accounts: Modules → Multi-account. Passing values without Remote Config uses different native initializers (flutter-sdk-advanced-setup › Other initializers; the direct-mode file).

| Module | Status |
|---|---|
| Core, Push, In-App, Inbox API, Inbox UI, Visitor, Gamification | Documented |
| Multi-account | Documented (prefixed Remote Config keys, or values you fetch yourself) |

## Requirements
| Platform | Version |
|---|---|
| Flutter | >= 3.3.0 (Dart >= 3.0) |
| iOS | >= 15.0 |
| Android | >= API 23 (Android 6.0) |

- Packages `capillary_hydra` and `capillary_hydra_platform_interface` from pub.dev (`https://pub.dev/packages/capillary_hydra`), kept on the **same version**. The Hydra Android SDK is resolved from Maven Central: no extra repository or credentials needed.
- A Firebase project with this app registered, where you can add Remote Config parameters (step 1).
- Android: an AppCompat application theme (step 12); Google Services Gradle plugin `4.4.2` (step 10).
- iOS: CocoaPods with `use_frameworks!`, or Swift Package Manager; app-delegate or UIScene lifecycle (both supported); access to `developer.apple.com` (push capabilities, extension bundle ID, App Group).

> ⚠️ Correction: ✅ Use the pub.dev packages `capillary_hydra` and `capillary_hydra_platform_interface` (flutter-sdk-getting-started, flutter-sdk-install). ❌ Don't use the GitHub repository `https://github.com/Capillary/flutter-hydra-lib` (an internal Capillary page). *Pending SME confirmation.*

> ⚠️ Gap: Android compileSdk / AGP / Gradle / Kotlin, Xcode and CocoaPods versions aren't documented. Ask a Capillary engineer.

## Prerequisites
Common exchange: `_shared/prerequisites.md`. Firebase / Remote Config basics: `_shared/firebase-setup.md`.
- **Client gives Capillary's apps team:** iOS bundle ID (`{{bundle_id}}`), Android applicationId (`{{application_id}}`), app signature (SHA256) from the Android app signing report.
- **Capillary gives the client:** Account Id, Base URL (end point), SSL public key; Org Id (Anonymous/Visitor flow only); Gamification Key, Gamification Region and Gamification Base URL (gamification only).
- **CRM:** `customerId` must match the Account Linking Identifier (see `_shared/prerequisites.md`).
- **Loyalty View only:** a Capillary B2B short-lived token (cap token), set before the Loyalty View is mounted (how to obtain it isn't documented; see `_shared/prerequisites.md`).
- **Example app:** `https://pub.dev/packages/capillary_hydra/example`.

## Steps

### 1. Set up Firebase: register the app and add the Hydra parameters
1. Register the app on Firebase (the docs' link: `https://support.google.com/appsheet/answer/10104995?hl=en`) and download `google-services.json` and `GoogleService-Info.plist`. **Don't make any code changes the Firebase console suggests while generating these files.** You add them in steps 9 and 10.
2. In Firebase Remote Config, add these parameters **with these exact names**:

| Remote Config key | Value | When |
|---|---|---|
| `hydra_account_id` | `{{account_id}}` | Always |
| `hydra_base_url` | `{{base_url}}` | Always |
| `hydra_ssl_public_key` | `{{ssl_public_key}}` | Always |
| `hydra_remote_log_level` | `0`–`5` (0=off, 1=error, 2=warn, 3=info, 4=debug, 5=verbose) | Always |
| `hydra_org_id` | `{{org_id}}` | Anonymous/Visitor flow only |
| `hydra_gamification_key` | `{{gamification_key}}` | Gamification only |
| `hydra_gamification_region` | `{{gamification_region}}` | Gamification only |
| `hydra_gamification_base_url` | `{{gamification_base_url}}` | Gamification only |

The default keys are read automatically on Android when the Application class is exactly `HydraApplication` (step 11), and on iOS unless you call an initializer yourself. Several accounts (e.g. one per region): Modules → Multi-account.

> ⚠️ Gap: the Firebase registration link (flutter-sdk-getting-started, and the 2024 guide) points to a Google AppSheet help article, not Firebase documentation. Ask a Capillary engineer which guide is intended.

> ⚠️ Gap: the Remote Config value type (String or Number) for each parameter, e.g. `hydra_remote_log_level`, isn't documented. Ask a Capillary engineer.

### 2. Add the packages
```bash
flutter pub add capillary_hydra capillary_hydra_platform_interface
```

This adds the latest released version of each to `pubspec.yaml`. Keep both packages on the same version. To upgrade later:

```bash
flutter pub upgrade capillary_hydra capillary_hydra_platform_interface
```

Release notes: `https://pub.dev/packages/capillary_hydra/changelog` and `https://pub.dev/packages/capillary_hydra_platform_interface/changelog`.

> ⚠️ Correction: ✅ Use `flutter pub add capillary_hydra capillary_hydra_platform_interface`, which adds the latest release (flutter-sdk-install). ❌ Don't pin the 2024 guide's beta version (front-matter `sdk_version`; Flutter-Hydra-Integration-Guide p.2). *Pending SME confirmation.*

### 3. Create `capillary/hydra-config.json`
Create a `capillary` folder at the Flutter project root, with `hydra-config.json`:

```json file=capillary/hydra-config.json
{
  "console_log_level": 4,
  "enable_in_app_messaging": false,
  "enable_inbox_api": false,
  "enable_inbox_ui": false,
  "use_default_inbox_ui_config": true,
  "max_notification_count": 200,
  "hydra_notification_color": "#FF03DAC5",
  "enable_in_app_messaging_in_flutter": false,
  "enable_ssl_pinning": true
}
```

| Key | Type | Default | Platform | Meaning |
|---|---|---|---|---|
| `console_log_level` | number | `4` | Android & iOS | Console log level 0–5 (0=off, 1=error, 2=warn, 3=info, 4=debug, 5=verbose) |
| `enable_in_app_messaging` | boolean | `false` | Android & iOS | In-app messaging (needs the in-app placeholder image) |
| `enable_in_app_messaging_in_flutter` | boolean | `false` | Android only | **Currently non-functional. Don't enable in production.** |
| `enable_inbox_api` | boolean | `false` | Android & iOS | Inbox API |
| `enable_inbox_ui` | boolean | `false` | Android & iOS | Built-in notification center |
| `use_default_inbox_ui_config` | boolean | `true` | iOS only | SDK's default notification center layout |
| `max_notification_count` | number | `200` | Android & iOS | Max notifications kept in the inbox / notification center |
| `hydra_notification_color` | string | – | Android only | Notification tint colour, e.g. `"#FF03DAC5"` |
| `enable_ssl_pinning` | boolean | `true` | Android & iOS | `true`: the SDK pins the Hydra backend's SSL certificate against the SSL public key from the apps team. `false` turns pinning off |

The **remote** log level (same 0–5 scale) is set separately with `hydra_remote_log_level` in Remote Config (step 1).

### 4. Declare the config folder as assets
Add `capillary/icons/` once you add icon images (Modules → Push, In-App, Inbox UI).

```yaml file=pubspec.yaml
flutter:
  assets:
    - capillary/
    - capillary/icons/
```

### 5. Fetch the packages
```bash
flutter pub get
```

### 6. Call `HydraInitializer.initialize()` in `main()`, before `runApp`
```dart file=lib/main.dart
import 'package:capillary_hydra/hydra.dart';
import 'package:flutter/material.dart';

void main() {
  WidgetsFlutterBinding.ensureInitialized();
  HydraInitializer.initialize();
  runApp(const MyApp());
}
```

This Dart `HydraInitializer` (`package:capillary_hydra/hydra.dart`) is not the native Android `com.capillary.plugins.hydra.nativeapis.HydraInitializer` in step 11.

### 7. iOS: add Hydra to the Podfile (CocoaPods only)
**Skip steps 7–8 if Swift Package Manager is enabled.** At the top of `ios/Podfile`:

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

> ⚠️ Gap: with Swift Package Manager the docs only say to skip the Podfile steps (`require_relative`, `hydra_pods`, `pod install`, `extension_pods`); they give no SPM steps, including how the extension target gets `HydraPushNotificationServiceExtension`. Ask a Capillary engineer.

### 8. iOS: install pods
In the `ios` folder:

```bash
pod install
```

### 9. iOS: add `GoogleService-Info.plist` (no AppDelegate code needed)
Add `GoogleService-Info.plist` (step 1) to the iOS project using Xcode.

Both the app-delegate lifecycle and the UIScene lifecycle (`FlutterSceneDelegate` with `FlutterImplicitEngineDelegate`) are supported. **You don't need any Hydra code in `AppDelegate.swift`** for either: once registered, the plugin starts the Hydra SDK itself, reading the default Remote Config keys (step 1). Custom key names: Modules → Multi-account.

### 10. Android: add `google-services.json` and the Google Services plugin
1. Add `google-services.json` (step 1) to the `android/app` folder.
2. Declare the plugin in the root `plugins` block:

   ```kotlin file=android/settings.gradle.kts
   id("com.google.gms.google-services") version "4.4.2" apply false
   ```

   ```groovy file=android/settings.gradle
   id 'com.google.gms.google-services' version '4.4.2' apply false
   ```
3. Apply it in the app's `plugins` block:

   ```kotlin file=android/app/build.gradle.kts
   id("com.google.gms.google-services")
   ```

   ```groovy file=android/app/build.gradle
   id 'com.google.gms.google-services'
   ```

### 11. Android: set the Application class
Flutter has no custom Application class by default, but Hydra needs one to run initialisation.

**Option A: no Application class of your own.** Point the manifest at Hydra's class; it reads the default Remote Config keys (step 1):

```xml file=android/app/src/main/AndroidManifest.xml
<application
    android:name="com.capillary.plugins.hydra.HydraApplication"
    ...>
```

**Option B: you already have an Application class.** Make it extend `HydraApplication`, point `android:name` at its fully qualified name (package + class), and call an initializer **immediately after `super.onCreate()`**. The automatic initialisation only runs when the Application class is exactly `HydraApplication`; a subclass must call it itself.

```kotlin file=android/app/src/main/kotlin/<your-package>/ExampleApplication.kt
import com.capillary.plugins.hydra.HydraApplication
import com.capillary.plugins.hydra.nativeapis.HydraInitializer

class ExampleApplication : HydraApplication() {
    override fun onCreate() {
        super.onCreate()
        HydraInitializer.initializeUsingFirebaseRemoteConfig(this)
        // ...
    }
}
```

Custom key names: Modules → Multi-account.

### 12. Android: set an AppCompat theme
The Hydra plugin requires the application theme to derive from AppCompat:

```xml file=android/app/src/main/AndroidManifest.xml
<application
    ...
    android:theme="@style/Theme.AppCompat.DayNight.NoActionBar">
```

### 13. Register a native event handler and wait for initialisation
Before using any `capillary_hydra` API, make sure the SDK initialised successfully. Write a class that **extends** `HydraNativeEventHandler` and override only what you need (all methods have empty defaults). Prefer `extends` over `implements`: an implementing class must define every callback, including ones added in later releases, so it can stop compiling after an upgrade. Register it:

```dart
HydraNativeEvents.addEventHandler(handler);
```

The result arrives in:

```dart
void onHydraSdkInitializationResult({required bool success, String? error})
```

### 14. Identify, track and reset the user
Single account: nothing else to do first. Several accounts: set the account **before** `identify` (Modules → Multi-account).

`customerId` is required and **must match the Account Linking Identifier in Capillary CRM** (mobile, email, InTouchUserId, externalId or FCMToken; *Organisation Settings → Omni Channel Settings → Channel Configurations → MAPP_SDK → Account Linking Identifier*). `identify` also takes optional `customAttributes` (`Map<String, dynamic>?`).

```dart
import 'package:capillary_hydra/hydra.dart';
import 'package:capillary_hydra_platform_interface/capillary_hydra_platform_interface.dart';

HydraUserDetails userDetails = HydraUserDetails(
  customerId: '8888888888',
  firstName: 'FirstName',
  lastName: 'LastName',
  email: 'user@example.com',
  phoneNumber: '918888888888',
);

bool result = await Hydra.identify(userDetails: userDetails);
```

```dart
bool result = await Hydra.track(eventName: 'product_viewed', attributes: {'productId': 'abc123'});
```

```dart
bool result = await Hydra.reset(customerId: '8888888888');
```

Each returns `Future<bool>`: whether the request was **made** successfully.

### 15. (Optional) Update the user, geo config and push preferences
Static functions on `HydraCore` (`package:capillary_hydra/hydra.dart`). Each `subscriptions` entry includes `channel`, `accountId`, `priority`, `type` and `sourcename`.

```dart
bool updateUserResult = await HydraCore.updateUser(
  userDetails: updatedUserDetails,
  customData: {"Key": "Value"},
  subscriptions: [
    {"channel": "channel1", "type": "topic1", "priority": 1},
  ],
);
```

Pass your `HydraGeoConfig` instance as `config` (here, `geoConfig`):

```dart
HydraGeoConfig geoConfig = HydraGeoConfig(
  city: "Bangalore",
  country: "India",
  countryCode: "IN",
  timezone: "Asia/Kolkata",
);

bool updateGeoConfigResult = await HydraCore.updateGeoConfig(config: geoConfig);
```

Push preferences take the signed-in user's `customerId`:

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
Server side (how a push reaches the device, what must match at Capillary, how to test, FCM delivery reports): `_shared/push.md`.

**1. Firebase.** Steps 1, 9 and 10. On Android, that Firebase setup is all push needs.

**2. Small icon.** Create `capillary/icons/` if needed and add `hydra_notification_small_icon` (png, jpg or jpeg; png recommended). It's the notification-drawer icon. Declare the folder in assets (step 4).

**3. Android notification colour.** Set `hydra_notification_color` in `hydra-config.json` (step 3).

**4. iOS capabilities.** On `developer.apple.com`, add the **Push Notification** capability to the app identifier. In Xcode → app target → **Signing & Capabilities**, add **Push Notification** and **Background Modes** (enable **Background fetch** and **Remote notifications**).

**5. iOS Notification Service Extension (rich notifications are mandatory).**
1. In Xcode, add a **Notification Service Extension** target. Xcode appends the extension's product name to the main target's bundle ID to derive its bundle ID; add that bundle ID on `developer.apple.com`.
2. Add the **App Groups** capability to **both** the main target and the extension target, with the same group `group.<runner_target_bundle_id>.hydra` (e.g. `group.{{bundle_id}}.hydra`). Create this App Group on `developer.apple.com` for both identifiers.
3. **CocoaPods only (skip with SPM):** add `extension_pods` to the extension target in `ios/Podfile`, then run `pod install` again.

   ```ruby file=ios/Podfile
   target "HydraRichNotification" do
     use_frameworks!
     extension_pods
   end
   ```
4. Replace the **entire** contents of the extension's `NotificationService.swift` (the folder is named after your extension target; `HydraRichNotification` is the example):

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

**6. Permission and token (Dart).** Call `requestPermission` before you can receive push. It returns whether permission was granted and can throw.

```dart
bool granted = await HydraPushNotification.requestPermission();
```

```dart
String fcmToken = await HydraPushNotification.getFCMToken();
```

`getFCMToken` **throws if no FCM token is available**. Alternatively, use the `onTokenAvailable` callback.

**7. Android: your app gets FCM tokens itself** (e.g. with `firebase_messaging`): pass each new token to Hydra. On iOS `passFCMToken` does nothing, so it's safe to call on both platforms.

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

**8. Preferences and callbacks.** `HydraCore.updatePushPreferences` (step 15) controls promotional / transactional push. Callbacks `onHydraNotification*` and `onNonHydraNotification*` on your handler (API Reference); unsubscribe with `removeEventHandler` / `removeAllEventHandlers`.

### In-App
1. Set `enable_in_app_messaging` to `true` in `hydra-config.json`.
2. Add `hydra_in_app_placeholder` (png, jpg or jpeg) to `capillary/icons`.
3. **iOS:** at the top of `AppDelegate.swift` add:

   ```swift file=ios/Runner/AppDelegate.swift
   import capillary_hydra_ios
   ```

   and add this function:

   ```swift file=ios/Runner/AppDelegate.swift
   override func application(_ application: UIApplication, didReceiveRemoteNotification userInfo: [AnyHashable: Any], fetchCompletionHandler completionHandler: @escaping (UIBackgroundFetchResult) -> Void) {
       HydraNativeAPI.shared.application(application, didReceiveRemoteNotification: userInfo, fetchCompletionHandler: completionHandler)
   }
   ```

In-app clicks (CTA tapped on an in-app message) arrive in `onHydraNotificationClicked`. Keep `enable_in_app_messaging_in_flutter` `false` (non-functional).

### Inbox
**Inbox API** (build your own notification list). The SDK stores received notifications in a local database, capped by `max_notification_count`, so the inbox depends on Modules → Push.
1. Set `enable_inbox_api` to `true`.
2. **iOS:** the Notification Service Extension and App Group must be set up (Modules → Push, item 5).

```dart
List<HydraNotification> notifications = await HydraInbox.getInboxMessages();
int unreadNotificationCount = await HydraInbox.getUnreadInboxMessagesCount();
bool marked = await HydraInbox.markInboxMessageAsRead(notification: notification);
bool deleted = await HydraInbox.deleteInboxMessage(notification: notification);
bool deleted = await HydraInbox.deleteAllInboxMessages();
```

These are separate usage samples (rename variables if used together). `notification` must come from `getInboxMessages`. There's no "inbox updated" event: refresh from `onHydraNotificationReceived` or `onNotificationCenterDismissed`, or call `HydraInbox` on demand.

**Inbox UI** (built-in notification center).
1. Enable the Inbox API.
2. Set `enable_inbox_ui` to `true`.
3. Add `hydra_inbox_ui_placeholder` (png, jpg or jpeg) to `capillary/icons`.

```dart
HydraInboxUI.showNotificationCenter();
await HydraInboxUI.hideNotificationCenterIfShowing();
```

Override `onNotificationCenterDismissed()` for the dismiss callback.

> ⚠️ Gap: what `use_default_inbox_ui_config: false` does, and how to customise the notification center from Flutter, isn't documented. Ask a Capillary engineer.

### Visitor
States: `none` → `visitor` (anonymous) → `merged` / `legacyRegistered` (identified) → `signedOut`.
1. Add `hydra_org_id` to Remote Config (step 1); with custom key names, `keyForOrgId` (Multi-account).
2. Use the APIs:

   ```dart
   bool enabled = await Hydra.isVisitorFlowEnabled();
   ```

   ```dart
   UserState? state = await Hydra.getCurrentUserState();
   ```

   ```dart
   HydraVisitorInfo? info = await Hydra.getVisitorDetails();
   ```
3. Subscribe to `onConfigFetched`, `onLegacyFlowReady`, `onVisitorSessionReady`, `onUserStateChanged` on your handler.

`identify` / `track` / `reset` (step 14) are part of this flow.

> ⚠️ Gap: the difference between `legacyRegistered` and `merged`, when `onLegacyFlowReady` fires instead of `onVisitorSessionReady`, and what the app should do in each state aren't documented. Ask a Capillary engineer.

### Gamification
Floating Button, Popup and Bottom Sheet campaigns, plus Banner, Embed and Loyalty widgets. Part of `capillary_hydra`; no extra package.

> ⚠️ Gap: the public docs (gamification-flutter) give no minimum `capillary_hydra` version for gamification; the older Integration doc (pp.53, 58) names an unreleased minimum. Ask a Capillary engineer which release to require.

**1. Configure.** Add the three gamification parameters to Remote Config (step 1); `capillary_hydra` picks them up automatically, no Dart code needed:
- `hydra_gamification_key`
- `hydra_gamification_region`
- `hydra_gamification_base_url`

HydraGamification stays disabled if the key or region is missing. With custom key names: `keyForGamificationKey`, `keyForGamificationRegion`, `keyForGamificationBaseUrl` (Multi-account).

> ⚠️ Correction: ✅ Use all three values, Gamification Key, Region **and Base URL** (gamification-flutter, flutter-sdk-getting-started). ❌ Don't treat the base URL as optional (Integration doc p.54). *Pending SME confirmation.*

> ⚠️ Correction: ✅ Use `hydra_gamification_base_url` as the Remote Config key (flutter-sdk-getting-started; Flutter guide p.1, pp.7–8, p.22). ❌ Don't use `hydra_gamification_url` (Integration doc Flutter chapter, pp.53–54). If the SDK says the base URL isn't recognised, check this key name first. *Pending SME confirmation.*

**2. Report the current screen (mandatory for screen-targeted campaigns).** Call `gamificationScreenAppeared` when a screen appears and `gamificationScreenDisappeared` when it disappears, **with the same `screenName`**. Once a screen is reported, Floating Button, Popup and Bottom Sheet campaigns targeted at it show automatically; nothing else to implement for them.

```dart
Hydra.gamificationScreenAppeared(screenName: 'HomeScreen');
// ... later, when the screen unmounts:
Hydra.gamificationScreenDisappeared(screenName: 'HomeScreen');
```

Normal screen:

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

A screen that stays mounted under pushed routes (e.g. a persistent Home tab) doesn't get `initState` / `dispose` when it regains focus. Use `RouteObserver` + `RouteAware`, and observe the app lifecycle so campaigns re-evaluate on background / foreground (Integration doc):

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

> ⚠️ Correction: ✅ Use `Hydra.gamificationScreenDisappeared(screenName: ...)` with the same `screenName` as `...Appeared` (flutter-sdk-api-reference; Flutter guide p.15). ❌ Don't use `Hydra.gamificationScreenDisappeared()` with no argument (Integration doc samples, pp.54–55). *Pending SME confirmation.*

> ⚠️ Gap: the `RouteAware` sample omits subscribing to `routeObserver` and registering the `WidgetsBindingObserver` (and unsubscribing); without them the callbacks never fire. Ask a Capillary engineer for the full sample.

**3. Set the cap token (Loyalty View).** Call `Hydra.setCapToken(token: ...)` **before mounting** `GamificationLoyaltyView`: the token is read once, when the view binds, so setting it afterwards doesn't reach a view already on screen.

```dart
Hydra.setCapToken(token: token);
```

**4. Widgets** (native `PlatformView`s): `GamificationBannerView` (`bannerId`), `GamificationEmbedView` (`embedId`), `GamificationLoyaltyView` (`loyaltyId`), each with an optional `onHeightChanged`. All three report their content height via `onHeightChanged`. **A height of `0` is meaningful** (nothing to show: no matching entry point, or the campaign closed it), so collapse to it rather than ignoring it. Banner sample (Embed and Loyalty follow the same pattern):

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
          if (height >= 0) setState(() => _bannerHeight = height);
        },
      ),
    );
  }
}
```

The Integration doc's samples also check `mounted` before `setState`.

> ⚠️ Correction: ✅ Use `if (height >= 0)` and collapse on `0` (gamification-flutter). ❌ Don't use `if (height > 0)`, which ignores `0` (Flutter guide and Integration doc samples). *Pending SME confirmation.*

> ⚠️ Correction: ✅ Use `GamificationLoyaltyView({ required String loyaltyId, void Function(double height)? onHeightChanged })` and size it from `onHeightChanged` like the other widgets (gamification-flutter). ❌ Don't rely on "the Loyalty View never reports a height change, give it a fixed-height parent" (Flutter guide / Integration doc). *Pending SME confirmation.*

**5. Suppress campaigns** temporarily (e.g. checkout, onboarding), and allow them again with `false`. Both calls **throw if the SDK isn't initialised yet**: an error means suppression wasn't applied (or the value is unknown), not that it's `false`.

```dart
await Hydra.setGamificationSuppressed(suppressed: true);
// ... later
await Hydra.setGamificationSuppressed(suppressed: false);

bool suppressed = await Hydra.isGamificationSuppressed();
```

**6. Theme** of gamification UI (`HydraThemeMode`: `none` keeps the campaign's own theme, `auto` follows the device, `light`, `dark`). `setThemeMode` throws if the SDK isn't initialised; `getThemeMode` returns `HydraThemeMode.none` then.

```dart
await Hydra.setThemeMode(mode: HydraThemeMode.dark);

HydraThemeMode mode = await Hydra.getThemeMode();
```

**7. Events** on your handler: `onGamificationDeeplink` (a campaign asks the app to open `url`: route it in your navigation), `onGamificationEventTrigger` (a game or campaign triggered a named event with a `payload`, e.g. reward unlocked), `onGamificationAnalyticsEvent` (analytics events to forward to your own analytics tool).

### Multi-account
One app talking to several Hydra accounts (e.g. India, the USA, Europe). Get each account's values (Account Id, Base URL, SSL public key, and Org Id / gamification values if used) from the apps team. Single account: nothing to do here.

The native initialisation sets the **default** account; from Dart you then switch with one of two `HydraCore` methods, depending on where the values come from.

**Option A: Firebase Remote Config.** Keep the default account in the standard keys (step 1) and publish one extra set per additional account with a prefix of your choice, e.g. India: `ind_hydra_account_id`, `ind_hydra_base_url`, `ind_hydra_ssl_public_key`, `ind_hydra_remote_log_level`, plus `ind_hydra_org_id` (visitor flow) and `ind_hydra_gamification_key`, `ind_hydra_gamification_region`, `ind_hydra_gamification_base_url` (gamification). Switch with `setFirebaseRemoteConfigKeys`, passing one `HydraFirebaseRemoteConfigKeys` with that account's key names:

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

This reads the values Remote Config has **already fetched**; it doesn't fetch them, so the prefixed keys must be published. If they aren't, the account isn't switched: on iOS the call returns `false`, but **on Android it still returns `true`** and only logs "Failed to get values for these keys from Firebase remote config".

> ⚠️ Correction: ✅ Use a single `HydraFirebaseRemoteConfigKeys` object for `setFirebaseRemoteConfigKeys`, as above (flutter-sdk-advanced-setup). ❌ Don't pass the `Map` built in the `HydraFirebaseRemoteConfigKeys` usage sample (flutter-sdk-api-reference; Flutter guide p.22), which reuses the variable name of the `setFirebaseRemoteConfigKeys` call. *Pending SME confirmation.*

**Option B: values you fetch yourself** (your own backend or another CMS). Switch with `setHydraAccountConfig`:

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

**Order (don't call `identify` before the account is set):**
1. Wait for `onHydraSdkInitializationResult` (with Option A, this also means Remote Config has fetched its values).
2. Call `setHydraAccountConfig` or `setFirebaseRemoteConfigKeys` and wait for the `Future` to complete.
3. Call `Hydra.identify(...)`.

```dart
await HydraCore.setHydraAccountConfig(hydraAccountConfig: accountConfigForUser);
await Hydra.identify(userDetails: HydraUserDetails(customerId: customerId));
```

**How switching behaves:** the SDK re-initialises with the new account straight away; setting the already-active account changes nothing. **The chosen account (or, for Option A, its key names) persists** on the device and is used on every later launch in place of what the native initialisation passes; the native initialisation only decides the account for a fresh install.

**Start on a non-default account (custom key names at native init).** Call the initializer **after** `GeneratedPluginRegistrant.register(...)` (Hydra reads `capillary/hydra-config.json` through the plugin registrar, so plugins must already be registered).

*iOS, app-delegate lifecycle:* in `application(_:didFinishLaunchingWithOptions:)`, after `GeneratedPluginRegistrant.register(with: self)` and before `super.application(...)`. `keyForAccountId`, `keyForBaseUrl`, `keyForSsl`, `keyForRemoteLogLevel` are required; org and gamification keys optional.

```swift file=ios/Runner/AppDelegate.swift
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

*iOS, UIScene lifecycle:* plugins register in `didInitializeImplicitFlutterEngine(_:)`, after launch, so call it there, passing `UIApplication.shared` and `nil` launch options:

```swift
import capillary_hydra_ios

func didInitializeImplicitFlutterEngine(_ engineBridge: FlutterImplicitEngineBridge) {
  GeneratedPluginRegistrant.register(with: engineBridge.pluginRegistry)
  // `keys` is your Firebase Remote Config keys object; the docs' sample doesn't show how it is built
  HydraNativeAPI.shared.initApplicationWithFirebaseRemoteConfig(UIApplication.shared, didFinishLaunchingWithOptions: nil, firebaseRemoteConfigKeys: keys)
}
```

(`keys` is built as in the app-delegate sample.)

*Android:* in your `HydraApplication` subclass (step 11, Option B), immediately after `super.onCreate()`:

```kotlin file=android/app/src/main/kotlin/<your-package>/ExampleApplication.kt
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

> ⚠️ Gap: not documented: the Android `HydraFirebaseRemoteConfigKeys` call without the org / gamification keys, and whether to call `Hydra.reset` before switching accounts for a signed-in user. Ask a Capillary engineer.

## Verification
- **Init:** `onHydraSdkInitializationResult` reports `success: true` (or `false` with `error`).
- **Account switch:** the set call returns whether the update was requested. With `setFirebaseRemoteConfigKeys`, iOS returns `false` if the prefixed keys aren't published; Android returns `true` anyway, so check the log for "Failed to get values for these keys from Firebase remote config".
- **Push:** `requestPermission()` returns `true`; a token arrives (`onTokenAvailable` / `getFCMToken()`); `onHydraNotificationReceived` fires on a Hydra push.
- **Core calls** return `true` when the request was made (not proof Capillary processed it).
- **Inbox:** received pushes appear in `getInboxMessages()`. **Visitor:** `isVisitorFlowEnabled()`, `getCurrentUserState()`, `getVisitorDetails()`.
- **Gamification:** campaigns appear on reported screens; widgets report a height where content exists (`0` means collapse; use `height >= 0`); `isGamificationSuppressed()` returns the value you set.
- **Logs:** `console_log_level` `4` or `5` in `hydra-config.json`; remote level via `hydra_remote_log_level`.

**Gamification checklist.** Required: both packages on the same version; `hydra_gamification_key`, `hydra_gamification_region` and `hydra_gamification_base_url` in Remote Config; screen names reported; `Hydra.setCapToken(...)` before mounting the Loyalty View. Optional: Banner, Embed, Loyalty View.

> ⚠️ Gap: no expected log lines, dashboard checks or test-push procedure are documented, nor whether a handler registered after initialisation finishes still receives `onHydraSdkInitializationResult`. Ask a Capillary engineer.

## Known Issues
| Symptom | Cause | Fix |
|---|---|---|
| Hydra doesn't initialise with a custom Android Application class | Only exactly `HydraApplication` auto-initialises | Extend `HydraApplication`, register its FQN, call `HydraInitializer.initializeUsingFirebaseRemoteConfig(this)` right after `super.onCreate()` (step 11) |
| Android application theme doesn't derive from AppCompat | The Hydra plugin requires an AppCompat theme | e.g. `@style/Theme.AppCompat.DayNight.NoActionBar` (step 12) |
| iOS initializer called before `GeneratedPluginRegistrant.register(...)` | Hydra reads `capillary/hydra-config.json` through the plugin registrar, so plugins must already be registered | Call it after registration and before `super.application(...)`; with UIScene, in `didInitializeImplicitFlutterEngine(_:)` (Multi-account) |
| `setFirebaseRemoteConfigKeys` returns `true` on Android but the account doesn't switch | Prefixed keys not published / not fetched; Android only logs "Failed to get values for these keys from Firebase remote config" (iOS returns `false`) | Publish the prefixed keys; call after `onHydraSdkInitializationResult` |
| Multi-account: `identify` called before the account is set | The account must be set first | Await the set call, then `identify` |
| Native key names / default keys ignored after a switch | The chosen account persists on the device; native init only decides the account on a fresh install | Set the account again with the set method |
| iOS rich notifications / Inbox API not working | Notification Service Extension or shared App Group missing | Extension + same App Group `group.<runner_target_bundle_id>.hydra` on both targets |
| `getFCMToken()` throws | No FCM token available yet | Catch it, or use `onTokenAvailable` |
| Hydra has no token on Android although the app gets FCM tokens itself | App obtains tokens outside Hydra (e.g. `firebase_messaging`) | `HydraPushNotification.passFCMToken` on each new token (Push item 7) |
| Handler stops compiling after an SDK upgrade | Handler `implements` `HydraNativeEventHandler` and new callbacks were added | `extends` it instead (step 13) |
| Inbox UI doesn't refresh | No "inbox updated" event | Refresh on `onHydraNotificationReceived` / `onNotificationCenterDismissed`, or call `HydraInbox` on demand |
| Gamification base URL not recognised | Wrong Remote Config key name | `hydra_gamification_base_url`, not `hydra_gamification_url` |
| Gamification campaigns never appear | `hydra_gamification_key` / `hydra_gamification_region` missing, or screens not reported | Add the keys; call `gamificationScreenAppeared` |
| Campaigns don't re-evaluate on a persistent screen | No `initState` / `dispose` on refocus | `RouteObserver` + `RouteAware` + lifecycle observer |
| Loyalty View shows no loyalty content | Cap token set after the view bound, or missing | `setCapToken` **before** mounting the view |
| Widget keeps empty space after a campaign closes | `onHeightChanged` handler ignores `0` | Collapse on `0` (`height >= 0`) |
| `setGamificationSuppressed` / `isGamificationSuppressed` / `setThemeMode` throw | SDK not initialised yet | Call after `onHydraSdkInitializationResult(success: true)` |
| User not linked in CRM | `customerId` doesn't match the Account Linking Identifier | Use the configured identifier |
| In-app inside Flutter doesn't work | `enable_in_app_messaging_in_flutter` is non-functional | Keep it `false` |
| SDK log shows `Client Credentials Generation Failed` / `source not found` (400) | Android: the App Signature registered at Capillary doesn't match the build's SHA256 | Compare them and ask Capillary to update it (`_shared/push.md`) |
| Push never arrives although sign-in works | App's Firebase project differs from the one registered at Capillary, or the push gateway isn't set up | `_shared/push.md` › Common problems |

## API Reference
**Remote Config keys:** `hydra_account_id`, `hydra_base_url`, `hydra_ssl_public_key`, `hydra_remote_log_level`, `hydra_org_id`, `hydra_gamification_key`, `hydra_gamification_region`, `hydra_gamification_base_url`; multi-account uses a prefix (e.g. `ind_hydra_account_id`).

**`hydra-config.json` keys:** step 3. **Icons in `capillary/icons/`:** `hydra_notification_small_icon`, `hydra_in_app_placeholder`, `hydra_inbox_ui_placeholder` (png, jpg or jpeg).

**Dart APIs** (all static; `package:capillary_hydra/hydra.dart`; models from `package:capillary_hydra_platform_interface/capillary_hydra_platform_interface.dart`)

| API | Returns | Notes |
|---|---|---|
| `HydraInitializer.initialize()` | | In `main()` before `runApp` |
| `Hydra.identify({required HydraUserDetails userDetails, Map<String, dynamic>? customAttributes})` | `Future<bool>` | |
| `Hydra.track({required String eventName, Map<String, dynamic>? attributes})` | `Future<bool>` | |
| `Hydra.reset({required String customerId})` | `Future<bool>` | Sign out |
| `Hydra.getCurrentUserState()` | `Future<UserState?>` | Visitor |
| `Hydra.getVisitorDetails()` | `Future<HydraVisitorInfo?>` | Visitor |
| `Hydra.isVisitorFlowEnabled()` | `Future<bool>` | Visitor |
| `Hydra.gamificationScreenAppeared({required String screenName})` / `gamificationScreenDisappeared({required String screenName})` | `Future<void>` | Same `screenName` |
| `Hydra.setCapToken({required String token})` | `Future<void>` | Before mounting `GamificationLoyaltyView` |
| `Hydra.setGamificationSuppressed({required bool suppressed})` | `Future<void>` | Throws if SDK not initialised |
| `Hydra.isGamificationSuppressed()` | `Future<bool>` | Throws if SDK not initialised |
| `Hydra.setThemeMode({required HydraThemeMode mode})` | `Future<void>` | Throws if SDK not initialised |
| `Hydra.getThemeMode()` | `Future<HydraThemeMode>` | `none` if SDK not initialised |
| `HydraCore.updateUser({required HydraUserDetails userDetails, Map<String, dynamic>? customData, List<Map<String, dynamic>>? subscriptions})` | `Future<bool>` | |
| `HydraCore.updateGeoConfig({required HydraGeoConfig config})` | `Future<bool>` | |
| `HydraCore.updatePushPreferences({required String customerId, required HydraPushPreferences preferences})` | `Future<bool>` | |
| `HydraCore.setHydraAccountConfig({required HydraAccountConfig hydraAccountConfig})` | `Future<bool>` | Switch account with values you fetch yourself (Multi-account, Option B) |
| `HydraCore.setFirebaseRemoteConfigKeys({required HydraFirebaseRemoteConfigKeys hydraFirebaseRemoteConfigKeys})` | `Future<bool>` | Switch account via prefixed Remote Config key names (Multi-account, Option A) |
| `HydraPushNotification.requestPermission()` | `Future<bool>` | Can throw |
| `HydraPushNotification.getFCMToken()` | `Future<String>` | Throws if no token |
| `HydraPushNotification.passFCMToken({required String token})` | `Future<void>` | Android only; no-op on iOS |
| `HydraInbox.getInboxMessages()` | `Future<List<HydraNotification>>` | |
| `HydraInbox.getUnreadInboxMessagesCount()` | `Future<int>` | |
| `HydraInbox.markInboxMessageAsRead({required HydraNotification notification})` | `Future<bool>` | |
| `HydraInbox.deleteInboxMessage({required HydraNotification notification})` | `Future<bool>` | |
| `HydraInbox.deleteAllInboxMessages()` | `Future<bool>` | |
| `HydraInboxUI.showNotificationCenter()` / `hideNotificationCenterIfShowing()` | `Future<void>` | |
| `HydraNativeEvents.addEventHandler(handler)` / `removeEventHandler(handler)` / `removeAllEventHandlers()` | `void` | |

**`HydraNativeEventHandler` callbacks** (empty default bodies; extend it)

| Callback | Fires when |
|---|---|
| `onTokenAvailable({required String token})` | New FCM token |
| `onHydraNotificationReceived({required HydraNotification notification})` | Hydra notification received |
| `onHydraNotificationClicked({HydraNotificationCTA? cta, HydraNotification? notification})` | Clicked in system tray, built-in notification center, or CTA on an in-app message |
| `onHydraNotificationDismissed({required HydraNotification notification})` | Dismissed in system tray |
| `onHydraNotificationShown({required HydraNotification notification})` | Shown in system tray |
| `onNonHydraNotificationReceived({required NonHydraNotification notification})` / `onNonHydraNotificationClicked({NonHydraNotification? notification})` | Same, non-Hydra push |
| `onNotificationCenterDismissed()` | Built-in notification center dismissed |
| `onHydraSdkInitializationResult({required bool success, String? error})` | Init succeeded / failed |
| `onConfigFetched({required bool isVisitorFlowEnabled})`, `onLegacyFlowReady()`, `onVisitorSessionReady()`, `onUserStateChanged({UserState? userState})` | Visitor-flow lifecycle |
| `onGamificationEventTrigger({required String name, required Map<String, dynamic> payload})` | Campaign / game triggered a named event |
| `onGamificationAnalyticsEvent({required String name, required Map<String, dynamic> payload})` | Gamification UI analytics event |
| `onGamificationDeeplink({required String url})` | Campaign asks the app to open a deep link |

**Widgets:** `GamificationBannerView({ required String bannerId, void Function(double height)? onHeightChanged })`, `GamificationEmbedView({ required String embedId, void Function(double height)? onHeightChanged })`, `GamificationLoyaltyView({ required String loyaltyId, void Function(double height)? onHeightChanged })`.

**Models and enums**

| Type | Fields / values |
|---|---|
| `HydraUserDetails` | `customerId` (required), `email`, `phoneNumber`, `firstName`, `lastName` (`String?`) |
| `HydraGeoConfig` | `city`, `country`, `countryCode` (required); `timezone` (optional) |
| `HydraPushPreferences` | `promPushEnabled`, `transPushEnabled` (required `bool`) |
| `HydraLogLevel` | `off(0)`, `error(1)`, `warn(2)`, `info(3)`, `debug(4)`, `verbose(5)` |
| `HydraAccountConfig` | `accountId`, `baseUrl`, `sslPublicKey` (`String`), `remoteLogLevel` (`HydraLogLevel`) required; `orgId`, `gamificationKey`, `gamificationRegion`, `gamificationBaseUrl` (`String?`) optional |
| `HydraFirebaseRemoteConfigKeys` | `keyForAccountId`, `keyForBaseUrl`, `keyForSsl`, `keyForRemoteLogLevel` (`String`) required; `keyForOrgId`, `keyForGamificationKey`, `keyForGamificationRegion`, `keyForGamificationBaseUrl` (`String?`) optional |
| `HydraThemeMode` | `none`, `auto`, `light`, `dark` |
| `UserState` | `none`, `legacyRegistered`, `visitor`, `merged`, `signedOut` |
| `HydraVisitorInfo` | `String? visitorId` |
| `HydraNotification` (all final, nullable) | `cuid`, `scope`, `campaignId`, `variationId`, `senderId`, `senderSource`, `custom`, `customData` (`Map<String, dynamic>?`), `priority`, `validity`, `messageId`, `gateway` (`HydraNotificationGateway?`), `body` (`HydraNotificationBody?`), `expandableDetails` (`HydraNotificationExpandedDetails?`), `isRead`, `imageIdentifier`, `accountId`, `channelId`, `payload`, `createdAt` (`DateTime?`), `isExpanded`, `isMessageEllipsized`, `isTitleEllipsized`, `showArrow` |
| `HydraNotificationBody` | `title`, `message`, `image`, `cta` (`HydraNotificationCTA?`) |
| `HydraNotificationCTA` | `type` (`HydraNotificationCTAType?`), `action`, `actionText` |
| `HydraNotificationCTAType` | `external`, `deepLink`, `rating`, `feedback`, `appRating`, `unknown` |
| `HydraNotificationExpandedDetails` | `ctas` (`List<HydraNotificationCTA>?`), `message`, `image`, `style` |
| `HydraNotificationGateway` | `fcm`, `xiaomi`, `unknown` |
| `NonHydraNotification` | `title`, `body`, `icon`, `imageUrl` (`String?`); `data` (`Map<String, dynamic>`) |

**Native APIs**

| API | Notes |
|---|---|
| Android `com.capillary.plugins.hydra.HydraApplication` | Set in manifest (auto-init, default keys), or extend |
| Android `HydraInitializer.initializeUsingFirebaseRemoteConfig(this)` / `(this, keys)` (`com.capillary.plugins.hydra.nativeapis.HydraInitializer`) | From a `HydraApplication` subclass, right after `super.onCreate()` |
| Android `HydraFirebaseRemoteConfigKeys(...)` (`com.capillary.plugins.hydra.nativeapis.HydraFirebaseRemoteConfigKeys`) | Eight positional strings: account id, base URL, SSL key, remote log level, org id, gamification key, region, base URL |
| iOS `HydraFirebaseRemoteConfigKeys(keyForAccountId:keyForBaseUrl:keyForSsl:keyForRemoteLogLevel:keyForOrgId:keyForGamificationKey:keyForGamificationRegion:keyForGamificationBaseUrl:)` (`import capillary_hydra_ios`) | First four required |
| iOS `HydraNativeAPI.shared.initApplicationWithFirebaseRemoteConfig(_:didFinishLaunchingWithOptions:firebaseRemoteConfigKeys:)` | Custom keys; after `GeneratedPluginRegistrant.register(...)`; UIScene: in `didInitializeImplicitFlutterEngine(_:)` with `UIApplication.shared`, `nil` |
| iOS `HydraNativeAPI.shared.application(_:didReceiveRemoteNotification:fetchCompletionHandler:)` | In-App setup |
| iOS `HydraRemoteNotificationService` (`import HydraPushNotificationServiceExtension`) | In the extension: `didReceive(_:withContentHandler:)`, `serviceExtensionTimeWillExpire()` |
