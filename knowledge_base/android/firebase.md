---
platform: android
config_mode: firebase
sdk_package: com.capillary:hydra-core
sdk_version: 1.9.22-beta02             # gamification minimum (gamification-android); see the version Gap in Requirements
modules_covered: [core, push, inapp, inbox_api, inbox_ui, gamification]
modules_missing: [visitor, multi_account]
sources: ["Capillary developer docs (docs.capillarytech.com): android-sdk (updated 2026-08-14), android-sdk-getting-started (updated 2026-11-12), configure-firebase (updated 2026-03-04), installing-sdk, sdk-initialisation, configure-notification-center, android-sdk-api-reference, xiaomi-push-notification (updated 2026-03-25), push-notification (updated 2026-08-03), gamification-android (updated 2026-08-18, Option A), in-app-messaging (updated 2026-10-20)", "Integration document _ Experience+ pp.38–51 (Experience+ Android: Gamification Android Integration Guide, Kotlin + Java)", "Integration document _ Experience+ p.112 (one sentence on push, at the end of the Android without-Firebase guide)"]
owner: TBD
last_verified: null
review_status: draft   # drafted from the source docs; not yet SME-verified
---
# Android (with Firebase)

## Coverage
The standard Hydra Android integration: the app uses Firebase (FCM for push; Remote Config for the gamification keys). Kotlin and Java.

| Module | Status in this mode |
|---|---|
| Core (install, init, sign-in/up/update/out, behavioural events, user preferences) | Documented (steps 1–8) |
| Push (FCM, permission, token handling, listeners, CTAs/deep links, rich push) | Documented (steps 9–13); Xiaomi push amplification is deprecated (Modules › Push) |
| In-App, Inbox API, Inbox UI (Notification Center) | Documented (Modules) |
| Gamification (Remote Config keys, screen tracking, callback, late Remote Config, Banner, Embedded, Loyalty, cap token) | Documented (steps 14–19, Modules) |
| Visitor, multi-account | **Not documented** |

> ⚠️ Gap: the Android docs pass Account Id, Base URL and SSL key to `HydraConfig.Builder` in code; only the gamification values are documented as Firebase Remote Config keys. Android Remote Config key names for the core values, and how to read Remote Config, aren't documented. Ask a Capillary engineer.

## Requirements
From Getting Started (android-sdk-getting-started):
- Android SDK version V21 or above (minSdk 21)
- targetSdkVersion 34
- compileSdkVersion 34
- Google Firebase account
- Gradle: the version catalog (recommended install path) is a preview feature on Gradle 7.4 and below and must be enabled (step 2); it's on by default from 7.4.
- Hydra SDK: `{{sdk_version}}` (Beta, for UAT/POC) or later for gamification.

> ⚠️ Correction: ✅ Use `1.9.22-beta02` as the minimum SDK version for gamification (gamification-android). ❌ Don't use `1.9.22-beta01` (Integration document pp.39, 50). *Pending SME confirmation.*

> ⚠️ Gap: Getting Started lists every module (`hydra-core`, `hydra-pushbase`, `hydra-firebase`, `hydra-richnotification`, `hydra-inbox-core`, `hydra-inbox-ui`, `hydra-inapp`, `hydra-catalog`) at `1.9.20`, while gamification needs `1.9.22-beta02`. Whether the push, rich-notification and catalog modules are published at `1.9.22-beta02` isn't documented. Ask a Capillary engineer which version to use for each module.

> ⚠️ Gap: AGP, Kotlin and exact Gradle versions aren't documented. Ask a Capillary engineer.

## Prerequisites
Common exchange: `_shared/prerequisites.md`. Firebase project and Remote Config: `_shared/firebase-setup.md`. Push server side and testing: `_shared/push.md`.

Getting Started order: (1) Firebase and gateway are configured (Capillary mobile apps team), (2) the source account is configured (CSM / project manager), then (3) install, (4) initialise, (5) push, (6) APIs, (7) gamification.

- **Client gives Capillary:** the Android application ID and the app signature (SHA256); for push, the Firebase project ID and service account (`_shared/push.md`).
- **Capillary gives the client:** Account Id (the Source Account Id of your MAPP_SDK account), Base URL (specific to your Capillary cluster), SSL Public Key, Org Id (also passed to `updateRemoteConfig` for gamification, step 18), and the gamification values below.
- **Repository access:** read access to `https://github.com/Capillary/hydra-sdk-android-maven`, plus a GitHub username and a Personal Access Token (PAT) with the **`read:packages`** scope.
- **Behavioural events** you send with `pushEvent` must first be created in Capillary: *Organisation settings > Master Data Management > Data Model > Behavioural events*.

> ⚠️ Gap: the Android push page (push-notification) lists an **FCM server API key** (Firebase console › Project settings › Cloud Messaging › Server key) as the push prerequisite, while Configure Firebase (configure-firebase) asks for a **service account** with a custom role and a JSON private key. Ask a Capillary engineer which one Capillary needs.

| Firebase Remote Config key | Value from Capillary | Required? |
|---|---|---|
| `hydra_gamification_key` | Gamification write key for your account | Mandatory |
| `hydra_gamification_region` | Region for the gamification service | Mandatory |
| `hydra_gamification_base_url` | Override base URL for the gamification service | Optional |

## Steps

### 1. Store GitHub credentials locally
Create `github.properties` at the project root (same level as `settings.gradle`), and add it to `.gitignore`:

```properties file=github.properties
username=YOUR_GITHUB_USERNAME
token=YOUR_GITHUB_PAT
```

```text file=.gitignore
github.properties
```

