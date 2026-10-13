---
platform: android
config_mode: firebase
sdk_package: com.capillary:hydra-core   # the source (p.39) only says gamification is "bundled within HydraCore"; it gives no Maven coordinates
sdk_version: 1.9.22-beta01             # "Minimum Required Version" for gamification (pp.39, 50)
modules_covered: [gamification]        # gamification add-on only
modules_missing: [core, push, inapp, inbox_api, inbox_ui, visitor, multi_account]   # the core Android + Firebase integration is NOT in the source
sources: ["Integration document _ Experience+ pp.38–51 (Experience+ Android: Gamification Android Integration Guide, Kotlin + Java)", "Integration document _ Experience+ p.112 (one sentence on push, at the end of the Android without-Firebase guide)"]
owner: TBD
last_verified: null
review_status: draft   # drafted from the source doc; not yet SME-verified
---
# Android (with Firebase)

## Coverage
**What the source is:** pp.38–51 are a **gamification add-on guide** for apps that **already integrate the Hydra Android SDK with Firebase**. The guide says that if you already use the Hydra Android SDK, "no additional framework integration is required": HydraGamification is bundled within HydraCore and is turned on through configuration (Firebase Remote Config keys `hydra_gamification_*`). It does **not** describe how to integrate Hydra with Firebase in the first place.

> ⚠️ Gap: the **core Android + Firebase integration is not documented anywhere in this knowledge base.** That covers the repository and Maven setup, Gradle dependencies, the `google-services` plugin and `google-services.json`, reading Firebase Remote Config, Firebase-mode SDK initialisation, sign-in, sign-out, custom events, push via FCM, in-app and inbox. Don't fill these in from `android/direct.md` (that's the setup *without* Firebase) or from general knowledge. Ask a Capillary engineer.

| Module | Status in this mode |
|---|---|
| Core (dependencies, `google-services.json`, Firebase-mode init, sign-in, sign-out, custom events) | **Not documented.** The source assumes it's already done. Only the gamification-related `HydraConfig.Builder` / `HydraAPI.initialize` code is shown (step 2). |
| Gamification (automatic campaigns, late Remote Config, callback, Banner, Embedded, Loyalty, screen tracking, cap token) | Documented (pp.39–51) |
| Push notifications (FCM) | **Not documented.** Only one sentence elsewhere in the source (see Modules → Push). |
| In-App messaging | Not documented |
| Inbox / Notification Center | Not documented |
| Visitor flow | Not documented |
| Multi-account | Not documented |

## Requirements
- SDK version: `{{sdk_version}}` (Beta) or later. The guide says to update to "the latest Hydra Android SDK version that includes HydraGamification support" (p.39, checklist p.50).
- Languages: the guide gives code for Kotlin and Java.
- An app that already runs the Hydra Android SDK with Firebase (see Coverage).

> ⚠️ Source doc correction: this guide gives the minimum version as `1.9.22-beta01` (pp.39, 50) vs `1.9.22-beta02` as the required version in the Android without-Firebase guide (pp.100–112). Confirm which build to use for Firebase mode. *Pending SME confirmation.*

> ⚠️ Gap: the source doesn't state the minimum Android API level (minSdk), compileSdk, AGP, Gradle or Kotlin versions. It also doesn't say which library provides `ProcessLifecycleOwner` / `DefaultLifecycleObserver` (step 5), or whether the Hydra SDK brings it in. Ask a Capillary engineer.

## Prerequisites
See `_shared/prerequisites.md` for the common exchange with Capillary, and `_shared/firebase-setup.md` for the Firebase project and Remote Config setup.

The Android guide has no prerequisites section of its own. Its code uses these values:
- **For gamification (Firebase Remote Config keys, p.39):**

  | Remote Config key | Value from Capillary | Required? |
  |---|---|---|
  | `hydra_gamification_key` | Gamification Key (write key) | Listed as Required in the checklist (p.50) |
  | `hydra_gamification_region` | Gamification Region (`IN`, `US` or `ME`; see `_shared/prerequisites.md`) | Listed as Required in the checklist (p.50) |
  | `hydra_gamification_base_url` | Gamification Base URL | Optional (checklist p.50) |

  Step 2 of the source prints this key as `hydra_gamification_base_url ()` with empty parentheses; the checklist (p.50) marks it "(Optional)". Key names and mandatory rules vary across platforms: see the per-platform table in `_shared/firebase-setup.md`.
