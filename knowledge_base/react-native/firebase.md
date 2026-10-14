---
platform: react-native
config_mode: firebase
sdk_package: "@capillarytech/react-native-hydra-lib"
sdk_version: 1.7.0-beta.7    # minimum version for gamification per the source (p.3); install uses the npm `beta` tag
modules_covered: [gamification]
modules_missing: [core, push, inapp, inbox_api, inbox_ui, visitor, multi_account]
sources: ["Integration document _ Experience+ pp.1–6 (Gamification React Native Integration Guide, v1.0.1)"]
owner: TBD
last_verified: null
review_status: draft   # drafted from the source doc; not yet SME-verified
---
# React Native (with Firebase)

> ⚠️ Gap: **the core React Native + Firebase integration is not documented.** The only source (Gamification React Native Integration Guide, pp.1–6) assumes the app already runs the Hydra React Native package with Firebase Remote Config and only adds gamification. SDK install and init with Firebase, core Remote Config keys, sign-in / sign-out, push, in-app, inbox, visitor and multi-account are all missing. Don't fill them from `react-native/direct.md` (that guide is for apps without Firebase). Ask a Capillary engineer.

## Coverage
| Module | Status |
|---|---|
| Gamification: package update, Remote Config keys, screen reporting, Loyalty token, Banner / Embed / Loyalty views, callbacks, custom-event trigger | Documented |
| Core (install / init with Firebase, core Remote Config keys, sign-in / sign-out), Push, In-App, Inbox, Visitor, multi-account | **Not documented**: escalate |

Use this file only for an app that already runs Hydra with Firebase Remote Config and wants to add gamification.

