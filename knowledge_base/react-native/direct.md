---
platform: react-native
config_mode: direct
sdk_package: "@capillarytech/react-native-hydra-lib"
sdk_version: null            # the source installs the npm `beta` tag and pins no version number
modules_covered: [core, gamification]
modules_missing: [push, inapp, inbox_api, inbox_ui, visitor, multi_account]
sources: ["Integration document _ Experience+ pp.72–87 (React Native Hydra SDK – Integration Guide, Firebase excluded)"]
owner: TBD
last_verified: null
review_status: draft   # drafted from the source doc; not yet SME-verified
---
# React Native (without Firebase)

## Coverage
| Module | Status |
|---|---|
| Core: install, `hydra-config.json`, iOS init (Swift), Android init (Kotlin), init check, sign-in, sign-out | Documented (Objective-C: method signature only; no Java) |
| Gamification: screen reporting, Loyalty token, Banner / Embed / Loyalty views, callbacks, custom-event trigger, theme mode, suppress | Documented |
| Log levels | Documented, but the config keys conflict with the setup steps (see Verification) |
| Push, In-App, Inbox, Visitor, multi-account, sign-up / update user | **Not documented** (the sample config turns push, in-app and inbox off) |

## Requirements
- `@capillarytech/react-native-hydra-lib`, installed with the npm `beta` tag.
- npm or Yarn; CocoaPods for iOS.
- iOS: a Podfile whose main target calls `use_native_modules!`; a Swift `AppDelegate`.
- Android: a Kotlin `MainApplication` with `onCreate`.

> ⚠️ Gap: no exact SDK version, and no minimum React Native, Node, iOS, Android (minSdk / compileSdk), Xcode, Gradle or Kotlin versions. Don't reuse the `1.7.0-beta.7` minimum from the Firebase-mode gamification guide. Ask a Capillary engineer.

## Prerequisites
See `_shared/prerequisites.md` for the common exchange.

- **Client gives Capillary** (to register the app): Bundle ID `{{bundle_id}}` (iOS); Application ID `{{application_id}}` and App Signature SHA256 from the app signing report (Android).
- **Capillary gives client:** Account ID `{{account_id}}`, Base URL `{{base_url}}`, SSL Public Key `{{ssl_public_key}}`, Org ID `{{org_id}}`, Gamification Base URL `{{gamification_base_url}}`, Gamification Key (writeKey) `{{gamification_key}}`, Gamification Region `{{gamification_region}}`.
- **Also needed:** the Capillary B2B short-lived token (Loyalty View); entry-point IDs `{{banner_id}}`, `{{embed_id}}`, `{{loyalty_id}}`; a `customerId` matching the CRM Account Linking Identifier (step 8).

> ⚠️ Gap: allowed Gamification Region values (and case) and whether the Gamification Base URL is optional aren't stated for React Native. Ask a Capillary engineer.

## Steps

### 1. Install the package
```bash
npm install @capillarytech/react-native-hydra-lib@beta
```

```bash
yarn add @capillarytech/react-native-hydra-lib@beta
```

### 2. Add the Hydra configuration file
Create `<PROJECT_ROOT>/capillary/hydra-config.json` (sample from the source):

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

> ⚠️ Gap: the keys aren't explained and how the native builds pick up this file isn't shown. Ask a Capillary engineer before changing sample values.

### 3. iOS: update the Podfile
a) Just below the existing React Native `require` block:

```ruby file=ios/Podfile
require Pod::Executable.execute_command('node', ['-p',
  'require.resolve(
    "@capillarytech/react-native-hydra-lib/scripts/HydraPods.rb",
    {paths: [process.argv[1]]},
  )', __dir__]).strip
```

b) In your main target, just below `config = use_native_modules!`:

```ruby file=ios/Podfile
hydra_pods
```

### 4. iOS: install pods
From the `ios` folder:

```bash
pod install
```

### 5. iOS: initialise the SDK in `AppDelegate`
Add the import at the top of your `AppDelegate`:

```swift file=AppDelegate.swift
import react_native_hydra_lib
```

