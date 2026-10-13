---
platform: react-native
config_mode: direct
sdk_package: "@capillarytech/react-native-hydra-lib"
sdk_version: null            # the source installs the npm `beta` tag and pins no version number (see Requirements)
modules_covered: [core, gamification]
modules_missing: [push, inapp, inbox_api, inbox_ui, visitor, multi_account]
sources: ["Integration document _ Experience+ pp.72–87 (React Native Hydra SDK – Integration Guide, Firebase excluded)"]
owner: TBD
last_verified: null
review_status: draft   # drafted from the source doc; not yet SME-verified
---
# React Native (without Firebase)

## Coverage
| Module | Status in this mode |
|---|---|
| Core: install, `hydra-config.json`, iOS init (Podfile + `AppDelegate`), Android init (`MainApplication`), SDK initialisation check, sign-in (`identify`), sign-out (`reset`) | Documented. For iOS, Objective-C `AppDelegate`s get only a method signature (Swift is complete). For Android, only Kotlin is shown. |
| Gamification: screen reporting, Loyalty token, Banner / Embed / Loyalty views, analytics and deeplink callbacks, trigger on a custom event, enable / disable (suppress) | Documented |
| Theme mode (`setThemeMode` / `getThemeMode`) | APIs documented; what the theme applies to isn't stated |
| Log levels | Documented, but the config keys contradict the setup steps (see Verification) |
| Push notifications | **Not documented.** The sample `hydra-config.json` sets `enable_push_notification` and `enable_hydra_sdk_firebase_registration` to `false`. |
| In-App messaging | **Not documented.** The sample config sets `enable_in_app_messaging` and `enable_in_app_messaging_in_react_native` to `false`. |
| Inbox API / Inbox UI | **Not documented.** The sample config sets `enable_inbox_api`, `enable_inbox_ui` and `use_default_inbox_ui_config` to `false`, and `max_notification_count` to `0`. |
| Visitor flow, multi-account, sign-up and updating user details | **Not documented** |

## Requirements
- Package: `@capillarytech/react-native-hydra-lib`, installed with the npm `beta` tag (`@beta`).
- npm or Yarn.
- iOS: CocoaPods (`pod install`), and a Podfile whose main target calls `use_native_modules!`.
- iOS `AppDelegate`: the full code is given in Swift only.
- Android: a Kotlin `MainApplication` with an `onCreate` function.
- The screen-reporting snippet (step 10) uses `useFocusEffect`, a React Navigation hook.

> ⚠️ Gap: the source doesn't give an exact SDK version, or minimum React Native, Node, iOS deployment target, Android minSdk / compileSdk, Xcode, Gradle or Kotlin versions. Ask a Capillary engineer before giving numbers. The React Native gamification guide for Firebase mode (`react-native/firebase.md`) names a minimum version for gamification; this guide doesn't say whether it applies here, so don't quote it for this mode.

## Prerequisites
See `_shared/prerequisites.md` for the common exchange. For this platform and mode:

**Client gives Capillary** (to register the app):
| Credential | Platform |
|---|---|
| Bundle ID (`{{bundle_id}}`) | iOS |
| Application ID (`{{application_id}}`) | Android |
| App signature (SHA256), from your app signing report | Android |

**Capillary gives client** (after registration):
| Value | Placeholder | Description in the source |
|---|---|---|
| Account ID | `{{account_id}}` | Your unique account identifier |
| Base URL | `{{base_url}}` | API base endpoint |
| SSL Public Key | `{{ssl_public_key}}` | Public key for secure communication |
| Org ID | `{{org_id}}` | Your organization identifier |
| Gamification Base URL | `{{gamification_base_url}}` | Base URL for gamification services |
| Gamification Key | `{{gamification_key}}` | writeKey for gamification |
| Gamification Region | `{{gamification_region}}` | region value |

**Also needed:**
- **Loyalty View:** a Capillary B2B short-lived token (see `_shared/prerequisites.md`).
- **Banner / Embed / Loyalty views:** their entry-point IDs (`{{banner_id}}`, `{{embed_id}}`, `{{loyalty_id}}`).
- **Capillary CRM:** the `customerId` sent at sign-in must match the Account Linking Identifier configured in the CRM (step 8).

