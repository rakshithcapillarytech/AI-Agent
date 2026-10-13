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
| In-App messaging (`hydra-inapp`) | Dependency only; no setup steps documented |
| Inbox / Notification Center (`hydra-inbox-core`, `hydra-inbox-ui`) | Dependency only; no setup steps documented |
| Push notifications | **Not available in this mode.** Push needs the Firebase integration (`android/firebase.md`). |
| Visitor flow, multi-account | Not documented for this mode |

## Requirements
- SDK version: `{{sdk_version}}` (Beta for UAT/POC).
- Build: Gradle with a `settings.gradle` / `settings.gradle.kts` that uses `dependencyResolutionManagement`.

> ⚠️ Gap: the source doc doesn't state the minimum Android API level (minSdk), compileSdk, AGP, Gradle or Kotlin versions. Ask a Capillary engineer before giving numbers.

## Prerequisites
See `_shared/prerequisites.md` for the common exchange. For this platform and mode:
- **Client gives Capillary:** the Android application ID (package name).
- **Capillary gives client:**
  - Account Id
  - Base URL
  - SSL Public Key
  - Org Id
  - Gamification Key
  - Gamification Region (`IN`, `US` or `ME`)
  - Gamification URL (optional)
- **Repository access:**
  - Read access to the private GitHub Maven repo `https://github.com/Capillary/hydra-sdk-android-maven`. Request it from Capillary's access team.
  - A GitHub username plus a Personal Access Token (PAT) with the **`read:packages`** scope.

## Steps

### 1. Store GitHub credentials locally
Create `github.properties` at the project root, at the same level as `settings.gradle`:

```properties file=github.properties
username=YOUR_GITHUB_USERNAME
token=YOUR_GITHUB_PAT
```

Add it to `.gitignore` so the token is never committed:

```text file=.gitignore
github.properties
```

### 2. Add the GitHub Packages Maven repository
Add this inside `dependencyResolutionManagement.repositories` in your settings file.

Kotlin DSL:

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

Groovy DSL:

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

### 3. Add the SDK dependencies
Add these to `app/build.gradle(.kts)`. Only `hydra-core` is required; include the optional modules the client needs.

> **Important:** do NOT add the `com.google.gms.google-services` plugin. Do NOT add Firebase dependencies or `google-services.json`.

Kotlin DSL:

```kotlin file=app/build.gradle.kts
dependencies {
    // Hydra Core (required)
    implementation("com.capillary:hydra-core:{{sdk_version}}")
    // Gamification (optional)
    implementation("com.capillary:hydra-gamification:{{sdk_version}}")
    implementation("com.capillary:hydra-gamification-ui:{{sdk_version}}")
    // In-app messaging (optional)
    implementation("com.capillary:hydra-inapp:{{sdk_version}}")
    // Inbox / Notification Center (optional)
    implementation("com.capillary:hydra-inbox-core:{{sdk_version}}")
    implementation("com.capillary:hydra-inbox-ui:{{sdk_version}}")
}
```

Groovy DSL:

```groovy file=app/build.gradle
dependencies {
    implementation "com.capillary:hydra-core:{{sdk_version}}"                 // required
    implementation "com.capillary:hydra-gamification:{{sdk_version}}"         // optional
    implementation "com.capillary:hydra-gamification-ui:{{sdk_version}}"      // optional
    implementation "com.capillary:hydra-inapp:{{sdk_version}}"                // optional
    implementation "com.capillary:hydra-inbox-core:{{sdk_version}}"           // optional
    implementation "com.capillary:hydra-inbox-ui:{{sdk_version}}"             // optional
}
```

### 4. Initialise the SDK in `Application.onCreate()`
Kotlin:

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
    .gamificationRegion(GamificationRegion.{{gamification_region}})   // IN, US or ME
    .gamificationBaseUrl("{{gamification_base_url}}")                 // optional
    .build()