> ⚠️ Gap: the install page (installing-sdk) writes the values in quotes (`username="USERNAME"`, `token="TOKEN"`); the gamification page shows them unquoted (above). Ask a Capillary engineer if Gradle can't authenticate.

### 2. Add the GitHub Packages Maven repository and the version catalog
Inside `dependencyResolutionManagement` in `settings.gradle(.kts)`. The `versionCatalogs` block is the recommended path (installing-sdk); skip it if you use plain artifact coordinates (step 3).

```groovy file=settings.gradle
// Add this at the top level of settings.gradle (only for Gradle < 7.4)
enableFeaturePreview("VERSION_CATALOGS")

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
    versionCatalogs {
        create("hydra") {
            from("com.capillary:hydra-catalog:{{sdk_version}}")
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

The repository block (with `github.properties` loading) is from gamification-android; the `enableFeaturePreview` and `versionCatalogs` lines are from installing-sdk, which doesn't show a Kotlin DSL catalog block. Without a catalog, installing-sdk puts the `maven { … }` block in the `repositories` section of `project/build.gradle` instead.

### 3. Add the SDK dependencies
Core, push base and Firebase modules, plus the AndroidX libraries. **With the version catalog** (`hydra` = the catalog name from step 2):

```kotlin file=app/build.gradle.kts
dependencies {
   // AndroidX libraries
 implementation("androidx.core:core:xxx")
 implementation("androidx.appcompat:appcompat:xxx")
 implementation("androidx.lifecycle:lifecycle-process:xxx")
   // Hydra Sdk
 implementation(hydra.core)
  implementation(hydra.pushbase)
  implementation(hydra.firebase)
}
```

**Without the version catalog:**

```kotlin file=app/build.gradle
dependencies {
    // ...
    implementation("com.capillary:hydra-core:{{sdk_version}}")
    implementation("com.capillary:hydra-firebase:{{sdk_version}}")
    implementation("com.capillary:hydra-pushbase:{{sdk_version}}")
}
```

Optional modules: rich push (step 13), In-App and Inbox (Modules). Gamification needs **no extra dependency** in this mode: HydraGamification is bundled within HydraCore and enabled through configuration alone (gamification-android, Option A).

> ⚠️ Gap: the AndroidX library versions are shown only as `xxx`. Ask a Capillary engineer.

> ⚠️ Gap: installing-sdk uses unquoted catalog accessors (`implementation(hydra.core)`), while the push, In-App, Inbox and Xiaomi pages write quoted strings (`implementation("hydra.richnotification")`, `implementation("hydra.inapp")`, `implementation("hydra.inbox.core")`). Ask a Capillary engineer which form the catalog expects.

### 4. Add Firebase to the app
Create the Firebase project and set up Cloud Messaging per Firebase's Android documentation (configure-firebase, steps 1–2). Push needs the Firebase dependencies and `google-services.json` in the app (gamification-android). The Firebase console and service-account steps are in `_shared/firebase-setup.md` and `_shared/push.md`.

> ⚠️ Gap: the Capillary docs don't give the Gradle lines for the `com.google.gms.google-services` plugin or the Firebase (Messaging, Remote Config) dependencies. Ask a Capillary engineer.

### 5. Initialise the SDK in `Application.onCreate()`
Create one SDK instance per application, in `onCreate()` of the Application class. `accountId` is mandatory: **if it isn't provided, the SDK throws an exception**. All other parameters are optional.

```kotlin file=app/src/main/java/<your-package>/MyApplication.kt
val hydraConfig = HydraConfig.Builder(
   applicationContext,
   accountId = "{{account_id}}"
)
   .debugLevel(LogType.VERBOSE)
   .remoteDebugLevel(LogType.DEBUG)
   .captureViewPortDetails(true)
   .country("India")
   .city("Pune")
   .countryCode("91")
   .baseURL("{{base_url}}")
   .sslPublicKey("{{ssl_public_key}}")
   .build()

HydraAPI.instanceWithConfig(applicationContext, hydraConfig)
```

```java file=app/src/main/java/<your-package>/MyApplication.java
HydraConfig hydraConfig = new HydraConfig.Builder(applicationContext)
    .setAccountId("{{account_id}}")
    .setDebugLevel(LogType.VERBOSE)
    .setRemoteDebugLevel(LogType.DEBUG)
    .setCaptureViewPortDetails(true)
    .setCountry("India")
    .setCity("Pune")
    .setCountryCode("91")
    .setBaseURL("{{base_url}}")
    .setSslPublicKey("{{ssl_public_key}}")
    .build();

