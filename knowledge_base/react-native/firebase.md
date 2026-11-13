---
platform: react-native
config_mode: firebase
sdk_package: "@capillarytech/react-native-hydra-lib"
sdk_version: 1.7.0-beta.7    # minimum for gamification per the older guide (p.3); the public docs state no version
modules_covered: [core, push, inapp, inbox_api, inbox_ui, visitor, gamification, multi_account]
modules_missing: []
sources: ["SDK Agentic Integration For React Native (Confluence, space CAM, Hydra SDK team runbook, updated 2026-06-05)", "Capillary developer docs (docs.capillarytech.com): setting-up-react-native-project-for-hydra-sdk, react-native-sdk-getting-started, react-native-sdk-install, react-native-sdk-advanced-setup, react-native-sdk-setup-overview, react-native-sdk-push-notifications, react-native-sdk-notification-center, gamification-react-native, react-native-sdk-anonymous-visitor-flow, react-native-sdk-api-reference, in-app-messaging (updated 2026-11-12; gamification-react-native 2026-11-12; in-app-messaging 2026-10-20)", "Integration document _ Experience+ pp.1–6 (Gamification React Native Integration Guide, v1.0.1)"]
owner: TBD
last_verified: null
review_status: draft   # drafted from the source docs; not yet SME-verified
---
# React Native (with Firebase)
## Coverage
The SDK reads its settings (Account Id, Base URL, SSL key, remote log level, and Org Id / gamification values when used) from **Firebase Remote Config**, using the default key names or key names you pass (custom keys are how several Hydra accounts are set up). Main source: Capillary's public developer docs (2026-11-12); the 2026 runbook and the older gamification guide fill in what the docs omit.

| Module | Status |
|---|---|
| Core: install, `hydra-config.json`, Remote Config keys, iOS init (Swift, Objective-C), Android init (Kotlin), `HydraContainer`, identify / reset / track, update user | Documented |
| Push (incl. push preferences, custom actions) | Documented |
| In-App | Documented from the runbook only (Gap in Modules › In-App) |
| Inbox API and Inbox UI | Documented |
| Visitor (anonymous) flow | APIs and states documented (Gap in Modules › Visitor) |
| Gamification, Multi-account | Documented |
## Requirements
| Platform | Version |
|---|---|
| React Native | 0.77.0 or later |
| iOS | 15.0 or later |
| Android | API 21 (Android 5.0) or later |
| Node.js | 18.0.0 or later |
| targetSdk / compileSdk | 31 or later |

- `@capillarytech/react-native-hydra-lib`, installed with npm or Yarn (step 2).
- iOS: CocoaPods (Swift Package Manager optional, step 4d); a Podfile whose main target calls `use_native_modules!`; an `AppDelegate` in Swift or Objective-C (`AppDelegate.mm`). Xcode earlier than 16 can break Objective-C imports (Known Issues); Xcode 26 needs the extension fix in step 5.
- Android: `mavenCentral()` in the project's repositories (in the default React Native template); a Kotlin `MainApplication` with `onCreate`; for push, the `com.google.gms:google-services` Gradle plugin `4.4.2`.
- A Firebase project with `google-services.json` and `GoogleService-Info.plist`, and edit access to its Remote Config.
- Sample apps: branches `example_rn72_new_arch`, `example_rn72_old_arch`, `example_rn74_old_arch`, `example_rn75_old_arch`, `example_rn76_new_arch`, `example_rn77_new_arch` of `https://github.com/Capillary/react-native-hydra-lib`.

> ⚠️ Gap: the docs require React Native 0.77.0 or later yet ship sample apps for 0.72–0.76 (and the runbook describes the 0.76+ template). No SDK version or Gradle minimum is stated, and the only Xcode statement is that versions before 16 break Objective-C imports (Known Issues). Ask a Capillary engineer.
## Prerequisites
See `_shared/prerequisites.md` for the common exchange and `_shared/firebase-setup.md` for Firebase project and Remote Config basics.

- **Client gives Capillary** (to register the app with the Capillary apps team): Bundle ID `{{bundle_id}}` (iOS); Application ID `{{application_id}}` and App Signature SHA256 from the app signing report (Android).
- **Capillary gives client:** Account ID `{{account_id}}`, Base URL `{{base_url}}`, SSL Public Key `{{ssl_public_key}}` (for the Remote Config keys in step 8); for the Anonymous/Visitor Flow also Org ID `{{org_id}}`; for Gamification also Gamification Key `{{gamification_key}}`, Region `{{gamification_region}}` and Base URL `{{gamification_base_url}}`.
- **Firebase:** register the app on Firebase and download `google-services.json` (Android) and `GoogleService-Info.plist` (iOS); don't make the code changes Firebase suggests at this stage. Remote Config edit access.
- **Also needed:** the Capillary B2B short-lived token (Loyalty View); entry-point IDs `{{banner_id}}`, `{{embed_id}}`, `{{loyalty_id}}`; a `customerId` matching the CRM Account Linking Identifier (step 12).

> ⚠️ Gap: the documented region values are `IN`, `US` and `ME` (`_shared/prerequisites.md`), but whether React Native expects upper or lower case isn't stated. Ask a Capillary engineer.
## Steps
Steps or parts marked *(push)* are skipped when the app doesn't use push.

### 1. Package access
The npm package needs no registry entry or token, and the Hydra Android SDK (`com.capillarytech:hydra-*`) comes from Maven Central with no extra repository or credentials; the package bundles consumer ProGuard and R8 rules, so release builds need no extra keep rules.

**Migrating from `@capillary/react-native-hydra-lib`:** uninstall it, install `@capillarytech/react-native-hydra-lib` (step 2), and update your imports and the `HydraPods.rb` path in the Podfile (step 4). Remove the Hydra-specific `@capillary` registry and token entries from `.npmrc` and `.yarnrc.yml` and the `apply from: ".../hydra_github_setup.gradle"` line from `android/app/build.gradle`; you no longer need them.

> ⚠️ Gap: the 2026 runbook fetched the iOS SDK from the private repo `https://github.com/Capillary/hydra-sdk-ios-packages.git` with a GitHub username and Personal Access Token (a `scripts/setup_local.sh` stored `HYDRA_GITHUB_USER_NAME` / `HYDRA_GITHUB_PAT` in the shell profile and set a global git rule; the CI variant is below). The public docs resolve the iOS SDKs through CocoaPods (or Swift Package Manager from `https://github.com/Capillary/hydra-ios-sdk-spm.git`) and mention no credentials. Whether iOS still needs them isn't stated. Ask a Capillary engineer.

Only if `pod install` can't fetch `hydra-sdk-ios-packages` (runbook, keep the token in CI secrets, never in the repo or chat):

```bash file=scripts/setup_cicd.sh
#!/bin/bash

# Check if secrets are set
if [ -z "$HYDRA_GITHUB_USER_NAME" ] || [ -z "$HYDRA_GITHUB_PAT" ]; then
    echo "Error: HYDRA_GITHUB_USER_NAME or HYDRA_GITHUB_PAT not set in CI/CD secrets"
    exit 1
fi

# Configure Git URL rewrite
configure_git_url() {
    local original_url=$1
    local auth_url="https://${HYDRA_GITHUB_USER_NAME}:${HYDRA_GITHUB_PAT}@${original_url#https://}"
    local existing_configs=$(git config --global --get-regexp "url\..*\.insteadOf")
    while IFS= read -r line; do
        if [[ $line == *"$original_url"* ]]; then
            local key=$(echo "$line" | cut -d' ' -f1)
            git config --global --unset-all "$key"
        fi
    done <<< "$existing_configs"
    git config --global url."$auth_url".insteadOf "$original_url"
}

configure_git_url "https://github.com/Capillary/hydra-sdk-ios-packages.git"

echo "Git authentication configured successfully for CI/CD!"
```