- **Also passed to the SDK in the code:** Account Id, Base URL and SSL Public Key (step 2), and Org Id (step 7).
- **For the custom UI components (optional):** Banner, Embed and Loyalty entry-point IDs from the gamification campaign dashboard.
- **For the Loyalty View:** a Capillary B2B short-lived token from the client's backend (step 6).

## Steps
These steps come from the source in its order. They add gamification to an app that already has the core Hydra + Firebase integration (see the Coverage gap).

### 1. Update to the latest Hydra Android SDK version
Update the app to the latest Hydra Android SDK that includes HydraGamification support: `{{sdk_version}}` (Beta) or later. No separate gamification framework is needed, because HydraGamification is bundled within HydraCore (p.39).

> ⚠️ Gap: this source gives no dependency lines, Maven coordinates or repository for Firebase mode. Ask a Capillary engineer.

> ⚠️ Source doc correction: this guide says HydraGamification is "bundled within HydraCore" and "no additional framework integration is required" (p.39) vs the Android without-Firebase guide (pp.100–112), which adds separate optional `com.capillary:hydra-gamification` and `com.capillary:hydra-gamification-ui` dependencies. Confirm whether Firebase-mode apps need these modules. *Pending SME confirmation.*

### 2. Add the gamification configuration and pass it to `HydraConfig.Builder`
1. Add these Firebase Remote Config keys (how to add and publish a parameter: `_shared/firebase-setup.md`):
   - `hydra_gamification_key`
   - `hydra_gamification_region`
   - `hydra_gamification_base_url` (optional)
2. Configure Hydra with these values during SDK initialisation. This code goes inside the Application class's Hydra setup (the `initializeHydraSDK()` method in step 3).

Kotlin:

```kotlin
val hydraConfig = HydraConfig.Builder(applicationContext, accountId)
    .baseURL(baseURL)
    .sslPublicKey(sslPublicKey)
    .apply {
        if (writeKey.isNotEmpty()) {
            gamificationWriteKey(writeKey)
            if (baseUrl.isNotEmpty()) {
                gamificationBaseUrl(baseUrl)
            }
            if (region.isNotEmpty()) {
                gamificationRegion(GamificationRegion.valueOf(region.uppercase()))
            }
        }
    }
    .build()

HydraAPI.initialize(applicationContext, hydraConfig)
```

Java:

```java
HydraConfig.Builder builder = new HydraConfig.Builder(getApplicationContext(), accountId)
    .baseURL(baseURL)
    .sslPublicKey(sslPublicKey);

if (!writeKey.isEmpty()) {
    builder.gamificationWriteKey(writeKey);
    if (!baseUrl.isEmpty()) {
        builder.gamificationBaseUrl(baseUrl);
    }
    if (!region.isEmpty()) {
        builder.gamificationRegion(GamificationRegion.valueOf(region.toUpperCase()));
    }
}

HydraConfig hydraConfig = builder.build();
HydraAPI.initialize(getApplicationContext(), hydraConfig);
```

The variables in this code hold runtime values:

| Variable | Value | Where it comes from (per the source) |
|---|---|---|
| `accountId` | Account Id (`{{account_id}}`) | Not stated |
| `baseURL` | Hydra Base URL (`{{base_url}}`) | Not stated |
| `sslPublicKey` | SSL Public Key (`{{ssl_public_key}}`) | Not stated |
| `writeKey` | Gamification Key (`{{gamification_key}}`) | Remote Config `hydra_gamification_key` |
| `region` | Gamification Region (`{{gamification_region}}`) | Remote Config `hydra_gamification_region` |
| `baseUrl` | Gamification Base URL (`{{gamification_base_url}}`) | Remote Config `hydra_gamification_base_url` |

Notes:
- `baseURL` (the Hydra Base URL) and `baseUrl` (the gamification base URL) are **two different values** whose names differ only in letter case.
- The gamification settings are applied only when `writeKey` is non-empty. Within that, the base URL and region are each applied only when non-empty.
- The region string is upper-cased before `GamificationRegion.valueOf(...)`.