> ⚠️ Gap: the source describes Gamification Region only as "region value". It doesn't list the allowed values or their case, and doesn't say whether the Gamification Base URL is optional in this mode. `_shared/prerequisites.md` lists `IN`, `US` and `ME` and marks the base URL optional; confirm both for React Native. Ask a Capillary engineer.

## Steps

### 1. Install the package
npm:

```bash
npm install @capillarytech/react-native-hydra-lib@beta
```

Yarn:

```bash
yarn add @capillarytech/react-native-hydra-lib@beta
```

### 2. Add the Hydra configuration file
Create `<PROJECT_ROOT>/capillary/hydra-config.json` with this content (the source's sample):

```json file=capillary/hydra-config.json
{
  "console_log_level": 4,
  "enable_in_app_messaging": false,
  "enable_inbox_api": false,
  "enable_inbox_ui": false,
  "use_default_inbox_ui_config": false,
  "max_notification_count": 0,
  "enable_push_notification": false,
  "enable_hydra_sdk_firebase_registration": false,
  "hydra_notification_color": "#FF03DAC5",
  "enable_in_app_messaging_in_react_native": false
}
```

> ⚠️ Gap: the source gives this file only as a sample. It doesn't explain the keys or say which are required, and it doesn't show how the iOS and Android builds pick the file up. Ask a Capillary engineer before changing the sample values.

### 3. iOS: update the Podfile
In `ios/Podfile`, make two changes.

a) Add these lines just below the existing `require` block for React Native:

```ruby file=ios/Podfile
require Pod::Executable.execute_command('node', ['-p',
  'require.resolve(
    "@capillarytech/react-native-hydra-lib/scripts/HydraPods.rb",
    {paths: [process.argv[1]]},
  )', __dir__]).strip
```

b) In your main target, just below `config = use_native_modules!`, add:

```ruby file=ios/Podfile
hydra_pods
```

### 4. iOS: install pods
From the `ios` folder:

```bash
cd ios
pod install
```

### 5. iOS: initialise the SDK in `AppDelegate`
Add the import at the top of your `AppDelegate`:

```swift file=ios/<YourApp>/AppDelegate.swift
import react_native_hydra_lib
```

Then, in `application(_:didFinishLaunchingWithOptions:)`, replace the return statement as shown.

Swift:

```swift file=ios/<YourApp>/AppDelegate.swift
func application(
  _ application: UIApplication,
  didFinishLaunchingWithOptions launchOptions: [UIApplication.LaunchOptionsKey: Any]? = nil
) -> Bool {

  let result = super.application(application, didFinishLaunchingWithOptions: launchOptions)

  let config = HydraNativeRemoteConfig(
    accountId: "{{account_id}}",
    baseUrl: "{{base_url}}",
    sslPublicKey: "{{ssl_public_key}}",
    remoteLogLevel: 0,                  // 0–5, see "Log levels" under Verification
    orgId: "{{org_id}}",
    gamificationKey: "{{gamification_key}}",
    gamificationRegion: "{{gamification_region}}",
    gamificationBaseUrl: "{{gamification_base_url}}"
  )

  Hydra
    .sharedInstance()
    .initialize(
      application,
      didFinishLaunchingWithOptions: launchOptions ?? [:],
      with: nil,
      withHydraRemoteConfig: config
    )

  return result
}
```

> ⚠️ Source doc correction: the text (p.76) says to "replace the return statement" in your existing method, but the snippet shows the whole method. Pasting it as a second method won't compile. The consistent reading: keep your existing method declaration (including `override`, if it has one) and the code before the `return`. Replace the `return …` line with everything from `let result = super.application(…)` to `return result`. *Pending SME confirmation.*

> ⚠️ Gap: the snippet calls `super.application(…)`, so it assumes your `AppDelegate` inherits that method from a superclass. The source doesn't say which React Native versions or `AppDelegate` templates this targets, and doesn't explain the `with: nil` argument. Ask a Capillary engineer.

Objective-C: the source gives only the equivalent method signature:

```objectivec
- (BOOL)application:(UIApplication *)application
    didFinishLaunchingWithOptions:(NSDictionary *)launchOptions
```