### 2. Install the package
```shell
npm install @capillarytech/react-native-hydra-lib
```

```shell
yarn add @capillarytech/react-native-hydra-lib
```

> ⚠️ Correction: ✅ Use `@capillarytech/react-native-hydra-lib` from the public registry, with no registry or token entries (react-native-sdk-install: the package was renamed). ❌ Don't use `@capillary/react-native-hydra-lib` from GitHub Packages (`npm.pkg.github.com`) with `.npmrc` / `.yarnrc.yml` / `hydra_github_setup.gradle` (2026 runbook). *Pending SME confirmation.*

### 3. Add the Hydra configuration file
Create `<PROJECT_ROOT>/capillary/hydra-config.json` (create the `capillary` folder if missing); Android and iOS both read it. Runbook starting point (push and Inbox API on; in-app and Inbox UI off until enabled under Modules):

```json file=capillary/hydra-config.json
{
  "console_log_level": 4,
  "enable_in_app_messaging": false,
  "enable_in_app_messaging_in_react_native": false,
  "enable_inbox_api": true,
  "enable_inbox_ui": false,
  "use_default_inbox_ui_config": true,
  "max_notification_count": 200,
  "enable_hydra_sdk_firebase_registration": true,
  "hydra_notification_color": "<COLOR_HEX>"
}
```

| Key | Type, default | Meaning |
|---|---|---|
| `console_log_level` | number, `4` | Xcode / Logcat level, 0–5 (0 Off, 1 Error, 2 Warn, 3 Info, 4 Debug, 5 Verbose) |
| `enable_in_app_messaging` | boolean, `false` | In-app messaging; needs the in-app placeholder image |
| `enable_in_app_messaging_in_react_native` | boolean (runbook only) | `true` when your React Native code shows in-app messages; `false` lets the SDK show them |
| `enable_inbox_api` | boolean, `false` | The Inbox API |
| `enable_inbox_ui` | boolean, `false` | Built-in notification center; needs the Inbox API and the inbox UI placeholder |
| `use_default_inbox_ui_config` | boolean, `true` | **iOS only.** Default notification-center layout; `false` to supply a custom `INBOX_UI_CONFIG` |
| `max_notification_count` | number, `200` | Most notifications kept in the inbox and notification center |
| `enable_hydra_sdk_firebase_registration` | boolean, `true` | The SDK handles FCM token registration. **Android:** if `false`, call `HydraPushNotification.passFCMToken(token)` after init (the real token if your app owns the `FirebaseMessagingService`, else a dummy one); Gamification needs it either way |
| `enable_push_notification` | boolean, `true` | `false` turns push off entirely: no Firebase registration, small icon not required; Android swaps in a manifest variant without the Firebase notification icon meta-data |
| `enable_ssl_pinning` | boolean, `true` | Pins the Hydra backend's SSL certificate against the SSL public key from Capillary; `false` turns pinning off |
| `hydra_notification_color` | string | **Android** notification tint, e.g. `"#FF03DAC5"`. The build generates the `hydra_notification_color` resource (no `colors.xml` entry needed); one your app already defines in `android/app/src/main/res/values` wins |

**Notification small icon** *(push; not needed when `enable_push_notification` is `false`)*: add `hydra_notification_small_icon` to `capillary/icons/` (PNG recommended; JPG, JPEG accepted). The runbook recommends 96×96 px (xxxhdpi size of Android's 24 dp small icon). Android uses only the image's **alpha channel**, coloured with `hydra_notification_color`: draw the shape with transparency. A placeholder is fine while developing; replace it before shipping.

**Placeholder images** (shown while media loads), PNG recommended, in `capillary/icons/`: `hydra_in_app_placeholder` (in-app on), `hydra_inbox_ui_placeholder` (Inbox UI on).

### 4. iOS: update the Podfile
Skip the iOS steps if there is no iOS target.

a) Just below the React Native `require` block at the top of `ios/Podfile`:

```ruby file=ios/Podfile
require Pod::Executable.execute_command('node', ['-p',
  'require.resolve(
    "@capillarytech/react-native-hydra-lib/scripts/HydraPods.rb",
    {paths: [process.argv[1]]},
  )', __dir__]).strip
```

b) In the main app target, just below `config = use_native_modules!`:

```ruby file=ios/Podfile
hydra_pods
```

c) *(push)* A target for the Notification Service Extension (step 5 creates it); `HydraRichNotification` is the suggested name:

```ruby file=ios/Podfile
target 'HydraRichNotification' do
 extension_pods
end
```

d) *(optional)* **Swift Package Manager** for the Hydra binaries (requires dynamic frameworks). Above your `target` block:

```ruby file=ios/Podfile
$RNHydraUseSPM = true
use_frameworks! :linkage => :dynamic
```

FirebaseAnalytics then links onto your app target and needs the `-ObjC` linker flag; call `hydra_post_install` in `post_install` (a no-op when SPM is off):

```ruby file=ios/Podfile
post_install do |installer|
  hydra_post_install(installer)
  # ... your existing post_install steps (e.g. react_native_post_install)
end
```

`pod install` still runs either way; the option only changes where the SDK binaries come from. With SPM on, `extension_pods` does nothing (step 5).

> ⚠️ Correction: ✅ Use the path `@capillarytech/react-native-hydra-lib/scripts/HydraPods.rb` (react-native-sdk-install). ❌ Don't use `@capillary/react-native-hydra-lib/scripts/HydraPods.rb` (2026 runbook). *Pending SME confirmation.*

### 5. iOS: Xcode setup (done by the developer in Xcode)
Check first; do only what's missing. Look in the main app target's folder `ios/<APP_TARGET_NAME>/`, not with broad globs such as `ios/**/*.entitlements` (they match pods and other targets).

| Task | Already done if |
|---|---|
| *(push)* `GoogleService-Info.plist` added to the main target (drag into Xcode, target membership checked) | `ios/<APP_TARGET_NAME>/GoogleService-Info.plist` exists |
| *(push)* Push Notification capability on the app identifier at developer.apple.com, and **Push Notifications** under Signing & Capabilities | `<APP_TARGET_NAME>.entitlements` has `aps-environment` |
| *(push)* **Background Modes** with *Background fetch* and *Remote notifications* | `Info.plist` has `UIBackgroundModes` with `fetch` and `remote-notification` |
| *(push)* **Notification Service Extension** target (File → New → Target), language Objective-C if your AppDelegate is Objective-C, else Swift; Xcode derives its bundle ID from the main target's: register it on developer.apple.com | `ios/<EXTENSION_NAME>/` exists |
| *(push)* **App Groups** on the main app and the extension, group `group.{{bundle_id}}.hydra`, also added on developer.apple.com for both identifiers | main entitlements has `com.apple.security.application-groups` |

The extension and App Group (rich notifications) are mandatory for push on iOS; the Inbox API needs them too.