HydraAPI.instanceWithConfig(applicationContext, hydraConfig);
```

| Builder method | Type | Description | Required |
|---|---|---|---|
| `accountId` | String | Account ID of the partner (`{{account_id}}`) | Mandatory |
| `.debugLevel` | LogType | Logging: OFF(-1), INFO(0), DEBUG(1), VERBOSE(2) | Optional |
| `.remoteDebugLevel` | LogType | Remote logging: OFF(-1), INFO(0), DEBUG(1) | Optional |
| `.captureViewPortDetails` | Boolean | Capture ViewPort information | Optional |
| `.country` / `.city` / `.countryCode` | String | Country name / city name / country code value | Optional |
| `.baseURL` | String | Base URL of region (`{{base_url}}`) | Optional |
| `.sslPublicKey` | String | Valid SSL public key of the URL (`{{ssl_public_key}}`) | Optional |
| `.fcmConfig` | FcmConfig | Firebase configuration (step 10) | Optional |
| `.notificationConfig` | NotificationConfig | Notification configuration (step 11) | Optional |
| `.notificationCenterConfig` | NotificationCenterConfig | Inbox fallback image (Modules › Inbox) | Optional |

`HydraConfig` also has `isDisableAppLaunchedEvent: Boolean`; no builder method for it is shown. Java snippets are omitted from steps 7, 8, 10, 11, 16, 17 and Modules › Push/In-App/Inbox to save space: the docs' Java equivalents call the same API methods; only the builder style differs (step 5 Gap). Gamification builder methods: step 14.

> ⚠️ Gap: the Java samples disagree. sdk-initialisation and push-notification use `new HydraConfig.Builder(applicationContext).setAccountId(...)` with `set…` methods; configure-notification-center and gamification-android use `new HydraConfig.Builder(context, accountId)` with unprefixed methods (`.baseURL(...)`, `.notificationCenterConfig(...)`). Ask a Capillary engineer which matches your SDK version.

> ⚠️ Gap: sdk-initialisation doesn't list `.orgId()`; whether this mode needs `{{org_id}}` in the builder isn't stated (it's passed in `updateRemoteConfig`, step 18). Ask a Capillary engineer.

If the SDK initialises after app start-up, initialise the console logger yourself: `HydraAPI.initializeConsoleLogger(LogType.Debug)`.

### 6. Register the Application class
```xml file=app/src/main/AndroidManifest.xml
<application
    android:name=".MyApplication"
    ... >
</application>
```

### 7. Report user sign-in, sign-up, profile update and sign-out
Give every user a unique identifier (`cuid`: phone, email or external ID) at sign-up and sign-in; it must match the Account Linking Identifier configured in Capillary CRM (`_shared/prerequisites.md`). Get the instance with `HydraAPI.getDefaultInstance(context)` (nullable).

```kotlin
hydraAPI?.pushUserSignin(
   "9000090000",
   "Henry",
   "Williams",
   "henrywill@gmail.com",
   "9000090000",
   mapOf("Age" to "25","Gender" to "Male"))
```

Without the optional details, pass empty values: `hydraAPI?.pushUserSignin("9000090000", "", "", "", "", emptyMap())` (Java: `Collections.emptyMap()`). `pushUserSignup(...)` (registration; also an optional `subscriptions` list) and `pushUserUpdate(...)` (profile update) take the same first six arguments; see API Reference.

Sign-out needs only the `cuid`; it can be used to erase previously logged user information:

```kotlin
hydraAPI?.pushUserSignOut(
   "9000090000",
)
```

Push opt-in preferences (promotional / transactional):

```kotlin
hydraAPI?.passUserPreferences(
   "9000090000", UserPreferences(promOpted, transOpted)
)
```

### 8. Track behavioural events (optional)
Create the event in Capillary first (Prerequisites). Events are valid **only after a sign-in or sign-up** and invalid after a sign-out. The event name must be non-null and non-empty; attributes are optional.

```kotlin
hydraAPI?.pushEvent("button Click",
mapOf("Username" to "Henry", "Age" to "25", "Gender" to "Male")
)
```

Without attributes: `hydraAPI?.pushEvent("Page/Activity successfully opened")`.

### 9. Request the notification permission (Android 13+)
From Android 13, push notifications are disabled by default; the app must ask the user. This helper shows the permission dialog, tracks the response and sets up the required notification channel:

```kotlin
HydraPushApi.getInstance().requestPushPermission(context)
```

### 10. Choose who registers the push token
By default the SDK registers for push tokens. Pick **one** option.

**A. The SDK handles push.** Enable token registration and add the SDK's messaging service:

```kotlin
val hydraConfig = HydraConfig.Builder(
   applicationContext,
   accountId = "{{account_id}}"
)
   .fcmConfig(FcmConfig(true))
   .build()
HydraAPI.instanceWithConfig(applicationContext, hydraConfig)
```

```xml file=app/src/main/AndroidManifest.xml
<service
   android:name="com.capillary.hydra.firebase.HydraFirebaseMessagingService"
   android:exported="false">
   <intent-filter>
       <action android:name="com.google.firebase.MESSAGING_EVENT" />
   </intent-filter>
</service>
```

**B. The app handles push** (it already has its own Firebase Messaging Service). You **must** opt out of the SDK's token registration:

```kotlin
val hydraConfig = HydraConfig.Builder(
   applicationContext,
   accountId = "{{account_id}}"
)
   .fcmConfig(FcmConfig(false))
   .build()
HydraAPI.instanceWithConfig(applicationContext, hydraConfig)
```

Then pass every new token from your service's `onNewToken`. Pass the latest token every time it changes (app restored on a new device, uninstall/reinstall, app data cleared), or push stops arriving:

```kotlin
override fun onNewToken(token: String) {
   HydraFirebaseAPI.getInstance().passPushToken(applicationContext, token)
}
```

And pass Hydra payloads from `onMessageReceived()`, checking first that they come from the Hydra platform:

```kotlin
if (HydraPushApi.getInstance().isFromHydraPlatform(remoteMessage.data)) {
   HydraFirebaseAPI.getInstance().passPushPayload(applicationContext, remoteMessage.data)
}
```

> ⚠️ Gap: the push page's prose spells the classes `HydraPushAPI` and `HydraFirebaseApi`, but its code uses `HydraPushApi` and `HydraFirebaseAPI` (used here). Ask a Capillary engineer if these don't resolve.

### 11. Set notification options (optional)
```kotlin
val hydraConfig = HydraConfig.Builder(
   applicationContext,
   accountId = "{{account_id}}"
)
   .notificationConfig(
       NotificationConfig(
           smallIcon = R.drawable.small_icon,
           notificationColor = R.color.teal_200,
           isMultipleNotificationInDrawerEnabled = true,
       )
   )
   .build()
