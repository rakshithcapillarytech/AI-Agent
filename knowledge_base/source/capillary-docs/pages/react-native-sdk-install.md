---
updatedAt: 2026-11-12T06:08:47.000Z
agentTools:
  projectIndex: https://docs.capillarytech.com/llms.txt
---

# Install React Native SDK

# Setup for React Native

## 1. Add the package dependency

Add the package dependency in your `package.json` file:

* For npm:
  ```shell
  npm install @capillarytech/react-native-hydra-lib
  ```
* For Yarn:
  ```shell
  yarn add @capillarytech/react-native-hydra-lib
  ```

> 📘 Migrating from `@capillary/react-native-hydra-lib`
>
> The package was renamed. Uninstall the old package, install `@capillarytech/react-native-hydra-lib`, and update your imports and the `HydraPods.rb` path in your Podfile. For the Podfile change, see [Installing iOS SDK](#installing-ios-sdk).
>
> Also remove the Hydra-specific `@capillary` registry and token entries from `.npmrc` and `.yarnrc.yml`, and the `apply from: ".../hydra_github_setup.gradle"` line from `android/app/build.gradle`. You no longer need them.

## 2. Create the hydra-config.json file

Create a `hydra-config.json` file, set appropriate values, and add it to the `PROJECT_ROOT/capillary` folder. If you don't have a folder named `capillary`, create one in your project root folder.

# The hydra-config.json file

You configure the Hydra SDK with a single JSON file at `PROJECT_ROOT/capillary/hydra-config.json`. Both Android and iOS read this file. On iOS, the SDK might convert it internally for native use. The following table lists the supported keys.

| Key                                      | Type    | Default        | Description                                                                                                                                                                                                                                                                                                                                                                                                                                            |
| ---------------------------------------- | ------- | -------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| `console_log_level`                      | number  | 4              | Console log level (0 to 5) for Xcode and LogCat. See [HydraLogLevel](https://docs.capillarytech.com/docs/react-native-sdk-api-reference#hydraloglevel).                                                                                                                                                                                                                                                                                                |
| `enable_in_app_messaging`                | boolean | false          | Set to `true` to turn on in-app messaging. Requires the in-app placeholder asset. See [Configure In-App Messaging](https://docs.capillarytech.com/docs/react-native-sdk-in-app-messaging).                                                                                                                                                                                                                                                             |
| `enable_inbox_api`                       | boolean | false          | Set to `true` to turn on the Inbox API. See [Configure Notification Center](https://docs.capillarytech.com/docs/react-native-sdk-notification-center).                                                                                                                                                                                                                                                                                                 |
| `enable_inbox_ui`                        | boolean | false          | Set to `true` to use the built-in notification center. Requires the Inbox API and the inbox UI placeholder. See [Configure Notification Center](https://docs.capillarytech.com/docs/react-native-sdk-notification-center).                                                                                                                                                                                                                             |
| `use_default_inbox_ui_config`            | boolean | true           | **iOS only.** Use the SDK default notification center layout. Set to `false` to supply a custom `INBOX_UI_CONFIG`.                                                                                                                                                                                                                                                                                                                                     |
| `max_notification_count`                 | number  | 200            | Maximum number of notifications kept in the inbox and the notification center.                                                                                                                                                                                                                                                                                                                                                                         |
| `enable_hydra_sdk_firebase_registration` | boolean | true           | When `true`, the Hydra SDK handles FCM token registration. **Android:** if you set it to `false`, pass a token to Hydra yourself after initialization with [HydraPushNotification.passFCMToken(token)](https://docs.capillarytech.com/docs/react-native-sdk-api-reference#pass-fcm-token-android-only). This is the real FCM token if your app owns the `FirebaseMessagingService`, or a dummy one without Firebase. Gamification needs it either way. |
| `enable_push_notification`               | boolean | true           | Set to `false` to turn off push notifications entirely. When `false`, the SDK skips Firebase registration and the `hydra_notification_small_icon` asset is not required. Android also swaps in a manifest variant without the Firebase notification icon meta-data.                                                                                                                                                                                    |
| `enable_ssl_pinning`                     | boolean | true           | When `true`, the SDK pins the Hydra backend's SSL certificate against the SSL public key from the apps team. Set it to `false` to turn pinning off.                                                                                                                                                                                                                                                                                                    |
| `hydra_notification_color`               | string  | Not applicable | **Android:** Notification tint color, for example `"#FF03DAC5"`. The build generates the `hydra_notification_color` color resource from this value, so you don't need to add it to `colors.xml`. If your app already defines `hydra_notification_color` in `android/app/src/main/res/values`, that definition is used instead. See [Configure Push Notifications](https://docs.capillarytech.com/docs/react-native-sdk-push-notifications).            |

**Example:**

```json
{
  "console_log_level": 4,
  "enable_in_app_messaging": true,
  "enable_inbox_api": true,
  "enable_inbox_ui": true,
  "use_default_inbox_ui_config": true,
  "max_notification_count": 200,
  "enable_hydra_sdk_firebase_registration": true,
  "enable_push_notification": true,
  "enable_ssl_pinning": true,
  "hydra_notification_color": "#FF03DAC5"
}
```

# Platform Specific Setup

Once you have set up the React Native SDK, you can install the platform-specific SDKs (Android and iOS).

## Installing iOS SDK

To install React Native for iOS, follow these steps:

1. In **ios/Podfile**, make the following changes:

   1. Add the following lines just below the `require` block for React Native:

      ```ruby
      require Pod::Executable.execute_command('node', ['-p',
        'require.resolve(
          "@capillarytech/react-native-hydra-lib/scripts/HydraPods.rb",
          {paths: [process.argv[1]]},
        )', __dir__]).strip
      ```
   2. Add the following line just below `config = use_native_modules!`, in your main target:

      ```ruby
      hydra_pods
      ```
   3. (Optional) Use Swift Package Manager. By default, `react-native-hydra-lib` resolves the Hydra native SDKs through CocoaPods. To use Swift Package Manager instead, add the following lines above your `target` block. This option requires dynamic frameworks.

      ```ruby
      $RNHydraUseSPM = true
      use_frameworks! :linkage => :dynamic
      ```

      With Swift Package Manager, FirebaseAnalytics links directly onto your app target and needs the `-ObjC` linker flag. Call `hydra_post_install` from the `post_install` block in your Podfile to add it. The call does nothing when Swift Package Manager isn't turned on.

      ```ruby
      post_install do |installer|
        hydra_post_install(installer)
        # ... your existing post_install steps (e.g. react_native_post_install)
      end
      ```

      CocoaPods still runs `pod install` either way. This option only changes where the Hydra SDK binaries come from. If you don't set `$RNHydraUseSPM`, everything resolves through CocoaPods as before.
2. Go to the terminal, navigate to the **ios** folder of your project, and run `pod install`.
3. Add `GoogleServices-Info.plist` to your iOS project using Xcode.
4. In your `AppDelegate`, initialise the Hydra SDK using the `Hydra` initialiser. Add the import at the top of the file. Then, in `application:didFinishLaunchingWithOptions:`, replace the `return` statement.

   **Objective-C** (`AppDelegate.mm`). Add the following import at the top of the file. The module name differs depending on whether the Hydra SDKs resolve through Swift Package Manager or CocoaPods, so the import checks for both:

   ```objectivec
   #if __has_include(<react-native-hydra-lib/Hydra.h>)
   #import <react-native-hydra-lib/Hydra.h>
   #else
   #import <react_native_hydra_lib/Hydra.h>
   #endif
   ```

   Then replace the `return` statement:

   ```objectivec
   BOOL result = [super application:application didFinishLaunchingWithOptions:launchOptions];

   [[Hydra sharedInstance] initialize:application
         didFinishLaunchingWithOptions:launchOptions
                              withKeys:NULL
                 withHydraRemoteConfig:NULL];

   return result;
   ```

   **Swift.** Add `import react_native_hydra_lib` at the top of the file, then replace the `return` statement:

   ```swift
   let result = super.application(application, didFinishLaunchingWithOptions: launchOptions)

   Hydra.sharedInstance().initialize(application, didFinishLaunchingWithOptions: launchOptions ?? [:], with: nil, withHydraRemoteConfig: nil)

   return result
   ```

   Passing `nil` or `NULL` for both parameters reads the account values from Firebase Remote Config using the default key names. For the default key names, see [Getting Started](https://docs.capillarytech.com/docs/react-native-sdk-getting-started). To use different key names, or to pass the values directly without Firebase Remote Config, see [Other initializers](https://docs.capillarytech.com/docs/react-native-sdk-advanced-setup#other-initializers).

> 📘 Note
>
> The order of calls matters when `enable_inbox_ui` is `true`. Keep the `super application:didFinishLaunchingWithOptions:` call above the Hydra initialiser, as shown. With the inbox UI turned on, Hydra wraps the root view controller of your app in a `UINavigationController` so the notification center can be pushed onto it. Your window and its `rootViewController` must already exist when you call `initialize`.
>
> If you call the Hydra initialiser before `super`, the app crashes at launch. The same happens if the window isn't on the app delegate, for example with a scene-based lifecycle, where the window belongs to the `UIWindowScene`. If your app can't follow this order, leave `enable_inbox_ui` off. Hydra then never touches your root view controller.

> 📘 Note
>
> If you use a version of Xcode earlier than 16, you might encounter import issues in iOS Objective-C classes for this package. To fix the issue you can try either of the following:
>
> * Upgrade Xcode to the latest version (for example, 16.2).
> * Change the import statements and create a patch for this package.

## Installing Android SDK

The Hydra Android SDK (`com.capillarytech:hydra-*`) is resolved from Maven Central, so you don't need an extra repository or credentials. Make sure `mavenCentral()` is in your project's repositories. It is in the default React Native template. The package also bundles consumer ProGuard and R8 rules, so you don't need extra keep rules for release builds.

To install React Native for Android, follow these steps:

1. Add `google-services.json` to the `android/app` folder.
2. In your `MainApplication` file, initialise the Hydra SDK using `Hydra.initialize()`:

   ```kotlin
   import com.hydralib.nativeapis.Hydra

   Hydra.initialize(this)
   ```

   With no arguments, this call reads the account values from Firebase Remote Config using the default key names. For the default key names, see [Getting Started](https://docs.capillarytech.com/docs/react-native-sdk-getting-started). To use different key names, or to pass the values directly without Firebase Remote Config, see [Other initializers](https://docs.capillarytech.com/docs/react-native-sdk-advanced-setup#other-initializers).

## Initialising React Native

Before you can use APIs from the `react-native-hydra-lib` package, ensure the Hydra SDK is initialised successfully.

To check the initialisation, use one of the following:

* Register for the one-time event using the [Get callback for Hydra SDK initialisation result API](https://docs.capillarytech.com/docs/react-native-sdk-api-reference#get-callback-for-hydra-sdk-initialization-result). The callback tells you whether the initialisation succeeded or failed.
* Check on demand using the [HydraCore.isSdkInitialized()](https://docs.capillarytech.com/docs/react-native-sdk-api-reference#check-if-hydra-sdk-is-initialized-or-not-on-demand) API.