Then, in `application(_:didFinishLaunchingWithOptions:)`, replace the return statement:

```swift file=AppDelegate.swift
func application(
  _ application: UIApplication,
  didFinishLaunchingWithOptions launchOptions: [UIApplication.LaunchOptionsKey: Any]? = nil
) -> Bool {

  let result = super.application(application, didFinishLaunchingWithOptions: launchOptions)

  let config = HydraNativeRemoteConfig(
    accountId: "{{account_id}}",
    baseUrl: "{{base_url}}",
    sslPublicKey: "{{ssl_public_key}}",
    remoteLogLevel: 0,
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

> ⚠️ Correction: ✅ Use the snippet's body (`let result = …` to `return result`) in place of your existing method's `return` line, keeping your own declaration (and `override`, if present). ❌ Don't use the full `func application(…)` as a second method; it won't compile (p.76 shows the whole method but says "replace the return statement"). *Pending SME confirmation.*

Objective-C: the source gives only the equivalent method signature:

```objectivec
- (BOOL)application:(UIApplication *)application
    didFinishLaunchingWithOptions:(NSDictionary *)launchOptions
```

> ⚠️ Gap: no Objective-C import, config or `initialize` code (p.77); don't translate the Swift yourself. The Swift calls `super.application(…)`, so it assumes a superclass provides it; the targeted React Native `AppDelegate` template isn't stated. Ask a Capillary engineer.

Replace every placeholder with the values from registration.

### 6. Android: initialise the SDK in `MainApplication`
Add the imports to your `MainApplication`:

```kotlin file=MainApplication.kt
import com.hydralib.nativeapis.Hydra
import com.hydralib.nativeapis.HydraRemoteConfig
```

In `onCreate`, **after** the default React Native generated code:

```kotlin file=MainApplication.kt
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

Replace every placeholder with the values from registration. Parameter names differ by platform: iOS `baseUrl` / `remoteLogLevel`, Android `baseURL` / `remoteDebugLevel`; copy each exactly.

> ⚠️ Gap: it isn't confirmed that `remoteDebugLevel` (Android) takes the same 0–5 level as `remoteLogLevel` (iOS); no Java `MainApplication` is documented. Ask a Capillary engineer.

### 7. Check that the SDK is initialised (JavaScript)
Before using any API from the package:

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

> ⚠️ Gap: no JavaScript `import` lines are given for `Hydra`, `HydraCore`, `HydraNativeEventEmitter`, `HydraUserDetails`, `ThemeMode` or the `Gamification…View` components, and the `result` / `message` values aren't described. Ask a Capillary engineer.

### 8. Sign the user in (`identify`)
Sign in first. `customerId` is required; other details are optional (see `HydraUserDetails`). `customerId` must match the Account Linking Identifier in Capillary CRM.

```javascript
const userDetails = new HydraUserDetails(customerId);
await Hydra.identify(userDetails);
```

### 9. Sign the user out (`reset`)
```javascript
await Hydra.reset(customerId);
```

### 10. Report the current screen (required for campaigns)
To display Floating Button, Popup and Bottom Sheet campaigns, report the current screen **after sign-in** with `Hydra.gamificationScreenAppeared(...)`, and call `Hydra.gamificationScreenDisappeared()` on cleanup:

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

The 500 ms delay is required so the screen animation completes before reporting.

> ⚠️ Gap: which screen names to pass (`'home'` is an example) and how to report screens without `useFocusEffect` aren't documented. Ask a Capillary engineer.

### 11. Set the Capillary token (for Loyalty View)
Set the Capillary B2B short-lived token (replace `'token'` with it):

```javascript
Hydra.setCapToken('token');
```

## Modules

### Push
> ⚠️ Gap: not documented for this mode; the sample config sets `enable_push_notification` and `enable_hydra_sdk_firebase_registration` to `false`. Ask a Capillary engineer.

### In-App
> ⚠️ Gap: not documented; the sample config sets `enable_in_app_messaging` and `enable_in_app_messaging_in_react_native` to `false`. Ask a Capillary engineer.

