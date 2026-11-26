---
updatedAt: 2026-11-23T06:02:22.000Z
agentTools:
  projectIndex: https://docs.capillarytech.com/llms.txt
---

# Configure Gamification (Experience+)

Add Capillary's Experience+ gamification campaigns and views to your Android app.

HydraCore bundles **HydraGamification**, which lets you deliver Experience+ campaigns (floating buttons, popups, and bottom sheets) and embed optional gamification surfaces (banners, embedded views, and loyalty views) in your Android app. This guide covers Kotlin and Java.

<Callout icon="📘" theme="info">
  ### SDK version

  Minimum SDK version: `1.10.6`
</Callout>

## How it works

Once gamification is configured, Capillary renders these surfaces automatically:

* **Floating button, popup, and bottom sheet campaigns**: appear automatically on any screen you report, based on campaign targeting rules configured in the Gamification dashboard. No additional implementation is required, Hydra automatically evaluates campaign eligibility and displays content when applicable.
* **Banner, embedded, and loyalty views**: optional views you place in your own XML layout, identified by an entry-point ID.

## Choose your configuration path

There are two ways to set up gamification, depending on how your app is already configured:

* **[Option A: Using Firebase Remote Config](#option-a-using-firebase-remote-config)** — your app already uses Firebase Remote Config for Hydra SDK setup.
* **[Option B: Without Firebase Remote Config](#option-b-without-firebase-remote-config)** — your app is not using Firebase Remote Config, and gets its configuration values directly from the Capillary team.

Follow only the section that matches your setup. The two paths differ in dependencies, initialization, and one UI component's binding behavior.

***

## Option A: Using Firebase Remote Config

### Dependencies

If you're already using the Hydra Android SDK, no additional dependency is required. HydraGamification is bundled within HydraCore and is enabled through configuration alone.

### Configuration

Add these keys to your Firebase Remote Config:

| Key                           | Required  | Description                                     |
| ----------------------------- | --------- | ----------------------------------------------- |
| `hydra_gamification_key`      | Mandatory | Gamification write key for your account.        |
| `hydra_gamification_region`   | Mandatory | Region for the gamification service.            |
| `hydra_gamification_base_url` | Optional  | Override base URL for the gamification service. |

Fetch these values from Remote Config at runtime, then apply them conditionally since Remote Config values may not have loaded yet:

**Kotlin:**

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

**Java:**

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

Region arrives from Remote Config as a plain string and is matched case-insensitively: `GamificationRegion.valueOf(region.uppercase())` accepts `"in"`, `"IN"`, `"In"`, and so on, as long as it matches an enum member name once uppercased.

### Late initialization

If gamification keys arrive via Firebase Remote Config *after* Hydra is already initialized, use `updateRemoteConfig`. The SDK lazily initializes gamification internally once the call succeeds.

**Kotlin:**

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

**Java:**

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

### Wiring the UI manager

`GamificationUIManager` drives screen reporting and view rendering. Create and store it in your `Application` class, right after SDK initialization, and assign your `GamificationCallback` implementation (if you have one) at the same time:

**Kotlin:**

```kotlin
class MyApplication : Application() {

    var gamificationUIManager: GamificationUIManager? = null

    private fun initializeHydraSDK() {
        // ... HydraConfig setup and HydraAPI.initialize() ...

        HydraAPI.getDefaultInstance(applicationContext)?.getGamificationManager()
            ?.let { flowManager ->
                flowManager.callback = MyGamificationCallback()
                gamificationUIManager = GamificationUIManager(flowManager, applicationContext)
            }
    }
}
```

**Java:**

```java
public class MyApplication extends Application {

    private GamificationUIManager gamificationUIManager;

    private void initializeHydraSDK() {
        // ... HydraConfig setup and HydraAPI.initialize() ...

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

### Reporting screens

Register `ActivityLifecycleCallbacks` in your `Application.onCreate()` to report screen changes for every activity:

**Kotlin:**

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

**Java:**

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

<Callout icon="📘" theme="info">
  ### Note

  - Screen reporting is mandatory for screen-targeted campaigns. Campaign visibility and eligibility depend on the currently reported screen.
  - Calling `onActivityDestroyed` is required to prevent memory leaks from attached entry point views.
</Callout>

### Foreground and background lifecycle

Register a `ProcessLifecycleOwner` observer so gamification knows when the app moves to the foreground or background. This enables freshness checks.

**Kotlin:**

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

**Java:**

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

### Optional: gamification callback

Implement `GamificationCallback` to receive raw lifecycle and analytics events without any UI:

**Kotlin:**

```kotlin
class MyGamificationCallback : GamificationCallback {
    override fun onInitSuccess() { }
    override fun onInitFailure(error: GamificationError) { }
    override fun onEntryPointsLoaded(entryPoints: List<EntryPointData>) { }
    override fun onCampaignOpened(campaignId: String) { }
    override fun onCampaignClosed(campaignId: String) { }
    override fun onAnalyticsEvent(eventName: String, data: Map<String, Any?>) { }
}
```

**Java:**

```java
public class MyGamificationCallback implements GamificationCallback {
    @Override
    public void onInitSuccess() { }
    @Override
    public void onInitFailure(@NonNull GamificationError error) { }
    @Override
    public void onEntryPointsLoaded(@NonNull List<EntryPointData> entryPoints) { }
    @Override
    public void onCampaignOpened(@NonNull String campaignId) { }
    @Override
    public void onCampaignClosed(@NonNull String campaignId) { }
    @Override
    public void onAnalyticsEvent(@NonNull String eventName, @NonNull Map<String, ?> data) { }
}
```

<Callout icon="✏️" theme="default">
  ### **TBD — confirm with dev:** the fields of `GamificationError` and `EntryPointData` aren't defined anywhere in the source guide. Get their shape from engineering before documenting them in detail here.
</Callout>

### Setting the B2B token

The loyalty view requires a short-lived Capillary B2B token. Set it before the view renders, or its content won't display.

**Kotlin:**

```kotlin
val hydra = HydraAPI.getDefaultInstance(context)
hydra?.setCapToken(token)
```

**Java:**

```java
HydraAPI hydra = HydraAPI.getDefaultInstance(context);
if (hydra != null) {
    hydra.setCapToken(token);
}
```

<Callout icon="📘" theme="info">
  ### Note

  The Capillary token must be set before rendering the loyalty view. Failure to provide a valid token may result in loyalty content not being displayed.
</Callout>

### Embeddable views

Add each view to your XML layout. The `android:id` must correspond to the ID configured in the campaign dashboard (for the loyalty view, the `embedId` from the API response).

```xml
<com.capillarytech.hydra.gamification.ui.entrypoints.BannerView
    android:id="@+id/banner110"
    android:layout_width="match_parent"
    android:layout_height="wrap_content" />

<com.capillarytech.hydra.gamification.ui.entrypoints.EmbedWebView
    android:id="@+id/rn_embed1"
    android:layout_width="match_parent"
    android:layout_height="wrap_content" />

<com.capillarytech.hydra.gamification.ui.entrypoints.LoyaltyEmbedView
    android:id="@+id/embedLoyalty1"
    android:layout_width="match_parent"
    android:layout_height="match_parent" />
```

All three views, banner, embedded, and loyalty, are automatically bound and rendered by `GamificationUIManager` once `onScreenChanged` is called. No additional code is needed. Ensure `setCapToken(...)` has been called before the screen reports for the loyalty view to display.

### Option A checklist

**Required:**

* Update to the minimum required Hydra Android SDK version.
* Add `hydra_gamification_key` to Firebase Remote Config.
* Add `hydra_gamification_region` to Firebase Remote Config.
* Add `hydra_gamification_base_url` to Firebase Remote Config (optional).
* Wire `GamificationUIManager` in your `Application` class after SDK initialization.
* Register `ActivityLifecycleCallbacks` to report screen names via `onScreenChanged`.
* Register a `ProcessLifecycleOwner` observer for `onAppForegrounded` / `onAppBackgrounded`.
* Call `onActivityDestroyed` in lifecycle callbacks for cleanup.
* Set the Capillary token using `setCapToken(token)` (required for the loyalty view).

**Optional:**

* Implement `GamificationCallback` for lifecycle events.
* Add a banner view.
* Add an embedded view.
* Add a loyalty view.

**Result:** After completing the required steps, floating button, bottom sheet, and popup campaigns become automatically available in your app. If you also add the optional UI components, banner, embedded, and loyalty experiences can be displayed directly within your app screens.

***

## Option B: Without Firebase Remote Config

### Prerequisites

Before you get started, register your app with the Capillary team. Provide the **application ID (package name)** for your Android app.

The Capillary app team will register the app and provide you with:

* Account Id
* Base URL
* SSL Public Key
* Org Id
* Gamification Key
* Gamification Region
* Gamification URL (Optional)

You'll also need access to this GitHub repository from the Capillary access team:

* <https://github.com/Capillary/hydra-sdk-android-maven>

### Installation

#### Access to the Hydra SDK library

The Hydra SDK is hosted in a private GitHub Maven repository. You need:

* A GitHub username and Personal Access Token (PAT) with `read:packages` scope.
* Access granted to the `Capillary/hydra-sdk-android-maven` repository.

Create a `github.properties` file at the project root (same level as `settings.gradle`):

```properties
username=YOUR_GITHUB_USERNAME
token=YOUR_GITHUB_PAT
```

Add it to `.gitignore`:

```
github.properties
```

#### Add the GitHub Packages Maven repository

Add this to your `settings.gradle`, inside `dependencyResolutionManagement.repositories`:

**Groovy DSL (**`settings.gradle`**):**

```groovy
dependencyResolutionManagement {
    repositoriesMode.set(RepositoriesMode.FAIL_ON_PROJECT_REPOS)
    repositories {
        google()
        mavenCentral()
        maven {
            def propsFile = file('github.properties')
            def props = new Properties()
            props.load(new FileInputStream(propsFile))

            name "GitHubPackages"
            url = uri("https://maven.pkg.github.com/Capillary/hydra-sdk-android-maven")
            credentials {
                username = props['username']
                password = props['token']
            }
        }
    }
}
```

**Kotlin DSL (**`settings.gradle.kts`**):**

```kotlin
dependencyResolutionManagement {
    repositoriesMode.set(RepositoriesMode.FAIL_ON_PROJECT_REPOS)
    repositories {
        google()
        mavenCentral()
        maven {
            val propsFile = file("github.properties")
            val props = java.util.Properties().apply { load(propsFile.inputStream()) }

            name = "GitHubPackages"
            url = uri("https://maven.pkg.github.com/Capillary/hydra-sdk-android-maven")
            credentials {
                username = props["username"] as String
                password = props["token"] as String
            }
        }
    }
}
```

#### Add dependencies

Add the Hydra SDK dependencies to `app/build.gradle`.

<Callout icon="⚠️" theme="warn">
  ### Do **not** add the `com.google.gms.google-services` plugin. Do **not** add Firebase dependencies or `google-services.json`.
</Callout>

**Groovy DSL:**

```groovy
dependencies {
    // Hydra Core (required)
    implementation "com.capillarytech:hydra-core:1.10.6"

    // In-app messaging (optional)
    implementation "com.capillarytech:hydra-inapp:1.10.6"

    // Inbox / Notification Center (optional)
    implementation "com.capillarytech:hydra-inbox-core:1.10.6"
    implementation "com.capillarytech:hydra-inbox-ui:1.10.6"

    // Gamification (optional)
    implementation "com.capillarytech:hydra-gamification:1.10.6"
    implementation "com.capillarytech:hydra-gamification-ui:1.10.6"
}
```

**Kotlin DSL:**

```kotlin
dependencies {
    // Hydra Core (required)
    implementation("com.capillarytech:hydra-core:1.10.6")

    // In-app messaging (optional)
    implementation("com.capillarytech:hydra-inapp:1.10.6")

    // Inbox / Notification Center (optional)
    implementation("com.capillarytech:hydra-inbox-core:1.10.6")
    implementation("com.capillarytech:hydra-inbox-ui:1.10.6")

    // Gamification (optional)
    implementation("com.capillarytech:hydra-gamification:1.10.6")
    implementation("com.capillarytech:hydra-gamification-ui:1.10.6")
}
```

### Configuration

Get these values directly from the Capillary team when your app is registered: Gamification Key, Gamification Region, Gamification URL (Optional), along with your account ID, base URL, SSL public key, and org ID. Pass them as literal values, including the region as an actual enum member rather than a string.

Initialize the Hydra SDK in your `Application.onCreate()` method:

**Kotlin:**

```kotlin
val hydraConfig = HydraConfig.Builder(applicationContext, accountId = accountId)
    .orgId(orgId)
    .baseURL(baseUrl)
    .sslPublicKey(sslKey)
    .debugLevel(LogType.DEBUG)
    .gamificationWriteKey(gamificationWriteKey)
    .gamificationRegion(gamificationRegion)   // GamificationRegion.IN, .US, or .ME
    .gamificationBaseUrl(gamificationBaseUrl) // Optional
    .build()

HydraAPI.instanceWithConfig(applicationContext, hydraConfig)
```

**Java:**

```java
HydraConfig hydraConfig = new HydraConfig.Builder(getApplicationContext(), accountId)
    .orgId(orgId)
    .baseURL(baseUrl)
    .sslPublicKey(sslKey)
    .debugLevel(LogType.DEBUG)
    .gamificationWriteKey(gamificationWriteKey)
    .gamificationRegion(gamificationRegion)
    .gamificationBaseUrl(gamificationBaseUrl)
    .build();

HydraAPI.instanceWithConfig(getApplicationContext(), hydraConfig);
```

Register your `Application` class in `AndroidManifest.xml`:

```xml
<application
    android:name=".MyApplication"
    ... >
</application>
```

### Reporting screens

Set up screen tracking in your `Application.onCreate()`, after SDK initialization:

**Kotlin:**

```kotlin
var gamificationUIManager: GamificationUIManager? = null

HydraAPI.getDefaultInstance(applicationContext)?.getGamificationManager()?.let { manager ->
    gamificationUIManager = GamificationUIManager(manager, applicationContext)
}

// Register activity lifecycle for screen tracking
registerActivityLifecycleCallbacks(object : ActivityLifecycleCallbacks {
    override fun onActivityResumed(activity: Activity) {
        gamificationUIManager?.onScreenChanged(activity, activity::class.simpleName)
    }

    override fun onActivityDestroyed(activity: Activity) {
        gamificationUIManager?.onActivityDestroyed(activity)
    }

    override fun onActivityCreated(activity: Activity, savedInstanceState: Bundle?) {}
    override fun onActivityStarted(activity: Activity) {}
    override fun onActivityPaused(activity: Activity) {}
    override fun onActivityStopped(activity: Activity) {}
    override fun onActivitySaveInstanceState(activity: Activity, outState: Bundle) {}
})

// Register app foreground/background lifecycle
ProcessLifecycleOwner.get().lifecycle.addObserver(object : DefaultLifecycleObserver {
    override fun onStart(owner: LifecycleOwner) {
        gamificationUIManager?.onAppForegrounded()
    }

    override fun onStop(owner: LifecycleOwner) {
        gamificationUIManager?.onAppBackgrounded()
    }
})
```

<Callout icon="📘" theme="info">
  ### Note

  Screen reporting is mandatory for screen-targeted campaigns. Campaign visibility and eligibility depend on the currently reported screen.
</Callout>

The source guide only shows this wiring in Kotlin.

### Setting the B2B token

The loyalty view requires a short-lived Capillary B2B token. Set it before the view renders, or its content won't display.

**Kotlin:**

```kotlin
val hydraAPI = HydraAPI.getDefaultInstance(context)
hydraAPI?.setCapToken(token)
```

**Java:**

```java
HydraAPI hydraAPI = HydraAPI.getDefaultInstance(context);
if (hydraAPI != null) {
    hydraAPI.setCapToken(token);
}
```

<Callout icon="📘" theme="info">
  ### Note

  The Capillary token must be set before rendering the loyalty view. Failure to provide a valid token may result in loyalty content not being displayed.
</Callout>

### Embeddable views

Add each view to your XML layout, same package names as Option A:

```xml
<com.capillarytech.hydra.gamification.ui.entrypoints.BannerView
    android:id="@+id/banner110"
    android:layout_width="match_parent"
    android:layout_height="wrap_content" />

<com.capillarytech.hydra.gamification.ui.entrypoints.EmbedWebView
    android:id="@+id/embedView"
    android:layout_width="match_parent"
    android:layout_height="wrap_content" />

<com.capillarytech.hydra.gamification.ui.entrypoints.LoyaltyEmbedView
    android:id="@+id/embedLoyalty1"
    android:layout_width="match_parent"
    android:layout_height="match_parent" />
```

Banner and loyalty views are automatically bound and rendered once `onScreenChanged` is called. The embedded view needs an explicit binding call:

**Kotlin:**

```kotlin
val embedView = findViewById<EmbedWebView>(R.id.embedView)
gamificationUIManager?.bindEmbedView(embedView, EMBED_ENTRY_POINT_ID, this)
```

### Option B checklist

**Required:**

* Add `github.properties` with credentials and add it to `.gitignore`.
* Add the GitHub Packages Maven repository to `settings.gradle`.
* Add the `hydra-core` dependency to `app/build.gradle`.
* Update to the minimum required Hydra Android SDK version.
* Initialize the SDK in `Application.onCreate()` via `HydraConfig.Builder`.
* Register your `Application` class in `AndroidManifest.xml`.
* Add `hydra_gamification_region`.
* Add `hydra_gamification_key`.
* Add `hydra_gamification_base_url` (optional).
* Report screen names via `GamificationUIManager`.
* Set the Capillary token using `setCapToken(...)` (required for the loyalty view).
* Make sure there's **no** Google Services plugin, Firebase dependencies, or `google-services.json`.

**Optional:**

* Add in-app messaging (`hydra-inapp`).
* Add inbox / notification center (`hydra-inbox-core`, `hydra-inbox-ui`).
* Add a banner view.
* Add an embedded view (bind explicitly with `bindEmbedView()`).
* Add a loyalty view.
* For CI/CD: generate `github.properties` from secrets before the Gradle build.

**Result:** After completing the required steps, floating button, bottom sheet, and popup campaigns become automatically available in your app. If you also add the optional UI components, banner, embedded, and loyalty experiences can be displayed directly within your app screens.

<Callout icon="📘" theme="info">
  ### Note

  Push notifications aren't available in this integration mode. To add push notification support later, include the `hydra-pushbase` and `hydra-firebase` modules along with Firebase dependencies and `google-services.json`, and follow the standard integration guide.
</Callout>

## Game and CMS event payloads

Experience+ sends the following events for game and CMS interactions. This section covers seven events (five game events and two CMS events): what each event is, when it fires, which attributes it carries, and a sample payload. It also describes how event fields map to the event-creation fields.

* `cuid` is **required** on every event. All other attributes are optional.
* `event_name` identifies the event and is always sent.
* Payloads are flat JSON with no nested objects. Numbers are sent as numbers, not strings.
* While creating the events, map the fields as described in [Field mapping](#field-mapping) (`cuid` → `customerId`, `identifierType`, `source`, `accountId`).

| #  | Flow | Event name       | When it fires                                                                                       |
| :- | :--- | :--------------- | :-------------------------------------------------------------------------------------------------- |
| 1  | Game | `game_open`      | A game entry surface opens or launches the game (pop-up, floating icon, modal, or embedded banner). |
| 2  | Game | `game_viewed`    | The game UI is rendered and actually visible to the user.                                           |
| 3  | Game | `game_played`    | The user makes the first real interaction with the game (spin, scratch, tap, or select).            |
| 4  | Game | `game_completed` | The game ends: won, lost, completed, or abandoned.                                                  |
| 5  | Game | `reward_seen`    | The user views the reward (reveal screen or wallet).                                                |
| 6  | CMS  | `content_open`   | A CMS surface is opened or displayed (widget, banner, or full page).                                |
| 7  | CMS  | `content_viewed` | The CMS content is rendered and visible.                                                            |

### game\_open

**Flow:** Game

**Fires when:** A game entry surface opens or launches the game (pop-up, floating icon, modal, or embedded banner).

| Attribute              | Type   | Required | Example                | Description                                                                                                                                                       |
| :--------------------- | :----- | :------- | :--------------------- | :---------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `cuid`                 | string | Yes      | `stringxxx`            | Customer identifier: the loginIdentifier value (mobile number, email, or externalId). Maps to customerId when creating the event.                                 |
| `event_name`           | string | Yes      | `game_open`            | Event identifier.                                                                                                                                                 |
| `campaign_id`          | string | No       | `camp_44`              | Game instance ID. Join key across game and reward events.                                                                                                         |
| `game_type`            | string | No       | `spinthewheel`         | Which game was opened. *Values include: spinthewheel, scratchcard, slotmachine, quiz, memorygame, giftbox, streak, multistep, referral (list is not exhaustive).* |
| `entry_surface`        | string | No       | `popup`                | Which surface opened the game. *Values: popup, floating\_icon, modal, banner\_embedded.*                                                                          |
| `embed_id`             | string | No       | `home_hero`            | For banner\_embedded only: which placement or slot the banner sat in.                                                                                             |
| `entry_point_id`       | string | No       | `ep_12`                | Entry-point identifier.                                                                                                                                           |
| `entry_point_location` | string | No       | `home_screen`          | Where in the app the entry surface appeared.                                                                                                                      |
| `deep_link_url`        | string | No       | `/home`                | Which screen the user needs to open.                                                                                                                              |
| `hyper_link_url`       | string | No       | `https://your-url.com` | External URL to be opened.                                                                                                                                        |

**Sample payload**

```json
{
  "cuid": "stringxxx",
  "event_name": "game_open",
  "campaign_id": "camp_44",
  "game_type": "spinthewheel",
  "entry_surface": "popup",
  "embed_id": "home_hero",
  "entry_point_id": "ep_12",
  "entry_point_location": "home_screen",
  "deep_link_url": "/home",
  "hyper_link_url": "https://your-url.com"
}
```

### game\_viewed

**Flow:** Game

**Fires when:** The game UI is rendered and actually visible to the user.

| Attribute      | Type   | Required | Example        | Description                                                                                                                       |
| :------------- | :----- | :------- | :------------- | :-------------------------------------------------------------------------------------------------------------------------------- |
| `cuid`         | string | Yes      | `stringxxx`    | Customer identifier: the loginIdentifier value (mobile number, email, or externalId). Maps to customerId when creating the event. |
| `event_name`   | string | Yes      | `game_viewed`  | Event identifier.                                                                                                                 |
| `campaign_id`  | string | No       | `camp_44`      | Join key across game and reward events.                                                                                           |
| `game_type`    | string | No       | `spinthewheel` | Segment views by game type. Same values as game\_open.                                                                            |
| `load_time_ms` | number | No       | `850`          | Render or load time in milliseconds.                                                                                              |

**Sample payload**

```json
{
  "cuid": "stringxxx",
  "event_name": "game_viewed",
  "campaign_id": "camp_44",
  "game_type": "spinthewheel",
  "load_time_ms": 850
}
```

### game\_played

**Flow:** Game

**Fires when:** The user makes the first real interaction with the game (spin, scratch, tap, or select).

| Attribute     | Type   | Required | Example        | Description                                                                                                                       |
| :------------ | :----- | :------- | :------------- | :-------------------------------------------------------------------------------------------------------------------------------- |
| `cuid`        | string | Yes      | `stringxxx`    | Customer identifier: the loginIdentifier value (mobile number, email, or externalId). Maps to customerId when creating the event. |
| `event_name`  | string | Yes      | `game_played`  | Event identifier.                                                                                                                 |
| `campaign_id` | string | No       | `camp_44`      | Join key across game and reward events.                                                                                           |
| `game_type`   | string | No       | `spinthewheel` | Segment plays by game type. Same values as game\_open.                                                                            |

**Sample payload**

```json
{
  "cuid": "stringxxx",
  "event_name": "game_played",
  "campaign_id": "camp_44",
  "game_type": "spinthewheel"
}
```

### game\_completed

**Flow:** Game

**Fires when:** The game ends: won, lost, completed, or abandoned.

| Attribute       | Type   | Required | Example          | Description                                                                                                                       |
| :-------------- | :----- | :------- | :--------------- | :-------------------------------------------------------------------------------------------------------------------------------- |
| `cuid`          | string | Yes      | `stringxxx`      | Customer identifier: the loginIdentifier value (mobile number, email, or externalId). Maps to customerId when creating the event. |
| `event_name`    | string | Yes      | `game_completed` | Event identifier.                                                                                                                 |
| `campaign_id`   | string | No       | `camp_44`        | Join key across game and reward events.                                                                                           |
| `game_type`     | string | No       | `spinthewheel`   | Segment completions by game type. Same values as game\_open.                                                                      |
| `total_time_ms` | number | No       | `8200`           | Total play duration from start to finish, in milliseconds.                                                                        |

**Sample payload**

```json
{
  "cuid": "stringxxx",
  "event_name": "game_completed",
  "campaign_id": "camp_44",
  "game_type": "spinthewheel",
  "total_time_ms": 8200
}
```

### reward\_seen

**Flow:** Game

**Fires when:** The user views the reward (reveal screen or wallet).

| Attribute     | Type   | Required | Example       | Description                                                                                                                          |
| :------------ | :----- | :------- | :------------ | :----------------------------------------------------------------------------------------------------------------------------------- |
| `cuid`        | string | Yes      | `stringxxx`   | Customer identifier: the loginIdentifier value (mobile number, email, or externalId). Maps to customerId when creating the event.    |
| `event_name`  | string | Yes      | `reward_seen` | Event identifier.                                                                                                                    |
| `reward_id`   | string | No       | `rew_88`      | Reward ID. Join key for the reward.                                                                                                  |
| `campaign_id` | string | No       | `camp_44`     | Source game that issued the reward.                                                                                                  |
| `reward_type` | string | No       | `points`      | Segment by reward type. *Values include: points, coupons, cashback, discount, freebie, buyXgetY, noReward (list is not exhaustive).* |

**Sample payload**

```json
{
  "cuid": "stringxxx",
  "event_name": "reward_seen",
  "reward_id": "rew_88",
  "campaign_id": "camp_44",
  "reward_type": "points"
}
```

### content\_open

**Flow:** CMS

**Fires when:** A CMS surface is opened or displayed (widget, banner, or full page).

| Attribute         | Type   | Required | Example        | Description                                                                                                                       |
| :---------------- | :----- | :------- | :------------- | :-------------------------------------------------------------------------------------------------------------------------------- |
| `cuid`            | string | Yes      | `stringxxx`    | Customer identifier: the loginIdentifier value (mobile number, email, or externalId). Maps to customerId when creating the event. |
| `event_name`      | string | Yes      | `content_open` | Event identifier.                                                                                                                 |
| `content_surface` | string | No       | `full_page`    | Which CMS surface opened. *Values: widget, banner, full\_page.*                                                                   |

**Sample payload**

```json
{
  "cuid": "stringxxx",
  "event_name": "content_open",
  "content_surface": "full_page"
}
```

### content\_viewed

**Flow:** CMS

**Fires when:** The CMS content is rendered and visible.

| Attribute         | Type   | Required | Example          | Description                                                                                                                       |
| :---------------- | :----- | :------- | :--------------- | :-------------------------------------------------------------------------------------------------------------------------------- |
| `cuid`            | string | Yes      | `stringxxx`      | Customer identifier: the loginIdentifier value (mobile number, email, or externalId). Maps to customerId when creating the event. |
| `event_name`      | string | Yes      | `content_viewed` | Event identifier.                                                                                                                 |
| `page_id`         | string | No       | `page_9`         | Page ID. Join key for the CMS page.                                                                                               |
| `content_surface` | string | No       | `full_page`      | Segment views by surface. *Values: widget, banner, full\_page.*                                                                   |
| `load_time_ms`    | number | No       | `700`            | Load time in milliseconds; helps catch slow or empty loads.                                                                       |

**Sample payload**

```json
{
  "cuid": "stringxxx",
  "event_name": "content_viewed",
  "page_id": "page_9",
  "content_surface": "full_page",
  "load_time_ms": 700
}
```

### Field mapping

When creating the events, map the event fields to the event-creation fields below. All four are required.

| Event-creation field | Maps from                       | Required | Notes                                                                                         |
| :------------------- | :------------------------------ | :------- | :-------------------------------------------------------------------------------------------- |
| `customerId`         | `cuid` (from the event payload) | Yes      | `cuid` on every event must be mapped to `customerId` when creating the events.                |
| `identifierType`     | Identifier passed to the SDK    | Yes      | Set based on what is passed to the SDK as the login identifier: mobile, email, or externalId. |
| `source`             | SDK                             | Yes      | Map `source` to SDK.                                                                          |
| `accountId`          | SDK account ID                  | Yes      | Map to the SDK account ID.                                                                    |