HydraAPI.instanceWithConfig(applicationContext, hydraConfig)
```

| Parameter | Description |
|---|---|
| `smallIcon` | Resource ID for the notification small icon |
| `notificationColor` | Icon colour for the notification |
| `isMultipleNotificationInDrawerEnabled` | Default `true` (multiple notifications shown). Set `false` to show a single notification. |

The docs show each option in its own snippet; `.fcmConfig(...)` and `.notificationConfig(...)` are methods of the same `HydraConfig.Builder` as step 5.

### 12. Register the push listeners in `Application.onCreate()`
Add listeners in `onCreate()` of the Application class, after `HydraAPI` is initialised, so callbacks arrive even when the app is in the background. **The push notification listener is mandatory.**

```kotlin
class ApplicationPushMessageListener: HydraPushNotificationListener {
    private val TAG = HydraPushNotificationListener::class.java.name

    override fun onNotificationReceived(context: Context, payload: Bundle) {
        super.onNotificationReceived(context, payload)
    }

    override fun onNotificationShown(context: Context, payload: Bundle) {
        super.onNotificationShown(context, payload)
    }

    override fun onNotificationClick(context: Context, payload: NotificationPayload, cta: CTA ? ): Boolean {
        return super.onNotificationClick(context, payload, cta)
    }
    override fun onNotificationDismissed(context: Context, payload: Bundle) {
        super.onNotificationDismissed(context, payload)
    }
    override fun handleCustomAction(context: Context, payload: Bundle) {
        super.handleCustomAction(context, payload)
    }
}
```

```kotlin
HydraPushApi.getInstance()
    .registerPushNotificationListener(ApplicationPushMessageListener())
```

```java
HydraPushApi.getInstance()
   .registerPushNotificationListener(new ApplicationPushMessageListener());
```

`onNotificationClick` returns `false` → the SDK performs the action; `true` → your app handles it.

**Token callback (optional, when the SDK handles push):** called when a token is registered or refreshed.

```kotlin
class ApplicationTokenListener : TokenAvailableListener {
   private val TAG = ApplicationTokenListener::class.java.name

   override fun onTokenAvailable(token: Token) {
       Log.w(TAG, "Application Token $token")
   }
}
```

```kotlin
HydraFirebaseAPI.getInstance().addTokenListener(ApplicationTokenListener())
```

Java imports: `com.capillary.hydra.sdk.entity.Token`, `com.capillary.hydra.sdk.listeners.TokenAvailableListener`.

**Non-Hydra payload callback (optional):** for push payloads from servers other than Capillary.

```kotlin
class ApplicationPayloadListener : NonHydraPushListener {
   override fun onPushReceived(remoteMessage: RemoteMessage) {
       val pushNotificationPayload = remoteMessage.data
       Log.w(TAG, "Application Push Payload $pushNotificationPayload")
   }
}
```

```kotlin
HydraFirebaseAPI.getInstance().addNonHydraPushListener(ApplicationPayloadListener())
```

```java
HydraFirebaseAPI.getInstance().addNonHydraPushListener(new ApplicationPayloadListener());
```

Java import: `com.capillary.hydra.firebase.NonHydraPushListener`.

> ⚠️ Gap: the push page names the `NonHydraPushListener` method two ways: `onPushReceived(RemoteMessage)` in the example class and `onNonHydraPushReceived(RemoteMessage)` in its inline Java sample. Ask a Capillary engineer.

### 13. Handle CTAs, deep links and rich push
- **Primary CTA:** one per push; runs when the user taps the notification body. Opens a URI in the browser or a deep link; if none is configured, the app's **launcher activity** opens.
- **Non-primary CTAs:** up to 3 buttons per push.
- **Deep links:** any valid `http`/`https` URL or custom URL (for example `cap://handleDeeplink/1234`) set on the campaign. The SDK sends it to the app in an intent, so the target activity needs an intent filter:

```xml file=app/src/main/AndroidManifest.xml
<activity android:name=".SignUpActivity" android:exported="true">
<!-- url examples: cap://checkdeeplink:888/anythingsuffix, cap://checkdeeplink:888/prefixanything -->
<intent-filter>
       <action android:name="android.intent.action.VIEW" />
       <category android:name="android.intent.category.DEFAULT" />
       <category android:name="android.intent.category.BROWSABLE" />
        <data
           android:host="checkdeeplink"
           android:pathPrefix="/prefix"
           android:pathSuffix="suffix"
           android:port="888"
           android:scheme="cap" />
   </intent-filter>
</activity>
```

- **Rich push templates (optional):** add `implementation("hydra.richnotification")` (catalog) or `implementation("com.capillary:hydra-richnotification:{{sdk_version}}")` (artifact) to `app/build.gradle`. For carousel timing, check and request the exact-alarm permission (Android 12+):

```kotlin
if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.S) {
    if (!AlarmPermissionUtils.canScheduleExactAlarms(context)) {
        // Optionally guide users to grant permission for better carousel timing
        AlarmPermissionUtils.requestExactAlarmPermission(context)
    }
}
```

`AlarmPermissionUtils.logExactAlarmStatus(context)` logs the current status for debugging.

### 14. Add the gamification Remote Config keys and pass them to `HydraConfig.Builder`
Add the three Remote Config keys (Prerequisites). Fetch them at runtime and apply them **conditionally**, because Remote Config values may not have loaded yet:

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

