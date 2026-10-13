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
In this mode the SDK reads its account values (Account Id, Base URL, SSL public key, log level, and optionally Org Id and the gamification values) from **Firebase Remote Config**. This is the default path in the Flutter guide.

| Module | Status in this mode |
|---|---|
| Core (initialisation, `identify` / `track` / `reset`, user / geo / push-preference updates) | Documented |
| Push notifications (FCM; iOS rich notifications are mandatory) | Documented |
| In-App messaging | Documented: a config flag, a placeholder image and one iOS `AppDelegate` hook. The separate `enable_in_app_messaging_in_flutter` flag isn't explained and is marked non-functional. |
| Inbox API (`HydraInbox`) | Documented |
| Inbox UI (built-in notification center, `HydraInboxUI`) | Documented |
| Visitor (anonymous) flow | Documented |
| Gamification (automatic campaigns, Banner / Embed / Loyalty widgets, screen tracking) | Documented |
| Multi-account (several Hydra accounts in one app) | Documented, using prefixed Remote Config keys |
| Passing config values without Firebase Remote Config | Not in this file. See `flutter/direct.md`. |

The main source is the Flutter guide, written for `capillary_hydra` `{{sdk_version}}`. The gamification section also uses the Integration document's Flutter chapter, which was written against an unreleased 1.1.0. Where the two disagree, a callout says so.

## Requirements
- Packages (from pub.dev): `capillary_hydra` and `capillary_hydra_platform_interface`, both at `^{{sdk_version}}`. Package page: `https://pub.dev/packages/capillary_hydra`.
- A Firebase project where you can add Remote Config parameters, with this app registered in it (step 11).
- Android:
  - the application theme must derive from AppCompat (step 8),
  - Gradle with Kotlin DSL or Groovy (the guide shows both),
  - the Google Services Gradle plugin at the version the guide shows, `4.4.2` (step 11).
- iOS:
  - CocoaPods with `use_frameworks!`, or Swift Package Manager,
  - Xcode, to add capabilities and the Notification Service Extension,
  - access to `developer.apple.com`, to enable Push Notifications, register the extension's bundle ID and create the App Group.

> ⚠️ Gap: the guide doesn't state the minimum Flutter / Dart SDK, Android minSdk / compileSdk, AGP / Gradle / Kotlin, iOS deployment target, Xcode or CocoaPods versions. Ask a Capillary engineer before giving numbers.

## Prerequisites
See `_shared/prerequisites.md` for the common exchange, and `_shared/firebase-setup.md` for the Firebase project and Remote Config basics shared by every platform. For Flutter in this mode:
- **Client gives Capillary's apps team:**
  - the iOS bundle ID (`{{bundle_id}}`),
  - the Android applicationId (`{{application_id}}`),
  - the app signature (SHA256) from the Android app signing report.
- **Capillary gives the client:**
  - Account Id
  - Base URL (end point)
  - SSL public key
  - Org Id: only for the visitor flow
  - Gamification Key, Gamification Region and Gamification Base URL: only for gamification
- **Firebase:** a Firebase project where the client adds the Hydra Remote Config parameters (step 1).
- **CRM:** the `customerId` the app sends must match the **Account Linking Identifier** configured in Capillary CRM (see `_shared/prerequisites.md`).
- **Loyalty View only:** the client's backend must supply a Capillary B2B short-lived token after login (see `_shared/prerequisites.md`).
- **Banner / Embed / Loyalty IDs:** the Flutter sources don't say where these come from. `_shared/prerequisites.md` says they're configured in the gamification dashboard.
- **Example app:** the guide points to an example app on the package's pub.dev page: `https://pub.dev/packages/capillary_hydra/example`.
- The Flutter guide doesn't ask for access to the private native SDK repositories listed in `_shared/prerequisites.md`.

## Steps

### 1. Add the Hydra parameters to Firebase Remote Config
The SDK must get Account Id, SSL public key, Base URL and remote log level from a remote configuration tool. By default it reads them from Firebase Remote Config. In the Firebase console, add the parameters below **with these exact names**:

| Remote Config key | Value | When |
|---|---|---|
| `hydra_account_id` | `{{account_id}}` | Always |
| `hydra_base_url` | `{{base_url}}` | Always |
| `hydra_ssl_public_key` | `{{ssl_public_key}}` | Always |
| `hydra_remote_log_level` | `0`–`5` (0=off, 1=error, 2=warn, 3=info, 4=debug, 5=verbose) | Always |
| `hydra_org_id` | `{{org_id}}` | Only for the visitor flow |
| `hydra_gamification_key` | `{{gamification_key}}` | Only for gamification |
| `hydra_gamification_region` | `{{gamification_region}}` | Only for gamification |
| `hydra_gamification_base_url` | `{{gamification_base_url}}` | Gamification (see Modules → Gamification for whether it's optional) |

Which keys the SDK reads:
- on Android, the default keys are read automatically when the Application class is exactly `HydraApplication` (step 7, Option A). With your own subclass, you trigger the read yourself (step 7, Option B);
- on iOS, the default keys are read automatically unless you initialise the SDK yourself in `AppDelegate.swift`.

If you use several Hydra accounts, see Modules → Multi-account.

> ⚠️ Gap: the guide doesn't say which Remote Config value type (String or Number) each parameter should use, for example `hydra_remote_log_level`. Ask a Capillary engineer.

### 2. Add the packages to `pubspec.yaml`
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

### 3. Create `capillary/hydra-config.json`
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

The console log level is set here. The remote log level is set separately, with `hydra_remote_log_level` in Remote Config (step 1), on the same 0–5 scale.

### 4. Declare the config folder as assets
In `pubspec.yaml`, declare the `capillary/` folder as assets. Add its `icons` subfolder once you add the icon images described in Modules (Push, In-App, Inbox UI).

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
Flutter doesn't use a custom Application class by default, but the Hydra SDK needs one to run its initialisation.

**Option A: you don't have your own Application class.** Point the manifest straight at the class Hydra provides:

```xml file=android/app/src/main/AndroidManifest.xml
<application
    android:name="com.capillary.plugins.hydra.HydraApplication"
    ...>
```

**Option B: you already have your own Application class.**
1. Make it extend `HydraApplication`.
2. Point `android:name` in `AndroidManifest.xml` at your class's fully qualified name (package + class name).
3. In `onCreate()`, call `HydraInitializer.initializeUsingFirebaseRemoteConfig(this)` **immediately after `super.onCreate()`**.

Automatic default-key initialisation only happens when the Application class is exactly `HydraApplication`. A subclass must call the initialiser itself.

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

The guide shows this in Kotlin only. To read custom (prefixed) Remote Config keys instead of the defaults, see Modules → Multi-account.

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

With the default Remote Config keys, you don't need to add initialisation code to `AppDelegate.swift`: the plugin initialises the SDK automatically. To read custom keys instead, see Modules → Multi-account.

### 11. Register the app with Firebase and add the config files
The guide gives these steps under Push Notification. They come first here because the app must also be connected to the Firebase project that holds the Remote Config parameters from step 1. *(Derived: Remote Config is read from that Firebase project.)*

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

> ⚠️ Gap: the guide lists the Firebase files only under Push Notification. It doesn't say whether all of them (for example the Google Services Gradle plugin) are needed for an app that uses Remote Config but not push. Ask a Capillary engineer.

### 12. Register a native event handler and wait for initialisation
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

Initialisation happens automatically, so this callback is how you find out whether it succeeded, or why it failed (`error`). The full callback list is in the API Reference.

### 13. Identify, track and reset the user
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

### 14. (Optional) Update the user, geo config and push preferences
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
Complete step 11 (Firebase registration and config files) first.

**1. iOS: capabilities**
- On `developer.apple.com`, make sure the **Push Notification** capability is added to the app identifier.
- In Xcode, open the app target's **Signing & Capabilities** and add:
  - **Push Notification**,
  - **Background Modes**, with **Background fetch** and **Remote notifications** enabled.

**2. iOS: Notification Service Extension (rich notifications are mandatory)**
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

**3. Android: notification colour.** Set `hydra_notification_color` in `capillary/hydra-config.json` (step 3), for example `"#FF03DAC5"`.

**4. Notification small icon.** If `capillary/icons/` doesn't exist yet, create it. Add an image named `hydra_notification_small_icon` (png, jpg or jpeg; png recommended). This is the small icon shown in the notification drawer. Make sure `capillary/icons/` is declared in assets (step 4).

**5. Ask for permission and get the token (Dart).** Call `requestPermission` before you can receive push:

```dart
bool granted = await HydraPushNotification.requestPermission();
```
It returns whether permission was granted. It can also throw.

To get the FCM token on demand:

```dart
String fcmToken = await HydraPushNotification.getFCMToken();
```
**If no FCM token is available, it throws an error.** You can also get the token from the `onTokenAvailable({required String token})` callback on your `HydraNativeEventHandler`, which fires whenever a new FCM token is available.

**6. Notification callbacks** on `HydraNativeEventHandler`:
- `onHydraNotificationReceived`, `onHydraNotificationShown`, `onHydraNotificationDismissed`: fired when a Hydra notification is received, or is shown / dismissed in the system tray.
- `onHydraNotificationClicked({HydraNotificationCTA? cta, HydraNotification? notification})`: fired when a Hydra notification is clicked in the system tray, in the SDK's built-in notification center, or in an in-app message.
- `onNonHydraNotificationReceived` / `onNonHydraNotificationClicked`: the same, for push notifications that don't come from Hydra.

### In-App
1. Set `enable_in_app_messaging` to `true` in `hydra-config.json`.
2. Add an image named `hydra_in_app_placeholder` to `capillary/icons` (png, jpg or jpeg).
3. **iOS:** in `AppDelegate.swift`, add this import at the top:

   ```swift file=ios/Runner/AppDelegate.swift
   import capillary_hydra_ios
   ```

   Then add this function:

   ```swift file=ios/Runner/AppDelegate.swift
   override func application(_ application: UIApplication, didReceiveRemoteNotification userInfo: [AnyHashable: Any], fetchCompletionHandler completionHandler: @escaping (UIBackgroundFetchResult) -> Void) {
       HydraNativeAPI.shared.application(application, didReceiveRemoteNotification: userInfo, fetchCompletionHandler: completionHandler)
   }
   ```

Clicks on in-app messages arrive in `onHydraNotificationClicked`.

> ⚠️ Gap: the `hydra-config.json` table says to "see InApp Messaging" for `enable_in_app_messaging_in_flutter`, but the InApp Messaging section never mentions that key. What it does is undocumented. The table marks it as currently non-functional, so keep it `false`. Ask a Capillary engineer.

### Inbox
**Inbox API** (notifications stored on the device)
1. Set `enable_inbox_api` to `true` in `hydra-config.json`.
2. **iOS:** the Notification Service Extension must be set up (Modules → Push, item 2).

The SDK stores received notifications in a local database. `max_notification_count` (default 200) caps how many it keeps. Use `HydraInbox`:

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
The SDK supports an anonymous visitor flow. A user moves through these states: `none` → `visitor` (anonymous) → `merged` / `legacyRegistered` (identified) → `signedOut`.

1. Add the Org Id to Remote Config as `hydra_org_id` (step 1). Accounts that use custom key names pass it as `keyForOrgId` (Modules → Multi-account).
2. Check whether the visitor flow is enabled for the account:

   ```dart
   bool enabled = await Hydra.isVisitorFlowEnabled();
   ```
3. Get the current state:

   ```dart
   UserState? state = await Hydra.getCurrentUserState();
   ```
4. Get the visitor details (`visitorId`):

   ```dart
   HydraVisitorInfo? info = await Hydra.getVisitorDetails();
   ```
5. Subscribe to the visitor-flow lifecycle callbacks on your `HydraNativeEventHandler`:
   - `onConfigFetched({required bool isVisitorFlowEnabled})`
   - `onLegacyFlowReady()`
   - `onVisitorSessionReady()`
   - `onUserStateChanged({UserState? userState})`

`Hydra.identify` / `track` / `reset` (step 13) are also part of this flow.

> ⚠️ Gap: the guide doesn't explain the difference between `legacyRegistered` and `merged`, when `onLegacyFlowReady` fires rather than `onVisitorSessionReady`, or what the app should do in each state. Ask a Capillary engineer.

### Gamification
Gamification adds Floating Button, Popup and Bottom Sheet campaigns, plus Banner, Embed and Loyalty widgets placed directly as Flutter widgets. It's part of the `capillary_hydra` package; no extra package is needed.

> ⚠️ Source doc correction: the Integration document (p.53) gives the minimum version for gamification as "1.1.0 (To be released)", and its checklist (p.58) says "1.1.0 (next release) or later". The Flutter guide (p.2), which documents gamification, pins `^1.1.1-beta.6`. Use the Flutter guide's version (`{{sdk_version}}`). Whether a stable 1.1.0 with gamification has shipped isn't confirmed. *Pending SME confirmation.*

**1. Configure.** Add the gamification parameters to Remote Config (step 1). `capillary_hydra` picks them up automatically; no Dart code is needed.
- `hydra_gamification_key`: **mandatory**
- `hydra_gamification_region`: **mandatory**
- `hydra_gamification_base_url`

**HydraGamification stays disabled if either mandatory value is missing.**

> ⚠️ Source doc correction: the Integration document's Flutter chapter (pp.53–54) names the URL key `hydra_gamification_url`. The Flutter guide (p.1) and the native key class (`keyForGamificationBaseUrl`, examples `ind_hydra_gamification_base_url`, pp.7–8, p.22) use `hydra_gamification_base_url`, and so do the Integration document's other platform chapters. Use `hydra_gamification_base_url`. *Pending SME confirmation.*

> ⚠️ Source doc correction: the Integration document (p.54) says the URL is **optional** and only key and region are mandatory. The Flutter guide (p.1) lists Gamification Base Url among the values gamification needs, and its `HydraAccountConfig` table (p.21) marks `gamificationBaseUrl` "Required only for Gamification". Treat key and region as mandatory. Whether the base URL can be left out is unconfirmed. *Pending SME confirmation.*

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
1. Put the most-default account's values in the standard keys (step 1).
2. For each additional Hydra account, define new Remote Config keys with a prefix. For an India account:
   - `ind_hydra_account_id`
   - `ind_hydra_base_url`
   - `ind_hydra_ssl_public_key`
   - `ind_hydra_remote_log_level`
   - if applicable: `ind_hydra_org_id`, `ind_hydra_gamification_key`, `ind_hydra_gamification_region`, `ind_hydra_gamification_base_url`
3. Choose how the SDK picks up the custom key names:
   - natively at launch: Android or iOS, below;
   - from Dart, to switch account at runtime.

**Android: initialise at launch with custom keys.** Your Application class extends `HydraApplication` and is registered in the manifest (step 7, Option B). Call this immediately after `super.onCreate()`:

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

> ⚠️ Gap: the Android sample passes all eight key names positionally. The guide doesn't show the call without the org or gamification keys. (For iOS it says those are optional.) Ask a Capillary engineer.

**iOS: initialise at launch with custom keys.** In `AppDelegate.swift`, initialise the SDK yourself **after `GeneratedPluginRegistrant.register(with:)` and before `super.application(...)`**. `keyForAccountId`, `keyForBaseUrl`, `keyForSsl` and `keyForRemoteLogLevel` are required. The org ID and gamification keys are optional.

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

**Dart: switch to a custom account.** Pass the custom key names with `HydraCore.setFirebaseRemoteConfigKeys`. It returns whether the update was requested successfully.

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

> ⚠️ Source doc correction: in the guide's `HydraFirebaseRemoteConfigKeys` usage (p.22), `hydraFirebaseRemoteConfigKeys` is a **map** keyed by account name (`'ind_account'`). The `setFirebaseRemoteConfigKeys` usage (p.13) passes a variable with the same name to a parameter typed `HydraFirebaseRemoteConfigKeys` (p.13), which is a single object. Pass one `HydraFirebaseRemoteConfigKeys` (for example the map entry for the account you're switching to), not the whole map. *Pending SME confirmation.*