> ⚠️ Gap: for Objective-C the source (p.77) shows only this signature. It doesn't show the import, the `HydraNativeRemoteConfig` construction or the `initialize` call in Objective-C. Don't improvise a translation of the Swift code. Ask a Capillary engineer.

Replace every placeholder with the values Capillary gave you at registration.

### 6. Android: initialise the SDK in `MainApplication`
Add these imports to your `MainApplication` file:

```kotlin file=android/app/src/main/java/<your-package>/MainApplication.kt
import com.hydralib.nativeapis.Hydra
import com.hydralib.nativeapis.HydraRemoteConfig
```

Add this to `onCreate`, **after** the default React Native generated code:

```kotlin file=android/app/src/main/java/<your-package>/MainApplication.kt
val config = HydraRemoteConfig(
  accountId = "{{account_id}}",
  baseURL = "{{base_url}}",
  sslPublicKey = "{{ssl_public_key}}",
  remoteDebugLevel = 0,
  orgId = "{{org_id}}",
  gamificationKey = "{{gamification_key}}",
  gamificationRegion = "{{gamification_region}}",
  gamificationBaseUrl = "{{gamification_base_url}}"
)

Hydra.initialize(this, remoteConfig = config)
```

Replace every placeholder with the values Capillary gave you at registration.

> ⚠️ Gap: some parameter names differ between platforms: iOS uses `baseUrl` and `remoteLogLevel`, Android uses `baseURL` and `remoteDebugLevel`. Copy each exactly as written for its platform. The source doesn't confirm that `remoteDebugLevel` takes the same 0–5 remote log level as iOS's `remoteLogLevel`. Ask a Capillary engineer.

> ⚠️ Gap: only a Kotlin `MainApplication` is documented. There's no Java variant. Ask a Capillary engineer if the client's `MainApplication` is Java.

### 7. Check that the SDK is initialised (JavaScript)
Before using any API from the package, check that the Hydra SDK has initialised:

```javascript
HydraCore.isSdkInitialized()
  .then((isInitialized) => {
    console.log('Hydra Instance Status: ', isInitialized);

    if (isInitialized) {
      // SDK is ready - proceed with your logic
    } else {
      // Register for the initialization callback
      const subscription =
        HydraNativeEventEmitter.getInstance()
          .addHydraSdkInitializationResultListener((result, message) => {
            // Handle initialization result
          });
    }
  })
  .catch((error) => {
    console.error('Error checking Hydra initialization status:', error);
  });
```

> ⚠️ Gap: the source never shows the JavaScript `import` lines for `Hydra`, `HydraCore`, `HydraNativeEventEmitter`, `HydraUserDetails`, `ThemeMode`, `GamificationBannerView`, `GamificationEmbedView` or `GamificationLoyaltyView`. Ask a Capillary engineer which module paths to import them from.

> ⚠️ Gap: the source doesn't describe the `result` and `message` values passed to `addHydraSdkInitializationResultListener`, or when to remove that subscription. Ask a Capillary engineer.

### 8. Sign the user in (`identify`)
Sign the user in with `identify` before using the rest of the SDK. `customerId` is required; the other user details are optional (see `HydraUserDetails` in the API Reference). `customerId` **must match the Account Linking Identifier configured in Capillary CRM** (see `_shared/prerequisites.md`).

```javascript
const userDetails = new HydraUserDetails(customerId);
await Hydra.identify(userDetails);
```

### 9. Sign the user out (`reset`)
```javascript
await Hydra.reset(customerId);
```

### 10. Report the current screen (required for campaigns)
To display Floating Button, Popup and Bottom Sheet campaigns, report the current screen **after sign-in**:

```javascript
useFocusEffect(
  useCallback(() => {
    const timer = setTimeout(() => {
      Hydra.gamificationScreenAppeared('home');
    }, 500);

    return () => {
      clearTimeout(timer);
      Hydra.gamificationScreenDisappeared();
    };
  }, [])
);
```

The 500 ms delay is required so the screen animation can finish before the screen is reported.

> ⚠️ Gap: the source uses `'home'` as the example screen name. It doesn't say which names to pass or how they relate to campaign targeting, or how to report screens in an app that doesn't use React Navigation. Ask a Capillary engineer.