HydraAPI.instanceWithConfig(applicationContext, hydraConfig)
```

Java:

```java
HydraConfig hydraConfig = new HydraConfig.Builder(getApplicationContext(), "{{account_id}}")
        .orgId("{{org_id}}")
        .baseURL("{{base_url}}")
        .sslPublicKey("{{ssl_public_key}}")
        .debugLevel(LogType.DEBUG)
        .gamificationWriteKey("{{gamification_key}}")
        .gamificationRegion(GamificationRegion.{{gamification_region}})
        .gamificationBaseUrl("{{gamification_base_url}}")   // optional
        .build();
HydraAPI.instanceWithConfig(getApplicationContext(), hydraConfig);
```

### 5. Register the Application class
In `AndroidManifest.xml`:

```xml file=app/src/main/AndroidManifest.xml
<application
    android:name=".MyApplication"
    ... >
</application>
```

### 6. Report user sign-in and sign-out
Sign-in (Kotlin). `customerId` is required and **must match the Account Linking Identifier configured in Capillary CRM** (see `_shared/prerequisites.md`):

```kotlin
val hydraAPI = HydraAPI.getDefaultInstance(context)
val customAttributes = hashMapOf<String, Any>("key1" to "value1", "key2" to "value2")
hydraAPI?.pushUserSignin(
    customerId,        // required
    firstName,         // optional
    lastName,          // optional
    email,             // optional
    phone,             // optional
    customAttributes   // optional
)
```

Sign-out (Kotlin):

```kotlin
HydraAPI.getDefaultInstance(context)?.pushUserSignout()
```

Java equivalents: `hydraAPI.pushUserSignin(customerId, firstName, lastName, email, phone, customAttributes);` and `hydraAPI.pushUserSignout();`. Guard each with `if (hydraAPI != null)`.

### 7. Report the current screen (required for gamification)
Gamification decides when and where to show campaigns from the reported screen. **Screen reporting is mandatory for screen-targeted campaigns.** Add this in `Application.onCreate()` after SDK initialisation:

```kotlin
var gamificationUIManager: GamificationUIManager? = null
HydraAPI.getDefaultInstance(applicationContext)?.getGamificationManager()?.let { manager ->
    gamificationUIManager = GamificationUIManager(manager, applicationContext)
}

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