> ⚠️ Gap: the guide doesn't say when to call `setFirebaseRemoteConfigKeys` (for example before or after `identify`), or whether the current user must be reset before switching account. Ask a Capillary engineer.

## Verification
What the sources support:
- **SDK initialised:** `onHydraSdkInitializationResult` on your registered `HydraNativeEventHandler` reports `success: true`. On failure it reports `success: false` with an optional `error`.
- **Push:**
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
- **Logs:** set `console_log_level` to `4` (debug) or `5` (verbose) in `hydra-config.json` for console logs. Set `hydra_remote_log_level` in Remote Config for the remote log level.

**Gamification checklist** (from the Integration document, adjusted per the callouts above):
- Required:
  - `capillary_hydra` at `^{{sdk_version}}`
  - `hydra_gamification_region` in Remote Config
  - `hydra_gamification_key` in Remote Config
  - screen names reported
  - `Hydra.setCapToken(...)` called (Loyalty View only)
- Optional:
  - Banner View
  - Embedded View
  - Loyalty View

> ⚠️ Gap: there's no formal verification procedure. No expected log lines and no Capillary dashboard checks are documented, for example to confirm that a user or event reached Capillary, or how to send a test push or in-app message. Ask a Capillary engineer.

> ⚠️ Gap: initialisation happens automatically at app start. The guide doesn't say when the Dart handler must be registered to receive `onHydraSdkInitializationResult`, or whether a handler registered after initialisation finished still gets the result. Ask a Capillary engineer.