> ⚠️ Gap: the source doesn't show how the app reads these values from Firebase Remote Config (fetch, activate, defaults), or whether `accountId`, `baseURL` and `sslPublicKey` also come from Remote Config on Android. `_shared/firebase-setup.md` lists the core key names (`hydra_account_id` …), but those come from the Flutter guide and aren't confirmed for native Android. Ask a Capillary engineer.

> ⚠️ Gap: this snippet doesn't call `.orgId(...)` or `.debugLevel(...)`, although step 7 passes an `orgId`. The source doesn't say whether Firebase mode needs them. Ask a Capillary engineer.

> ⚠️ Source doc correction: this guide initialises with `HydraAPI.initialize(context, hydraConfig)` (p.40) vs `HydraAPI.instanceWithConfig(context, hydraConfig)` in the Android without-Firebase guide (pp.100–112). The source doesn't say whether they're the same call or which one Firebase mode should use. *Pending SME confirmation.*

### 3. Wire `GamificationUIManager`
After Hydra initialisation, create and store the `GamificationUIManager` in your Application class. This sets the gamification callback and enables automatic campaign rendering.

Kotlin:

```kotlin file=app/src/main/java/<your-package>/MyApplication.kt
class MyApplication : Application() {

    private var gamificationUIManager: GamificationUIManager? = null

    fun getGamificationUIManager(): GamificationUIManager? = gamificationUIManager

    private fun initializeHydraSDK() {
        // ... HydraConfig setup and HydraAPI.initialize() ...

        // Wire gamification UI manager if gamification is enabled
        HydraAPI.getDefaultInstance(applicationContext)?.getGamificationManager()
            ?.let { flowManager ->
                flowManager.callback = MyGamificationCallback()
                gamificationUIManager = GamificationUIManager(flowManager, applicationContext)
            }
    }
}
```

Java:

```java file=app/src/main/java/<your-package>/MyApplication.java
public class MyApplication extends Application {

    private GamificationUIManager gamificationUIManager;

    public GamificationUIManager getGamificationUIManager() {
        return gamificationUIManager;
    }

    private void initializeHydraSDK() {
        // ... HydraConfig setup and HydraAPI.initialize() ...

        // Wire gamification UI manager if gamification is enabled
        HydraAPI hydra = HydraAPI.getDefaultInstance(getApplicationContext());
        if (hydra != null) {
            GamificationFlowManager flowManager = hydra.getGamificationManager();
            if (flowManager != null) {
                flowManager.setCallback(new MyGamificationCallback());
                gamificationUIManager = new GamificationUIManager(flowManager, getApplicationContext());
            }
        }
    }
}
```

- `MyGamificationCallback` is the class from the source's "Optional: Gamification Callback" section (Modules → Gamification). Define it before compiling this code.
- The source's comment says the UI manager is wired "if gamification is enabled". The code null-checks `getGamificationManager()` before creating it.

> ⚠️ Gap: the source doesn't show where `initializeHydraSDK()` is called from, or how it is ordered relative to the `onCreate()` code in steps 4–5. Ask a Capillary engineer.

### 4. Report the current screen
HydraGamification uses screen information to decide when and where campaigns are displayed. Register `ActivityLifecycleCallbacks` in `Application.onCreate()` so every Activity reports screen changes automatically.

Kotlin:

```kotlin
override fun onCreate() {
    super.onCreate()

    registerActivityLifecycleCallbacks(object : ActivityLifecycleCallbacks {
        override fun onActivityCreated(activity: Activity, savedInstanceState: Bundle?) {}
        override fun onActivityStarted(activity: Activity) {}

        override fun onActivityResumed(activity: Activity) {
            gamificationUIManager?.onScreenChanged(activity, activity.javaClass.simpleName)
        }

        override fun onActivityPaused(activity: Activity) {}
        override fun onActivityStopped(activity: Activity) {}
        override fun onActivitySaveInstanceState(activity: Activity, outState: Bundle) {}

        override fun onActivityDestroyed(activity: Activity) {
            gamificationUIManager?.onActivityDestroyed(activity)
        }
    })

    // ... rest of initialization
}
```