**With SPM (step 4d):** select your app project (not Pods) → **File** > **Add Package Dependencies** → `https://github.com/Capillary/hydra-ios-sdk-spm.git`, pinned to the exact version in `HYDRA_SPM_REQUIREMENT` in `node_modules/@capillarytech/react-native-hydra-lib/scripts/HydraPods.rb`. Then extension target → **General** > **Frameworks, Libraries, and Embedded Content** → add the `HydraPushNotificationServiceExtension` product.

**Xcode 26:** a new extension target is a "File System Synchronized Group" that CocoaPods' `xcodeproj` (< 1.26) can't read, so `pod install` fails. Before running it, right-click the extension's folder in the Project Navigator → **Convert to Group** (or **Convert to Classic Reference**).

**Build errors on the extension target:** extension target → Build Settings → **User Script Sandboxing** → **No**, for Debug and Release.

### 6. iOS: install pods
From the project root (again after adding the extension target):

```bash
cd ios && pod install && cd ..
```

### 7. iOS: Notification Service Extension code (push)
Replace the whole generated `NotificationService` file with the version for your AppDelegate's language.

Swift, `ios/<EXTENSION_NAME>/NotificationService.swift`:
```swift file=NotificationService.swift
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

Objective-C, `ios/<EXTENSION_NAME>/NotificationService.mm`:
```objectivec file=NotificationService.mm
#import "NotificationService.h"
#import "HydraPushNotificationServiceExtension/HydraPushNotificationServiceExtension.h"

@implementation NotificationService
HydraRemoteNotificationService* service;

- (id)init {
  self = [super init];
  service = [[HydraRemoteNotificationService alloc] init];
  return self;
}

- (void)didReceiveNotificationRequest:(UNNotificationRequest *)request withContentHandler:(void (^)(UNNotificationContent * _Nonnull))contentHandler {
  [service didReceiveNotificationRequest:request withContentHandler:contentHandler];
}

- (void)serviceExtensionTimeWillExpire {
  [service serviceExtensionTimeWillExpire];
}

@end
```
### 8. iOS: initialise the SDK in `AppDelegate`
The SDK reads its values from **Firebase Remote Config** at launch, so they can change without an app release (the SSL key expires about every 9 months). In the Firebase console add these parameters, names exactly as shown, before the first run (values from Capillary):

| Remote Config key | Value | When |
|---|---|---|
| `hydra_account_id` | Account Id | Always |
| `hydra_base_url` | Base URL | Always |
| `hydra_ssl_public_key` | SSL Public Key | Always |
| `hydra_remote_log_level` | Remote log level, 0–5 (`0` = off) | Always |
| `hydra_org_id` | Org Id | Anonymous/Visitor Flow |
| `hydra_gamification_key`, `hydra_gamification_region`, `hydra_gamification_base_url` | Gamification values | Gamification |

> ⚠️ Correction: ✅ Use `Hydra.sharedInstance().initialize(…)` (react-native-sdk-install, react-native-sdk-advanced-setup). ❌ Don't use `HydraNativeInitializer.sharedInstance().initApplication(usingFirebaseRemoteConfig:…)` (2026 runbook). *Pending SME confirmation.*

**Swift** (`AppDelegate.swift`): add `import react_native_hydra_lib` at the top, then replace the `return` statement of `application(_:didFinishLaunchingWithOptions:)`. Passing `nil` for both reads the default key names above:
```swift file=AppDelegate.swift
let result = super.application(application, didFinishLaunchingWithOptions: launchOptions)

Hydra.sharedInstance().initialize(application, didFinishLaunchingWithOptions: launchOptions ?? [:], with: nil, withHydraRemoteConfig: nil)

return result
```

**Objective-C** (`AppDelegate.mm`): add at the top (the module name differs between SPM and CocoaPods, so both are checked):
```objectivec file=AppDelegate.mm
#if __has_include(<react-native-hydra-lib/Hydra.h>)
#import <react-native-hydra-lib/Hydra.h>
#else
#import <react_native_hydra_lib/Hydra.h>
#endif
```

Replace the `return` statement:
```objectivec file=AppDelegate.mm
BOOL result = [super application:application didFinishLaunchingWithOptions:launchOptions];

[[Hydra sharedInstance] initialize:application
      didFinishLaunchingWithOptions:launchOptions
                           withKeys:NULL
              withHydraRemoteConfig:NULL];

return result;
```

**Custom key names** (different names in Remote Config, e.g. a prefixed set for a second account; Modules › Multi-account). Build the keys and pass them as the keys parameter, in the same place and still after `super`:
```swift file=AppDelegate.swift
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
```objectivec file=AppDelegate.mm
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

**Order matters with the Inbox UI.** Keep `super.application(…)` above the Hydra call. With `enable_inbox_ui` on, Hydra wraps your root view controller in a `UINavigationController`, so the window and its `rootViewController` must already exist on the app delegate. Calling Hydra before `super`, or a scene-based lifecycle (window on the `UIWindowScene`), crashes the app at launch; if you can't follow this order, leave `enable_inbox_ui` off.

> ⚠️ Gap: the docs show only an `AppDelegate` that calls `super.application(…)`. The React Native 0.76+ template (`RCTReactNativeFactory`) has no `super` call; the runbook put its own (older) initialiser just before `factory.startReactNative(...)`. Where `Hydra.sharedInstance().initialize(…)` goes in that template, and whether the Inbox UI works there, isn't stated. Ask a Capillary engineer.

### 9. Android: Gradle and Firebase file (push)
Skip if there is no Android target (or no push).

1. Put `google-services.json` (from your Firebase project; its package name must be your application ID) in `android/app/`.
2. In `android/build.gradle`, inside `dependencies`:
```gradle file=android/build.gradle
classpath 'com.google.gms:google-services:4.4.2'
```
3. In `android/app/build.gradle`, with the other plugins at the top:
```gradle file=android/app/build.gradle
apply plugin: "com.google.gms.google-services"
```

Don't add `hydra_github_setup.gradle` (step 1).
### 10. Android: initialise the SDK in `MainApplication`
Inside `onCreate()` of `MainApplication.kt`, **after** the default React Native generated code. With no arguments it reads the four (or more) Remote Config keys from step 8 under the default names.

> ⚠️ Correction: ✅ Use `Hydra.initialize(this)` (react-native-sdk-install). ❌ Don't use `HydraInitializer.initializeUsingFirebaseRemoteConfig(this)` (2026 runbook). *Pending SME confirmation.*

```kotlin file=MainApplication.kt
import com.hydralib.nativeapis.Hydra

Hydra.initialize(this)
```

Custom key names:
```kotlin file=MainApplication.kt
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

> ⚠️ Gap: no Java `MainApplication` code is documented for `Hydra.initialize`. Ask a Capillary engineer.
### 11. React Native: the `HydraContainer` component
One component registers the SDK's event listeners and removes them on unmount; mount it near the app root (inside the navigation container, above all screens). Keep only the blocks for the features you enabled.