## Known Issues

**Android: the Hydra plugin needs an AppCompat theme**
- Symptom: not described in the source.
- Cause: the application theme doesn't derive from AppCompat.
- Fix: set an AppCompat theme, for example `@style/Theme.AppCompat.DayNight.NoActionBar` (step 8).

*From the source doc (Flutter guide p.3).*

**Android: a custom Application class doesn't initialise Hydra**
- Cause: automatic default-key initialisation only happens when the Application class is exactly `HydraApplication`.
- Fix:
  1. Make the class extend `HydraApplication`.
  2. Register its fully qualified name in the manifest.
  3. Call `HydraInitializer.initializeUsingFirebaseRemoteConfig(this)`, or the `keys` variant, immediately after `super.onCreate()`.

*From the source doc (Flutter guide p.6).*

**iOS: manual initialisation in the wrong place**
- Cause: when you initialise with custom keys, the call must come **after** `GeneratedPluginRegistrant.register(with:)` and **before** `super.application(...)` in `AppDelegate.swift`.

*From the source doc (Flutter guide p.8).*

**iOS: Swift Package Manager projects**
- With SPM enabled, skip the Podfile steps: `require_relative`, `hydra_pods` and `extension_pods`.
- The guide gives no SPM replacement for them (see the gaps in step 9 and Modules → Push).