### Inbox
> ⚠️ Gap: not documented; the sample config turns the inbox keys off. Ask a Capillary engineer.

### Visitor
> ⚠️ Gap: not documented for this mode. Ask a Capillary engineer.

### Gamification
Gamification values go into the native init (steps 5–6). Floating Button, Popup and Bottom Sheet campaigns show once the screen is reported after sign-in (step 10). `BANNER_ID`, `EMBED_ID` and `LOYALTY_ID` in the snippets are your entry-point IDs (`{{banner_id}}`, `{{embed_id}}`, `{{loyalty_id}}`); the source uses them without declaring them, so declare them yourself.

#### Banner View
Register a height listener and render the banner:

```javascript
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

#### Loyalty View
Needs the token from step 11.

```jsx
<ScrollView style={styles.container}>
  <GamificationLoyaltyView
    loyaltyId={LOYALTY_ID}
    style={[styles.loyalty, { height: loyaltyHeight }]}
  />
</ScrollView>
```

> ⚠️ Gap: `embedHeight` and `loyaltyHeight` are used but never defined (pp.80–81), so these snippets fail as-is. The docs don't say whether `addGamificationViewHeightChangedListener` also reports Embed / Loyalty heights or what initial height to use. Ask a Capillary engineer.

#### Callback for analytics events
Fires for game events:

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
Fires when a click in the game needs to redirect to a deeplink:

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

> ⚠️ Gap: analytics event names, the `payload` shape, and whether the app must open the deeplink `url` itself aren't documented. Ask a Capillary engineer.

#### Trigger a campaign on a custom event
```javascript
Hydra.track('<YOUR_EVENT>');
```

> ⚠️ Gap: event attributes for `track` aren't documented. Ask a Capillary engineer.

#### Theme mode
Set (values in the `ThemeMode` enum):

```typescript
Hydra.setThemeMode(ThemeMode.dark)
  .then(() => {
    console.log('Theme mode set to dark');
  })
  .catch((error) => {
    console.error('Error setting theme mode:', error);
  });
```

Get:

```typescript
Hydra.getThemeMode()
  .then((mode) => {
    console.log('Current theme mode is', mode);
  })
  .catch((error) => {
    console.error('Error getting theme mode:', error);
  });
```

#### Enable or disable (suppress) gamification
Pass `true` to disable (suppress), `false` to enable:

```typescript
Hydra.setGamificationSuppressed(true)
  .then(() => {
    console.log('Gamification suppressed set to true');
  })
  .catch((error) => {
    console.error('Error setting gamification suppressed:', error);
  });
