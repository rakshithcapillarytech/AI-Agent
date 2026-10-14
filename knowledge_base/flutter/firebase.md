---
platform: flutter
config_mode: firebase
sdk_package: capillary_hydra
sdk_version: 1.1.1-beta.6
modules_covered: [core, push, inapp, inbox_api, inbox_ui, visitor, gamification, multi_account]
modules_missing: []
sources: ["Flutter-Hydra-Integration-Guide pp.1–24", "Integration document _ Experience+ pp.52–59 (Gamification Flutter Integration Guide)"]
owner: TBD
last_verified: null
review_status: draft   # drafted from the source docs; not yet SME-verified
---
# Flutter (with Firebase Remote Config)

## Coverage
The SDK reads its account values from **Firebase Remote Config** (the Flutter guide's default path). Passing values without Remote Config: see `flutter/direct.md`.

| Module | Status |
|---|---|
| Core, Push, In-App, Inbox API, Inbox UI, Visitor, Gamification | Documented |
| Multi-account | Documented (prefixed Remote Config keys) |

## Requirements
- `capillary_hydra` and `capillary_hydra_platform_interface` at `^{{sdk_version}}` from pub.dev (`https://pub.dev/packages/capillary_hydra`).
- A Firebase project with this app registered (step 11), where you can add Remote Config parameters.
- Android: an AppCompat application theme (step 8); Google Services Gradle plugin `4.4.2` (step 11).
- iOS: CocoaPods with `use_frameworks!`, or Swift Package Manager; Xcode; access to `developer.apple.com` (capabilities, extension bundle ID, App Group).

> ⚠️ Gap: minimum Flutter / Dart, Android minSdk / compileSdk / AGP / Gradle / Kotlin, iOS deployment target, Xcode and CocoaPods versions aren't documented. Ask a Capillary engineer.

## Prerequisites
Common exchange: `_shared/prerequisites.md`. Firebase / Remote Config basics: `_shared/firebase-setup.md`.
- **Client gives Capillary's apps team:** iOS bundle ID (`{{bundle_id}}`), Android applicationId (`{{application_id}}`), app signature (SHA256) from the Android signing report.
- **Capillary gives the client:** Account Id, Base URL (end point), SSL public key; Org Id (visitor flow only); Gamification Key, Region and Base URL (gamification only).
- **CRM:** `customerId` must match the Account Linking Identifier (see `_shared/prerequisites.md`).
- **Loyalty View only:** a Capillary B2B short-lived token, set before the Loyalty View is mounted (how to obtain it isn't documented; see `_shared/prerequisites.md`).
- **Example app:** `https://pub.dev/packages/capillary_hydra/example`.

## Steps

### 1. Add the Hydra parameters to Firebase Remote Config
Add these parameters **with these exact names**:

| Remote Config key | Value | When |
|---|---|---|
| `hydra_account_id` | `{{account_id}}` | Always |
| `hydra_base_url` | `{{base_url}}` | Always |
| `hydra_ssl_public_key` | `{{ssl_public_key}}` | Always |
| `hydra_remote_log_level` | `0`–`5` (0=off, 1=error, 2=warn, 3=info, 4=debug, 5=verbose) | Always |
| `hydra_org_id` | `{{org_id}}` | Visitor flow only |
| `hydra_gamification_key` | `{{gamification_key}}` | Gamification only |
| `hydra_gamification_region` | `{{gamification_region}}` | Gamification only |
| `hydra_gamification_base_url` | `{{gamification_base_url}}` | Gamification only |

Default keys are read automatically on Android when the Application class is exactly `HydraApplication` (step 7), and on iOS unless you initialise manually. Several accounts: Modules → Multi-account.

> ⚠️ Gap: the Remote Config value type (String or Number) for each parameter, e.g. `hydra_remote_log_level`, isn't documented. Ask a Capillary engineer.

### 2. Add the packages to `pubspec.yaml`
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
  "enable_in_app_messaging_in_flutter": false
}
```

| Key | Type | Default | Platform | Meaning |
|---|---|---|---|---|
| `console_log_level` | number | `4` | Android & iOS | Console log level 0–5 (same scale as `hydra_remote_log_level`) |
| `enable_in_app_messaging` | boolean | `false` | Android & iOS | In-app messaging (needs placeholder image) |
| `enable_in_app_messaging_in_flutter` | boolean | `false` | Android only | **Currently non-functional. Don't enable in production.** |
| `enable_inbox_api` | boolean | `false` | Android & iOS | Inbox API |
| `enable_inbox_ui` | boolean | `false` | Android & iOS | Built-in notification center |
| `use_default_inbox_ui_config` | boolean | `true` | iOS only | SDK's default notification center layout |
| `max_notification_count` | number | `200` | Android & iOS | Max notifications kept |
| `hydra_notification_color` | string | – | Android only | Notification tint colour |

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

### 7. Android: set the Application class
Flutter has no custom Application class by default, but Hydra needs one to initialise.

**Option A: no Application class of your own.** Point the manifest at Hydra's class:

```xml file=android/app/src/main/AndroidManifest.xml
<application
    android:name="com.capillary.plugins.hydra.HydraApplication"
    ...>
```

**Option B: you already have an Application class.** Make it extend `HydraApplication`, point `android:name` at its fully qualified name (package + class), and call `HydraInitializer.initializeUsingFirebaseRemoteConfig(this)` **immediately after `super.onCreate()`**. A subclass doesn't auto-initialise; only exactly `HydraApplication` does.

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

For custom (prefixed) keys, see Modules → Multi-account.

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

With the default Remote Config keys, no `AppDelegate.swift` init code is needed; the plugin initialises the SDK automatically. For custom keys, see Modules → Multi-account.

### 11. Register the app with Firebase and add the config files
The guide lists these under Push Notification.
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

### 12. Register a native event handler and wait for initialisation
Before using any `capillary_hydra` API, make sure the SDK initialised successfully. Write a class that extends or implements `HydraNativeEventHandler` (override only what you need; all methods have empty defaults) and register it:

```dart
HydraNativeEvents.addEventHandler(handler);
```

Initialisation is automatic; the result arrives in:

```dart
void onHydraSdkInitializationResult({required bool success, String? error})
```

### 13. Identify, track and reset the user
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

### 14. (Optional) Update the user, geo config and push preferences
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
Do step 11 first.

**1. iOS capabilities.** On `developer.apple.com`, add the **Push Notification** capability to the app identifier. In Xcode → app target → **Signing & Capabilities**, add **Push Notification** and **Background Modes** (enable **Background fetch** and **Remote notifications**).

**2. iOS Notification Service Extension (rich notifications are mandatory).**
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

**3. Android notification colour.** Set `hydra_notification_color` in `hydra-config.json` (step 3).

**4. Small icon.** Create `capillary/icons/` if needed and add `hydra_notification_small_icon` (png, jpg or jpeg; png recommended). It's the notification-drawer icon. Declare the folder in assets (step 4).

**5. Permission and token (Dart).** Call `requestPermission` before you can receive push. It returns whether permission was granted and can throw.

```dart
bool granted = await HydraPushNotification.requestPermission();
```

```dart
String fcmToken = await HydraPushNotification.getFCMToken();
```

`getFCMToken` **throws if no FCM token is available**. Alternatively, use the `onTokenAvailable` callback.

**6. Callbacks:** `onHydraNotification*` and `onNonHydraNotification*` on `HydraNativeEventHandler` (API Reference).

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

In-app clicks arrive in `onHydraNotificationClicked`. Keep `enable_in_app_messaging_in_flutter` `false` (non-functional).

### Inbox
**Inbox API.** The SDK stores received notifications in a local database, capped by `max_notification_count`.
1. Set `enable_inbox_api` to `true`.
2. **iOS:** the Notification Service Extension must be set up (Modules → Push, item 2).

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
1. Add `hydra_org_id` to Remote Config (step 1); with custom keys, use `keyForOrgId` (Multi-account).
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

`identify` / `track` / `reset` (step 13) are part of this flow.

> ⚠️ Gap: the difference between `legacyRegistered` and `merged`, when `onLegacyFlowReady` fires instead of `onVisitorSessionReady`, and what the app should do in each state aren't documented. Ask a Capillary engineer.

### Gamification
Floating Button, Popup and Bottom Sheet campaigns, plus Banner, Embed and Loyalty widgets. Part of `capillary_hydra`; no extra package.

> ⚠️ Gap: the Integration doc (pp.53, 58) gives the minimum as an unreleased "1.1.0"; the Flutter guide (p.2) pins `^1.1.1-beta.6`. Whether a stable release with gamification exists is undocumented. Ask a Capillary engineer.

**1. Configure.** Add to Remote Config (step 1); `capillary_hydra` picks them up automatically, no Dart code needed.
- `hydra_gamification_key`: **mandatory**
- `hydra_gamification_region`: **mandatory**
- `hydra_gamification_base_url`

**HydraGamification stays disabled if either mandatory value is missing.**

> ⚠️ Correction: ✅ Use `hydra_gamification_base_url` as the Remote Config key. ❌ Don't use `hydra_gamification_url` (Integration doc Flutter chapter, pp.53–54); the Flutter guide (p.1, pp.7–8, p.22) uses `hydra_gamification_base_url`. If the SDK says the base URL isn't recognised, check this key name first. *Pending SME confirmation.*

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
1. Put the most-default account in the standard keys (step 1).
2. For each other account, add prefixed keys, e.g. India: `ind_hydra_account_id`, `ind_hydra_base_url`, `ind_hydra_ssl_public_key`, `ind_hydra_remote_log_level`, and if applicable `ind_hydra_org_id`, `ind_hydra_gamification_key`, `ind_hydra_gamification_region`, `ind_hydra_gamification_base_url`.
3. Tell the SDK the key names natively at launch (Android / iOS below) or from Dart to switch at runtime.

**Android** (Application class extends `HydraApplication`, registered in the manifest; call right after `super.onCreate()`):

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

**iOS** (in `AppDelegate.swift`, **after `GeneratedPluginRegistrant.register(with:)` and before `super.application(...)`**; the first four keys are required, org and gamification keys optional):

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

**Dart** (switch at runtime; returns whether the update was requested):

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

```dart
bool result = await HydraCore.setFirebaseRemoteConfigKeys(hydraFirebaseRemoteConfigKeys:
    hydraFirebaseRemoteConfigKeys);
```

> ⚠️ Correction: ✅ Use a single `HydraFirebaseRemoteConfigKeys` object for `setFirebaseRemoteConfigKeys` (the parameter type, p.13), e.g. `hydraFirebaseRemoteConfigKeys['ind_account']!`. ❌ Don't use the whole map (the p.22 sample builds a map with the same variable name used in the p.13 call). *Pending SME confirmation.*

> ⚠️ Gap: not documented: the Android `HydraFirebaseRemoteConfigKeys` call without the org / gamification keys, and when to call `setFirebaseRemoteConfigKeys` (e.g. relative to `identify`, or whether to `reset` first). Ask a Capillary engineer.

## Verification
- **Init:** `onHydraSdkInitializationResult` reports `success: true` (or `false` with `error`).
- **Push:** `requestPermission()` returns `true`; a token arrives (`onTokenAvailable` / `getFCMToken()`); `onHydraNotificationReceived` fires on a Hydra push.
- **Core calls** return `true` when the request was made (not proof Capillary processed it).
- **Inbox:** received pushes appear in `getInboxMessages()`. **Visitor:** `isVisitorFlowEnabled()`, `getCurrentUserState()`, `getVisitorDetails()`.
- **Gamification:** campaigns appear on reported screens; widgets render where placed.
- **Logs:** `console_log_level` `4` or `5`.

**Gamification checklist.** Required: `capillary_hydra` `^{{sdk_version}}`; `hydra_gamification_region` and `hydra_gamification_key` in Remote Config; screen names reported; `Hydra.setCapToken(...)` (Loyalty View only). Optional: Banner, Embedded, Loyalty View.

> ⚠️ Gap: no expected log lines, dashboard checks or test-push procedure are documented, nor whether a handler registered after initialisation finishes still receives `onHydraSdkInitializationResult`. Ask a Capillary engineer.

## Known Issues
| Issue | Fix |
|---|---|
| Custom Android Application class doesn't initialise Hydra (only exactly `HydraApplication` auto-initialises) | Extend `HydraApplication`, register its FQN, call the initialiser right after `super.onCreate()` (step 7) |
| Android theme not AppCompat | Use e.g. `@style/Theme.AppCompat.DayNight.NoActionBar` (step 8) |
| iOS manual init misplaced | After `GeneratedPluginRegistrant.register(with:)`, before `super.application(...)` |
| iOS rich notifications / Inbox API not working | Notification Service Extension + same App Group `group.<runner_target_bundle_id>.hydra` on both targets |
| `getFCMToken()` throws (no token yet) | Catch it, or use `onTokenAvailable` |
| Inbox UI doesn't refresh (no "inbox updated" event) | Refresh on `onHydraNotificationReceived` / `onNotificationCenterDismissed`, or poll |
| Gamification campaigns never appear | Add `hydra_gamification_key` and `hydra_gamification_region`; report screens |
| Campaigns don't re-evaluate on a persistent screen | `RouteObserver` + `RouteAware` + lifecycle observer |
| Loyalty View blank or collapsed | Fixed-height parent; `setCapToken` before mounting |
| User not linked in CRM | `customerId` must match the Account Linking Identifier |
| `enable_in_app_messaging_in_flutter` | Non-functional; keep `false` |

## API Reference
**Remote Config keys:** `hydra_account_id`, `hydra_base_url`, `hydra_ssl_public_key`, `hydra_remote_log_level`, `hydra_org_id`, `hydra_gamification_key`, `hydra_gamification_region`, `hydra_gamification_base_url`; multi-account uses a prefix (e.g. `ind_hydra_account_id`).

**`hydra-config.json` keys:** see step 3. **Icons in `capillary/icons/`:** `hydra_notification_small_icon`, `hydra_in_app_placeholder`, `hydra_inbox_ui_placeholder` (png, jpg or jpeg).

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
| `HydraCore.setFirebaseRemoteConfigKeys({required HydraFirebaseRemoteConfigKeys hydraFirebaseRemoteConfigKeys})` | `Future<bool>` | Multi-account |
| `HydraCore.setHydraAccountConfig({required HydraAccountConfig hydraAccountConfig})` | `Future<bool>` | Direct values; see `flutter/direct.md` |
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
| `HydraFirebaseRemoteConfigKeys` | `keyForAccountId`, `keyForBaseUrl`, `keyForSsl`, `keyForRemoteLogLevel` (required); `keyForOrgId`, `keyForGamificationKey`, `keyForGamificationRegion`, `keyForGamificationBaseUrl` (optional) |
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
| Android `com.capillary.plugins.hydra.HydraApplication` | Set in manifest, or extend |
| Android `HydraInitializer.initializeUsingFirebaseRemoteConfig(this[, keys])` (`com.capillary.plugins.hydra.nativeapis`) | From a `HydraApplication` subclass |
| Android `HydraFirebaseRemoteConfigKeys(...)` (`com.capillary.plugins.hydra.nativeapis`) | Eight positional strings: account id, base URL, SSL key, remote log level, org id, gamification key, region, base URL |
| iOS `HydraFirebaseRemoteConfigKeys(keyForAccountId:keyForBaseUrl:keyForSsl:keyForRemoteLogLevel:keyForOrgId:keyForGamificationKey:keyForGamificationRegion:keyForGamificationBaseUrl:)` (`import capillary_hydra_ios`) | First four required |
| iOS `HydraNativeAPI.shared.initApplicationWithFirebaseRemoteConfig(_:didFinishLaunchingWithOptions:firebaseRemoteConfigKeys:)` | Manual init with custom keys |
| iOS `HydraNativeAPI.shared.application(_:didReceiveRemoteNotification:fetchCompletionHandler:)` | In-App setup |
| iOS `HydraRemoteNotificationService` (`import HydraPushNotificationServiceExtension`) | In the extension: `didReceive(_:withContentHandler:)`, `serviceExtensionTimeWillExpire()` |