ProcessLifecycleOwner.get().lifecycle.addObserver(object : DefaultLifecycleObserver {
    override fun onStart(owner: LifecycleOwner) { gamificationUIManager?.onAppForegrounded() }
    override fun onStop(owner: LifecycleOwner) { gamificationUIManager?.onAppBackgrounded() }
})
```

### 8. Custom behavioural events (optional)
```kotlin
val attributes = mapOf("key1" to "value1", "key2" to "value2")
HydraAPI.getDefaultInstance(context)?.pushEvent("custom_event_name", attributes)
```

### 9. Set the Capillary token (required for Loyalty View)
Set the Capillary B2B short-lived token **before** a Loyalty View is displayed. Without a valid token, loyalty content may not appear.

```kotlin
HydraAPI.getDefaultInstance(context)?.setCapToken(token)
```

## Modules

### Push
Not available in this integration mode. Push requires the `hydra-pushbase` and `hydra-firebase` modules plus Firebase dependencies and `google-services.json`, which means the Firebase integration (`android/firebase.md`).

### In-App
Add the `hydra-inapp` dependency (step 3).
> ⚠️ Gap: no further setup steps are documented for this mode.

### Inbox
Add the `hydra-inbox-core` and `hydra-inbox-ui` dependencies (step 3).
> ⚠️ Gap: no further setup steps are documented for this mode.

### Visitor
> ⚠️ Gap: not documented for this mode.

### Gamification
**Automatic experiences.** Once steps 1–7 are done, Hydra shows these with no extra code:
- Floating Button campaigns
- Popup campaigns
- Bottom Sheet campaigns

**Custom UI components** (optional, added to XML layouts):
- **Banner View:** rendered automatically when `onScreenChanged()` reports the screen.
  ```xml
  <com.capillary.hydra.gamification.ui.entrypoints.BannerView
      android:id="@+id/bannerView"
      android:layout_width="match_parent"
      android:layout_height="wrap_content" />
  ```
- **Embed View:** needs explicit binding.
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
- **Loyalty View:** rendered automatically when the screen is reported. Call `setCapToken(...)` before the screen is reported.
  ```xml
  <com.capillary.hydra.gamification.ui.entrypoints.LoyaltyEmbedView
      android:id="@+id/loyaltyView"
      android:layout_width="match_parent"
      android:layout_height="wrap_content" />
  ```

## Verification
After the required steps, Floating Button, Bottom Sheet and Popup campaigns should appear in the app automatically, for screens that have campaigns configured. If you added the custom UI components, Banner, Embed and Loyalty content should appear too.

**Required checklist** (from the source):
- `github.properties` created and git-ignored.
- GitHub Packages repo added to `settings.gradle`.
- `hydra-core` added to `app/build.gradle`, at version `{{sdk_version}}`.
- SDK initialised in `Application.onCreate()` with `HydraConfig.Builder`.
- Application class registered in `AndroidManifest.xml`.
- Gamification key, region and (optional) base URL set in the `HydraConfig.Builder`.
- Screen names reported via `GamificationUIManager`.
- `setCapToken(...)` called (if using Loyalty View).
- No google-services plugin, Firebase dependencies or `google-services.json`.

> ⚠️ Source doc correction: the source checklist (p.111) says "Add `hydra_gamification_region` / `hydra_gamification_key` / `hydra_gamification_base_url`". Those are Firebase Remote Config key names. In this mode the values go into `HydraConfig.Builder` (step 4). *Pending SME confirmation.*

> ⚠️ Gap: no log lines or callbacks are documented to confirm the SDK initialised successfully in this mode. `debugLevel(LogType.DEBUG)` enables debug logging. Ask an SME which Logcat lines to look for.

## Known Issues

**Gradle can't resolve `com.capillary:hydra-core` (401 / 403 from `maven.pkg.github.com`)**
- Cause: GitHub Packages rejected the credentials. Possible reasons:
  - the PAT is missing the `read:packages` scope,
  - the GitHub account hasn't been granted access to `Capillary/hydra-sdk-android-maven`,
  - `github.properties` is missing or has wrong keys (`username`, `token`).
- Fix:
  1. Create a PAT with `read:packages`.
  2. Confirm repo access with Capillary's access team.
  3. Check that `github.properties` sits next to `settings.gradle`.

*Derived from the prerequisites in the source doc, not yet from a reported case.*

**CI builds fail to resolve the SDK**
- Cause: `github.properties` is git-ignored, so it doesn't exist on CI.
- Fix: generate `github.properties` from CI secrets before the Gradle build.

## API Reference
| API | Purpose |
|---|---|
| `HydraConfig.Builder(context, accountId)` | Builds the SDK config. Methods: `.orgId()`, `.baseURL()`, `.sslPublicKey()`, `.debugLevel(LogType)`, `.gamificationWriteKey()`, `.gamificationRegion(GamificationRegion.IN/US/ME)`, `.gamificationBaseUrl()`, `.build()` |
| `HydraAPI.instanceWithConfig(context, config)` | Initialises the SDK |
| `HydraAPI.getDefaultInstance(context)` | Returns the SDK instance (nullable) |
| `pushUserSignin(customerId, firstName, lastName, email, phone, customAttributes)` | Reports sign-in |
| `pushUserSignout()` | Reports sign-out |
| `pushEvent(name, attributes)` | Reports a custom behavioural event |
| `setCapToken(token)` | Sets the Capillary B2B token for Loyalty View |
| `getGamificationManager()` | Returns the gamification manager for `GamificationUIManager` |
| `GamificationUIManager(manager, context)` | Methods: `.onScreenChanged(activity, name)`, `.onActivityDestroyed(activity)`, `.onAppForegrounded()`, `.onAppBackgrounded()`, `.bindEmbedView(view, entryPointId, lifecycleOwner)` |
| Views | `com.capillary.hydra.gamification.ui.entrypoints.BannerView`, `EmbedWebView`, `LoyaltyEmbedView` |
