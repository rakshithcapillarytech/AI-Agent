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
The account values (Account Id, Base URL, SSL public key, remote log level; optionally Org Id and gamification values) are passed straight to the SDK instead of read from Firebase Remote Config. They can come from another CMS or be hardcoded. Three ways: Android native (step 6), iOS native (step 11), or Dart `HydraCore.setHydraAccountConfig` (step 12).

**Direct mode only replaces Remote Config. Push still uses Firebase Cloud Messaging** (the guide's Push section isn't mode-specific, and tokens are FCM tokens), so push needs the Firebase files (Modules → Push). This differs from native Android direct mode (`android/direct.md`); don't carry its "no Firebase" rule over to Flutter.

| Module | Status |
|---|---|
| Core, Visitor, Gamification | Documented (values passed in the direct config) |
| Push, In-App, Inbox API, Inbox UI | Documented (same as Firebase mode; push needs FCM) |
| Multi-account | Partly documented (`HydraCore.setHydraAccountConfig`) |

> ⚠️ Gap: the guide doesn't say whether an app using neither Remote Config nor push can drop `google-services.json` / `GoogleService-Info.plist` / the Google Services plugin, or whether in-app works without the push setup. Ask a Capillary engineer before removing Firebase.

## Requirements
- `capillary_hydra` and `capillary_hydra_platform_interface` at `^{{sdk_version}}` from pub.dev (`https://pub.dev/packages/capillary_hydra`).
- Android: your own Application class extending `HydraApplication` (Kotlin sample); an AppCompat theme (step 8).
- iOS: CocoaPods with `use_frameworks!`, or Swift Package Manager; Xcode.
- Push only: a Firebase project with the app registered; Google Services Gradle plugin `4.4.2`; access to `developer.apple.com`.

> ⚠️ Gap: minimum Flutter / Dart, Android minSdk / compileSdk / AGP / Gradle / Kotlin, iOS deployment target, Xcode and CocoaPods versions aren't documented. Ask a Capillary engineer.

## Prerequisites
Common exchange: `_shared/prerequisites.md`.
- **Client gives Capillary's apps team:** iOS bundle ID (`{{bundle_id}}`), Android applicationId (`{{application_id}}`), app signature (SHA256) from the Android signing report.
- **Capillary gives the client:** Account Id, Base URL (end point), SSL public key (required); Org Id (visitor flow only); Gamification Key, Region and Base URL (gamification only).
- **Value source:** a CMS other than Firebase Remote Config, or hardcoded.
- **CRM:** `customerId` must match the Account Linking Identifier (see `_shared/prerequisites.md`).
- **Loyalty View only:** a Capillary B2B short-lived token, set before the Loyalty View is mounted (how to obtain it isn't documented; see `_shared/prerequisites.md`).
- **Example app:** `https://pub.dev/packages/capillary_hydra/example`.

> ⚠️ Gap: Getting Started (p.1) calls a remote configuration (CMS) tool "mandatory", while the direct-init sections (pp.7–8) allow hardcoded values; the samples also don't show fetching from a CMS (e.g. asynchronously) before native init. Ask a Capillary engineer.

## Steps

### 1. Add the packages to `pubspec.yaml`
Capillary announces new versions.

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
  "enable_in_app_messaging_in_flutter": false
}
```

| Key | Type | Default | Platform | Meaning |
|---|---|---|---|---|
| `console_log_level` | number | `4` | Android & iOS | Console log level 0–5 (0=off, 1=error, 2=warn, 3=info, 4=debug, 5=verbose) |
| `enable_in_app_messaging` | boolean | `false` | Android & iOS | In-app messaging (needs placeholder image) |
| `enable_in_app_messaging_in_flutter` | boolean | `false` | Android only | **Currently non-functional. Don't enable in production.** |
| `enable_inbox_api` | boolean | `false` | Android & iOS | Inbox API |
| `enable_inbox_ui` | boolean | `false` | Android & iOS | Built-in notification center |
| `use_default_inbox_ui_config` | boolean | `true` | iOS only | SDK's default notification center layout |
| `max_notification_count` | number | `200` | Android & iOS | Max notifications kept |
| `hydra_notification_color` | string | – | Android only | Notification tint colour |

The **remote** log level isn't a Remote Config key here: pass it in the direct config (Android Builder 4th argument, iOS `remoteLogLevel`, or `HydraAccountConfig.remoteLogLevel`).

### 3. Declare the config folder as assets
Add `capillary/icons/` once you add icon images (Modules → Push, In-App, Inbox UI).

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
Part of the guide's general Flutter setup, before any choice of config source.

```dart file=lib/main.dart
import 'package:capillary_hydra/hydra.dart';
import 'package:flutter/material.dart';