```typescript file=HydraContainer.tsx
import React, { useEffect } from 'react';
import {
  HydraNativeEventEmitter,
  HydraNotification,
  HydraNotificationCta,
  HydraNotificationCtaType,
} from '@capillarytech/react-native-hydra-lib';
// Only if the feature is enabled:
// import { HydraInAppMessage } from '@capillarytech/react-native-hydra-lib'; // in-app, React Native UI
// import { Linking } from 'react-native';

const HydraContainer: React.FC = () => {
  useEffect(() => {
    const emitter = HydraNativeEventEmitter.getInstance();
    const subscriptions: any[] = [];

    // Always register: SDK initialization result
    subscriptions.push(
      emitter.addHydraSdkInitializationResultListener((success, errorMessage) => {
        if (success) {
          console.log('[Hydra] SDK initialized successfully');
          // TODO: call Hydra.identify() here
        } else {
          console.warn('[Hydra] SDK initialization failed:', errorMessage);
        }
      })
    );

    // ── Push notifications: include only if push is enabled ──
    /*
    subscriptions.push(emitter.addTokenAvailableListener((token) => console.log('[Hydra] FCM token available:', token)));
    subscriptions.push(emitter.addHydraNotificationReceivedListener((n: HydraNotification) => {}));
    subscriptions.push(emitter.addHydraNotificationShownListener((n: HydraNotification) => {}));
    subscriptions.push(
      emitter.addHydraNotificationClickedListener(
        (notification: HydraNotification | null, cta: HydraNotificationCta | null) => {
          if (!cta) return;
          if (cta.type === HydraNotificationCtaType.deepLink && cta.action) {
            // TODO: handle deep link navigation
          } else if (cta.type === HydraNotificationCtaType.external && cta.action) {
            Linking.openURL(cta.action);
          }
        }
      )
    );
    subscriptions.push(emitter.addHydraNotificationDismissedListener((n: HydraNotification) => {}));
    subscriptions.push(emitter.addNonHydraNotificationReceivedListener((n) => {}));
    subscriptions.push(emitter.addNonHydraNotificationClickedListener((n) => {}));
    */

    // ── In-app messaging handled in React Native: only if enable_in_app_messaging and
    //    enable_in_app_messaging_in_react_native are true ──
    /*
    subscriptions.push(
      emitter.addHydraInAppMessageListener((message: HydraInAppMessage) => {
        // TODO: display the message, then call HydraInAppMessaging.reportMessageClicked(message)
        // or HydraInAppMessaging.reportMessageDismissed(message) on user action
        return true; // return false to let the SDK display the message instead
      })
    );
    */

    // ── Inbox API: only if enabled (then re-fetch HydraInbox.getInboxMessages()) ──
    /*
    subscriptions.push(emitter.addInboxUpdatedListener(() => {}));
    */

    // ── Inbox UI: only if enabled ──
    /*
    subscriptions.push(emitter.addNotificationCenterDismissedListener(() => {}));
    */

    return () => {
      subscriptions.forEach((sub) => emitter.removeListener(sub));
    };
  }, []);

  return null;
};

export default HydraContainer;
```

Mount it in the app entry file (for example `App.tsx`):
```tsx file=App.tsx
// In your app entry file (e.g. App.tsx):
import HydraContainer from './HydraContainer'; // adjust path as needed

// Inside your root component's return:
<>
  <HydraContainer />
  {/* rest of your app */}
</>
```

When un-commenting the push block, also import `Linking` from `react-native`. If you also use Gamification, open external links with `HydraPushNotification.openExternalUrl(cta.action)` instead of `Linking.openURL(cta.action)` (Modules › Gamification).

### 12. Identify the user (sign in) and reset (sign out)
After initialisation succeeds, call `Hydra.identify`. `customerId` is required and must be of the type set as the **Account Linking Identifier** in Capillary CRM (*Organisation Settings → Omni Channel Settings → Channel Configurations → MAPP_SDK*): mobile number, email, externalId, InTouchUserId or FCMToken. With several Hydra accounts, set the account first (Modules › Multi-account). Import `Hydra` and `HydraUserDetails` from `@capillarytech/react-native-hydra-lib`.

> ⚠️ Correction: ✅ Use `Hydra.identify(userDetails, customAttributes)` to register or sign in, `Hydra.reset(customerId)` to sign out, `Hydra.track(eventName, attributes)` for events (react-native-sdk-setup-overview, react-native-sdk-api-reference). ❌ Don't use the deprecated `HydraCore.signUp`, `HydraCore.signIn`, `HydraCore.signOut`, `HydraCore.reportUserEvent` (2026 runbook). *Pending SME confirmation.*

```typescript
const userDetails = new HydraUserDetails(
  '8888888888',
  'FirstName',
  'LastName',
  'user@example.com',
  '918888888888',
);

Hydra.identify(userDetails, customAttributesObj)
  .then((res) => console.log('Hydra.identify success', res))
  .catch((err) => console.log('Hydra.identify error', err));

// Sign out:
Hydra.reset(customerId)
  .then((res) => console.log('Hydra.reset success', res))
  .catch((err) => console.log('Hydra.reset error', err));

// Custom user action (analytics and segmentation); attributes optional:
Hydra.track('product_viewed', { productId: 'abc123' });
```

Later changes: `HydraCore.updateUser(userDetails, customAttributes, subscriptions)` for profile updates; `HydraCore.updateGeoConfig(geoConfig)` for city, country and countryCode (API Reference).

### 13. Ask for push permission (push)
Once, after the SDK is initialised, at a sensible point in the user flow:

```typescript
HydraPushNotification.requestPermission()
  .then((status) => {
    console.log('Notification permission status - ', status);
  })
  .catch((err: any) => {
    console.log('HydraPushNotification.requestPermission', err);
  });
```

### 14. Check that the SDK is initialised before calling other APIs
Outside `HydraContainer`, check first and register the one-time callback if it isn't ready:

```javascript
HydraCore.isSdkInitialized()
  .then((isInitialized) => {
    if (!isInitialized) {
      // not yet initialized: register for the one-time result
      const subscription =
        HydraNativeEventEmitter.getInstance().addHydraSdkInitializationResultListener(
          (result, message) => {}
        );
    }
  })
  .catch((error) => console.error('Error checking Hydra initialization status:', error));
```

These reject before initialisation: `passFCMToken`, `setGamificationSuppressed`, `isGamificationSuppressed`, `setThemeMode`, `setHydraAccountConfig`, `setFirebaseRemoteConfigKeys`.
### G1. Gamification: package version
Gamification is part of the package from step 2.

> ⚠️ Gap: the older gamification guide asks for at least `{{sdk_version}}` of the package (npm `beta` tag); the public docs state no minimum. Ask a Capillary engineer.

### G2. Gamification: add the keys to Firebase Remote Config
```text
hydra_gamification_region
hydra_gamification_key
hydra_gamification_base_url
```

| Remote Config key | Value |
|---|---|
| `hydra_gamification_key` | `{{gamification_key}}` |
| `hydra_gamification_region` | `{{gamification_region}}` |
| `hydra_gamification_base_url` | `{{gamification_base_url}}` |

The docs say Gamification requires all three. The older guide adds that Gamification stays disabled when the key or URL is missing. `hydra_org_id` is not a gamification value: it is only for the Anonymous/Visitor Flow. With custom key names (step 8), pass these in the `keyForGamification…` arguments.

### G3. Report the current screen (required for gamification campaigns)
Report screens **after sign-in** (`Hydra.identify`). Call `Hydra.gamificationScreenAppeared(screenName)` when a gamification screen appears and `Hydra.gamificationScreenDisappeared(screenName)` with the **same** name when it goes. The SDK then shows the Floating Button, Popup and Bottom Sheet campaigns for that screen automatically.

