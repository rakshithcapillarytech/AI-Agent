---
platform: android
config_mode: direct
sdk_package: com.capillary:hydra-core
sdk_version: 1.9.22-beta02
modules_covered: [core, gamification]
modules_missing: [inapp, inbox_api, inbox_ui, visitor, multi_account]
sources: ["Integration document _ Experience+ pp.100–112 (Hydra Android SDK Integration Guide, Without Firebase)"]
owner: TBD
last_verified: null
review_status: draft   # drafted from the source doc; not yet SME-verified
---
# Android (without Firebase)

## Coverage
| Module | Status in this mode |
|---|---|
| Core (sign-in, sign-out, custom events) | Documented |
| Gamification (automatic campaigns, Banner, Embed, Loyalty, screen tracking) | Documented |
| In-App (`hydra-inapp`), Inbox (`hydra-inbox-core`, `hydra-inbox-ui`) | Dependency only; no setup steps |
| Push | **Not available in this mode.** Needs Firebase (`android/firebase.md`). |
| Visitor, multi-account | Not documented |

## Requirements
- SDK version: `{{sdk_version}}` (Beta for UAT/POC).
- Gradle settings file using `dependencyResolutionManagement` (step 2).

> ⚠️ Gap: minSdk, compileSdk, AGP, Gradle and Kotlin versions aren't documented. Ask a Capillary engineer.