Variables: `accountId` = `{{account_id}}`, `baseURL` = `{{base_url}}` (Hydra), `sslPublicKey` = `{{ssl_public_key}}`; `writeKey` = `{{gamification_key}}`, `region` = `{{gamification_region}}`, `baseUrl` = `{{gamification_base_url}}`. `baseURL` and `baseUrl` are different values. The region arrives as a plain string and is matched case-insensitively: `valueOf(region.uppercase())` accepts `"in"`, `"IN"`, `"In"` as long as it matches a `GamificationRegion` member name once uppercased.

> ⚠️ Gap: the gamification page initialises with `HydraAPI.initialize(context, hydraConfig)`; sdk-initialisation, push-notification and configure-notification-center use `HydraAPI.instanceWithConfig(context, hydraConfig)` (step 5). Ask a Capillary engineer which to call when gamification is enabled.

### 15. Wire `GamificationUIManager`
Create and store it in the Application class right after SDK initialisation, and assign your `GamificationCallback` (Modules › Gamification) at the same time:

```kotlin file=app/src/main/java/<your-package>/MyApplication.kt
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

```java file=app/src/main/java/<your-package>/MyApplication.java
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

### 16. Report the current screen
In `Application.onCreate()`, for every activity:

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

**Important:** screen reporting is mandatory for screen-targeted campaigns (visibility and eligibility depend on the reported screen). Calling `onActivityDestroyed` is required to prevent memory leaks from attached entry-point views.

> ⚠️ Gap: where `initializeHydraSDK()` (step 15) is called relative to these callbacks isn't documented. Ask a Capillary engineer.

### 17. Handle the app foreground/background lifecycle
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

### 18. Handle late gamification keys from Remote Config
If the keys arrive **after** Hydra is initialised, pass them with `updateRemoteConfig`; the SDK lazily initialises gamification once the call succeeds. Then wire `GamificationUIManager` if it isn't created yet.

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

### 19. Set the Capillary token (required for Loyalty View)
Set the short-lived Capillary B2B token **before** the Loyalty View renders (before the screen is reported); without a valid token, loyalty content may not be displayed.

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

## Modules

### Push
Setup: steps 4 and 9–13. Capillary sends Android push through Firebase Cloud Messaging (FCM). Server side, what must match, and end-to-end testing: `_shared/push.md`.

**Delivery and campaign TTL.** If a push isn't delivered in real time (device offline, stale FCM token, connectivity), the SDK pulls it the next time the user opens the app. An undelivered notification stays eligible for the campaign Time-to-Live: **15 days by default**, configurable per organisation; within the TTL it can still arrive on app open even if the campaign has ended; after it, it's discarded. The TTL applies to promotional and transactional messages.

#### Xiaomi push amplification (deprecated)
> **Deprecated** (xiaomi-push-notification). For a new integration, ask your Capillary CSM for the recommended push amplification approach.

Sends each push through both Xiaomi Cloud Push and FCM; when one delivers, the other is suppressed, so the user gets it once. Steps as documented:
1. Register as a Xiaomi developer, create the app, note its Package name / App ID / AppKey / App Secret, and enable Push in the Mi Push Operational Console.
2. Download the Mi SDK into the app module's `libs` folder; in the app module's `build.gradle` add a `flatDir { dirs 'libs' }` repository under `android { repositories { … } }` and `implementation fileTree(include: ['*.aar'], dir: 'libs')`. With AGP 7.0.0+, also set `repositoriesMode.set(RepositoriesMode.PREFER_SETTINGS)` in `settings.gradle`'s `dependencyResolutionManagement`.
3. Add `implementation("hydra.mipushkit")` (catalog) or `implementation("com.capillary:hydra-mi-push-kit:x.x.x")` (artifact).
4. Download the helper class and broadcast receiver from `https://github.com/Capillary/push-amp-plus` into a package named `com.hydra.sdk.miPushKit`, and register the receiver:
   ```xml file=app/src/main/AndroidManifest.xml
   <receiver
       android:name="com.hydra.sdk.miPushKit.MiBroadcastReciever"
       android:exported="false">

       <intent-filter>
           <action android:name="com.xiaomi.mipush.RECEIVE_MESSAGE" />
       </intent-filter>

       <intent-filter>
           <action android:name="com.xiaomi.mipush.MESSAGE_ARRIVED" />
       </intent-filter>

       <intent-filter>
           <action android:name="com.xiaomi.mipush.ERROR" />
       </intent-filter>

   </receiver>
   ```
5. Where the app comes to the foreground: `MiPushHelper.initialiseMiPush(context, MI_APP_ID, MI_APP_KEY, Region);` (App-Id and App-Key from the Mi dashboard; Region = Mi data residency).
6. Only if your own receiver handles Mi tokens and messages: `HydraMiPushApi.getInstance().setDataRegion(context, MiRegion.valueOf(region.toString()));` (region from `MiPushClient.getAppRegion(context)`), `HydraMiPushApi.getInstance().passPushToken(context, pushToken);`, and pass Hydra payloads after `HydraPushApi.getInstance().isFromHydraPlatform(remoteMessage)` with `HydraMiPushApi.getInstance().passPushPayload(context, remoteMessage);`.

> ⚠️ Gap: the `hydra-mi-push-kit` version isn't listed in Getting Started. Ask a Capillary engineer.

### In-App
Delivered through Hydra's push mechanism: **the push module (steps 9–12) must already be integrated.** Supported layouts: Header, Footer, Popup, Interstitial.