```javascript
Hydra.gamificationScreenAppeared('HomeScreen');
// ... later, when the screen unmounts:
Hydra.gamificationScreenDisappeared('HomeScreen');
```

With React Navigation, the older Integration document reports it **after sign-in**, 500 ms after focus so the screen animation completes:

```javascript
useFocusEffect(
  useCallback(() => {
    const timer = setTimeout(() => {
      Hydra.gamificationScreenAppeared('home');
    }, 500);

    return () => {
      clearTimeout(timer);
      Hydra.gamificationScreenDisappeared('home');
    };
  }, [])
);
```

> ⚠️ Correction: ✅ Use `Hydra.gamificationScreenDisappeared(screenName)` with the name passed to `gamificationScreenAppeared` (gamification-react-native, react-native-sdk-api-reference). ❌ Don't call `Hydra.gamificationScreenDisappeared()` with no argument (older Integration document). *Pending SME confirmation.*

> ⚠️ Gap: which `screenName` values campaigns target isn't documented (`'HomeScreen'`, `'home'` are examples). Ask a Capillary engineer.

### G4. Set the Capillary token (for Loyalty View)
Before showing `GamificationLoyaltyView`:

```typescript
Hydra.setCapToken(token);
```
## Modules

### Push
On by default (`enable_push_notification` `true` or omitted): steps 3, 4c, 5, 7, 9, 11, 13 and, for the server side (how a push reaches the device, what must match at Capillary, how to test, delivery reports), `_shared/push.md`.

- **FCM token:** `addTokenAvailableListener`, or `HydraPushNotification.getFCMToken()` on demand (throws if unavailable).
- **Tapped notification:** `addHydraNotificationClickedListener` gives the notification and CTA; it also fires for taps in the built-in notification center and CTA taps on SDK-rendered in-app messages. `HydraNotificationCtaType.deepLink` → navigate in your app; `.external` → open the URL.
- **Pushes not from Capillary:** `addNonHydraNotificationReceivedListener` / `addNonHydraNotificationClickedListener`.
- **Android custom actions:** `addHandleCustomActionListener((payload) => …)` receives the payload when a CTA with a custom action is tapped (not emitted on iOS).
- **Push preferences:** `HydraCore.updatePushPreferences(customerId, new HydraPushPreferences(promPushOpted, transPushOpted))` for promotional / transactional pushes of the signed-in `customerId`.
- **Android, your app owns the `FirebaseMessagingService`:** set `enable_hydra_sdk_firebase_registration` to `false` and pass every new token after init (e.g. from `onNewToken` or `@react-native-firebase/messaging`):

```typescript
import messaging from '@react-native-firebase/messaging';

if (Platform.OS === 'android') {
  const token = await messaging().getToken();
  await HydraPushNotification.passFCMToken(token);
}
```


### In-App
Delivered through the push mechanism, so push must be integrated and on. Set `"enable_in_app_messaging": true` and add `capillary/icons/hydra_in_app_placeholder`.
- **SDK shows the message** (default): nothing else to do; CTA taps arrive in `addHydraNotificationClickedListener`.
- **Your React Native UI shows it (runbook):** also set `"enable_in_app_messaging_in_react_native": true` and un-comment the `addHydraInAppMessageListener` block in `HydraContainer`. Show the message yourself and report the outcome with `HydraInAppMessaging.reportMessageClicked(message)` or `HydraInAppMessaging.reportMessageDismissed(message)`. Return `true` from the listener if you handle it, `false` to let the SDK display it.

> ⚠️ Gap: `enable_in_app_messaging_in_react_native`, `addHydraInAppMessageListener` and `HydraInAppMessaging` come only from the runbook; the public `hydra-config.json` keys and API reference don't list them (the `HydraNativeEvent` enum does include `onHydraInAppMessage`). The public in-app page's configuration (`InAppConfig`, `HydraInAppUIHelper`) is for native Android. Ask a Capillary engineer.

