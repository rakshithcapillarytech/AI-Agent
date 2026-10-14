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
A **gamification add-on** for apps already running the Hydra Android SDK with Firebase.

> ⚠️ Gap: the **core Android + Firebase integration is not documented**: dependencies and repository, `google-services` plugin and `google-services.json`, reading Remote Config, Firebase-mode init, sign-in/sign-out, custom events, push, In-App, Inbox. Don't fill these in from `android/direct.md` (setup without Firebase) or general knowledge. Ask a Capillary engineer.

| Module | Status in this mode |
|---|---|
| Gamification (screen tracking, callback, late Remote Config, Banner, Embedded, Loyalty, cap token) | Documented |
| Core, Push, In-App, Inbox, Visitor, multi-account | **Not documented** (push: one-line hint, Modules → Push) |

## Requirements
- SDK version: `{{sdk_version}}` (Beta) or later. Kotlin or Java.

> ⚠️ Gap: this guide says minimum `1.9.22-beta01` (pp.39, 50); the without-Firebase guide requires `1.9.22-beta02` (p.104). Ask a Capillary engineer.

> ⚠️ Gap: minSdk, compileSdk, AGP, Gradle and Kotlin versions aren't documented, nor the library providing `ProcessLifecycleOwner` / `DefaultLifecycleObserver`. Ask a Capillary engineer.

## Prerequisites
Common exchange: `_shared/prerequisites.md`. Firebase project and Remote Config setup: `_shared/firebase-setup.md`.

| Firebase Remote Config key | Value from Capillary | Required? |
|---|---|---|
| `hydra_gamification_key` | Gamification Key (write key) | Required |
| `hydra_gamification_region` | Gamification Region | Required |
| `hydra_gamification_base_url` | Gamification Base URL | Optional |

Also used: Account Id, Base URL, SSL Public Key, Org Id; the Capillary B2B short-lived token (step 6).

## Steps
### 1. Update to the latest Hydra Android SDK version
Use `{{sdk_version}}` (Beta) or later. HydraGamification is bundled within HydraCore; no extra framework integration.

> ⚠️ Gap: no dependency lines are given, and "bundled within HydraCore" (p.39) conflicts with the separate `com.capillary:hydra-gamification` / `hydra-gamification-ui` dependencies in the without-Firebase guide (p.103). Ask a Capillary engineer.

### 2. Add the Remote Config keys and pass them to `HydraConfig.Builder`
Add the three Remote Config keys (Prerequisites), then pass them during SDK initialisation (in `initializeHydraSDK()`, step 3).

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

Variables: `accountId` = `{{account_id}}`, `baseURL` = `{{base_url}}` (Hydra), `sslPublicKey` = `{{ssl_public_key}}`; `writeKey` = `{{gamification_key}}`, `region` = `{{gamification_region}}`, `baseUrl` = `{{gamification_base_url}}` (from the Remote Config keys). `baseURL` and `baseUrl` are different values.

> ⚠️ Gap: not documented: how to read Remote Config; where `accountId`, `baseURL`, `sslPublicKey` come from; whether `.orgId()` / `.debugLevel()` are needed. Ask a Capillary engineer.

> ⚠️ Gap: this guide initialises with `HydraAPI.initialize(context, hydraConfig)` (p.40); the without-Firebase guide uses `HydraAPI.instanceWithConfig(context, hydraConfig)` (p.105). Ask a Capillary engineer.

### 3. Wire `GamificationUIManager`
After Hydra initialisation, store it in the Application class. Wires the callback (`MyGamificationCallback`, Modules → Gamification) and enables automatic campaign rendering.

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

> ⚠️ Gap: where `initializeHydraSDK()` is called (vs steps 4–5) isn't documented. Ask a Capillary engineer.

### 4. Report the current screen
In `Application.onCreate()`:

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

**Important:** screen reporting is mandatory for screen-targeted campaigns. `onActivityDestroyed` cleanup is required to prevent memory leaks from attached entry-point views.

### 5. Handle the app foreground/background lifecycle
Enables freshness checks.

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

### 6. Set the Capillary token (required for Loyalty View)
Set the Capillary B2B short-lived token **before** the Loyalty View is rendered. Without a valid token, loyalty content may not be displayed.

```kotlin
val hydra = HydraAPI.getDefaultInstance(context)
hydra?.setCapToken(token)
```

```java
HydraAPI hydra = HydraAPI.getDefaultInstance(context);
if (hydra != null) {
    hydra.setCapToken(token);
}
```

### 7. Handle late initialisation via Remote Config
If the gamification keys arrive **after** Hydra is initialised, pass them with `updateRemoteConfig` (gamification then initialises lazily), then wire `GamificationUIManager` if not yet created.

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

Variables: `newOrgId` = `{{org_id}}`, `newAccountId` = `{{account_id}}`, `newBaseUrl` = `{{base_url}}`, `newSslKey` = `{{ssl_public_key}}`, `newCgWriteKey` / `cgRegion` / `newCgBaseUrl` = the three `hydra_gamification_*` values.

> ⚠️ Gap: how to detect late Remote Config values, and the type of `cgRegion`, aren't documented. Ask a Capillary engineer.

## Modules

### Push
> ⚠️ Gap: Android push setup is not documented. The only hint (p.112): push needs the `hydra-pushbase` and `hydra-firebase` modules plus Firebase dependencies and `google-services.json`, per a "standard integration guide" not in the knowledge base (no coordinates, manifest, permission or FCM token flow). Ask a Capillary engineer.