void main() {
  WidgetsFlutterBinding.ensureInitialized();
  HydraInitializer.initialize();
  runApp(const MyApp());
}
```

This Dart `HydraInitializer` (`package:capillary_hydra/hydra.dart`) is not the native Android `com.capillary.plugins.hydra.nativeapis.HydraInitializer` in step 6.

### 6. Android: create an Application class that passes the values
Flutter has no custom Application class by default, but Hydra needs one. Create a class that **extends `HydraApplication`** (or change your existing one to), build a `HydraRemoteConfig` with its `Builder`, and pass it to `HydraInitializer.initialize` **immediately after `super.onCreate()`**.
- Required: `accountId`, `baseURL`, `sslPublicKey`. 4th argument: remote debug level (defaults to `0`; sample passes `4`, debug).
- Optional: `orgId` (visitor flow); `gamificationKey` / `gamificationRegion` / `gamificationBaseUrl`.

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

### 7. Android: register your Application class
Point `android:name` at your class's **fully qualified name** (package + class):

```xml file=android/app/src/main/AndroidManifest.xml
<application
    android:name="<your.package>.ExampleApplication"
    ...>
```

Don't point it at `com.capillary.plugins.hydra.HydraApplication` itself: exactly `HydraApplication` auto-initialises from the default Firebase Remote Config keys.

### 8. Android: set an AppCompat theme
The Hydra plugin requires the application theme to derive from AppCompat:

```xml file=android/app/src/main/AndroidManifest.xml
<application
    ...
    android:theme="@style/Theme.AppCompat.DayNight.NoActionBar">