### Inbox
The SDK keeps a local database of **Hydra** notifications only (never other senders' pushes).

- **Inbox API:** set `"enable_inbox_api": true` (on iOS the Notification Service Extension and App Group from step 5 are required too). Build your own list with `HydraInbox` (`getInboxMessages`, `getUnreadMessagesCount`, `markInboxMessageAsRead`, `deleteInboxMessage`, `deleteAllInboxMessages`) and refresh it from `addInboxUpdatedListener` (or `addHydraNotificationReceivedListener` when a push arrives):

```typescript
HydraInbox.getInboxMessages().then((messages) => {
  if (messages.length > 0) {
    console.log('Inbox message first - ', messages[0]);
  } else {
    console.log('No messages in inbox');
  }
});
```

- **Inbox UI** (built-in notification center): turn on the Inbox API, set `"enable_inbox_ui": true`, add `capillary/icons/hydra_inbox_ui_placeholder`, mind the init order (step 8), register `addNotificationCenterDismissedListener`, and open it from your UI (e.g. a bell icon). On iOS `use_default_inbox_ui_config` sets the layout; Android always uses the default.

```typescript
HydraInboxUI.showNotificationCenter();
// HydraInboxUI.hideNotificationCenterIfShowing() closes it
```

> ⚠️ Gap: the format of the custom iOS `INBOX_UI_CONFIG` isn't documented. Ask a Capillary engineer.

### Visitor
The anonymous visitor flow needs the Org Id in the initialiser (`orgId` or `hydra_org_id`, steps 8 and 10). A user's `UserState` goes `none` → `visitor` (anonymous) → `merged` or `legacyRegistered` (identified) → `signedOut`.

1. `Hydra.isVisitorFlowEnabled()`: is the flow on for your account.
2. `Hydra.getCurrentUserState()`: the `UserState`.
3. `Hydra.getVisitorDetails()`: the `HydraVisitorInfo` (`visitorId`).
4. Lifecycle callbacks on `HydraNativeEventEmitter.getInstance()`: `setConfigFetchedCallback((isVisitorFlowEnabled) => …)`, `setLegacyFlowReadyCallback(() => …)`, `setVisitorSessionReadyCallback(() => …)`, `setUserStateChangedCallback((userState) => …)`.

`Hydra.identify`, `Hydra.reset` and `Hydra.track` work as in step 12.

> ⚠️ Gap: how the visitor flow is turned on for an account, and when a user ends as `merged` versus `legacyRegistered`, aren't documented. Ask a Capillary engineer.

### Multi-account
For one app with several Hydra accounts (e.g. India, USA, Europe), get each account's values from Capillary (Account Id, Base URL, SSL key, plus Org Id and gamification values if used). The native initialiser (steps 8, 10) sets the **default** account; switch from React Native, **after** the SDK has initialised (the calls reject before) and **before** `Hydra.identify`.

**Option A: Firebase Remote Config.** Keep the default account in the standard keys (step 8) and publish one extra set per additional account with a prefix of your choice, e.g. for India: `ind_hydra_account_id`, `ind_hydra_base_url`, `ind_hydra_ssl_public_key`, `ind_hydra_remote_log_level`, `ind_hydra_org_id` (Visitor Flow), `ind_hydra_gamification_key`, `ind_hydra_gamification_region`, `ind_hydra_gamification_base_url` (Gamification). Switch with `HydraCore.setFirebaseRemoteConfigKeys`:

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

It reads values Firebase Remote Config has **already fetched** (it doesn't fetch), so the prefixed keys must be published; otherwise it rejects with "Failed to get values for these keys from Firebase remote config". The SDK saves the key names and uses them on later launches.

**Option B: values you fetch yourself.** `HydraCore.setHydraAccountConfig(new HydraAccountConfig(accountId, baseUrl, sslPublicKey, HydraLogLevel.off, orgId, gamificationKey, gamificationRegion, gamificationBaseUrl))`; the last four are optional.

Order: (1) wait for initialisation (step 14); (2) set the user's account and wait for the promise; (3) `Hydra.identify`. Never identify before setting the account.

```typescript
await HydraCore.setHydraAccountConfig(accountConfigForUser);
await Hydra.identify(new HydraUserDetails(customerId));
```

The SDK re-initialises with the new account at once and resolves `true`; setting the already-active account changes nothing. The chosen account **persists** on the device and is used on every later launch in place of what the native initialiser passes; the native initialiser only decides the account for a fresh install.

### Gamification
Needs the Gamification Key, Region and Base URL in Remote Config (step G2), screen reporting (step G3) and, for the Loyalty View, the Capillary token (step G4).

**Android:** if `enable_hydra_sdk_firebase_registration` is `false` (your app owns FCM, or no Firebase), call `HydraPushNotification.passFCMToken(token)` after the SDK initialises or Gamification doesn't work properly; a dummy token is fine.

**With Hydra push:** open external links with `HydraPushNotification.openExternalUrl(url)`, not `Linking.openURL(url)`; Capillary has seen external-link issues otherwise.

| Component | Prop (string) |
|---|---|
| `GamificationBannerView` | `bannerId` |
| `GamificationEmbedView` | `embedId` |
| `GamificationLoyaltyView` | `loyaltyId` (call `Hydra.setCapToken(token)` first) |

Size banner and embed views from `addGamificationViewHeightChangedListener`, not a fixed height. Height `0` means nothing to show yet (e.g. no matching entry point): collapse the container. If the entry point appears later (e.g. after `identify`), the SDK emits a new non-zero height. Use your entry-point IDs (`{{banner_id}}`, `{{embed_id}}`, `{{loyalty_id}}`) for the constants:

```tsx
import { useEffect, useState } from 'react';
import { GamificationBannerView, GamificationEmbedView, GamificationLoyaltyView, HydraNativeEventEmitter } from '@capillarytech/react-native-hydra-lib';

const BANNER_ID = 'your_banner_id';
const EMBED_ID = 'your_embed_id';
const LOYALTY_ID = 'your_loyalty_id';

const [bannerHeight, setBannerHeight] = useState(300);
const [embedHeight, setEmbedHeight] = useState(600);
const [loyaltyHeight, setLoyaltyHeight] = useState(600);

useEffect(() => {
  const subscription = HydraNativeEventEmitter.getInstance().addGamificationViewHeightChangedListener(
    (height, entryPointId) => {
      if (height < 0) return; // 0 is meaningful: collapse the view
      if (entryPointId === BANNER_ID) setBannerHeight(height);
      else if (entryPointId === EMBED_ID) setEmbedHeight(height);
      else if (entryPointId === LOYALTY_ID) setLoyaltyHeight(height);
    }
  );
  return () => HydraNativeEventEmitter.getInstance().removeListener(subscription);
}, []);

const bannerStyle = { width: '100%', height: bannerHeight };
const embedStyle = { width: '100%', height: embedHeight };
const loyaltyStyle = { width: '100%', height: loyaltyHeight };

<GamificationBannerView bannerId={BANNER_ID} style={bannerStyle} />
<GamificationEmbedView embedId={EMBED_ID} style={embedStyle} />
<GamificationLoyaltyView loyaltyId={LOYALTY_ID} style={loyaltyStyle} />
```

**Events** (on `HydraNativeEventEmitter.getInstance()`; remove the subscription on unmount):
- `addGamificationDeeplinkListener((url) => …)`: a campaign asks the app to open a deep link; route `url` in your navigation.
- `addGamificationEventTriggerListener((name, payload) => …)`: a game or campaign triggered a named event (e.g. a reward unlocked).
- `addGamificationAnalyticsEventListener((name, payload) => …)`: analytics events from the gamification UI, e.g. to forward to your own analytics tool.

> ⚠️ Gap: event and analytics-event names and payload contents aren't documented. Ask a Capillary engineer.

**Custom event and settings:**

```typescript
Hydra.track('<YOUR_EVENT>');   // attributes optional (step 12)

// Suppress campaigns (e.g. during checkout or onboarding); rejects before init, so a rejection is not `false`:
Hydra.setGamificationSuppressed(true);
Hydra.setGamificationSuppressed(false);
Hydra.isGamificationSuppressed().then((suppressed) => {
  console.log('Gamification suppressed - ', suppressed);
});

// Light or dark theme for Hydra's UI (rejects before init or for an invalid mode):
import { Hydra, ThemeMode } from '@capillarytech/react-native-hydra-lib';

Hydra.setThemeMode(ThemeMode.dark);
Hydra.getThemeMode().then((mode) => {
  console.log('Theme mode - ', mode);
});
```
## Verification
**Integration checklist** (skip what you didn't enable):
- `@capillarytech/react-native-hydra-lib` installs; no leftover `@capillary` registry entries or `hydra_github_setup.gradle` line.
- `capillary/hydra-config.json` has the right flags; *(push)* the small icon is in `capillary/icons/`.
- iOS: Podfile and AppDelegate steps (4, 8) and, for push, the extension (5, 7) are in place; Android: `MainApplication` calls `Hydra.initialize(…)` (10).
- `HydraContainer` is mounted near the root with `addHydraSdkInitializationResultListener`; `Hydra.identify` runs after initialisation succeeds.
- *(push)* `addTokenAvailableListener` and the notification listeners are registered and `requestPermission()` is called. *(in-app, React Native UI)* `addHydraInAppMessageListener` reports clicks / dismissals. *(Inbox API)* `addInboxUpdatedListener`. *(Inbox UI)* `showNotificationCenter()` wired to a control plus `addNotificationCenterDismissedListener`.
- TypeScript: `npx tsc --noEmit` shows no new errors (record the baseline first).
- Firebase Remote Config: the keys from step 8 (or your custom names) exist and are **published**.

**At runtime:** `HydraCore.isSdkInitialized()` (step 14) resolves `true`, or the initialisation listener reports success (`[Hydra] SDK initialized successfully` in the sample; on failure it gives an `errorMessage`). With push, `addTokenAvailableListener` logs the FCM token, then test a real push end to end (`_shared/push.md` › Test the push flow). Visitor: `Hydra.isVisitorFlowEnabled()` resolves `true` and `getCurrentUserState()` returns `visitor` before identify. Gamification: after identify and screen reporting (step G3) campaigns for that screen appear, banner / embed views get a non-zero height, and `isGamificationSuppressed()` resolves `false` unless suppressed.

**Before shipping:** replace any placeholder notification icon (transparent background, shape drawn with alpha only).

**Log levels:** Console (Xcode / Logcat) and Remote (saved to the Capillary backend), each 0–5: 0 Off, 1 Error, 2 Warn, 3 Info, 4 Debug, 5 Verbose (each includes those below). Console: `console_log_level` in `hydra-config.json`. Remote: `hydra_remote_log_level` in Firebase Remote Config.

> ⚠️ Correction: ✅ Use `console_log_level` in `capillary/hydra-config.json` for the console level and `hydra_remote_log_level` in Remote Config for the remote level (react-native-sdk-setup-overview). ❌ Don't use `log_levels` / `LOG_LEVELS` in `hydra-config.json` / `HydraConfig.plist` (older Integration document p.84). *Pending SME confirmation.*
## Known Issues

**APIs reject or do nothing right after launch** → called before the SDK initialised → check `HydraCore.isSdkInitialized()` and wait for `addHydraSdkInitializationResultListener` (step 14).

**iOS app crashes at launch with `enable_inbox_ui` on** → Hydra is initialised before `super.application(…)`, or the window isn't on the app delegate (scene-based lifecycle) → call Hydra after `super`; otherwise leave `enable_inbox_ui` off (step 8).

**Objective-C import errors for the package** → Xcode earlier than 16 → upgrade Xcode (e.g. 16.2), or change the imports and patch the package.

**User not matched to the CRM customer** → `customerId` isn't the CRM Account Linking Identifier → pass that identifier (step 12).

**Gamification doesn't work properly on Android** → `enable_hydra_sdk_firebase_registration` is `false` and no token was passed → `HydraPushNotification.passFCMToken(token)` after init (a dummy token is fine).

**Floating Button / Popup / Bottom Sheet campaigns don't appear** → screen not reported, reported before sign-in, or reported without the 500 ms delay → report after identify (step G3).

**Banner / embed view collapsed or empty** → the SDK reported height `0` (no matching entry point yet) → keep the container collapsed; a non-zero height follows when the entry point appears (e.g. after `identify`).

**Loyalty View empty** → Capillary token not set → `Hydra.setCapToken(...)` before showing it (step G4).

**`setHydraAccountConfig` / `setFirebaseRemoteConfigKeys` rejects** → called before initialisation, or (Firebase keys) the prefixed keys aren't published in Remote Config → wait for init (step 14) and publish the keys.

**SDK log shows `Client Credentials Generation Failed` / `source not found` (400)** → (Android) the App Signature registered at Capillary doesn't match the build's → compare the build's SHA256 with the registered one and ask Capillary to update it (`_shared/push.md`).

**Push never arrives although sign-in works** → the app's Firebase project isn't the one registered at Capillary, or the push gateway isn't set up → `_shared/push.md` › Test the push flow, › Common problems.

**`pod install` fails right after creating the Notification Service Extension (Xcode 26)** → the extension is a "File System Synchronized Group" that `xcodeproj` < 1.26 can't read → right-click the extension folder → Convert to Group, then pod install again.

**Extension has no Hydra SDK with Swift Package Manager** → `extension_pods` does nothing when `$RNHydraUseSPM = true` → add `hydra-ios-sdk-spm` and the `HydraPushNotificationServiceExtension` product to the extension in Xcode (step 5).

**Notification icon looks wrong (solid block or blank)** → Android uses only the icon's alpha channel, tinted with `hydra_notification_color` → redraw it with transparency (step 3).

**SDK stops connecting months after release (certificate pinning failure)** → the SSL public key expired (about 9 months) → get the new key from Capillary and update it (update the Remote Config value, no release needed). See `_shared/prerequisites.md`.

**Duplicate code after re-running the setup** → the change was already there → check for the Hydra lines before editing AppDelegate, MainApplication, the Podfile or Gradle files.

**SDK never initialises (the initialisation listener reports failure or never fires)** → the Remote Config keys are missing, unpublished, or named differently from what the code passes → add `hydra_account_id`, `hydra_base_url`, `hydra_ssl_public_key`, `hydra_remote_log_level` (or your custom names) and publish them (step 8).

**Gamification never appears** → a gamification key is missing in Remote Config (the SDK keeps it disabled) → set `hydra_gamification_key`, `hydra_gamification_region` and `hydra_gamification_base_url` (step G2).

## API Reference
Imports come from `@capillarytech/react-native-hydra-lib`. Methods are static and return Promises (the resolved value is shown).

### `Hydra`
| API | Resolves |
|---|---|
| `identify(userDetails: HydraUserDetails, customAttributes: Record<string, any> \| null = null)` | `boolean` |
| `reset(customerId: string)` | `boolean` |
| `track(eventName: string, attributes: Record<string, any> \| null = null)` | `boolean` |
| `getCurrentUserState()` / `getVisitorDetails()` / `isVisitorFlowEnabled()` | `UserState \| null` / `HydraVisitorInfo \| null` / `boolean` |
| `gamificationScreenAppeared(screenName: string)` / `gamificationScreenDisappeared(screenName: string)` | `void`; same name in both |
| `setCapToken(token: string)` | `void` |
| `setGamificationSuppressed(suppressed: boolean)` / `isGamificationSuppressed()` | `void` / `boolean`; reject before init |
| `setThemeMode(mode: ThemeMode)` / `getThemeMode()` | `void` / `ThemeMode`; set rejects before init or for an invalid mode |

### `HydraCore`
| API | Resolves / notes |
|---|---|
| `isSdkInitialized()` | `boolean` |
| `updateUser(userDetails: HydraUserDetails, customAttributes: Record<string, any> \| null = null, subscriptions: Object[] \| null = null)` | `boolean`; subscriptions carry channel, accountId, priority, type, sourcename |
| `updateGeoConfig(geoConfig: HydraGeoConfig)` | `boolean` |
| `updatePushPreferences(customerId: string, preferences: HydraPushPreferences)` | `boolean` |
| `setHydraAccountConfig(hydraAccountConfig: HydraAccountConfig)` | `true` once switched; after init, before `identify` |
| `setFirebaseRemoteConfigKeys(remoteConfigKeys: HydraFirebaseRemoteConfigKeys)` | `true` once switched; Firebase Remote Config apps |
| Deprecated: `signUp(userDetails, customAttributes)`, `signIn(userDetails, customAttributes)`, `signOut(customerId)`, `reportUserEvent(eventName, attributes)` | Use `Hydra.identify`, `Hydra.identify`, `Hydra.reset`, `Hydra.track` |

### `HydraPushNotification`, `HydraInbox`, `HydraInboxUI`, `HydraInAppMessaging`
| API | Resolves / notes |
|---|---|
| `HydraPushNotification.getFCMToken()` | `string`; throws if unavailable |
| `HydraPushNotification.requestPermission()` | `boolean` granted; can throw |
| `HydraPushNotification.openExternalUrl(url: string)` | `void` |
| `HydraPushNotification.passFCMToken(token: string)` | `void`; Android only (does nothing on iOS), rejects before init; any non-empty dummy string if there's no token |
| `HydraInbox.getInboxMessages()` / `getUnreadMessagesCount()` | `HydraNotification[]` (no arguments) / `number` |
| `HydraInbox.markInboxMessageAsRead(hydraNotification: HydraNotification)`, `deleteInboxMessage(hydraNotification: HydraNotification)`, `deleteAllInboxMessages()` | `boolean` |
| `HydraInboxUI.showNotificationCenter()` / `hideNotificationCenterIfShowing()` | `void` |
| `HydraInAppMessaging.reportMessageClicked(message)` / `reportMessageDismissed(message)` | runbook only |

### `HydraNativeEventEmitter`
Call everything on `HydraNativeEventEmitter.getInstance()`. Each `add…Listener` / `set…Callback` returns an `EmitterSubscription`: keep it and pass it to `removeListener(emitterSubscription)`. `removeAllListeners(eventType: HydraNativeEvent)` drops every listener of one event (e.g. `HydraNativeEvent.onInboxUpdated`).

| Listener | Callback arguments |
|---|---|
| `addHydraSdkInitializationResultListener` | `(success: boolean, errorMessage: string \| null)` |
| `addTokenAvailableListener` | `(token: string)` |
| `addHydraNotificationReceivedListener`, `addHydraNotificationShownListener`, `addHydraNotificationDismissedListener` | `(notification: HydraNotification)` |
| `addHydraNotificationClickedListener` | `(notification: HydraNotification \| null, cta: HydraNotificationCta \| null)` |
| `addNonHydraNotificationReceivedListener`, `addNonHydraNotificationClickedListener` | `(notification: NonHydraNotification)` |
| `addHandleCustomActionListener` | `(payload: string)`; Android only |
| `addNotificationCenterDismissedListener`, `addInboxUpdatedListener` | `()` |
| `addHydraInAppMessageListener` | `(message: HydraInAppMessage) => boolean`; runbook only |
| `setConfigFetchedCallback` / `setUserStateChangedCallback` | `(isVisitorFlowEnabled: boolean)` / `(userState: UserState \| null)` |
| `setLegacyFlowReadyCallback`, `setVisitorSessionReadyCallback` | `()` |
| `addGamificationViewHeightChangedListener` | `(height: number, entryPointId: string)` |
| `addGamificationDeeplinkListener` | `(url: string)` |
| `addGamificationEventTriggerListener`, `addGamificationAnalyticsEventListener` | `(name: string, payload: Record<string, any>)` |

> ⚠️ Correction: ✅ Use `HydraNativeEventEmitter.getInstance().removeListener(subscription)` and `getInstance().add…Listener(…)`, as in every usage example. ❌ Don't call `HydraNativeEventEmitter.removeListener(…)` or `.add…Listener(…)` statically (signatures in react-native-sdk-api-reference and the older Integration document p.85). *Pending SME confirmation.*

### Components and models
`GamificationBannerView` (`bannerId`), `GamificationEmbedView` (`embedId`), `GamificationLoyaltyView` (`loyaltyId`): string props plus `style`.

| Class | Constructor / fields |
|---|---|
| `HydraUserDetails` | `(customerId: string, firstName?: string \| null, lastName?: string \| null, email?: string \| null, phone?: string \| null)`; only `customerId` required |
| `HydraGeoConfig` | `(city: string, country: string, countryCode: string, timezone?: string \| null)`, e.g. `('Bangalore', 'India', 'IN', 'Asia/Kolkata')` |
| `HydraPushPreferences` | `(promPushOpted: boolean, transPushOpted: boolean)` |
| `HydraAccountConfig` | `(accountId: string, baseUrl: string, sslPublicKey: string, remoteDebugLevel: HydraLogLevel = HydraLogLevel.off, orgId?: string, gamificationKey?: string, gamificationRegion?: string, gamificationBaseUrl?: string)` |
| `HydraFirebaseRemoteConfigKeys` | `(keyForAccountId: string, keyForBaseUrl: string, keyForSsl: string, keyForRemoteDebugLevel: string, keyForOrgId?: string, keyForGamificationKey?: string, keyForGamificationRegion?: string, keyForGamificationBaseUrl?: string)` |
| `HydraVisitorInfo` | `visitorId: string` |
| `HydraNotification` (readonly, nullable) | `cuid`, `scope`, `campaignId`, `variationId`, `senderId`, `senderSource`, `custom`, `customData`, `priority`, `validity`, `messageId`, `gateway: HydraNotificationGateway`, `body: HydraNotificationBody`, `expandableDetails: HydraNotificationExpandedDetails`, `isRead`, `imageIdentifier`, `accountId`, `channelId`, `payload`, `createdAt: Date`, `isExpanded`, `isMessageEllipsized`, `isTitleEllipsized`, `showArrow` |
| `HydraNotificationBody` / `HydraNotificationCta` | `title`, `message`, `cta`, `image` / `type: HydraNotificationCtaType`, `action`, `actionText` |
| `HydraNotificationExpandedDetails` / `NonHydraNotification` | `ctas`, `message`, `image`, `style` / `title`, `body`, `icon`, `imageUrl`, `data` |

### Enums
- `HydraLogLevel`: `off = 0`, `error = 1`, `warn = 2`, `info = 3`, `debug = 4`, `verbose = 5`.
- `ThemeMode`: `none = 'NONE'`, `auto = 'AUTO'`, `light = 'LIGHT'`, `dark = 'DARK'`.
- `UserState`: `none`, `legacyRegistered`, `visitor`, `merged`, `signedOut` (string values equal the names).
- `HydraNotificationCtaType`: `external`, `deepLink`, `rating`, `feedback`, `appRating`, `unknown`. `HydraNotificationGateway`: `fcm`, `xiaomi`, `unknown`.
- `HydraNativeEvent`: `onTokenAvailable`, `onNonHydraNotificationReceived`, `onNonHydraNotificationClicked`, `onHydraNotificationReceived`, `onHydraNotificationClicked`, `onHydraNotificationShown`, `onHydraNotificationDismissed`, `handleCustomAction`, `onNotificationCenterDismissed`, `onInboxUpdated`, `onHydraSdkInitializationResult`, `onHydraInAppMessage`, `onConfigFetchedCallback`, `onLegacyFlowReady`, `onVisitorSessionReady`, `onUserStateChanged`, `onGamificationViewHeightChanged`, `gamificationAnalyticsEvent`, `gamificationDeeplink`, `gamificationEventTrigger`.

### Native
- iOS: `Hydra.sharedInstance().initialize(application, didFinishLaunchingWithOptions: launchOptions ?? [:], with: <keys or nil>, withHydraRemoteConfig: nil)`; Objective-C `initialize:didFinishLaunchingWithOptions:withKeys:withHydraRemoteConfig:`. `HydraNativeFirebaseRemoteConfigKeys(keyForAccountId:keyForBaseUrl:keyForSsl:keyForRemoteLogLevel:keyForOrgId:keyForGamificationKey:keyForGamificationRegion:keyForGamificationBaseUrl:)`.
- Android (`com.hydralib.nativeapis`): `Hydra.initialize(this)` or `Hydra.initialize(this, hydraFirebaseRemoteConfigKeys)`; `HydraFirebaseRemoteConfigKeys(...)` takes the eight key names in that order.
- Default Remote Config keys: `hydra_account_id`, `hydra_base_url`, `hydra_ssl_public_key`, `hydra_remote_log_level`, `hydra_org_id`, `hydra_gamification_key`, `hydra_gamification_region`, `hydra_gamification_base_url`.
- Passing values directly (`HydraNativeRemoteConfig` / `HydraRemoteConfig.Builder`) is not part of this mode.
- iOS push extension: `HydraRemoteNotificationService` (`HydraPushNotificationServiceExtension`). Podfile: `hydra_pods`, `extension_pods`, `hydra_post_install(installer)`, `$RNHydraUseSPM`. Config: step 3.