Firebase console side: `_shared/firebase-setup.md`.

### In-App
> ⚠️ Gap: not documented for Android in Firebase mode. Ask a Capillary engineer.

### Inbox
> ⚠️ Gap: Inbox API and Inbox UI aren't documented for Android in Firebase mode. Ask a Capillary engineer.

### Visitor
> ⚠️ Gap: the visitor flow isn't documented for Android in Firebase mode. Ask a Capillary engineer.

### Gamification
**Automatic** (no extra code after steps 1–5): Floating Button, Popup and Bottom Sheet campaigns.

**Gamification callback (optional)**, assigned in steps 3 and 7:

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

**Custom UI components (optional, in XML layouts).**
- **Banner View.** `android:id` must correspond to the **bannerId** configured in the campaign dashboard. Bound and rendered automatically by `GamificationUIManager` on `onScreenChanged`; no extra code.
  ```xml
  <com.capillary.hydra.gamification.ui.entrypoints.BannerView
      android:id="@+id/{{banner_id}}"
      android:layout_width="match_parent"
      android:layout_height="wrap_content" />
  ```
- **Embedded View.** Bound and rendered automatically on `onScreenChanged`, same as Banner; no extra code.
  ```xml
  <com.capillary.hydra.gamification.ui.entrypoints.EmbedWebView
      android:id="@+id/{{embed_id}}"
      android:layout_width="match_parent"
      android:layout_height="wrap_content" />
  ```
  > ⚠️ Gap: the docs disagree. This guide says the Embedded View's `android:id` must match the **bannerId** from the dashboard, "same pattern as Banner View" (p.49), yet its example ID is `rn_embed1`; and it says no binding code is needed (pp.49–50), while the without-Firebase guide requires `bindEmbedView()` (p.109). Ask a Capillary engineer.
- **Loyalty View.** `android:id` must match the **embedId** from the API response. Rendered automatically on `onScreenChanged`, provided `setCapToken()` was called (step 6).
  ```xml
  <com.capillary.hydra.gamification.ui.entrypoints.LoyaltyEmbedView
      android:id="@+id/{{loyalty_id}}"
      android:layout_width="match_parent"
      android:layout_height="match_parent" />
  ```
  > ⚠️ Gap: which API response returns the Loyalty `embedId` isn't documented. Ask a Capillary engineer.

## Verification
- `GamificationCallback`: `onInitSuccess()` / `onInitFailure(GamificationError)`; `onEntryPointsLoaded(...)` when entry points are ready.
- `updateRemoteConfig(...)` returns `true` on success.
- Expected: Floating Button, Bottom Sheet and Popup campaigns appear automatically; Banner, Embedded, Loyalty content if added.
- Checklist: required = steps 1–6 (base URL key optional, `onActivityDestroyed` included); optional = callback, Banner, Embedded, Loyalty views.

> ⚠️ Gap: no Logcat lines, `GamificationError` details or dashboard checks are documented. Ask a Capillary engineer.

## Known Issues
| Symptom | Cause | Fix |
|---|---|---|
| Memory leaks from entry-point views | `onActivityDestroyed` not forwarded | Call `gamificationUIManager?.onActivityDestroyed(activity)` (step 4) |
| Screen-targeted campaigns don't appear | Current screen not reported | Register the `onScreenChanged` callbacks (step 4) |
| Loyalty View empty | No valid token set before render | Call `setCapToken(token)` first (step 6) |
| Gamification keys arrive via Remote Config after Hydra is initialised | Hydra initialised before `hydra_gamification_*` values were available | Call `HydraAPI.updateRemoteConfig(...)`, then wire `GamificationUIManager` if null (step 7) |

## API Reference
| API | Purpose |
|---|---|
| `HydraConfig.Builder(context, accountId)` | `.baseURL()`, `.sslPublicKey()`, `.gamificationWriteKey()`, `.gamificationBaseUrl()`, `.gamificationRegion(GamificationRegion)`, `.build()` |
| `HydraAPI.initialize(context, config)` | Initialises the SDK (see step 2 gap) |
| `HydraAPI.getDefaultInstance(context)` | SDK instance (nullable) |
| `getGamificationManager()` | `GamificationFlowManager` (nullable) |
| `GamificationFlowManager.callback` / `setCallback(...)` | Sets the `GamificationCallback` |
| `GamificationUIManager(flowManager, context)` | `.onScreenChanged(activity, screenName)`, `.onActivityDestroyed(activity)`, `.onAppForegrounded()`, `.onAppBackgrounded()` |
| `setCapToken(token)` | Capillary B2B token for Loyalty View |
| `HydraAPI.updateRemoteConfig(orgId, accountId, baseURL, sslPublicKey, gamificationWriteKey, gamificationRegion, gamificationBaseUrl)` | Late Remote Config values; returns `Boolean` |
| `GamificationCallback` | `onInitSuccess()`, `onInitFailure(GamificationError)`, `onEntryPointsLoaded(List<EntryPointData>)`, `onCampaignOpened(campaignId)`, `onCampaignClosed(campaignId)`, `onAnalyticsEvent(eventName, data)` |
| Views (`com.capillary.hydra.gamification.ui.entrypoints`) | `BannerView`, `EmbedWebView`, `LoyaltyEmbedView` |