### 11. Set the Capillary token (for Loyalty View)
To support the Loyalty View, set the Capillary B2B short-lived token:

```javascript
Hydra.setCapToken(token); // the Capillary B2B short-lived token
```

## Modules

### Push
> ⚠️ Gap: not documented for this mode. The sample `hydra-config.json` sets `enable_push_notification` and `enable_hydra_sdk_firebase_registration` to `false`, and the source doesn't say whether push can work without Firebase. Ask a Capillary engineer.

### In-App
> ⚠️ Gap: not documented for this mode. The sample config has `enable_in_app_messaging` and `enable_in_app_messaging_in_react_native` set to `false`, but no setup steps are given. Ask a Capillary engineer.

### Inbox
> ⚠️ Gap: not documented for this mode. The sample config has `enable_inbox_api`, `enable_inbox_ui`, `use_default_inbox_ui_config` and `max_notification_count`, and the `removeListener` example names an `inboxUpdatedSubscription`, but no inbox APIs or listeners are documented. Ask a Capillary engineer.

### Visitor
> ⚠️ Gap: not documented for this mode. Ask a Capillary engineer.

### Gamification
Gamification is configured in the native init calls (steps 5 and 6: `gamificationKey`, `gamificationRegion`, `gamificationBaseUrl`). Floating Button, Popup and Bottom Sheet campaigns are displayed once the current screen is reported after sign-in (step 10). The Loyalty View also needs the token from step 11.

`BANNER_ID`, `EMBED_ID` and `LOYALTY_ID` below are the entry-point IDs. The source uses these constants without declaring them; the declaration in the Banner snippet is added here for clarity.

> ⚠️ Gap: the source doesn't say where the client gets the Banner, Embed and Loyalty IDs, or their type (the declaration below assumes a string). `_shared/prerequisites.md` says they're configured in the gamification dashboard. Ask a Capillary engineer.

#### Banner View
Register a height listener and render the banner:

```javascript
const BANNER_ID = '{{banner_id}}'; // declaration added; not in the source

const [bannerHeight, setBannerHeight] = useState(300);

useEffect(() => {
  const subscription =
    HydraNativeEventEmitter.getInstance()
      .addGamificationViewHeightChangedListener((height, entryPointId) => {
        if (height > 0 && entryPointId === BANNER_ID) {
          setBannerHeight(height);
        }
      });

  return () => {
    HydraNativeEventEmitter.getInstance().removeListener(subscription);
  };
}, []);
```

```jsx
<View style={styles.container}>
  <GamificationBannerView
    bannerId={BANNER_ID}
    style={[styles.banner, { height: bannerHeight }]}
  />
</View>
```

#### Embed View
```jsx
<ScrollView style={styles.container}>
  <GamificationEmbedView
    embedId={EMBED_ID}
    style={[styles.embed, { height: embedHeight }]}
  />
</ScrollView>
```

`EMBED_ID` = `{{embed_id}}`.

#### Loyalty View
Needs the Capillary token (step 11).

```jsx
<ScrollView style={styles.container}>
  <GamificationLoyaltyView
    loyaltyId={LOYALTY_ID}
    style={[styles.loyalty, { height: loyaltyHeight }]}
  />
</ScrollView>
```

`LOYALTY_ID` = `{{loyalty_id}}`.

> ⚠️ Source doc correction: the Embed and Loyalty snippets (pp.80–81) use `embedHeight` and `loyaltyHeight`, but the guide never defines them. `bannerHeight`, by contrast, comes from `useState` plus the height listener. Copied as-is, these snippets fail because the variables don't exist, so define them before use. The source doesn't say whether `addGamificationViewHeightChangedListener` also reports Embed and Loyalty heights, or what initial height to use. *Pending SME confirmation.*

#### Callback for analytics events
This listener fires for game events:

```javascript
useEffect(() => {
  const subscription =
    HydraNativeEventEmitter.getInstance().addGamificationAnalyticsEventListener(
      (name, payload) => {
        console.log('gamificationAnalyticsEvent: ', name, payload);
      }
    );
  return () => {
    HydraNativeEventEmitter.getInstance().removeListener(subscription);
  };
}, []);
```