Java:

```java
@Override
public void onCreate() {
    super.onCreate();

    registerActivityLifecycleCallbacks(new ActivityLifecycleCallbacks() {
        @Override public void onActivityCreated(Activity activity, Bundle savedInstanceState) {}
        @Override public void onActivityStarted(Activity activity) {}

        @Override
        public void onActivityResumed(Activity activity) {
            if (gamificationUIManager != null) {
                gamificationUIManager.onScreenChanged(activity, activity.getClass().getSimpleName());
            }
        }

        @Override public void onActivityPaused(Activity activity) {}
        @Override public void onActivityStopped(Activity activity) {}
        @Override public void onActivitySaveInstanceState(Activity activity, Bundle outState) {}

        @Override
        public void onActivityDestroyed(Activity activity) {
            if (gamificationUIManager != null) {
                gamificationUIManager.onActivityDestroyed(activity);
            }
        }
    });

    // ... rest of initialization
}
```

**Important** (p.44):
- Screen reporting is **mandatory** for screen-targeted campaigns.
- Campaign visibility and eligibility depend on the currently reported screen.
- The `onActivityDestroyed` cleanup is **required** to prevent memory leaks from attached entry-point views.

### 5. Handle the app foreground/background lifecycle
Register a `ProcessLifecycleOwner` observer that tells gamification when the app moves to the foreground or background. This enables freshness checks. The snippet uses the `gamificationUIManager` field from step 3.

Kotlin:

```kotlin
ProcessLifecycleOwner.get().lifecycle.addObserver(object : DefaultLifecycleObserver {
    override fun onStart(owner: LifecycleOwner) {
        gamificationUIManager?.onAppForegrounded()
    }

    override fun onStop(owner: LifecycleOwner) {
        gamificationUIManager?.onAppBackgrounded()
    }
})
```

Java:

```java
ProcessLifecycleOwner.get().getLifecycle().addObserver(new DefaultLifecycleObserver() {
    @Override
    public void onStart(@NonNull LifecycleOwner owner) {
        if (gamificationUIManager != null) {
            gamificationUIManager.onAppForegrounded();
        }
    }

    @Override
    public void onStop(@NonNull LifecycleOwner owner) {
        if (gamificationUIManager != null) {
            gamificationUIManager.onAppBackgrounded();
        }
    }
});
```

> ⚠️ Gap: the source doesn't say exactly where to register this observer (for example in `Application.onCreate()`). Ask a Capillary engineer.