## Prerequisites
Common exchange: `_shared/prerequisites.md`. For this mode:
- **Client gives Capillary:** the Android application ID (package name).
- **Capillary gives client:** Account Id, Base URL, SSL Public Key, Org Id, Gamification Key, Gamification Region (`IN`, `US` or `ME`), Gamification URL (optional).
- **Repository access** (request from Capillary's access team): read access to `https://github.com/Capillary/hydra-sdk-android-maven`, plus a GitHub username and a Personal Access Token (PAT) with the **`read:packages`** scope.

## Steps

### 1. Store GitHub credentials locally
Create `github.properties` at the project root (same level as `settings.gradle`):

```properties file=github.properties
username=YOUR_GITHUB_USERNAME
token=YOUR_GITHUB_PAT
```

Add it to `.gitignore`:

```text file=.gitignore
github.properties
```

### 2. Add the GitHub Packages Maven repository
Inside `dependencyResolutionManagement.repositories`:

```groovy file=settings.gradle
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

```kotlin file=settings.gradle.kts
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

### 3. Add the SDK dependencies
Only `hydra-core` is required.

> **Important:** do NOT add the `com.google.gms.google-services` plugin, Firebase dependencies or `google-services.json`.

```groovy file=app/build.gradle
dependencies {
    // Hydra Core (required)
    implementation "com.capillary:hydra-core:{{sdk_version}}"

    // In-app messaging (optional)
    implementation "com.capillary:hydra-inapp:{{sdk_version}}"

    // Inbox / Notification Center (optional)
    implementation "com.capillary:hydra-inbox-core:{{sdk_version}}"
    implementation "com.capillary:hydra-inbox-ui:{{sdk_version}}"

    // Gamification (optional)
    implementation "com.capillary:hydra-gamification:{{sdk_version}}"
    implementation "com.capillary:hydra-gamification-ui:{{sdk_version}}"
}
```

```kotlin file=app/build.gradle.kts
dependencies {
    // Hydra Core (required)
    implementation("com.capillary:hydra-core:{{sdk_version}}")

    // In-app messaging (optional)
    implementation("com.capillary:hydra-inapp:{{sdk_version}}")

    // Inbox / Notification Center (optional)
    implementation("com.capillary:hydra-inbox-core:{{sdk_version}}")
    implementation("com.capillary:hydra-inbox-ui:{{sdk_version}}")

    // Gamification (optional)
    implementation("com.capillary:hydra-gamification:{{sdk_version}}")
    implementation("com.capillary:hydra-gamification-ui:{{sdk_version}}")
}
```

### 4. Initialise the SDK in `Application.onCreate()`
```kotlin file=app/src/main/java/<your-package>/MyApplication.kt
val hydraConfig = HydraConfig.Builder(
    applicationContext,
    accountId = "{{account_id}}"
)
    .orgId("{{org_id}}")
    .baseURL("{{base_url}}")
    .sslPublicKey("{{ssl_public_key}}")
    .debugLevel(LogType.DEBUG)
    .gamificationWriteKey("{{gamification_key}}")
    .gamificationRegion(GamificationRegion.{{gamification_region}})   // GamificationRegion.IN, .US, or .ME
    .gamificationBaseUrl("{{gamification_base_url}}")                 // Optional
    .build()

HydraAPI.instanceWithConfig(applicationContext, hydraConfig)
```

```java file=app/src/main/java/<your-package>/MyApplication.java
HydraConfig hydraConfig = new HydraConfig.Builder(
    getApplicationContext(), "{{account_id}}"
)
    .orgId("{{org_id}}")
    .baseURL("{{base_url}}")
    .sslPublicKey("{{ssl_public_key}}")
    .debugLevel(LogType.DEBUG)
    .gamificationWriteKey("{{gamification_key}}")
    .gamificationRegion(GamificationRegion.{{gamification_region}})
    .gamificationBaseUrl("{{gamification_base_url}}")
    .build();

HydraAPI.instanceWithConfig(getApplicationContext(), hydraConfig);
```

### 5. Register the Application class
```xml file=app/src/main/AndroidManifest.xml
<application
    android:name=".MyApplication"
    ... >
</application>
```

### 6. Report user sign-in and sign-out
`customerId` is required and must match the Account Linking Identifier configured in Capillary CRM (`_shared/prerequisites.md`).

```kotlin
val hydraAPI = HydraAPI.getDefaultInstance(context)

val customAttributes = hashMapOf<String, Any>("key1" to "value1", "key2" to "value2")

hydraAPI?.pushUserSignin(
    customerId,        // required — must match your Capillary CRM Account Linking Identifier
    firstName,         // optional
    lastName,          // optional
    email,             // optional
    phone,             // optional
    customAttributes   // optional
)
```

```java
HydraAPI hydraAPI = HydraAPI.getDefaultInstance(context);

Map<String, Object> customAttributes = new HashMap<>();
customAttributes.put("key1", "value1");
customAttributes.put("key2", "value2");

if (hydraAPI != null) {
    hydraAPI.pushUserSignin(customerId, firstName, lastName, email, phone, customAttributes);
}
```

Sign-out:

```kotlin
val hydraAPI = HydraAPI.getDefaultInstance(context)

hydraAPI?.pushUserSignout()
```

```java
HydraAPI hydraAPI = HydraAPI.getDefaultInstance(context);

if (hydraAPI != null) {
    hydraAPI.pushUserSignout();
}
```

### 7. Report the current screen (required for gamification)
Add in `Application.onCreate()` after SDK initialisation. **Screen reporting is mandatory for screen-targeted campaigns**: campaign visibility and eligibility depend on the reported screen.

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

### 8. Custom behavioural events (optional)
```kotlin
val hydraAPI = HydraAPI.getDefaultInstance(context)

val attributes = mapOf("key1" to "value1", "key2" to "value2")

hydraAPI?.pushEvent("custom_event_name", attributes)
```

```java
HydraAPI hydraAPI = HydraAPI.getDefaultInstance(context);

Map<String, Object> attributes = new HashMap<>();
attributes.put("key1", "value1");
attributes.put("key2", "value2");

if (hydraAPI != null) {
    hydraAPI.pushEvent("custom_event_name", attributes);
}
```

### 9. Set the Capillary token (required for Loyalty View)
Set the Capillary B2B short-lived token **before** the Loyalty View is rendered. Without a valid token, loyalty content may not be displayed.

```kotlin
val hydraAPI = HydraAPI.getDefaultInstance(context)

hydraAPI?.setCapToken(token)
```

```java
HydraAPI hydraAPI = HydraAPI.getDefaultInstance(context);

if (hydraAPI != null) {
    hydraAPI.setCapToken(token);
}
```

## Modules

### Push
Not available in this mode. Adding push later needs the `hydra-pushbase` and `hydra-firebase` modules plus Firebase dependencies and `google-services.json`, following the standard (Firebase) integration guide: see `android/firebase.md`.

### In-App
Add `hydra-inapp` (step 3).
> ⚠️ Gap: no further In-App setup is documented for this mode. Ask a Capillary engineer.

### Inbox
Add `hydra-inbox-core` and `hydra-inbox-ui` (step 3).
> ⚠️ Gap: no further Inbox setup is documented for this mode. Ask a Capillary engineer.

### Visitor
> ⚠️ Gap: the visitor flow isn't documented for this mode. Ask a Capillary engineer.

### Gamification
**Automatic experiences** (no extra code after steps 1–7): Floating Button, Popup and Bottom Sheet campaigns. Hydra evaluates eligibility and displays them.

**Custom UI components** (optional, in XML layouts):
- **Banner View:** rendered automatically when `onScreenChanged()` reports the screen; no manual binding.
  ```xml
  <com.capillary.hydra.gamification.ui.entrypoints.BannerView
      android:id="@+id/bannerView"
      android:layout_width="match_parent"
      android:layout_height="wrap_content" />
  ```
- **Embed View:** needs explicit binding via `bindEmbedView()`.
  ```xml
  <com.capillary.hydra.gamification.ui.entrypoints.EmbedWebView
      android:id="@+id/embedView"
      android:layout_width="match_parent"
      android:layout_height="wrap_content" />
  ```
  ```kotlin
  val embedView = findViewById<EmbedWebView>(R.id.embedView)
  gamificationUIManager?.bindEmbedView(embedView, EMBED_ENTRY_POINT_ID, this)
  ```
  > ⚠️ Gap: where `EMBED_ENTRY_POINT_ID` comes from isn't documented. Ask a Capillary engineer.
- **Loyalty View:** rendered automatically when `onScreenChanged()` reports the screen. Call `setCapToken(...)` (step 9) before the screen is reported.
  ```xml
  <com.capillary.hydra.gamification.ui.entrypoints.LoyaltyEmbedView
      android:id="@+id/loyaltyView"
      android:layout_width="match_parent"
      android:layout_height="wrap_content" />
  ```

## Verification
Expected result: Floating Button, Bottom Sheet and Popup campaigns appear automatically; Banner, Embed and Loyalty content too if those views were added.

**Required checklist:**
- `github.properties` created and git-ignored; GitHub Packages repo in `settings.gradle`.
- `hydra-core` in `app/build.gradle`, on the latest SDK version (`{{sdk_version}}`).
- SDK initialised in `Application.onCreate()` via `HydraConfig.Builder`; Application class registered in `AndroidManifest.xml`.
- Gamification key, region and base URL (optional) set.
- Screen names reported via `GamificationUIManager`.
- `setCapToken(...)` called (required for Loyalty View).
- No google-services plugin, Firebase dependencies or `google-services.json`.

**Optional:** `hydra-inapp`; `hydra-inbox-core` + `hydra-inbox-ui`; Banner, Embed, Loyalty views; CI/CD generates `github.properties` from secrets.

> ⚠️ Correction: ✅ Use `HydraConfig.Builder` (`.gamificationWriteKey()`, `.gamificationRegion()`, `.gamificationBaseUrl()`, step 4) for the gamification values. ❌ Don't use `hydra_gamification_key` / `hydra_gamification_region` / `hydra_gamification_base_url` Remote Config keys in this mode (checklist, p.111). *Pending SME confirmation.*

> ⚠️ Gap: no log lines or callbacks confirm successful initialisation in this mode (`debugLevel(LogType.DEBUG)` only enables debug logging). Ask a Capillary engineer.

## Known Issues

**Gradle can't resolve `com.capillary:hydra-core` (401/403 from `maven.pkg.github.com`)** — derived from the prerequisites, not a reported case.
- Cause: GitHub Packages rejected the credentials: PAT lacks `read:packages`, the account has no access to `Capillary/hydra-sdk-android-maven`, or `github.properties` is missing / has wrong keys (`username`, `token`).
- Fix: use a PAT with `read:packages`; confirm repo access with Capillary's access team; keep `github.properties` next to `settings.gradle`.

**CI builds can't resolve the SDK**
- Cause: `github.properties` is git-ignored, so it doesn't exist on CI.
- Fix: generate `github.properties` from CI secrets before the Gradle build (listed in the source checklist).

## API Reference
| API | Purpose |
|---|---|
| `HydraConfig.Builder(context, accountId)` | SDK config: `.orgId()`, `.baseURL()`, `.sslPublicKey()`, `.debugLevel(LogType)`, `.gamificationWriteKey()`, `.gamificationRegion(GamificationRegion.IN/US/ME)`, `.gamificationBaseUrl()`, `.build()` |
| `HydraAPI.instanceWithConfig(context, config)` | Initialises the SDK |
| `HydraAPI.getDefaultInstance(context)` | SDK instance (nullable) |
| `pushUserSignin(customerId, firstName, lastName, email, phone, customAttributes)` | Sign-in |
| `pushUserSignout()` | Sign-out |
| `pushEvent(name, attributes)` | Custom event |
| `setCapToken(token)` | Capillary B2B token for Loyalty View |
| `getGamificationManager()` | Manager passed to `GamificationUIManager` |
| `GamificationUIManager(manager, context)` | `.onScreenChanged(activity, name)`, `.onActivityDestroyed(activity)`, `.onAppForegrounded()`, `.onAppBackgrounded()`, `.bindEmbedView(view, entryPointId, owner)` |
| Views (`com.capillary.hydra.gamification.ui.entrypoints`) | `BannerView`, `EmbedWebView`, `LoyaltyEmbedView` |