1. Add `implementation("hydra.inapp")` (catalog) or `implementation("com.capillary:hydra-inapp:{{sdk_version}}")` (artifact) to `app/build.gradle`.
2. Fallback image if the payload image fails to download: `InAppConfig(@DrawableRes val defaultImage: Int)` (`defaultImage`: resource ID of the fallback drawable, mandatory).
3. Register the click listener in `Application.onCreate()` after initialising Hydra. **Mandatory** for custom actions on message click. Return `false` → the SDK performs the action; `true` → your app handles it.

```kotlin
class ApplicationInAppMessageClickListener : OnMessageClickListener {
  override fun onMessageClick(context: Context, cta: CTA): Boolean {
       return super.onMessageClick(context, cta)
   }
}
```

```kotlin
HydraInAppUIHelper.getInstance()
   .registerOnMessageClickListener(ApplicationInAppMessageClickListener())
```

`triggerInAppOnLaunch(currentActivity: Activity)` manually triggers in-app messages after the SDK initialises; it's meant for Flutter apps whose activity callbacks (e.g. `onResume`) are lost through late initialisation.

> ⚠️ Gap: how `InAppConfig` is passed to the SDK (no `HydraConfig.Builder` method is shown) and which object `triggerInAppOnLaunch` is called on aren't documented. Ask a Capillary engineer.

### Inbox
The Notification Center lists the push notifications the user has received.

1. Add `implementation("hydra.inbox.core")` and `implementation("hydra.inbox.ui")` (catalog), or `implementation("com.capillary:hydra-inbox-core:{{sdk_version}}")` and `implementation("com.capillary:hydra-inbox-ui:{{sdk_version}}")` (artifact).
2. Set a fallback image (shown when a notification's image fails to download) during SDK initialisation:

```kotlin
val hydraConfig = HydraConfig.Builder(
   applicationContext,
   accountId = "{{account_id}}"
)
   .notificationCenterConfig(NotificationCenterConfig(R.drawable.notification_center_fallback))
.build()

HydraAPI.instanceWithConfig(applicationContext, hydraConfig)
```

3. **Default UI:** launch the SDK's activity (already declared in the SDK's manifest), or embed its fragment:

```kotlin
val inboxActivity = Intent(this, InboxActivity::class.java)
startActivity(inboxActivity)
```

```kotlin
private fun attachFragment() {
   try {
       supportFragmentManager.beginTransaction().replace(
           R.id.hydraInboxFragmentFrameLayout,
           InboxFragment(),
           "inboxFragment"
       ).commit()
   } catch (e: Exception) {
       Logger.v("loadInboxMessageFragment(): ")
   }
}
```

4. **Click listener** in `Application.onCreate()` after initialising Hydra. **Mandatory** for custom actions on inbox message click. Return `false` → the SDK performs the action; `true` → your app handles it.

```kotlin
HydraInboxUIHelper.getInstance()
   .registerOnMessageClickListener(ApplicationMessageClickListener())
```

The page's Kotlin sample of this class calls `super.onMessageClick(context, cta)`, but the parameter is `inboxMessage`.

5. **Inbox API** (your own UI), via `HydraInboxCoreApi.getInstance()`:

```kotlin
HydraInboxCoreApi.getInstance().getUnReadMessagesCount(
    this,
    object : UnReadCountListener {
        override fun onCountAvailable(unReadMessagesCount: Int) {
            // Handle the unread message count
        }
    }
)
```

Also `fetchInboxMessages(context, OnMessagesAvailableListener)`, `deleteInboxMessage(context, inboxMessage)`, `trackInboxMessageClick(context, inboxMessage)` (sends a click DLR event) and `deleteAllInboxMessages(context)` (API Reference).

> ⚠️ Gap: the callback method of `OnMessagesAvailableListener` and the fields of `InboxMessage` aren't documented. Ask a Capillary engineer.

6. **Customise the default UI.** `InboxActivity` inherits the app's default theme. Override these in your resources: `HydraInboxToolbarStyle` (parent `Theme.AppCompat`; toolbar title and `android:navigationIcon`; also `android:textColorPrimary`/`textColorSecondary`, `android:background`), `HydraInboxToolbarTextStyle` (unread count), `HydraInboxToolbarButtonStyle` ("CLEAR ALL"), colours `hydra_unread_message_background_color` / `hydra_read_message_background_color`, `HydraUnReadInboxTitleTextStyle` / `HydraReadInboxTitleTextStyle`, `HydraUnReadInboxMessageTextStyle` / `HydraReadInboxMessageTextStyle` (summary), `HydraUnReadInboxMessageTimeStyle` / `HydraReadInboxMessageTimeStyle` (timestamp), `HydraInboxEmptyBoxTextStyle` (empty state). Style items used: `android:textSize`, `android:textColor`, `android:fontFamily`, `android:textStyle`, plus `android:maxLines` (title 2, summary 3).

### Visitor
> ⚠️ Gap: the visitor flow isn't documented for Android. Ask a Capillary engineer.

### Gamification
Setup: steps 14–19. **Automatic** (no extra code): Floating Button, Popup and Bottom Sheet campaigns appear on any reported screen, per the targeting rules in the Gamification dashboard.

**Gamification callback (optional)**, assigned in steps 15 and 18; raw lifecycle and analytics events without UI:

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

> ⚠️ Gap: the fields of `GamificationError` and `EntryPointData` aren't documented (the gamification page itself marks them "TBD — confirm with dev"). Ask a Capillary engineer.