### 6. Set the Capillary token (required for Loyalty View)
Set the Capillary B2B short-lived token **before** a Loyalty View is displayed (the client's backend provides it; see `_shared/prerequisites.md`).

Kotlin:

```kotlin
val hydra = HydraAPI.getDefaultInstance(context)
hydra?.setCapToken(token)
```

Java:

```java
HydraAPI hydra = HydraAPI.getDefaultInstance(context);
if (hydra != null) {
    hydra.setCapToken(token);
}
```

**Important** (p.45):
- The Capillary token must be set before the Loyalty View is rendered.
- Without a valid token, loyalty content may not be displayed.

### 7. Handle late initialisation via Remote Config
If the gamification keys arrive from Firebase Remote Config **after** Hydra is already initialised, pass them with `HydraAPI.updateRemoteConfig(...)`. The SDK then initialises gamification lazily. After `updateRemoteConfig` succeeds, wire the `GamificationUIManager` (step 3) if it hasn't been created yet.

Kotlin:

```kotlin
val success = HydraAPI.updateRemoteConfig(
    orgId = newOrgId,
    accountId = newAccountId,
    baseURL = newBaseUrl,
    sslPublicKey = newSslKey,
    gamificationWriteKey = newCgWriteKey.takeIf { it.isNotEmpty() },
    gamificationRegion = cgRegion,
    gamificationBaseUrl = newCgBaseUrl
)

if (success && gamificationUIManager == null) {
    HydraAPI.getDefaultInstance(applicationContext)
        ?.getGamificationManager()
        ?.let { flowManager ->
            flowManager.callback = MyGamificationCallback()
            gamificationUIManager = GamificationUIManager(flowManager, applicationContext)
        }
}
```

Java:

```java
boolean success = HydraAPI.updateRemoteConfig(
    newOrgId,
    newAccountId,
    newBaseUrl,
    newSslKey,
    newCgWriteKey.isEmpty() ? null : newCgWriteKey,
    cgRegion,
    newCgBaseUrl
);

if (success && gamificationUIManager == null) {
    HydraAPI hydra = HydraAPI.getDefaultInstance(getApplicationContext());
    if (hydra != null) {
        GamificationFlowManager flowManager = hydra.getGamificationManager();
        if (flowManager != null) {
            flowManager.setCallback(new MyGamificationCallback());
            gamificationUIManager = new GamificationUIManager(flowManager, getApplicationContext());
        }
    }
}
```

| Argument (variable) | Value |
|---|---|
| `orgId` (`newOrgId`) | Org Id (`{{org_id}}`) |
| `accountId` (`newAccountId`) | Account Id (`{{account_id}}`) |
| `baseURL` (`newBaseUrl`) | Hydra Base URL (`{{base_url}}`) |
| `sslPublicKey` (`newSslKey`) | SSL Public Key (`{{ssl_public_key}}`) |
| `gamificationWriteKey` (`newCgWriteKey`) | Gamification Key (`hydra_gamification_key`). The code passes `null` when it's empty. |
| `gamificationRegion` (`cgRegion`) | Gamification Region (`hydra_gamification_region`) |
| `gamificationBaseUrl` (`newCgBaseUrl`) | Gamification Base URL (`hydra_gamification_base_url`) |

> ⚠️ Gap: the source doesn't show how the app detects that Remote Config values arrived late (which Firebase listener or callback to use), the type of `cgRegion` (in step 2 the region is converted with `GamificationRegion.valueOf(...)`), or which arguments may be null. Ask a Capillary engineer.

## Modules

### Push
**Not documented in this source.** The only push guidance in the knowledge base is one sentence at the end of the Android without-Firebase guide (Integration doc p.112, also quoted in `android/direct.md`):

> "To add push notification support later, include the hydra-pushbase, hydra-firebase modules along with Firebase dependencies and google-services.json, and follow the standard integration guide."

> ⚠️ Gap: that "standard integration guide" isn't in the knowledge base yet. Nothing documents the Gradle coordinates for `hydra-pushbase` / `hydra-firebase`, the Firebase dependencies, the `google-services` plugin, where `google-services.json` goes, the manifest entries, notification permission, the FCM token flow or the notification icon and colour. Ask a Capillary engineer.

For the Firebase console side (creating the project, registering the app, downloading `google-services.json`, enabling Cloud Messaging), see `_shared/firebase-setup.md`.

### In-App
> ⚠️ Gap: not documented for Android in Firebase mode. Ask a Capillary engineer.

### Inbox
> ⚠️ Gap: Inbox API and Inbox UI (Notification Center) aren't documented for Android in Firebase mode. Ask a Capillary engineer.

### Visitor
> ⚠️ Gap: the visitor (anonymous) flow isn't documented for Android in Firebase mode. Ask a Capillary engineer.

### Gamification
**Automatic experiences.** Once configured (steps 1–5), Hydra handles these campaign types automatically, with no additional implementation. Hydra evaluates campaign eligibility and displays content when applicable (p.47):
- Floating Button campaigns
- Popup campaigns
- Bottom Sheet campaigns

**Gamification callback (optional).** Implement `GamificationCallback` to receive gamification lifecycle events. Steps 3 and 7 assign it to the flow manager.

Kotlin:

```kotlin
class MyGamificationCallback : GamificationCallback {

    override fun onInitSuccess() {
        // Gamification initialized successfully
    }

    override fun onInitFailure(error: GamificationError) {
        // Handle initialization failure
    }

    override fun onEntryPointsLoaded(entryPoints: List<EntryPointData>) {
        // Entry points are ready
    }

    override fun onCampaignOpened(campaignId: String) {
        // A campaign was opened
    }

    override fun onCampaignClosed(campaignId: String) {
        // A campaign was closed
    }

    override fun onAnalyticsEvent(eventName: String, data: Map<String, Any?>) {
        // Analytics event received
    }
}
```

Java:

```java
public class MyGamificationCallback implements GamificationCallback {

    @Override
    public void onInitSuccess() {
        // Gamification initialized successfully
    }

    @Override
    public void onInitFailure(@NonNull GamificationError error) {
        // Handle initialization failure
    }

    @Override
    public void onEntryPointsLoaded(@NonNull List<EntryPointData> entryPoints) {
        // Entry points are ready
    }

    @Override
    public void onCampaignOpened(@NonNull String campaignId) {
        // A campaign was opened
    }

    @Override
    public void onCampaignClosed(@NonNull String campaignId) {
        // A campaign was closed
    }

    @Override
    public void onAnalyticsEvent(@NonNull String eventName, @NonNull Map<String, ?> data) {
        // Analytics event received
    }
}
```

**Custom UI components (optional).** These show gamification content directly inside the app's screens. Add them to XML layouts.

- **Banner View.** The `android:id` must correspond to the **bannerId** configured in the campaign dashboard. `GamificationUIManager` binds and renders Banner views automatically when `onScreenChanged` is called, so no extra code is needed.
  ```xml
  <com.capillary.hydra.gamification.ui.entrypoints.BannerView
      android:id="@+id/{{banner_id}}"
      android:layout_width="match_parent"
      android:layout_height="wrap_content" />
  ```
- **Embedded View.** `GamificationUIManager` binds and renders Embedded views automatically when `onScreenChanged` is called, the same way as Banner views. No extra code is needed.
  ```xml
  <com.capillary.hydra.gamification.ui.entrypoints.EmbedWebView
      android:id="@+id/{{embed_id}}"
      android:layout_width="match_parent"
      android:layout_height="wrap_content" />
  ```
  > ⚠️ Source doc correction: the source says the Embedded View's `android:id` "must correspond to the bannerId configured in the campaign dashboard, same pattern as Banner View" (p.49) vs the embed ID being the likely intent. The source's own example ID is `rn_embed1`, and the Flutter and React Native guides key Embed views by `embedId`. *Pending SME confirmation.*

  > ⚠️ Source doc correction: this guide says Embedded views are bound automatically with no additional code (pp.49–50) vs the Android without-Firebase guide (pp.100–112), which says "Embed views require explicit binding via bindEmbedView()". Confirm whether Firebase-mode apps need `bindEmbedView`. *Pending SME confirmation.*
- **Loyalty View.** The `android:id` must match the **embedId** from the API response. `GamificationUIManager` renders Loyalty views automatically when `onScreenChanged` is called, **provided the Capillary token has been set with `setCapToken()`** (step 6).
  ```xml
  <com.capillary.hydra.gamification.ui.entrypoints.LoyaltyEmbedView
      android:id="@+id/{{loyalty_id}}"
      android:layout_width="match_parent"
      android:layout_height="match_parent" />
  ```
  > ⚠️ Gap: the source doesn't say which API response returns the Loyalty `embedId`, or how the client obtains it. Ask a Capillary engineer.

## Verification
- **Gamification initialisation:** implement `GamificationCallback` (Modules → Gamification). `onInitSuccess()` is called when gamification initialises successfully. `onInitFailure(error: GamificationError)` is called when it fails. `onEntryPointsLoaded(entryPoints)` means the entry points are ready.
- **Late Remote Config:** `HydraAPI.updateRemoteConfig(...)` returns `true` on success (step 7).
- **Result** (p.51): after the required steps, Floating Button, Bottom Sheet and Popup campaigns become available in the app automatically. If you added the optional UI components, Banner, Embedded and Loyalty content can also appear in your screens.

**Integration checklist** (from the source, pp.50–51).

Required:
- Update to the latest Hydra Android SDK version (`{{sdk_version}}` or later).
- Add `hydra_gamification_key` to Firebase Remote Config.
- Add `hydra_gamification_region` to Firebase Remote Config.
- Add `hydra_gamification_base_url` to Firebase Remote Config (optional).
- Wire `GamificationUIManager` in your Application class after SDK initialisation.
- Register `ActivityLifecycleCallbacks` to report screen names via `onScreenChanged`.
- Register the `ProcessLifecycleOwner` observer for `onAppForegrounded` / `onAppBackgrounded`.
- Call `onActivityDestroyed` in the lifecycle callbacks for cleanup.
- Set the Capillary token with `setCapToken(token)` (required for Loyalty View).

Optional:
- Implement `GamificationCallback` for lifecycle events.
- Add Banner View.
- Add Embedded View.
- Add Loyalty View.

> ⚠️ Gap: there's no formal verification procedure. The source documents no Logcat lines, no way to confirm that the core SDK initialised in Firebase mode or read Remote Config, no fields or codes for `GamificationError`, and no dashboard checks. Ask a Capillary engineer.

## Known Issues

**Memory leaks from attached entry-point views**
- Cause: `onActivityDestroyed` isn't forwarded to `GamificationUIManager`.
- Fix: call `gamificationUIManager?.onActivityDestroyed(activity)` in `onActivityDestroyed` (step 4).

*From the source doc (p.44).*

**Screen-targeted campaigns don't appear**
- Cause: the current screen isn't reported. Campaign visibility and eligibility depend on the currently reported screen, and screen reporting is mandatory for screen-targeted campaigns.
- Fix: register the `ActivityLifecycleCallbacks` that call `onScreenChanged` (step 4).

*From the source doc (p.44).*

**Loyalty View shows no content**
- Cause: no valid Capillary token was set before the Loyalty View rendered.
- Fix: call `setCapToken(token)` before the Loyalty View is rendered (step 6).

*From the source doc (pp.45, 50).*

**Gamification keys arrive via Remote Config after Hydra is already initialised**
- Cause: Hydra was initialised before the `hydra_gamification_*` values were available.
- Fix: pass the keys with `HydraAPI.updateRemoteConfig(...)`. If it returns `true` and `gamificationUIManager` is still null, wire the `GamificationUIManager` (step 7).

*From the source doc (pp.45–46).*

## API Reference
| API | Purpose |
|---|---|
| `HydraConfig.Builder(context, accountId)` | Builds the SDK config. Methods used in this guide: `.baseURL()`, `.sslPublicKey()`, `.gamificationWriteKey()`, `.gamificationBaseUrl()`, `.gamificationRegion(GamificationRegion)`, `.build()` |
| `GamificationRegion.valueOf(String)` | Converts the upper-cased region string to the enum (values: see `_shared/prerequisites.md`) |
| `HydraAPI.initialize(context, config)` | Initialises the SDK (see the step 2 correction about `instanceWithConfig`) |
| `HydraAPI.getDefaultInstance(context)` | Returns the SDK instance (nullable) |
| `getGamificationManager()` | Returns the `GamificationFlowManager` (nullable; the source's code null-checks it) |
| `GamificationFlowManager.callback` (Kotlin) / `setCallback(GamificationCallback)` (Java) | Sets the gamification callback |
| `GamificationUIManager(flowManager, context)` | Methods: `.onScreenChanged(activity, screenName)`, `.onActivityDestroyed(activity)`, `.onAppForegrounded()`, `.onAppBackgrounded()` |
| `setCapToken(token)` | Sets the Capillary B2B short-lived token for Loyalty View |
| `HydraAPI.updateRemoteConfig(orgId, accountId, baseURL, sslPublicKey, gamificationWriteKey, gamificationRegion, gamificationBaseUrl)` | Passes late-arriving Remote Config values. Returns `Boolean` (success). |
| `GamificationCallback` | `onInitSuccess()`, `onInitFailure(GamificationError)`, `onEntryPointsLoaded(List<EntryPointData>)`, `onCampaignOpened(campaignId)`, `onCampaignClosed(campaignId)`, `onAnalyticsEvent(eventName, data)` |
| Views | `com.capillary.hydra.gamification.ui.entrypoints.BannerView`, `EmbedWebView`, `LoyaltyEmbedView` |
| Remote Config keys | `hydra_gamification_key`, `hydra_gamification_region`, `hydra_gamification_base_url` (optional) |