*From the source doc (Flutter guide pp.4–5).*

**Firebase config file generation**
- Don't make the code changes the Firebase console suggests while generating `google-services.json` / `GoogleService-Info.plist`.

*From the source doc (Flutter guide p.4).*

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
  - `hydra_gamification_key` or `hydra_gamification_region` is missing (HydraGamification stays disabled);
  - the screen isn't reported.
- Fix: add both keys (step 1) and report screens (Modules → Gamification).

*From the source doc (Integration document pp.54–55).*

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

**Remote Config keys** (step 1):
- Default keys: `hydra_account_id`, `hydra_base_url`, `hydra_ssl_public_key`, `hydra_remote_log_level`, `hydra_org_id`, `hydra_gamification_key`, `hydra_gamification_region`, `hydra_gamification_base_url`
- Multi-account: the same names with a prefix, e.g. `ind_hydra_account_id`

**`capillary/hydra-config.json` keys** (step 3): `console_log_level`, `enable_in_app_messaging`, `enable_in_app_messaging_in_flutter`, `enable_inbox_api`, `enable_inbox_ui`, `use_default_inbox_ui_config`, `max_notification_count`, `hydra_notification_color`

**Asset images in `capillary/icons/`:** `hydra_notification_small_icon`, `hydra_in_app_placeholder`, `hydra_inbox_ui_placeholder` (png, jpg or jpeg)

**Dart APIs.** Import `package:capillary_hydra/hydra.dart`. Model classes come from `package:capillary_hydra_platform_interface/capillary_hydra_platform_interface.dart`.

