---
platform: react-native
config_mode: firebase
sdk_package: "@capillarytech/react-native-hydra-lib"
sdk_version: 1.7.0-beta.7    # minimum version for gamification per the source (p.3); the install command uses the npm `beta` tag
modules_covered: [gamification]
modules_missing: [core, push, inapp, inbox_api, inbox_ui, visitor, multi_account]
sources: ["Integration document _ Experience+ pp.1–6 (Gamification React Native Integration Guide, v1.0.1)"]
owner: TBD
last_verified: null
review_status: draft   # drafted from the source doc; not yet SME-verified
---
# React Native (with Firebase)

> ⚠️ Gap: **the core React Native + Firebase integration is not documented.** The only source for this mode is the *Gamification React Native Integration Guide* (pp.1–6). It assumes the app **already** has the Hydra React Native package (`@capillarytech/react-native-hydra-lib`) integrated with Firebase Remote Config, and it only covers adding gamification on top. These are not documented anywhere for React Native with Firebase:
> - installing and initialising the SDK with Firebase;
> - the Remote Config keys for the core SDK settings;
> - sign-in and sign-out;
> - push, in-app messaging, inbox, the visitor flow and multi-account.
>
> Ask a Capillary engineer. Don't fill these gaps from `react-native/direct.md`: that guide is for apps **without** Firebase, and the source doesn't say any of it applies when the SDK reads its settings from Firebase Remote Config.

## Coverage
| Module | Status in this mode |
|---|---|
| Core: SDK install and initialisation with Firebase, Firebase project and Remote Config setup, core Remote Config keys, sign-in / sign-out | **Not documented** |
| Custom events | Only `Hydra.track('<YOUR_EVENT>')`, shown as a way to trigger a campaign (Gamification module) |
| Push notifications | **Not documented** |
| In-App messaging | **Not documented** |
| Inbox API / Inbox UI | **Not documented** |
| Visitor flow, multi-account | **Not documented** |
| Gamification: package update, gamification Remote Config keys, screen reporting, Loyalty token, Banner / Embed / Loyalty views, analytics and deeplink callbacks, trigger on a custom event | **Documented** (pp.1–6) |

**What this file can help with:** a client whose React Native app already runs Hydra with Firebase Remote Config and wants to add gamification. For anyone still doing the base integration in this mode, escalate.

## Requirements
- `@capillarytech/react-native-hydra-lib` at version **`{{sdk_version}}` or later**. The source calls this the minimum required version (the "current Beta version"). The install command uses the npm `beta` tag (`@beta`).
- An existing Hydra React Native integration that reads its settings from Firebase Remote Config. This isn't documented; see the gap at the top.
- npm or Yarn.
- The screen-reporting snippet (step 3) uses `useFocusEffect`, a React Navigation hook.

> ⚠️ Gap: the source doesn't give minimum React Native, Node, iOS, Android, Xcode or Gradle versions, or the Firebase package versions to use. Ask a Capillary engineer before giving numbers.

## Prerequisites
See `_shared/prerequisites.md` for the common exchange, and `_shared/firebase-setup.md` for the Firebase project and Remote Config basics shared by every platform. For this platform and mode:
- **Existing integration:** the app already uses the Hydra React Native package with Firebase Remote Config. The source says that if you already use it, no additional package integration is needed for gamification.
- **Firebase access:** someone who can edit the app's Firebase Remote Config, to add the keys in step 2.
- **Capillary gives client:** the values for the gamification Remote Config keys:

  | Value | Placeholder |
  |---|---|
  | Gamification Region | `{{gamification_region}}` |
  | Gamification Key | `{{gamification_key}}` |
  | Gamification Base URL | `{{gamification_base_url}}` |
  | Org Id | `{{org_id}}` |

- **Loyalty View:** a Capillary B2B short-lived token (see `_shared/prerequisites.md`).
- **Banner / Embed / Loyalty views:** their entry-point IDs (`{{banner_id}}`, `{{embed_id}}`, `{{loyalty_id}}`).