```

### 9. iOS: add Hydra to the Podfile (CocoaPods only)
**Skip if Swift Package Manager is enabled.** At the top of `ios/Podfile`:

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

> ⚠️ Gap: with Swift Package Manager the guide only says to skip the Podfile steps (`require_relative`, `hydra_pods`, `extension_pods`); it gives no SPM steps, including how the extension target gets `HydraPushNotificationServiceExtension`. Ask a Capillary engineer.

### 10. iOS: install pods
In the `ios` folder:

```bash
pod install
```

### 11. iOS: initialise the SDK in `AppDelegate.swift` with the values
By default the plugin auto-initialises from the default Remote Config keys. To pass values directly, initialise it yourself **after `GeneratedPluginRegistrant.register(with:)` and before `super.application(...)`**. Required: `accountId`, `baseUrl`, `sslPublicKey`. Optional: `orgId` (visitor flow) and the gamification values.

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

> ⚠️ Gap: the guide doesn't show this call without the optional values (omit them or pass `nil`?), or say when `HydraRemoteConfig(...)` returns `nil` (the sample force-unwraps `remoteConfig!`, which would crash at launch). Ask a Capillary engineer.

### 12. (Alternative) Pass the values from Dart with `HydraCore.setHydraAccountConfig`
For when you fetch the account values yourself rather than via Remote Config. `HydraAccountConfig` requires `accountId`, `baseUrl`, `sslPublicKey`, `remoteLogLevel` (`HydraLogLevel`); `orgId` and the gamification values are optional. Fill the variables with `{{account_id}}`, `{{base_url}}`, `{{ssl_public_key}}`, `{{org_id}}`, `{{gamification_key}}`, `{{gamification_region}}`, `{{gamification_base_url}}`. Returns whether the update was requested.

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

> ⚠️ Gap: the native setup to pair with the Dart-only path isn't documented (which Android initialiser, if any; exactly `HydraApplication` would auto-read Remote Config), nor what happens before the call or whether values persist. Until confirmed, prefer steps 6 and 11. Ask a Capillary engineer.

### 13. Register a native event handler and wait for initialisation
Before using any `capillary_hydra` API, make sure the SDK initialised successfully. Write a class that extends or implements `HydraNativeEventHandler` (override only what you need; all methods have empty defaults) and register it:

```dart
HydraNativeEvents.addEventHandler(handler);
```

The result arrives in:

```dart
void onHydraSdkInitializationResult({required bool success, String? error})
```

### 14. Identify, track and reset the user
`customerId` is required and **must match the Account Linking Identifier in Capillary CRM** (mobile, email, InTouchUserId, externalId or FCMToken; *Organisation Settings → Omni Channel Settings → Channel Configurations → MAPP_SDK → Account Linking Identifier*). `identify` also takes optional `customAttributes` (`Map<String, dynamic>?`).

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

bool updateGeoConfigResult = await HydraCore.updateGeoConfig(config: config);
```

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
**1. Register the app with Firebase and add the config files** (still needed: push uses FCM).
1. Register the app on Firebase (the guide's link: `https://support.google.com/appsheet/answer/10104995?hl=en`).
2. Download `google-services.json` and `GoogleService-Info.plist`. **Don't make the code changes the Firebase console suggests while generating them.**
3. **iOS:** add `GoogleService-Info.plist` to the iOS project in Xcode.
4. **Android:** add `google-services.json` to `android/app`.
5. **Android:** declare the Google Services plugin in the root `plugins` block.

   ```kotlin file=android/settings.gradle.kts
   id("com.google.gms.google-services") version "4.4.2" apply false
   ```

   ```groovy file=android/settings.gradle
   id 'com.google.gms.google-services' version '4.4.2' apply false
   ```
6. **Android:** apply the plugin in the app's `plugins` block.

   ```kotlin file=android/app/build.gradle.kts
   id("com.google.gms.google-services")
   ```

   ```groovy file=android/app/build.gradle
   id 'com.google.gms.google-services'
   ```

> ⚠️ Gap: the guide's Firebase registration link points to a Google AppSheet help article, not Firebase documentation. Ask a Capillary engineer which guide is intended.

**2. iOS capabilities.** On `developer.apple.com`, add the **Push Notification** capability to the app identifier. In Xcode → app target → **Signing & Capabilities**, add **Push Notification** and **Background Modes** (enable **Background fetch** and **Remote notifications**).

**3. iOS Notification Service Extension (rich notifications are mandatory).**
1. In Xcode, add a **Notification Service Extension** target. Its bundle ID is the main bundle ID plus the extension's product name; register it on `developer.apple.com`.
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

**4. Android notification colour.** Set `hydra_notification_color` in `hydra-config.json` (step 2).

**5. Small icon.** Create `capillary/icons/` if needed and add `hydra_notification_small_icon` (png, jpg or jpeg; png recommended). It's the notification-drawer icon. Declare the folder in assets (step 3).

**6. Permission and token (Dart).** Call `requestPermission` before you can receive push. It returns whether permission was granted and can throw.

```dart
bool granted = await HydraPushNotification.requestPermission();
```

```dart
String fcmToken = await HydraPushNotification.getFCMToken();
```

`getFCMToken` **throws if no FCM token is available**. Alternatively, use the `onTokenAvailable` callback.

**7. Callbacks:** `onHydraNotification*` and `onNonHydraNotification*` on `HydraNativeEventHandler` (API Reference).

### In-App
1. Set `enable_in_app_messaging` to `true` in `hydra-config.json`.
2. Add `hydra_in_app_placeholder` (png, jpg or jpeg) to `capillary/icons`.
3. **iOS:** at the top of `AppDelegate.swift` add (already there if you did step 11):

   ```swift file=ios/Runner/AppDelegate.swift
   import capillary_hydra_ios
   ```

   and add this function:

   ```swift file=ios/Runner/AppDelegate.swift
   override func application(_ application: UIApplication, didReceiveRemoteNotification userInfo: [AnyHashable: Any], fetchCompletionHandler completionHandler: @escaping (UIBackgroundFetchResult) -> Void) {
       HydraNativeAPI.shared.application(application, didReceiveRemoteNotification: userInfo, fetchCompletionHandler: completionHandler)
   }
   ```

In-app clicks arrive in `onHydraNotificationClicked`. Keep `enable_in_app_messaging_in_flutter` `false` (non-functional).

### Inbox
**Inbox API.** The SDK stores received notifications in a local database, capped by `max_notification_count`, so the inbox depends on Modules → Push.
1. Set `enable_inbox_api` to `true`.
2. **iOS:** the Notification Service Extension must be set up (Modules → Push, item 3).

```dart
List<HydraNotification> notifications = await HydraInbox.getInboxMessages();
int unreadNotificationCount = await HydraInbox.getUnreadInboxMessagesCount();
bool marked = await HydraInbox.markInboxMessageAsRead(notification: notification);
bool deleted = await HydraInbox.deleteInboxMessage(notification: notification);
bool deleted = await HydraInbox.deleteAllInboxMessages();
```

These are separate usage samples (rename variables if used together). `notification` must come from `getInboxMessages`. There's no "inbox updated" event: refresh from `onHydraNotificationReceived` or `onNotificationCenterDismissed`, or poll `HydraInbox`.

**Inbox UI** (built-in notification center).
1. Enable the Inbox API.
2. Set `enable_inbox_ui` to `true`.
3. Add `hydra_inbox_ui_placeholder` (png, jpg or jpeg) to `capillary/icons`.

```dart
HydraInboxUI.showNotificationCenter();
await HydraInboxUI.hideNotificationCenterIfShowing();
```

`onNotificationCenterDismissed()` fires when it closes.

> ⚠️ Gap: what `use_default_inbox_ui_config: false` does, and how to customise the notification center, isn't documented. Ask a Capillary engineer.

### Visitor
States: `none` → `visitor` (anonymous) → `merged` / `legacyRegistered` (identified) → `signedOut`.
1. Pass the Org Id in the direct config: `.orgId("{{org_id}}")` on the Android Builder (step 6), `orgId:` in iOS `HydraRemoteConfig` (step 11), or `orgId` in `HydraAccountConfig` (step 12).
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

> ⚠️ Gap: the Integration doc (pp.53, 58) gives the minimum as an unreleased "1.1.0"; the Flutter guide (p.2) pins `^1.1.1-beta.6`. Whether a stable release with gamification exists is undocumented. Ask a Capillary engineer.

**1. Configure.** Pass the gamification values in the direct config, configured the same way as the base account values:
- **Android:** `.gamificationKey(...)`, `.gamificationRegion(...)`, `.gamificationBaseUrl(...)` on the Builder (step 6);
- **iOS:** `gamificationKey:`, `gamificationRegion:`, `gamificationBaseUrl:` in `HydraRemoteConfig` (step 11);
- **Dart:** the same fields in `HydraAccountConfig` (step 12).

Key and region are mandatory; HydraGamification stays disabled if either is missing.

> ⚠️ Gap: the Integration doc (p.54) says the base URL is optional; the Flutter guide (pp.1, 10, 21) says gamification requires it. Ask a Capillary engineer.

**2. Report the current screen (mandatory for screen-targeted campaigns).** Campaign visibility and eligibility depend on the reported screen. Call `gamificationScreenAppeared` when a screen appears and `gamificationScreenDisappeared` when it disappears, **with the same `screenName`**.

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

A screen that stays mounted under pushed routes (e.g. a persistent Home tab) doesn't get `initState` / `dispose` when it regains focus. Use `RouteObserver` + `RouteAware`, and observe the app lifecycle so campaigns re-evaluate on background / foreground:

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

> ⚠️ Correction: ✅ Use `Hydra.gamificationScreenDisappeared(screenName: ...)` with the same `screenName` as `...Appeared` (Flutter guide p.15 declares it required). ❌ Don't use `Hydra.gamificationScreenDisappeared()` with no argument (Integration doc samples, pp.54–55). *Pending SME confirmation.*

> ⚠️ Gap: the `RouteAware` sample omits subscribing to `routeObserver` and registering the `WidgetsBindingObserver` (and unsubscribing); without them the callbacks never fire. Ask a Capillary engineer for the full sample.

**3. Set the Capillary token (required for Loyalty View).** Set the Capillary B2B short-lived token **before** rendering the Loyalty View; without a valid token, loyalty content may not show.

```dart
Hydra.setCapToken(token: 'token');
```

**4. Automatic experiences.** Once a screen is reported, Floating Button, Popup and Bottom Sheet campaigns targeted at it show automatically.

**5. Optional widgets** (native `PlatformView`s): `GamificationBannerView`, `GamificationEmbedView`, `GamificationLoyaltyView` (signatures: API Reference).

*Banner View.* Pass a unique ID; use `onHeightChanged` to resize as content loads:

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

The Integration doc's version also checks `mounted` before `setState` (`if (height > 0 && mounted)`).

*Embed View.* Same pattern; `embedHeight` is a state field:

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

*Loyalty View.* Fills the size it's given and **never reports a height change**: give it a fixed-height parent (`SizedBox`) or `Expanded`. **Call `Hydra.setCapToken(token: ...)` before mounting it**; the native SDK can't bind the view without a cap token.

```dart
SizedBox(
    height: 611,
    child: GamificationLoyaltyView(loyaltyId: '{{loyalty_id}}'),
)
```

### Multi-account
Pass the other account's values from Dart with `HydraCore.setHydraAccountConfig` (step 12); the guide labels it "multi-account setup". Prefixed Remote Config keys and `setFirebaseRemoteConfigKeys` are Firebase-mode only (`flutter/firebase.md`).

> ⚠️ Gap: how `setHydraAccountConfig` interacts with native init (steps 6, 11), when to call it relative to `identify`, and whether to `reset` first aren't documented. Ask a Capillary engineer.

## Verification
- **Init:** `onHydraSdkInitializationResult` reports `success: true` (or `false` with `error`); with step 12, `setHydraAccountConfig` returns whether the update was requested.
- **Push** (needs the Firebase setup): `requestPermission()` returns `true`; a token arrives (`onTokenAvailable` / `getFCMToken()`); `onHydraNotificationReceived` fires on a Hydra push.
- **Core calls** return `true` when the request was made (not proof Capillary processed it).
- **Inbox:** received pushes appear in `getInboxMessages()`. **Visitor:** `isVisitorFlowEnabled()`, `getCurrentUserState()`, `getVisitorDetails()`.
- **Gamification:** campaigns appear on reported screens; widgets render where placed.
- **Logs:** `console_log_level` `4` or `5`; remote level via the direct config.

> ⚠️ Gap: no expected log lines, dashboard checks or test-push procedure are documented, nor whether a handler registered after initialisation finishes still receives `onHydraSdkInitializationResult`. Ask a Capillary engineer.

## Known Issues
| Issue | Fix |
|---|---|
| SDK reads Remote Config instead of your values, or doesn't initialise | Manifest must point at your own `HydraApplication` subclass (FQN), which calls `HydraInitializer.initialize(this, hydraRemoteConfig)` right after `super.onCreate()` (steps 6–7) |
| Android theme not AppCompat | Use e.g. `@style/Theme.AppCompat.DayNight.NoActionBar` (step 8) |
| iOS manual init misplaced | After `GeneratedPluginRegistrant.register(with:)`, before `super.application(...)` |
| iOS crash at launch on `remoteConfig!` | `HydraRemoteConfig(...)` returned `nil`; when that happens is undocumented (step 11 Gap) |
| iOS rich notifications / Inbox API not working | Notification Service Extension + same App Group `group.<runner_target_bundle_id>.hydra` on both targets |
| `getFCMToken()` throws (no token yet) | Catch it, or use `onTokenAvailable` |
| Inbox UI doesn't refresh (no "inbox updated" event) | Refresh on `onHydraNotificationReceived` / `onNotificationCenterDismissed`, or poll |
| Gamification campaigns never appear | Pass gamification key and region in the direct config; report screens |
| Campaigns don't re-evaluate on a persistent screen | `RouteObserver` + `RouteAware` + lifecycle observer |
| Loyalty View blank or collapsed | Fixed-height parent; `setCapToken` before mounting |
| User not linked in CRM | `customerId` must match the Account Linking Identifier |
| `enable_in_app_messaging_in_flutter` | Non-functional; keep `false` |

## API Reference
**`hydra-config.json` keys:** see step 2. **Icons in `capillary/icons/`:** `hydra_notification_small_icon`, `hydra_in_app_placeholder`, `hydra_inbox_ui_placeholder` (png, jpg or jpeg).

**Dart APIs** (`package:capillary_hydra/hydra.dart`; models from `package:capillary_hydra_platform_interface/capillary_hydra_platform_interface.dart`)

| API | Returns | Notes |
|---|---|---|
| `HydraInitializer.initialize()` | | In `main()` before `runApp` |
| `Hydra.identify({required HydraUserDetails userDetails, Map<String, dynamic>? customAttributes})` | `Future<bool>` | |
| `Hydra.track({required String eventName, Map<String, dynamic>? attributes})` | `Future<bool>` | |
| `Hydra.reset({required String customerId})` | `Future<bool>` | Sign out |
| `Hydra.getCurrentUserState()` | `Future<UserState?>` | Visitor |
| `Hydra.getVisitorDetails()` | `Future<HydraVisitorInfo?>` | Visitor |
| `Hydra.isVisitorFlowEnabled()` | `Future<bool>` | Visitor |
| `Hydra.gamificationScreenAppeared({required String screenName})` | `Future<void>` | |
| `Hydra.gamificationScreenDisappeared({required String screenName})` | `Future<void>` | Same `screenName` |
| `Hydra.setCapToken({required String token})` | `Future<void>` | Before `GamificationLoyaltyView` |
| `HydraCore.updateUser({required HydraUserDetails userDetails, Map<String, dynamic>? customData, List<Map<String, dynamic>>? subscriptions})` | `Future<bool>` | |
| `HydraCore.updateGeoConfig({required HydraGeoConfig config})` | `Future<bool>` | |
| `HydraCore.updatePushPreferences({required String customerId, required HydraPushPreferences preferences})` | `Future<bool>` | |
| `HydraCore.setHydraAccountConfig({required HydraAccountConfig hydraAccountConfig})` | `Future<bool>` | Direct values from Dart / multi-account (step 12) |
| `HydraPushNotification.requestPermission()` | `Future<bool>` | Can throw |
| `HydraPushNotification.getFCMToken()` | `Future<String>` | Throws if no token |
| `HydraInbox.getInboxMessages()` | `Future<List<HydraNotification>>` | |
| `HydraInbox.getUnreadInboxMessagesCount()` | `Future<int>` | |
| `HydraInbox.markInboxMessageAsRead({required HydraNotification notification})` | `Future<bool>` | |
| `HydraInbox.deleteInboxMessage({required HydraNotification notification})` | `Future<bool>` | |
| `HydraInbox.deleteAllInboxMessages()` | `Future<bool>` | |
| `HydraInboxUI.showNotificationCenter()` / `hideNotificationCenterIfShowing()` | `Future<void>` | |
| `HydraNativeEvents.addEventHandler(handler)` / `removeEventHandler(handler)` / `removeAllEventHandlers()` | `void` | |

**`HydraNativeEventHandler` callbacks** (empty default bodies)

| Callback | Fires when |
|---|---|
| `onTokenAvailable({required String token})` | New FCM token |
| `onHydraNotificationReceived({required HydraNotification notification})` | Hydra notification received |
| `onHydraNotificationClicked({HydraNotificationCTA? cta, HydraNotification? notification})` | Clicked in system tray, built-in notification center or in-app message |
| `onHydraNotificationDismissed({required HydraNotification notification})` | Dismissed in system tray |
| `onHydraNotificationShown({required HydraNotification notification})` | Shown in system tray |
| `onNonHydraNotificationReceived({required NonHydraNotification notification})` / `onNonHydraNotificationClicked({NonHydraNotification? notification})` | Same, non-Hydra push |
| `onNotificationCenterDismissed()` | Built-in notification center dismissed |
| `onHydraSdkInitializationResult({required bool success, String? error})` | Init succeeded / failed |
| `onConfigFetched({required bool isVisitorFlowEnabled})`, `onLegacyFlowReady()`, `onVisitorSessionReady()`, `onUserStateChanged({UserState? userState})` | Visitor-flow lifecycle |

**Widgets:** `GamificationBannerView({ required String bannerId, void Function(double height)? onHeightChanged })`, `GamificationEmbedView({ required String embedId, void Function(double height)? onHeightChanged })`, `GamificationLoyaltyView({ required String loyaltyId })`.

**Models and enums**

| Type | Fields / values |
|---|---|
| `HydraUserDetails` | `customerId` (required), `email`, `phoneNumber`, `firstName`, `lastName` |
| `HydraGeoConfig` | `city`, `country`, `countryCode` (required); `timezone` (optional) |
| `HydraPushPreferences` | `promPushEnabled`, `transPushEnabled` (required `bool`) |
| `HydraLogLevel` | `off(0)`, `error(1)`, `warn(2)`, `info(3)`, `debug(4)`, `verbose(5)` |
| `HydraAccountConfig` | `accountId`, `baseUrl`, `sslPublicKey` (`String`), `remoteLogLevel` (`HydraLogLevel`) required; `orgId`, `gamificationKey`, `gamificationRegion`, `gamificationBaseUrl` (`String?`) optional |
| `UserState` | `none`, `legacyRegistered`, `visitor`, `merged`, `signedOut` |
| `HydraVisitorInfo` | `String? visitorId` |
| `HydraNotification` (all final, nullable) | `cuid`, `scope`, `campaignId`, `variationId`, `senderId`, `senderSource`, `custom`, `customData` (`Map<String, dynamic>?`), `priority`, `validity`, `messageId`, `gateway` (`HydraNotificationGateway?`), `body` (`HydraNotificationBody?`), `expandableDetails` (`HydraNotificationExpandedDetails?`), `isRead`, `imageIdentifier`, `accountId`, `channelId`, `payload`, `createdAt` (`DateTime?`), `isExpanded`, `isMessageEllipsized`, `isTitleEllipsized`, `showArrow` |
| `HydraNotificationBody` | `title`, `message`, `image`, `cta` (`HydraNotificationCTA?`) |
| `HydraNotificationCTA` | `type` (`HydraNotificationCTAType?`), `action`, `actionText` |
| `HydraNotificationCTAType` | `external`, `deepLink`, `rating`, `feedback`, `appRating`, `unknown` |
| `HydraNotificationExpandedDetails` | `ctas` (`List<HydraNotificationCTA>?`), `message`, `image`, `style` |
| `HydraNotificationGateway` | `fcm`, `xiaomi`, `unknown` |
| `NonHydraNotification` | `title`, `body`, `icon`, `imageUrl` (`String?`); `data` (`Map<String, dynamic>`) |

**Native APIs (direct init)**

| API | Notes |
|---|---|
| Android `com.capillary.plugins.hydra.HydraApplication` | Base class your Application class extends |
| Android `HydraRemoteConfig.Builder(accountId, baseURL, sslPublicKey, remoteDebugLevel)` (`com.capillary.plugins.hydra.nativeapis.HydraRemoteConfig`) | First three required; `remoteDebugLevel` defaults to `0`. Optional `.orgId()`, `.gamificationKey()`, `.gamificationRegion()`, `.gamificationBaseUrl()`; then `.build()` |
| Android `HydraInitializer.initialize(this, hydraRemoteConfig)` (`com.capillary.plugins.hydra.nativeapis.HydraInitializer`) | Right after `super.onCreate()` |
| iOS `HydraRemoteConfig(accountId:baseUrl:sslPublicKey:remoteLogLevel:orgId:gamificationKey:gamificationRegion:gamificationBaseUrl:)` (`import capillary_hydra_ios`) | `accountId`, `baseUrl`, `sslPublicKey` required; sample force-unwraps the result |
| iOS `HydraNativeAPI.shared.initApplication(_:didFinishLaunchingWithOptions:hydraRemoteConfig:)` | After `GeneratedPluginRegistrant.register(with:)`, before `super.application(...)` |
| iOS `HydraNativeAPI.shared.application(_:didReceiveRemoteNotification:fetchCompletionHandler:)` | In-App setup |
| iOS `HydraRemoteNotificationService` (`import HydraPushNotificationServiceExtension`) | In the extension: `didReceive(_:withContentHandler:)`, `serviceExtensionTimeWillExpire()` |

Remote Config APIs (`setFirebaseRemoteConfigKeys`, `HydraFirebaseRemoteConfigKeys`, `initializeUsingFirebaseRemoteConfig`, `initApplicationWithFirebaseRemoteConfig`) aren't used in this mode; see `flutter/firebase.md`.