#### Callback for deeplinks
This listener fires when a click in the game needs to redirect to a deeplink:

```javascript
useEffect(() => {
  const subscription =
    HydraNativeEventEmitter.getInstance().addGamificationDeeplinkListener(
      (url) => {
        console.log('gamificationDeeplink: ', url);
      }
    );
  return () => {
    HydraNativeEventEmitter.getInstance().removeListener(subscription);
  };
}, []);
```

> ⚠️ Gap: the source doesn't list the analytics event names or `payload` shape, or say whether the app must navigate to the deeplink `url` itself. Ask a Capillary engineer.

#### Trigger a campaign on a custom event
```javascript
Hydra.track('<YOUR_EVENT>');
```

> ⚠️ Gap: the source shows `track` only with an event name. It doesn't document event attributes, or general custom-event tracking beyond campaign triggers. Ask a Capillary engineer.

#### Theme mode
Set the theme mode (values are in the `ThemeMode` enum, see API Reference):

```typescript
Hydra.setThemeMode(ThemeMode.dark)
  .then(() => {
    console.log('Theme mode set to dark');
  })
  .catch((error) => {
    console.error('Error setting theme mode:', error);
  });
```

Get the current theme mode:

```typescript
Hydra.getThemeMode()
  .then((mode) => {
    console.log('Current theme mode is', mode);
  })
  .catch((error) => {
    console.error('Error getting theme mode:', error);
  });
```

> ⚠️ Gap: the source doesn't say what the theme mode applies to, or what `none` and `auto` do. Ask a Capillary engineer.

#### Enable or disable (suppress) gamification
Pass `true` to disable (suppress) Hydra gamification, or `false` to enable it:

```typescript
Hydra.setGamificationSuppressed(true)
  .then(() => {
    console.log('Gamification suppressed set to true');
  })
  .catch((error) => {
    console.error('Error setting gamification suppressed:', error);
  });
```

Check whether gamification is disabled (suppressed):

```typescript
Hydra.isGamificationSuppressed()
  .then((suppressed) => {
    console.log('Gamification suppressed is', suppressed);
  })
  .catch((error) => {
    console.error('Error getting gamification suppressed:', error);
  });
```

## Verification
**SDK initialisation.** Run the check from step 7. `HydraCore.isSdkInitialized()` resolves to `true` once the SDK has initialised. If it resolves to `false`, the `addHydraSdkInitializationResultListener` callback reports the result later as `(result, message)`.

**Sign-in and campaigns.** After `Hydra.identify(...)` (step 8) and screen reporting (step 10), Floating Button, Popup and Bottom Sheet campaigns can display on the reported screen.

**Gamification state.**
- `Hydra.isGamificationSuppressed()` should resolve to `false` unless you suppressed gamification.
- With the listeners from the Gamification module added, game events log `gamificationAnalyticsEvent:` and deeplink clicks log `gamificationDeeplink:`. These lines come from the snippets' own `console.log` calls, not from the SDK.
- For the Banner View, the height listener fires with your `BANNER_ID` and a height above 0.

**Log levels** (source: Log Configuration, p.84). There are two kinds of log level:

| Log type | Where the logs go |
|---|---|
| Console Log Level | Xcode console (iOS) and Logcat (Android) |
| Remote Log Level | Saved to the Capillary backend |

Both must be an integer from 0 to 5 (each level includes the levels below it):

| Level | Name | Logs |
|---|---|---|
| 0 | Off | Logging disabled |
| 1 | Error | Error-level messages only |
| 2 | Warn | Warnings and above |
| 3 | Info | Informational messages and above |
| 4 | Debug | Debug messages and above |
| 5 | Verbose | All messages |

The sample `hydra-config.json` (step 2) sets `"console_log_level": 4` (Debug). The remote level is passed in the native init call: `remoteLogLevel` on iOS (step 5), `remoteDebugLevel` on Android (step 6). Both are `0` (Off) in the samples.