## Steps

### 1. Update the package
Update the app to the latest, publicly available HydraLib version. Gamification is part of the React Native HydraLib package, so no extra package is needed.

npm:

```bash
npm install @capillarytech/react-native-hydra-lib@beta
```

Yarn:

```bash
yarn add @capillarytech/react-native-hydra-lib@beta
```

The minimum required version is `{{sdk_version}}`.

### 2. Add the gamification keys to Firebase Remote Config
Add these keys to Firebase Remote Config:

```text
hydra_gamification_region
hydra_gamification_key
hydra_gamification_base_url
hydra_org_id
```

| Remote Config key | Value |
|---|---|
| `hydra_gamification_region` | `{{gamification_region}}` |
| `hydra_gamification_key` | `{{gamification_key}}` |
| `hydra_gamification_base_url` | `{{gamification_base_url}}` |
| `hydra_org_id` | `{{org_id}}` |

**Important (from the source):** the key and URL values are mandatory. HydraGamification stays disabled if either value is missing.

> ⚠️ Gap: the source lists only the key names. It doesn't give the value formats (for example, the allowed region values and their case) or say how to publish the Remote Config. Ask a Capillary engineer.

> ⚠️ Gap: the source says the key and URL values (`hydra_gamification_key`, `hydra_gamification_base_url`) are mandatory, but doesn't say whether `hydra_gamification_region` and `hydra_org_id` are too. This also conflicts with `_shared/prerequisites.md`, which marks the Gamification Base URL as optional. For React Native, follow this guide (set the URL) until a Capillary engineer confirms.

### 3. Report the current screen (required for campaigns)
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

> ⚠️ Gap: the source doesn't document how to sign the user in for this mode, though this step depends on it. It also doesn't give the JavaScript `import` lines for `Hydra`, `HydraNativeEventEmitter` and the `Gamification…View` components. It uses `'home'` as the example screen name without saying which names to pass, and doesn't cover apps that don't use React Navigation. Ask a Capillary engineer.

### 4. Set the Capillary token (for Loyalty View)
To support the Loyalty View, set the Capillary B2B short-lived token:

```javascript
Hydra.setCapToken(token); // the Capillary B2B short-lived token
```

## Modules

### Push
> ⚠️ Gap: not documented for React Native with Firebase. Ask a Capillary engineer.

### In-App
> ⚠️ Gap: not documented for React Native with Firebase. Ask a Capillary engineer.

### Inbox
> ⚠️ Gap: not documented for React Native with Firebase (neither the Inbox API nor the Inbox UI). Ask a Capillary engineer.

### Visitor
> ⚠️ Gap: not documented for React Native with Firebase. Ask a Capillary engineer.

### Gamification
**Floating Button, Popup and Bottom Sheet campaigns.** These are displayed once steps 1–3 are done and the current screen is reported after sign-in. The source shows no other code for them.

**Optional components and callbacks** (source steps 5–10, in order). `BANNER_ID`, `EMBED_ID` and `LOYALTY_ID` are the entry-point IDs. The source uses these constants without declaring them; the declaration in the Banner snippet is added here for clarity.

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
Needs the Capillary token (step 4).

```jsx
<ScrollView style={styles.container}>
  <GamificationLoyaltyView
    loyaltyId={LOYALTY_ID}
    style={[styles.loyalty, { height: loyaltyHeight }]}
  />
</ScrollView>
```

`LOYALTY_ID` = `{{loyalty_id}}`.

> ⚠️ Source doc correction: the Embed and Loyalty snippets (p.5) use `embedHeight` and `loyaltyHeight`, but the guide never defines them. `bannerHeight`, by contrast, comes from `useState` plus the height listener. Copied as-is, these snippets fail because the variables don't exist, so define them before use. The source doesn't say whether `addGamificationViewHeightChangedListener` also reports Embed and Loyalty heights, or what initial height to use. *Pending SME confirmation.*

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