**Custom views (optional, in XML layouts).** Each `android:id` must correspond to the ID configured in the campaign dashboard (for the Loyalty View, the `embedId` from the API response). In this mode **all three** are bound and rendered automatically by `GamificationUIManager` once `onScreenChanged` is called; no extra code. Call `setCapToken(...)` (step 19) before the screen is reported, for the Loyalty View.

```xml
<com.capillary.hydra.gamification.ui.entrypoints.BannerView
    android:id="@+id/{{banner_id}}"
    android:layout_width="match_parent"
    android:layout_height="wrap_content" />

<com.capillary.hydra.gamification.ui.entrypoints.EmbedWebView
    android:id="@+id/{{embed_id}}"
    android:layout_width="match_parent"
    android:layout_height="wrap_content" />

<com.capillary.hydra.gamification.ui.entrypoints.LoyaltyEmbedView
    android:id="@+id/{{loyalty_id}}"
    android:layout_width="match_parent"
    android:layout_height="match_parent" />
```

The Firebase and no-Firebase paths differ on purpose in dependencies, initialisation and the Embedded View's binding (no-Firebase needs `bindEmbedView()`; this mode doesn't).

> ⚠️ Gap: which API response returns the Loyalty `embedId` isn't documented. Ask a Capillary engineer.

## Verification
- **Init:** no exception at `instanceWithConfig` (an exception means `accountId` is missing). Set `.debugLevel(LogType.VERBOSE)` for SDK logs.
- **Push:** with the SDK handling push, `TokenAvailableListener.onTokenAvailable(token)` fires when a token is registered or refreshed. `HydraPushNotificationListener` gets `onNotificationReceived`, `onNotificationShown`, `onNotificationClick`, `onNotificationDismissed`. End-to-end test: `_shared/push.md` › Test the push flow.
- **Inbox:** `getUnReadMessagesCount` → `onCountAvailable(unReadMessagesCount)`; the Notification Center tracks opens, views and deletions.
- **Gamification:** `onInitSuccess()` / `onInitFailure(GamificationError)`; `onEntryPointsLoaded(...)` when entry points are ready; `updateRemoteConfig(...)` returns `true` on success. Floating Button, Bottom Sheet and Popup campaigns appear automatically; Banner, Embedded, Loyalty content if added.
- **Gamification checklist (required):** SDK at the minimum version; the three Remote Config keys (base URL optional); `GamificationUIManager` wired after init; `onScreenChanged` and `onActivityDestroyed` in `ActivityLifecycleCallbacks`; `ProcessLifecycleOwner` observer; `setCapToken(token)` for the Loyalty View. Optional: callback, Banner, Embedded, Loyalty views.

> ⚠️ Gap: no Logcat lines for a successful init or token registration are documented for Android. Ask a Capillary engineer.

## Known Issues
| Symptom | Cause | Fix |
|---|---|---|
| SDK throws an exception at initialisation | `accountId` not provided to `HydraConfig.Builder` | Pass `{{account_id}}` (step 5) |
| Gradle can't resolve `com.capillary:hydra-core` (401/403 from `maven.pkg.github.com`); derived from the prerequisites, not a reported case | PAT lacks `read:packages`, no access to `Capillary/hydra-sdk-android-maven`, or `github.properties` missing / wrong keys | Use a PAT with `read:packages`; confirm repo access with Capillary; keep `github.properties` next to `settings.gradle` (steps 1–2) |
| No notifications on Android 13+ | Notifications are disabled by default from Android 13 | Call `HydraPushApi.getInstance().requestPushPermission(context)` (step 9) |
| App has its own Firebase Messaging Service and push is mishandled | SDK token registration not opted out | Use `FcmConfig(false)` and pass tokens and Hydra payloads yourself (step 10 B) |
| Push stops after a reinstall, a restore on a new device or cleared app data (app handles push) | The FCM token changed and the new one wasn't passed | Pass every `onNewToken` token with `passPushToken` (step 10 B) |
| Other servers' payloads reach the SDK | `passPushPayload` called without checking the source | Wrap it in `isFromHydraPlatform(...)` (step 10 B) |
| Push callbacks missing while the app is in the background | Listeners not registered in `Application.onCreate()` | Register them there, after init (step 12) |
| Your custom click handling never runs / SDK opens the CTA anyway | `onNotificationClick` / `onMessageClick` returned `false`, or the listener isn't registered | Return `true` to handle it in the app (step 12, Modules) |
| Tapping a push opens the launcher activity | No primary CTA URI / deep link on the campaign | Expected; set a CTA, and add the intent filter for custom schemes (step 13) |
| Deep link doesn't open the target activity | No matching `intent-filter` in the manifest | Add it (step 13) |
| Only one notification shows in the drawer | `isMultipleNotificationInDrawerEnabled = false` | Set it to `true` (default) (step 11) |
| A push arrives late, on app open, even after its campaign ended | Real-time delivery failed; the SDK pulled it within the campaign TTL (15 days default) | Expected (Modules › Push) |
| Behavioural events don't show up | Sent before sign-in/sign-up or after sign-out, or the event isn't created in org settings | Sign the user in first; create the event in Capillary (step 8) |
| In-app messages never appear | Push module not integrated | Integrate push (steps 9–12) before In-App |
| Inbox or in-app images missing | Image download failed and no fallback set | Set `NotificationCenterConfig` / `InAppConfig` fallback image |
| Memory leaks from entry-point views | `onActivityDestroyed` not forwarded | Call `gamificationUIManager?.onActivityDestroyed(activity)` (step 16) |
| Screen-targeted campaigns don't appear | Current screen not reported | Register the `onScreenChanged` callbacks (step 16) |
| Loyalty View empty | No valid token set before render | Call `setCapToken(token)` first (step 19) |
| Gamification keys arrive via Remote Config after Hydra is initialised | Hydra initialised before `hydra_gamification_*` values were available | Call `HydraAPI.updateRemoteConfig(...)`, then wire `GamificationUIManager` if null (step 18) |
| SDK log shows `Client Credentials Generation Failed` / `{"error":"source not found","status":400}` | The App Signature registered at Capillary (MAPP_SDK) doesn't match the signature of the build being run | Compare the build's SHA256 with the registered one and ask Capillary to update it (`_shared/push.md`) |
| Push never arrives although sign-in works | The app's Firebase project isn't the one registered at Capillary, or the push gateway isn't set up yet | Follow `_shared/push.md` › Test the push flow and › Common problems |