> ⚠️ Source doc correction: the Log Configuration section (p.84) says log levels are configured in `hydra-config.json` (Android) and `HydraConfig.plist` (iOS), using the key `log_levels` (Android) and `LOG_LEVELS` (iOS). That doesn't match the setup steps:
> - the only `hydra-config.json` the guide creates is in `<PROJECT_ROOT>/capillary/` (not Android-only), and it uses `console_log_level` (p.74);
> - no step creates a `HydraConfig.plist`;
> - the remote level is passed in the native init call (pp.76–77).
>
> The value format for `log_levels` / `LOG_LEVELS` is never shown. Until confirmed, use what the setup steps show: `console_log_level` in `capillary/hydra-config.json`, and the remote level in the native init. *Pending SME confirmation.*

> ⚠️ Gap: the source has no formal verification procedure. It gives no expected SDK log lines, no meaning for the `result` / `message` initialisation values, and no dashboard checks to confirm sign-in, events or campaigns reached Capillary. Ask a Capillary engineer.

## Known Issues

**Calling SDK APIs before the SDK has initialised**
- From the source doc (p.78): check `HydraCore.isSdkInitialized()` before using any API from the package. If it's `false`, wait for `addHydraSdkInitializationResultListener` (step 7).

**`customerId` must match the CRM Account Linking Identifier**
- From the source doc (p.86): `customerId` can be mobile, email, InTouchUserId, externalId or FCMToken. Which one is determined by the Account Linking Identifier set in the Capillary CRM dashboard under *Organisation Settings > Omni Channel Settings > Channel Configurations > MAPP_SDK*. Pass the value of that identifier for the signed-in user.

**Floating Button, Popup or Bottom Sheet campaigns don't appear**
- From the source doc (p.79): these campaigns need the current screen reported **after sign-in** (step 10).
- Keep the 500 ms delay: it's required so the screen animation can finish before the screen is reported.

**Loyalty View content missing**
- From the source doc (p.79): the Loyalty View needs the Capillary B2B short-lived token, set with `Hydra.setCapToken(...)` (step 11). `_shared/prerequisites.md` adds that it must be set before the Loyalty View is shown.

**Placeholder values left in the native init**
- From the source doc (pp.77–78): replace every placeholder in the `AppDelegate` and `MainApplication` code with the values Capillary gave you at registration.

## API Reference

### JavaScript: `Hydra` and `HydraCore`
| API | Purpose |
|---|---|
| `HydraCore.isSdkInitialized()` | Promise that resolves to whether the SDK has initialised |
| `Hydra.identify(userDetails: HydraUserDetails)` | Signs the user in (awaitable) |
| `Hydra.reset(customerId)` | Signs the user out (awaitable) |
| `Hydra.gamificationScreenAppeared(screenName)` | Reports that a screen appeared (call after sign-in, with the 500 ms delay) |
| `Hydra.gamificationScreenDisappeared()` | Reports that the current screen went away |
| `Hydra.setCapToken(token)` | Sets the Capillary B2B short-lived token for the Loyalty View |
| `Hydra.track(eventName)` | Triggers a campaign on a custom event |
| `Hydra.setThemeMode(mode: ThemeMode)` | Sets the theme mode (Promise) |
| `Hydra.getThemeMode()` | Promise that resolves to the current theme mode |
| `Hydra.setGamificationSuppressed(suppressed: boolean)` | `true` disables (suppresses) gamification, `false` enables it (Promise) |
| `Hydra.isGamificationSuppressed()` | Promise that resolves to whether gamification is suppressed |

### JavaScript: `HydraNativeEventEmitter`
| API | Purpose |
|---|---|
| `static getInstance(): HydraNativeEventEmitter` | Returns the singleton used to call all other emitter methods |
| `removeListener(emitterSubscription: EmitterSubscription): void` | Removes a listener. `emitterSubscription` (required) is the object returned when the listener was added. |
| `addHydraSdkInitializationResultListener((result, message) => …)` | Fires with the SDK initialisation result; returns a subscription |
| `addGamificationViewHeightChangedListener((height, entryPointId) => …)` | Fires when a gamification view's height changes; returns a subscription |
| `addGamificationAnalyticsEventListener((name, payload) => …)` | Fires for game events; returns a subscription |
| `addGamificationDeeplinkListener((url) => …)` | Fires when a game click needs to redirect to a deeplink; returns a subscription |

Example: `HydraNativeEventEmitter.getInstance().removeListener(subscription);`