## Verification
- **Campaigns:** after sign-in, report a screen (step 3). A Floating Button, Popup or Bottom Sheet campaign for that screen should then appear.
- **Banner View:** the height listener fires with your `BANNER_ID` and a height above 0, and the banner resizes to it.
- **Callbacks:** with the listeners above added, game events log `gamificationAnalyticsEvent:`, and game clicks that redirect to a deeplink log `gamificationDeeplink:`. These lines come from the snippets' own `console.log` calls, not from the SDK.
- **Gamification enabled:** if nothing appears, check that `hydra_gamification_key` and `hydra_gamification_base_url` both have values in Remote Config. Gamification stays disabled if either is missing.

> ⚠️ Gap: this mode's source has no formal verification procedure. It gives no SDK-initialisation check, no SDK log lines or log-level settings, and no dashboard checks. Ask a Capillary engineer how to confirm that the base integration and gamification initialised.

## Known Issues

**Gamification never appears**
- Cause: the `hydra_gamification_key` or `hydra_gamification_base_url` value is missing from Firebase Remote Config.
- From the source doc (p.3): the key and URL values are mandatory. HydraGamification stays disabled if either value is missing.
- Fix: set both keys in Remote Config (step 2).

**Floating Button, Popup or Bottom Sheet campaigns don't appear**
- From the source doc (p.3): these campaigns need the current screen reported **after sign-in** (step 3).
- From the source doc (p.4): keep the 500 ms delay. It's required so the screen animation can finish before the screen is reported.

**Loyalty View content missing**
- From the source doc (p.4): the Loyalty View needs the Capillary B2B short-lived token, set with `Hydra.setCapToken(...)` (step 4). `_shared/prerequisites.md` adds that it must be set before the Loyalty View is shown.

## API Reference

### Firebase Remote Config keys (gamification)
| Key | Value | Notes |
|---|---|---|
| `hydra_gamification_region` | `{{gamification_region}}` | Whether it's mandatory isn't stated |
| `hydra_gamification_key` | `{{gamification_key}}` | Mandatory |
| `hydra_gamification_base_url` | `{{gamification_base_url}}` | Mandatory per this source (see the gap in step 2) |
| `hydra_org_id` | `{{org_id}}` | Whether it's mandatory isn't stated |

### JavaScript APIs shown in the source
| API | Purpose |
|---|---|
| `Hydra.gamificationScreenAppeared(screenName)` | Reports that a screen appeared (after sign-in, with the 500 ms delay) |
| `Hydra.gamificationScreenDisappeared()` | Reports that the current screen went away |
| `Hydra.setCapToken(token)` | Sets the Capillary B2B short-lived token for the Loyalty View |
| `Hydra.track(eventName)` | Triggers a campaign on a custom event |
| `HydraNativeEventEmitter.getInstance()` | Returns the emitter instance used to add and remove listeners |
| `.addGamificationViewHeightChangedListener((height, entryPointId) => …)` | Fires when a gamification view's height changes; returns a subscription |
| `.addGamificationAnalyticsEventListener((name, payload) => …)` | Fires for game events; returns a subscription |
| `.addGamificationDeeplinkListener((url) => …)` | Fires when a game click needs to redirect to a deeplink; returns a subscription |
| `.removeListener(subscription)` | Removes a listener added above |

### Components
| Component | Props shown in the source |
|---|---|
| `GamificationBannerView` | `bannerId`, `style` (height from the height listener) |
| `GamificationEmbedView` | `embedId`, `style` |
| `GamificationLoyaltyView` | `loyaltyId`, `style` |

> ⚠️ Gap: no API reference for the core SDK (initialisation, sign-in / sign-out, user model) is documented for this mode. Ask a Capillary engineer.