```

Check whether it's suppressed:

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
- **Init:** `HydraCore.isSdkInitialized()` (step 7) resolves `true`; if `false`, the `addHydraSdkInitializationResultListener` callback reports the result later.
- **Campaigns:** after `identify` (step 8) and screen reporting (step 10), Floating Button, Popup and Bottom Sheet campaigns can appear on the reported screen.
- **Gamification:** `isGamificationSuppressed()` resolves `false` unless suppressed; the listener snippets log `gamificationAnalyticsEvent:` / `gamificationDeeplink:` (their own `console.log`).

**Log levels:** Console (Xcode console / Logcat) and Remote (saved to the Capillary backend), each an integer 0–5: 0 Off, 1 Error, 2 Warn, 3 Info, 4 Debug, 5 Verbose (each includes those below). The setup steps use `"console_log_level": 4` (step 2) and the native-init remote level (`0`, steps 5–6).

> ⚠️ Gap: Log Configuration (p.84) says to set levels in `hydra-config.json` (Android) / `HydraConfig.plist` (iOS) with keys `log_levels` / `LOG_LEVELS` (format not shown), which conflicts with the setup steps (pp.74–77: `console_log_level` in `capillary/hydra-config.json`, no plist, remote level in native init). No expected SDK log lines or dashboard checks are documented either. Ask a Capillary engineer.

## Known Issues

**APIs fail or do nothing right after launch** → called before the SDK initialised → check `HydraCore.isSdkInitialized()` first and wait for `addHydraSdkInitializationResultListener` if `false` (step 7).

**User not matched to the CRM customer** → `customerId` isn't the CRM Account Linking Identifier → pass that identifier (see `HydraUserDetails`).

**Floating Button / Popup / Bottom Sheet campaigns don't appear** → screen not reported, reported before sign-in, or reported without the delay → report after sign-in with the 500 ms delay (step 10).

**Loyalty View empty** → Capillary token not set → call `Hydra.setCapToken(...)` before showing the view (step 11).

## API Reference

### `Hydra` / `HydraCore`
| API | Purpose |
|---|---|
| `HydraCore.isSdkInitialized()` | Promise → whether the SDK is initialised |
| `Hydra.identify(userDetails)` | Sign in (awaitable) |
| `Hydra.reset(customerId)` | Sign out (awaitable) |
| `Hydra.gamificationScreenAppeared(screenName)` | Report screen shown (after sign-in, 500 ms delay) |
| `Hydra.gamificationScreenDisappeared()` | Report screen gone |
| `Hydra.setCapToken(token)` | Set B2B short-lived token (Loyalty View) |
| `Hydra.track(eventName)` | Trigger a campaign on a custom event |
| `Hydra.setThemeMode(mode)` / `Hydra.getThemeMode()` | Set / get `ThemeMode` (Promise) |
| `Hydra.setGamificationSuppressed(bool)` / `Hydra.isGamificationSuppressed()` | `true` disables, `false` enables / Promise → state |

### `HydraNativeEventEmitter`
| API | Purpose |
|---|---|
| `static getInstance(): HydraNativeEventEmitter` | Singleton used to call all other methods |
| `removeListener(emitterSubscription: EmitterSubscription): void` | Remove a listener; pass the subscription returned when it was added (required) |
| `addHydraSdkInitializationResultListener((result, message) => …)` | SDK init result |
| `addGamificationViewHeightChangedListener((height, entryPointId) => …)` | Gamification view height changed |
| `addGamificationAnalyticsEventListener((name, payload) => …)` | Game events |
| `addGamificationDeeplinkListener((url) => …)` | Game click needs a deeplink redirect |

Each `add…Listener` returns a subscription.

> ⚠️ Correction: ✅ Use `HydraNativeEventEmitter.getInstance().removeListener(subscription)`, as in the source's own example and every snippet. ❌ Don't use `HydraNativeEventEmitter.removeListener(…)` as a static call (signature in the API Reference, p.85). *Pending SME confirmation.*

### Components
| Component | Props |
|---|---|
| `GamificationBannerView` | `bannerId`, `style` |
| `GamificationEmbedView` | `embedId`, `style` |
| `GamificationLoyaltyView` | `loyaltyId`, `style` |

### `HydraUserDetails`
Model for sign-up, sign-in and updating user details (only sign-in is documented).

```typescript
new HydraUserDetails(
  customerId: string,
  firstName?: string | null,
  lastName?: string | null,
  email?: string | null,
  phone?: string | null
): HydraUserDetails
```

Only `customerId` is required: mobile, email, InTouchUserId, externalId or FCMToken, as set by the CRM Account Linking Identifier (*Organisation Settings > Omni Channel Settings > Channel Configurations > MAPP_SDK*). Example:

```javascript
const userDetails = new HydraUserDetails(
  '8888888888',
  'FirstName',
  'LastName',
  'hydra.test@capillarytech.com',
  '918888888888'
);
```

### Enums
`HydraLogLevel`: console and remote log levels; each higher level includes those below.

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

### Native and config
- iOS: `HydraNativeRemoteConfig(...)` + `Hydra.sharedInstance().initialize(...)` (step 5); Podfile `HydraPods.rb` + `hydra_pods` (step 3).
- Android: `HydraRemoteConfig(...)` + `Hydra.initialize(this, remoteConfig = config)` (step 6).
- `capillary/hydra-config.json`: keys and sample values in step 2 (none described in the source).