## API Reference
Signatures are in the steps above; this is the index. Kotlin names as documented; `HydraAPI.getDefaultInstance(context)` returns the nullable instance.

| Area | APIs |
|---|---|
| Init | `HydraConfig.Builder(context, accountId)` (methods: step 5; gamification: `.gamificationWriteKey()`, `.gamificationBaseUrl()`, `.gamificationRegion(GamificationRegion)`), `HydraAPI.instanceWithConfig(context: Context, config: HydraConfig): HydraAPI`, `HydraAPI.initialize(context, config)` (step 14 Gap), `HydraAPI.initializeConsoleLogger(LogType.Debug)` (other samples write `LogType.DEBUG`), `HydraAPI.updateRemoteConfig(orgId, accountId, baseURL, sslPublicKey, gamificationWriteKey, gamificationRegion, gamificationBaseUrl): Boolean` |
| Users and events | `pushUserSignin(cuid: String, firstName: String? = null, lastName: String? = null, email: String? = null, phone: String? = null, customData: Map<String, Any>? = null)`; `pushUserSignup(cuid, firstName, lastName, email, phone: String, customData: Map<String, Any>?, subscriptions: List<Any>?)` (all mandatory but the last two; `subscriptions`: channel, accountId, priority, type, sourcename; the Java signature has no `subscriptions`); `pushUserUpdate(...)` (same as sign-in); `pushUserSignOut(cuid: String)`; `passUserPreferences(cuid: String, userPreference: UserPreferences)` with `UserPreferences(promPushOpted: Boolean, transPushOpted: Boolean)` (null `cuid` uses the stored CUID); `pushEvent(eventName: String, attributes: Map<String, Any>? = null)`; `setCapToken(token)` |
| Push | `FcmConfig(Boolean)`, `NotificationConfig(smallIcon, notificationColor, isMultipleNotificationInDrawerEnabled)`, `HydraPushApi.getInstance()`: `requestPushPermission(context)`, `isFromHydraPlatform(data)`, `registerPushNotificationListener(HydraPushNotificationListener)` (`onNotificationReceived(context, payload: Bundle)`, `onNotificationShown(context, payload: Bundle)`, `onNotificationClick(context, payload: NotificationPayload, cta: CTA?): Boolean`, `onNotificationDismissed(context, payload: Bundle)`, `handleCustomAction(context, payload: Bundle)`); `HydraFirebaseAPI.getInstance()`: `passPushToken(context, token)`, `passPushPayload(context, data)`, `addTokenListener(TokenAvailableListener)` (`onTokenAvailable(token: Token)`), `addNonHydraPushListener(NonHydraPushListener)`; manifest service `com.capillary.hydra.firebase.HydraFirebaseMessagingService`; `AlarmPermissionUtils.canScheduleExactAlarms(context)` / `.requestExactAlarmPermission(context)` / `.logExactAlarmStatus(context)`; Xiaomi (deprecated): `MiPushHelper.initialiseMiPush(...)`, `HydraMiPushApi.getInstance().setDataRegion(...)` / `.passPushToken(...)` / `.passPushPayload(...)` |
| In-App | `InAppConfig(@DrawableRes defaultImage: Int)`, `HydraInAppUIHelper.getInstance().registerOnMessageClickListener(listener)` (`OnMessageClickListener.onMessageClick(context: Context, cta: CTA): Boolean`), `triggerInAppOnLaunch(currentActivity: Activity)` |
| Inbox | `NotificationCenterConfig(@DrawableRes defaultImage: Int)`, `InboxActivity`, `InboxFragment`, `HydraInboxUIHelper.getInstance().registerOnMessageClickListener(listener)` (`onMessageClick(context: Context, inboxMessage: InboxMessage): Boolean`), `HydraInboxCoreApi.getInstance()`: `getUnReadMessagesCount(context, UnReadCountListener)`, `fetchInboxMessages(context, OnMessagesAvailableListener)`, `deleteInboxMessage(context, inboxMessage)`, `trackInboxMessageClick(context, inboxMessage)`, `deleteAllInboxMessages(context)` |
| Gamification | `getGamificationManager()` (`GamificationFlowManager`, nullable; `.callback` / `setCallback(...)`), `GamificationUIManager(flowManager, context)`: `.onScreenChanged(activity, screenName)`, `.onActivityDestroyed(activity)`, `.onAppForegrounded()`, `.onAppBackgrounded()`; `GamificationCallback`: `onInitSuccess()`, `onInitFailure(GamificationError)`, `onEntryPointsLoaded(List<EntryPointData>)`, `onCampaignOpened(campaignId)`, `onCampaignClosed(campaignId)`, `onAnalyticsEvent(eventName, data)`; views in `com.capillary.hydra.gamification.ui.entrypoints`: `BannerView`, `EmbedWebView`, `LoyaltyEmbedView` |