| API | Purpose |
|---|---|
| `HydraInitializer.initialize()` | Call in `main()` before `runApp` |
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
| `HydraCore.setFirebaseRemoteConfigKeys({required HydraFirebaseRemoteConfigKeys hydraFirebaseRemoteConfigKeys})` → `Future<bool>` | Multi-account: switches to custom Remote Config key names |
| `HydraCore.setHydraAccountConfig({required HydraAccountConfig hydraAccountConfig})` → `Future<bool>` | Passes values directly instead of through Remote Config. See `flutter/direct.md`. |
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
| `HydraUserDetails` | `customerId` (required), `email`, `phoneNumber`, `firstName`, `lastName` |
| `HydraGeoConfig` | `city`, `country`, `countryCode` (required), `timezone` (optional) |
| `HydraPushPreferences` | `promPushEnabled`, `transPushEnabled` (both required `bool`) |
| `HydraLogLevel` | `off(0)`, `error(1)`, `warn(2)`, `info(3)`, `debug(4)`, `verbose(5)`; `final int value` |
| `HydraFirebaseRemoteConfigKeys` | `keyForAccountId`, `keyForBaseUrl`, `keyForSsl`, `keyForRemoteLogLevel` (required); `keyForOrgId`, `keyForGamificationKey`, `keyForGamificationRegion`, `keyForGamificationBaseUrl` (optional) |
| `UserState` | `none`, `legacyRegistered`, `visitor`, `merged`, `signedOut` |
| `HydraVisitorInfo` | `String? visitorId` |
| `HydraNotification` (all fields final and nullable) | `cuid`, `scope`, `campaignId`, `variationId`, `senderId`, `senderSource`, `custom`, `customData` (`Map<String, dynamic>?`), `priority`, `validity`, `messageId`, `gateway` (`HydraNotificationGateway?`), `body` (`HydraNotificationBody?`), `expandableDetails` (`HydraNotificationExpandedDetails?`), `isRead`, `imageIdentifier`, `accountId`, `channelId`, `payload`, `createdAt` (`DateTime?`), `isExpanded`, `isMessageEllipsized`, `isTitleEllipsized`, `showArrow` |
| `HydraNotificationBody` | `title`, `message`, `image`, `cta` (`HydraNotificationCTA?`) |
| `HydraNotificationCTA` | `type` (`HydraNotificationCTAType?`), `action`, `actionText` |
| `HydraNotificationCTAType` | `external`, `deepLink`, `rating`, `feedback`, `appRating`, `unknown` |
| `HydraNotificationExpandedDetails` | `ctas` (`List<HydraNotificationCTA>?`), `message`, `image`, `style` |
| `HydraNotificationGateway` | `fcm`, `xiaomi`, `unknown` |
| `NonHydraNotification` | `title`, `body`, `icon`, `imageUrl` (`String?`); `data` (`Map<String, dynamic>`) |

**Native APIs (this mode)**

| API | Purpose |
|---|---|
| Android `com.capillary.plugins.hydra.HydraApplication` | Application class. Set it directly in the manifest, or extend it. |
| Android `HydraInitializer.initializeUsingFirebaseRemoteConfig(this)` (`com.capillary.plugins.hydra.nativeapis`) | Initialises with the default Remote Config keys, from a `HydraApplication` subclass |
| Android `HydraInitializer.initializeUsingFirebaseRemoteConfig(this, keys)` | The same, with custom key names |
| Android `HydraFirebaseRemoteConfigKeys(...)` (`com.capillary.plugins.hydra.nativeapis`) | Custom key names: eight positional strings, in the sample's order: account id, base URL, SSL public key, remote log level, org id, gamification key, gamification region, gamification base URL. The guide doesn't give the Kotlin parameter names. |
| iOS `HydraFirebaseRemoteConfigKeys(keyForAccountId:keyForBaseUrl:keyForSsl:keyForRemoteLogLevel:keyForOrgId:keyForGamificationKey:keyForGamificationRegion:keyForGamificationBaseUrl:)` (`import capillary_hydra_ios`) | Custom key names. The first four are required. |
| iOS `HydraNativeAPI.shared.initApplicationWithFirebaseRemoteConfig(_:didFinishLaunchingWithOptions:firebaseRemoteConfigKeys:)` | Manual initialisation with custom keys |
| iOS `HydraNativeAPI.shared.application(_:didReceiveRemoteNotification:fetchCompletionHandler:)` | Forwards remote notifications (In-App setup) |
| iOS `HydraRemoteNotificationService` (`import HydraPushNotificationServiceExtension`) | Used in the Notification Service Extension: `didReceive(_:withContentHandler:)`, `serviceExtensionTimeWillExpire()` |