> ⚠️ Source doc correction: the reference (p.85) writes the signature as `HydraNativeEventEmitter.removeListener(…)`, like a static method. Its own example, and every snippet, call it on the singleton instead: `HydraNativeEventEmitter.getInstance().removeListener(subscription)`. *Pending SME confirmation.*

### JavaScript: components
| Component | Props shown in the source |
|---|---|
| `GamificationBannerView` | `bannerId`, `style` (height from the height listener) |
| `GamificationEmbedView` | `embedId`, `style` |
| `GamificationLoyaltyView` | `loyaltyId`, `style` |

### JavaScript: `HydraUserDetails`
A model class used for signing up, signing in and updating user details. Only sign-in (`identify`) is documented.

```typescript
new HydraUserDetails(
  customerId: string,
  firstName?: string | null,
  lastName?: string | null,
  email?: string | null,
  phone?: string | null
): HydraUserDetails
```

| Parameter | Type | Required | Description |
|---|---|---|---|
| `customerId` | string | Yes | Can be mobile, email, InTouchUserId, externalId or FCMToken. Determined by the Account Linking Identifier configured in the Capillary CRM dashboard under *Organisation Settings > Omni Channel Settings > Channel Configurations > MAPP_SDK*. |
| `firstName` | string | No | First name of the user |
| `lastName` | string | No | Last name of the user |
| `email` | string | No | Email address of the user |
| `phone` | string | No | Phone number of the user |

Example from the source:

```javascript
const userDetails = new HydraUserDetails(
  '8888888888',
  'FirstName',
  'LastName',
  'hydra.test@capillarytech.com',
  '918888888888'
);
```

### JavaScript: enums
```typescript
enum HydraLogLevel {
  off     = 0,
  error   = 1,
  warn    = 2,
  info    = 3,
  debug   = 4,
  verbose = 5,
}

export enum ThemeMode {
  none = 'NONE',
  auto = 'AUTO',
  light = 'LIGHT',
  dark = 'DARK',
}
```

`HydraLogLevel` holds the constants for the console and remote log levels; each higher level includes all the levels below it. The source doesn't show an API that takes a `HydraLogLevel`.

### Native initialisation
| Platform | API | Notes |
|---|---|---|
| iOS (Swift) | `HydraNativeRemoteConfig(accountId:baseUrl:sslPublicKey:remoteLogLevel:orgId:gamificationKey:gamificationRegion:gamificationBaseUrl:)` | `remoteLogLevel` is an integer 0–5. Requires `import react_native_hydra_lib`. |
| iOS (Swift) | `Hydra.sharedInstance().initialize(_:didFinishLaunchingWithOptions:with:withHydraRemoteConfig:)` | Called in `application(_:didFinishLaunchingWithOptions:)` with `launchOptions ?? [:]`, `with: nil` and the config |
| Android (Kotlin) | `HydraRemoteConfig(accountId, baseURL, sslPublicKey, remoteDebugLevel, orgId, gamificationKey, gamificationRegion, gamificationBaseUrl)` | `com.hydralib.nativeapis.HydraRemoteConfig` |
| Android (Kotlin) | `Hydra.initialize(this, remoteConfig = config)` | `com.hydralib.nativeapis.Hydra`. Called in `MainApplication.onCreate`, after the generated React Native code. |
| iOS (Podfile) | `HydraPods.rb` (via `require.resolve`) and `hydra_pods` | See step 3 |

### Config file: `capillary/hydra-config.json`
| Key | Sample value | Meaning in the source |
|---|---|---|
| `console_log_level` | `4` | Not described; matches "Console Log Level" (see the log-level correction under Verification) |
| `enable_in_app_messaging` | `false` | Not described |
| `enable_inbox_api` | `false` | Not described |
| `enable_inbox_ui` | `false` | Not described |
| `use_default_inbox_ui_config` | `false` | Not described |
| `max_notification_count` | `0` | Not described |
| `enable_push_notification` | `false` | Not described |
| `enable_hydra_sdk_firebase_registration` | `false` | Not described |
| `hydra_notification_color` | `"#FF03DAC5"` | Not described |
| `enable_in_app_messaging_in_react_native` | `false` | Not described |