## Requirements
- `@capillarytech/react-native-hydra-lib` **`{{sdk_version}}` or later** (the source's minimum, "current Beta version"); installed with the npm `beta` tag.
- An existing Hydra React Native integration using Firebase Remote Config (not documented; see the gap above).
- npm or Yarn.

> ⚠️ Gap: no minimum React Native, Node, iOS, Android, Xcode or Gradle versions, and no Firebase package versions. Ask a Capillary engineer.

## Prerequisites
See `_shared/prerequisites.md` for the common exchange and `_shared/firebase-setup.md` for Firebase project and Remote Config basics. For this mode:
- If the app already uses the RN HydraLib package, no additional package integration is needed for gamification.
- Edit access to the app's Firebase Remote Config (step 2).
- **Capillary gives client:** `{{gamification_region}}`, `{{gamification_key}}`, `{{gamification_base_url}}`, `{{org_id}}`.
- The Capillary B2B short-lived token (Loyalty View) and entry-point IDs `{{banner_id}}`, `{{embed_id}}`, `{{loyalty_id}}` for the views used.

## Steps

### 1. Update the package
Update to the latest publicly available HydraLib version (minimum `{{sdk_version}}`). Gamification is part of the package.

```bash
npm install @capillarytech/react-native-hydra-lib@beta
```

```bash
yarn add @capillarytech/react-native-hydra-lib@beta
```

### 2. Add the gamification keys to Firebase Remote Config
```text
hydra_gamification_region
hydra_gamification_key
hydra_gamification_base_url
hydra_org_id
```

| Remote Config key | Value | Mandatory |
|---|---|---|
| `hydra_gamification_region` | `{{gamification_region}}` | Not stated |
| `hydra_gamification_key` | `{{gamification_key}}` | Yes |
| `hydra_gamification_base_url` | `{{gamification_base_url}}` | Yes |
| `hydra_org_id` | `{{org_id}}` | Not stated |

**Important:** the key and URL values are mandatory; HydraGamification stays disabled if either is missing.

> ⚠️ Gap: value formats (e.g. allowed region values and case) and whether region and org ID are mandatory aren't stated, and this guide makes the base URL mandatory while other platforms treat it as optional. Until a Capillary engineer confirms, set all four. Ask a Capillary engineer.

### 3. Report the current screen (required for campaigns)
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

> ⚠️ Gap: how to sign in for this mode, the JavaScript `import` lines (`Hydra`, `HydraNativeEventEmitter`, `Gamification…View`), which screen names to pass (`'home'` is an example), and how to report screens without `useFocusEffect` aren't documented. Ask a Capillary engineer.

### 4. Set the Capillary token (for Loyalty View)
Set the Capillary B2B short-lived token (replace `'token'` with it):

```javascript
Hydra.setCapToken('token');
```

## Modules

### Push
> ⚠️ Gap: not documented for React Native with Firebase. Ask a Capillary engineer.

### In-App
> ⚠️ Gap: not documented for React Native with Firebase. Ask a Capillary engineer.

### Inbox
> ⚠️ Gap: Inbox API and Inbox UI are not documented for React Native with Firebase. Ask a Capillary engineer.

### Visitor
> ⚠️ Gap: not documented for React Native with Firebase. Ask a Capillary engineer.

### Gamification
Floating Button, Popup and Bottom Sheet campaigns need only steps 1–4. The optional views and callbacks below use `BANNER_ID`, `EMBED_ID` and `LOYALTY_ID`, your entry-point IDs (`{{banner_id}}`, `{{embed_id}}`, `{{loyalty_id}}`); the source doesn't declare them, so declare them yourself.

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
Needs the token from step 4.

```jsx
<ScrollView style={styles.container}>
  <GamificationLoyaltyView
    loyaltyId={LOYALTY_ID}
    style={[styles.loyalty, { height: loyaltyHeight }]}
  />
</ScrollView>
```

> ⚠️ Gap: `embedHeight` and `loyaltyHeight` are used but never defined (p.5), so these snippets fail as-is. The docs don't say whether `addGamificationViewHeightChangedListener` also reports Embed / Loyalty heights or what initial height to use. Ask a Capillary engineer.

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

## Verification
- **Campaigns:** after sign-in, report a screen (step 3); a Floating Button, Popup or Bottom Sheet campaign for that screen should appear.
- **Banner View:** the height listener fires with your `BANNER_ID` and a height above 0.
- **Callbacks:** the listener snippets log `gamificationAnalyticsEvent:` / `gamificationDeeplink:` (their own `console.log`, not SDK lines).
- **Nothing appears:** check `hydra_gamification_key` and `hydra_gamification_base_url` both have values in Remote Config.

> ⚠️ Gap: no SDK-initialisation check, log lines, log-level settings or dashboard checks are documented for this mode. Ask a Capillary engineer.

## Known Issues

**Gamification never appears** → `hydra_gamification_key` or `hydra_gamification_base_url` missing in Remote Config (HydraGamification stays disabled) → set both (step 2).

**Floating Button / Popup / Bottom Sheet campaigns don't appear** → screen not reported, reported before sign-in, or reported without the delay → report after sign-in with the 500 ms delay (step 3).

**Loyalty View empty** → Capillary token not set → call `Hydra.setCapToken(...)` before showing the view (step 4).

## API Reference
Remote Config keys: see the table in step 2.

| API | Purpose |
|---|---|
| `Hydra.gamificationScreenAppeared(screenName)` | Report screen shown (after sign-in, 500 ms delay) |
| `Hydra.gamificationScreenDisappeared()` | Report screen gone |
| `Hydra.setCapToken(token)` | Set B2B short-lived token (Loyalty View) |
| `Hydra.track(eventName)` | Trigger a campaign on a custom event |
| `HydraNativeEventEmitter.getInstance()` | Emitter used to add / remove listeners |
| `.addGamificationViewHeightChangedListener((height, entryPointId) => …)` | Gamification view height changed; returns a subscription |
| `.addGamificationAnalyticsEventListener((name, payload) => …)` | Game events; returns a subscription |
| `.addGamificationDeeplinkListener((url) => …)` | Game click needs a deeplink redirect; returns a subscription |
| `.removeListener(subscription)` | Remove a listener |

| Component | Props |
|---|---|
| `GamificationBannerView` | `bannerId`, `style` |
| `GamificationEmbedView` | `embedId`, `style` |
| `GamificationLoyaltyView` | `loyaltyId`, `style` |
