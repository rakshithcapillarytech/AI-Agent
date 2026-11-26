---
updatedAt: 2026-11-12T06:11:18.000Z
agentTools:
  projectIndex: https://docs.capillarytech.com/llms.txt
---

# Install Flutter SDK

# Installing the Flutter SDK

1. Add the 2 packages to your app. This adds the latest released version of each to your `pubspec.yaml`:

   ```bash
   flutter pub add capillary_hydra capillary_hydra_platform_interface
   ```

   Keep both packages on the same version. To upgrade later, run:

   ```bash
   flutter pub upgrade capillary_hydra capillary_hydra_platform_interface
   ```

   Release notes are in the changelog on each package's pub.dev page: [`capillary_hydra`](https://pub.dev/packages/capillary_hydra/changelog) and [`capillary_hydra_platform_interface`](https://pub.dev/packages/capillary_hydra_platform_interface/changelog).

2. Add the config file as an asset:
   * Create a folder named `capillary` at the root of your Flutter project.

   * Create a file named `hydra-config.json` inside `capillary/` with these contents:

     ```json
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

   * Set the values as needed — see [hydra-config.json](https://docs.capillarytech.com/docs/flutter-sdk-install#hydra-configjson).

   * In your `pubspec.yaml`, declare the folder (and its `icons` subfolder, once you add icon assets per later sections) as assets:

     ```yaml
     flutter:
       assets:
         - capillary/
         - capillary/icons/
     ```

3. Run:

   ```bash
   flutter pub get
   ```

4. Call `HydraInitializer.initialize()` in `main()`, before `runApp`:

   ```dart
   import 'package:capillary_hydra/hydra.dart';
   import 'package:flutter/material.dart';

   void main() {
     WidgetsFlutterBinding.ensureInitialized();
     HydraInitializer.initialize();
     runApp(const MyApp());
   }
   ```

# hydra-config.json

| Key                                  | Type    | Default | Platform         | Description                                                                                                                                                                |
| ------------------------------------ | ------- | ------- | ---------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `console_log_level`                  | number  | 4       | Android & iOS    | Console log level (0–5). 0=off, 1=error, 2=warn, 3=info, 4=debug, 5=verbose.                                                                                               |
| `enable_in_app_messaging`            | boolean | false   | Android & iOS    | Set to `true` to enable in-app messaging. Requires the in-app placeholder asset — see [InApp Messaging](https://docs.capillarytech.com/docs/flutter-sdk-in-app-messaging). |
| `enable_in_app_messaging_in_flutter` | boolean | false   | **Android only** | See [InApp Messaging](https://docs.capillarytech.com/docs/flutter-sdk-in-app-messaging) — **currently non-functional, do not enable in production**.                       |
| `enable_inbox_api`                   | boolean | false   | Android & iOS    | Set to `true` to enable the Inbox API — see [Inbox API](https://docs.capillarytech.com/docs/configuring-notification-center#configuring-the-inbox-api).                    |
| `enable_inbox_ui`                    | boolean | false   | Android & iOS    | Set to `true` to use the built-in notification center — see [Inbox UI](https://docs.capillarytech.com/docs/configuring-notification-center#configuring-the-inbox-ui).      |
| `use_default_inbox_ui_config`        | boolean | true    | **iOS only**     | Use the SDK default notification center layout.                                                                                                                            |
| `max_notification_count`             | number  | 200     | Android & iOS    | Maximum number of notifications kept in the inbox / notification center.                                                                                                   |
| `hydra_notification_color`           | string  | –       | **Android only** | Notification tint color (e.g. `"#FF03DAC5"`) — see [Push Notification](https://docs.capillarytech.com/docs/flutter-sdk-push-notifications).                                |
| `enable_ssl_pinning`                 | boolean | true    | Android & iOS    | When `true`, the SDK pins the Hydra backend's SSL certificate against the SSL public key from the apps team. Set it to `false` to turn pinning off.                        |

You can also set a remote log level (0–5, same scale) via `hydra_remote_log_level` in Firebase Remote Config, as described in [Getting Started](https://docs.capillarytech.com/docs/flutter-sdk-getting-started#getting-started).

# Setting up iOS

If Swift Package Manager is enabled in your project, skip steps 1–3 below.

1. In `ios/Podfile`, add this line at the top:

   ```ruby
   require_relative './.symlinks/plugins/capillary_hydra_ios/script/HydraPods.rb'
   ```

2. In your `Runner` target, add `hydra_pods`:

   ```ruby
   target 'Runner' do
     use_frameworks!

     hydra_pods
     flutter_install_all_ios_pods File.dirname(File.realpath(__FILE__))
     target 'RunnerTests' do
       inherit! :search_paths
     end
   end
   ```

3. In your `ios` folder, run:

   ```bash
   pod install
   ```

4. Add `GoogleService-Info.plist` to your iOS project using Xcode.

5. Both the app-delegate lifecycle and the UIScene lifecycle (`FlutterSceneDelegate` with `FlutterImplicitEngineDelegate`) are supported. You don't need any Hydra-specific code in `AppDelegate.swift` for either one: the plugin starts the Hydra SDK itself once it's registered, reading the account values from Firebase Remote Config using the default key names (see [Getting Started](https://docs.capillarytech.com/docs/flutter-sdk-getting-started#getting-started)). To use different key names, or to pass the values directly without Firebase Remote Config, see [Other initializers](https://docs.capillarytech.com/docs/flutter-sdk-advanced-setup#other-initializers).

# Setting up Android

The Hydra Android SDK is resolved from Maven Central, so no extra repository or credentials are needed.

1. Add `google-services.json` to the `android/app` folder.

2. Declare the Google Services plugin in your root `plugins` block:

   `android/settings.gradle.kts` (Kotlin):

   ```kotlin
   id("com.google.gms.google-services") version "4.4.2" apply false
   ```

   `android/settings.gradle` (Groovy):

   ```groovy
   id 'com.google.gms.google-services' version '4.4.2' apply false
   ```

   Then apply it in your app's `plugins` block:

   `android/app/build.gradle.kts` (Kotlin):

   ```kotlin
   id("com.google.gms.google-services")
   ```

   `android/app/build.gradle` (Groovy):

   ```groovy
   id 'com.google.gms.google-services'
   ```

3. **Set the Application class in `AndroidManifest.xml`.** Flutter doesn't use a custom Application class by default, but the Hydra SDK needs to run initialization in one. If you don't already have your own Application class, point directly at the one we provide:

   ```xml
   <application
       android:name="com.capillary.plugins.hydra.HydraApplication"
       ...>
   ```

   `HydraApplication` reads the account values from Firebase Remote Config using the default key names (see [Getting Started](https://docs.capillarytech.com/docs/flutter-sdk-getting-started#getting-started)).

   **If you already have your own Application class**, make it extend `HydraApplication` instead, and point `android:name` at your class's fully-qualified name (package + class name). The automatic initialization only runs when the Application class is exactly `HydraApplication`, so a subclass must call an initializer itself, immediately after `super.onCreate()`:

   ```kotlin
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

   To use different key names, or to pass the values directly without Firebase Remote Config, see [Other initializers](https://docs.capillarytech.com/docs/flutter-sdk-advanced-setup#other-initializers).

4. **Set an AppCompat theme.** The Hydra plugin requires your application theme to derive from AppCompat:

   ```xml
   <application
       ...
       android:theme="@style/Theme.AppCompat.DayNight.NoActionBar">
   ```

# Initialising the Flutter SDK

Before using any APIs from `capillary_hydra`, make sure the Hydra SDK has initialized successfully. Implement a [HydraNativeEventHandler](https://docs.capillarytech.com/docs/flutter-sdk-api-reference#hydranativeeventhandler-class) and register it:

```dart
HydraNativeEvents.addEventHandler(handler);
```

You'll receive the initialization result via:

```dart
void onHydraSdkInitializationResult({required bool success, String? error})
```