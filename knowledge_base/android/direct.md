---
platform: android
config_mode: direct
sdk_package: com.capillary:hydra-core
sdk_version: 1.9.22-beta02
modules_covered: [core, inbox_api, inbox_ui, gamification]
modules_missing: [inapp, visitor, multi_account]
sources: ["Capillary developer docs (docs.capillarytech.com): gamification-android Option B (updated 2026-08-18), android-sdk-getting-started (updated 2026-11-12), installing-sdk, sdk-initialisation, android-sdk-api-reference, configure-notification-center (updated 2026-03-25), in-app-messaging (updated 2026-10-20)", "Integration document _ Experience+ pp.100–112 (Hydra Android SDK Integration Guide, Without Firebase)"]
owner: TBD
last_verified: null
review_status: draft   # drafted from the source docs; not yet SME-verified
---
# Android (without Firebase)

## Coverage
The app doesn't use Firebase: all values come from Capillary and are passed in code. Kotlin and Java (some gamification wiring is Kotlin-only in the docs).

| Module | Status in this mode |
|---|---|
| Core (install, init, sign-in/up/update/out, behavioural events) | Documented (steps 1–8) |
| Gamification (automatic campaigns, Banner, Embed, Loyalty, screen tracking) | Documented (steps 9–10, Modules) |
| Inbox (`hydra-inbox-core`, `hydra-inbox-ui`) | Documented (Modules › Inbox); see the Gap there |
| In-App (`hydra-inapp`) | Dependency listed, but the In-App page requires the push module (Modules › In-App) |
| Push | **Not available in this mode.** Needs Firebase (`android/firebase.md`). |
| Visitor, multi-account | Not documented |

## Requirements
- Hydra SDK `{{sdk_version}}` (Beta, for UAT/POC) or later.
- Gradle settings file using `dependencyResolutionManagement` (step 2).
- From Getting Started (android-sdk-getting-started): Android SDK version V21 or above (minSdk 21), targetSdkVersion 34, compileSdkVersion 34. (Its "Google Firebase account" prerequisite is for the Firebase integration, not this mode.)

> ⚠️ Gap: AGP, Kotlin and exact Gradle versions aren't documented. Ask a Capillary engineer.

## Prerequisites
Common exchange: `_shared/prerequisites.md`. For this mode:
- **Client gives Capillary:** the Android application ID (package name), and the app signature (SHA256 from the signing report; see the Gap below).
- **Capillary gives client:** Account Id (the Source Account Id of your MAPP_SDK account), Base URL (specific to your Capillary cluster), SSL Public Key, Org Id, Gamification Key, Gamification Region (`IN`, `US` or `ME`), Gamification URL (optional).
- **Repository access** (request from Capillary's access team): read access to `https://github.com/Capillary/hydra-sdk-android-maven`, plus a GitHub username and a Personal Access Token (PAT) with the **`read:packages`** scope.
- **Behavioural events** you send with `pushEvent` must first be created in Capillary: *Organisation settings > Master Data Management > Data Model > Behavioural events*.

> ⚠️ Gap: the older source of this guide doesn't list the app signature as a client item, but Capillary registers an App Signature for every Android app and a mismatch stops the SDK (`_shared/prerequisites.md`). Send it and confirm with Capillary.

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

For CI/CD, generate `github.properties` from secrets before the Gradle build.

> ⚠️ Gap: the install page (installing-sdk) writes the values in quotes (`username="USERNAME"`, `token="TOKEN"`); the gamification page shows them unquoted (above). Ask a Capillary engineer if Gradle can't authenticate.

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
Only `hydra-core` is required. Use the SDK version provided by the Capillary team.

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

> ⚠️ Gap: the standard install page (installing-sdk) also adds AndroidX libraries (`androidx.core:core`, `androidx.appcompat:appcompat`, `androidx.lifecycle:lifecycle-process`, versions shown only as `xxx`); this mode's guide doesn't list them, though step 9 uses `ProcessLifecycleOwner`. Ask a Capillary engineer whether and at which versions to add them.

### 4. Initialise the SDK in `Application.onCreate()`
Pass the values from Capillary as literals, including the region as an actual `GamificationRegion` enum member (not a string). `accountId` is mandatory: **if it isn't provided, the SDK throws an exception**.

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

Other optional builder methods (sdk-initialisation):

| Builder method | Type | Description |
|---|---|---|
| `.debugLevel` | LogType | Logging: OFF(-1), INFO(0), DEBUG(1), VERBOSE(2) |
| `.remoteDebugLevel` | LogType | Remote logging: OFF(-1), INFO(0), DEBUG(1) |
| `.captureViewPortDetails` | Boolean | Capture ViewPort information |
| `.country` / `.city` / `.countryCode` | String | Country name / city name / country code value |
| `.notificationCenterConfig` | NotificationCenterConfig | Inbox fallback image (Modules › Inbox) |

> ⚠️ Gap: sdk-initialisation's Java sample uses a different builder style, `new HydraConfig.Builder(applicationContext).setAccountId(...)` with `set…` methods (`setBaseURL`, `setSslPublicKey`, `setDebugLevel` …), not the `new HydraConfig.Builder(context, accountId).orgId(...)` form above. Ask a Capillary engineer which matches your SDK version.

If the SDK initialises after app start-up, initialise the console logger yourself: `HydraAPI.initializeConsoleLogger(LogType.Debug)`.

### 5. Register the Application class
```xml file=app/src/main/AndroidManifest.xml
<application
    android:name=".MyApplication"
    ... >
</application>
```

### 6. Report user sign-in and sign-out
Give every user a unique identifier (`cuid`: phone, email or external ID) at sign-up and sign-in. It's required and must match the Account Linking Identifier configured in Capillary CRM (`_shared/prerequisites.md`). The other fields are optional.

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

Without the optional details, pass empty values: `hydraAPI?.pushUserSignin("9000090000", "", "", "", "", emptyMap())` (Java: `Collections.emptyMap()`).

Sign-out needs only the `cuid`; it can be used to erase previously logged user information:

```kotlin
hydraAPI?.pushUserSignOut(
   "9000090000",
)
```

```java
if (hydraAPI != null) {
    hydraAPI.pushUserSignOut("9000090000");
}
```

> ⚠️ Gap: the API reference (android-sdk-api-reference) documents `pushUserSignOut(cuid: String)`, while the without-Firebase guide (Integration document pp.100–112) shows `pushUserSignout()` with no argument. Ask a Capillary engineer which one your SDK version has.

### 7. Report sign-up and profile updates
```kotlin
hydraAPI?.pushUserSignup(
   "9000090000",
   "Henry",
   "Williams",
   "henrywill@gmail.com",
   "9000090000",
   mapOf("Age" to "25","Gender" to "Male")
)
```

```java
if (hydraAPI != null) {
    hydraAPI.pushUserSignup(
        "9000090000",
        "Henry",
        "Williams",
        "henrywill@gmail.com",
        "9000090000",
        Map.of("Age", "25", "Gender", "Male")
    );
}
```

`pushUserUpdate(...)` takes the same six arguments (only `cuid` mandatory). Signatures: API Reference.

### 8. Custom behavioural events (optional)
Create the event in Capillary first (Prerequisites). Events are valid **only after a sign-in or sign-up** and invalid after a sign-out. The event name must be non-null and non-empty; attributes are optional.

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

Without attributes: `hydraAPI?.pushEvent("Page/Activity successfully opened")`.

### 9. Report the current screen (required for gamification)
Add in `Application.onCreate()` after SDK initialisation. **Screen reporting is mandatory for screen-targeted campaigns**: campaign visibility and eligibility depend on the reported screen. The docs show this wiring in Kotlin only.

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

### 10. Set the Capillary token (required for Loyalty View)
Set the short-lived Capillary B2B token **before** the Loyalty View renders (before the screen is reported); without a valid token, loyalty content may not be displayed.

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

> ⚠️ Gap: the In-App page (in-app-messaging) says Hydra delivers in-app messages through its push mechanism, so the app must already have Hydra's push module integrated; push isn't available in this mode, yet this mode's guide lists `hydra-inapp` as optional. Ask a Capillary engineer whether In-App works without Firebase.

### Inbox
The Notification Center lists the push notifications the user has received.

> ⚠️ Gap: this mode's guide lists the Inbox modules as optional, but the Notification Center is described as a list of received push notifications and push isn't available here. Ask a Capillary engineer what the Inbox shows without Firebase.

1. Add `hydra-inbox-core` and `hydra-inbox-ui` (step 3).
2. Set a fallback image (shown when a notification's image fails to download) on the builder from step 4:

```kotlin
   .notificationCenterConfig(NotificationCenterConfig(R.drawable.notification_center_fallback))
```

```java
    .notificationCenterConfig(new NotificationCenterConfig(R.drawable.notification_center_fallback))
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

```java
public class ApplicationMessageClickListener implements OnMessageClickListener {
    @Override
    public boolean onMessageClick(Context context, InboxMessage inboxMessage) {
        return super.onMessageClick(context, inboxMessage);
    }
}
```

```kotlin
HydraInboxUIHelper.getInstance()
   .registerOnMessageClickListener(ApplicationMessageClickListener())
```

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

6. **Customise the default UI.** `InboxActivity` inherits the app's default theme. Override these resources: `HydraInboxToolbarStyle` (parent `Theme.AppCompat`; toolbar title and navigation icon), `HydraInboxToolbarTextStyle` (unread count), `HydraInboxToolbarButtonStyle` ("CLEAR ALL"), colours `hydra_unread_message_background_color` / `hydra_read_message_background_color`, `HydraUnReadInboxTitleTextStyle` / `HydraReadInboxTitleTextStyle`, `HydraUnReadInboxMessageTextStyle` / `HydraReadInboxMessageTextStyle` (summary), `HydraUnReadInboxMessageTimeStyle` / `HydraReadInboxMessageTimeStyle` (timestamp), `HydraInboxEmptyBoxTextStyle` (empty state). The docs set `android:textSize`, `android:textColor`, `android:fontFamily`, `android:textStyle` (plus `android:maxLines` for title/summary; `android:background` for the toolbar and empty box; `android:textColorPrimary`, `android:textColorSecondary`, `android:navigationIcon` for the toolbar).

### Visitor
> ⚠️ Gap: the visitor flow isn't documented for this mode. Ask a Capillary engineer.

### Gamification
**Automatic experiences** (no extra code after steps 1–10): Floating Button, Popup and Bottom Sheet campaigns appear on any reported screen. Hydra evaluates eligibility and displays them.

**Custom UI components** (optional, in XML layouts). The Banner and Loyalty `android:id` must correspond to the ID configured in the campaign dashboard (for the Loyalty View, the `embedId` from the API response).
- **Banner View:** rendered automatically when `onScreenChanged()` reports the screen; no manual binding.
  ```xml
  <com.capillary.hydra.gamification.ui.entrypoints.BannerView
      android:id="@+id/{{banner_id}}"
      android:layout_width="match_parent"
      android:layout_height="wrap_content" />
  ```
- **Embed View:** in this mode it needs explicit binding via `bindEmbedView()`.
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
- **Loyalty View:** rendered automatically when `onScreenChanged()` reports the screen. Call `setCapToken(...)` (step 10) before the screen is reported.
  ```xml
  <com.capillary.hydra.gamification.ui.entrypoints.LoyaltyEmbedView
      android:id="@+id/{{loyalty_id}}"
      android:layout_width="match_parent"
      android:layout_height="match_parent" />
  ```
  > ⚠️ Gap: which API response returns the Loyalty `embedId` isn't documented. Ask a Capillary engineer.

## Verification
Expected result: Floating Button, Bottom Sheet and Popup campaigns appear automatically; Banner, Embed and Loyalty content too if those views were added. Inbox: `getUnReadMessagesCount` → `onCountAvailable(unReadMessagesCount)`.

**Required checklist:**
- `github.properties` created and git-ignored; GitHub Packages repo in `settings.gradle`.
- `hydra-core` in `app/build.gradle`, on the minimum SDK version (`{{sdk_version}}`).
- SDK initialised in `Application.onCreate()` via `HydraConfig.Builder`; Application class registered in `AndroidManifest.xml`.
- Gamification key, region and base URL (optional) set.
- Screen names reported via `GamificationUIManager`.
- `setCapToken(...)` called (required for Loyalty View).
- No Google Services plugin, Firebase dependencies or `google-services.json`.

**Optional:** `hydra-inapp`; `hydra-inbox-core` + `hydra-inbox-ui`; Banner, Embed (bound with `bindEmbedView()`), Loyalty views; CI/CD generates `github.properties` from secrets.

> ⚠️ Correction: ✅ Use `HydraConfig.Builder` (`.gamificationWriteKey()`, `.gamificationRegion()`, `.gamificationBaseUrl()`, step 4) for the gamification values. ❌ Don't use `hydra_gamification_key` / `hydra_gamification_region` / `hydra_gamification_base_url` Remote Config keys in this mode (Option B checklist in gamification-android, and Integration document p.111). *Pending SME confirmation.*

> ⚠️ Gap: no log lines or callbacks confirm successful initialisation in this mode (`debugLevel(LogType.DEBUG)` only enables debug logging). Ask a Capillary engineer.

## Known Issues

**Gradle can't resolve `com.capillary:hydra-core` (401/403 from `maven.pkg.github.com`)** — derived from the prerequisites, not a reported case.
- Cause: GitHub Packages rejected the credentials: PAT lacks `read:packages`, the account has no access to `Capillary/hydra-sdk-android-maven`, or `github.properties` is missing / has wrong keys (`username`, `token`).
- Fix: use a PAT with `read:packages`; confirm repo access with Capillary's access team; keep `github.properties` next to `settings.gradle`.

**CI builds can't resolve the SDK**
- Cause: `github.properties` is git-ignored, so it doesn't exist on CI.
- Fix: generate `github.properties` from CI secrets before the Gradle build (listed in the source checklist).

**SDK throws an exception at initialisation** → `accountId` not provided to `HydraConfig.Builder` → pass `{{account_id}}` (step 4).

**SDK log shows `Client Credentials Generation Failed` / `source not found` (400)** → (Android) the App Signature registered at Capillary doesn't match the build's signature → compare the build's SHA256 with the registered one and ask Capillary to update it (see `_shared/troubleshooting.md` section 2).

**Behavioural events don't show up** → sent before sign-in/sign-up or after sign-out, or the event isn't created in org settings → sign the user in first; create the event in Capillary (step 8).

**Screen-targeted campaigns don't appear** → current screen not reported → register the `onScreenChanged` callbacks (step 9).

**Memory leaks from entry-point views** → `onActivityDestroyed` not forwarded → call `gamificationUIManager?.onActivityDestroyed(activity)` (step 9).

**Loyalty View empty** → no valid token before render → call `setCapToken(token)` first (step 10).

**Embed View stays empty** → in this mode it isn't bound automatically → call `bindEmbedView(...)` (Modules › Gamification).

**Inbox images missing** → image download failed and no fallback set → set `NotificationCenterConfig` (Modules › Inbox).

## API Reference
| API | Purpose |
|---|---|
| `HydraConfig.Builder(context, accountId)` | SDK config: `.orgId()`, `.baseURL()`, `.sslPublicKey()`, `.debugLevel(LogType)`, `.remoteDebugLevel(LogType)`, `.captureViewPortDetails()`, `.country()`, `.city()`, `.countryCode()`, `.notificationCenterConfig()`, `.gamificationWriteKey()`, `.gamificationRegion(GamificationRegion.IN/US/ME)`, `.gamificationBaseUrl()`, `.build()` |
| `HydraAPI.instanceWithConfig(context: Context, config: HydraConfig): HydraAPI` | Initialises the SDK; both parameters mandatory |
| `HydraAPI.getDefaultInstance(context)` | SDK instance (nullable) |
| `HydraAPI.initializeConsoleLogger(LogType.Debug)` | Console logger when the SDK initialises after app start-up (other samples write `LogType.DEBUG`) |
| `pushUserSignin(cuid: String, firstName: String? = null, lastName: String? = null, email: String? = null, phone: String? = null, customData: Map<String, Any>? = null)` | Sign-in; only `cuid` mandatory |
| `pushUserSignup(cuid: String, firstName: String, lastName: String, email: String, phone: String, customData: Map<String, Any>?, subscriptions: List<Any>?)` | Registration; `customData`, `subscriptions` (channel, accountId, priority, type, sourcename) optional. The Java signature has no `subscriptions` |
| `pushUserUpdate(cuid: String, firstName: String? = null, lastName: String? = null, email: String? = null, phone: String? = null, customData: Map<String, Any>? = null)` | Profile update |
| `pushUserSignOut(cuid: String)` | Sign-out (step 6 Gap) |
| `passUserPreferences(cuid: String, userPreference: UserPreferences)` | Push opt-in preferences: `UserPreferences(promPushOpted: Boolean, transPushOpted: Boolean)`; null `cuid` uses the stored CUID |
| `pushEvent(eventName: String, attributes: Map<String, Any>? = null)` | Custom event |
| `setCapToken(token)` | Capillary B2B token for Loyalty View |
| `getGamificationManager()` | Manager passed to `GamificationUIManager` |
| `GamificationUIManager(manager, context)` | `.onScreenChanged(activity, name)`, `.onActivityDestroyed(activity)`, `.onAppForegrounded()`, `.onAppBackgrounded()`, `.bindEmbedView(view, entryPointId, owner)` |
| Views (`com.capillary.hydra.gamification.ui.entrypoints`) | `BannerView`, `EmbedWebView`, `LoyaltyEmbedView` |
| `NotificationCenterConfig(@DrawableRes defaultImage: Int)` | Inbox fallback image (mandatory parameter) |
| `InboxActivity`, `InboxFragment` | Default Notification Center UI |
| `HydraInboxUIHelper.getInstance().registerOnMessageClickListener(listener)` | `OnMessageClickListener.onMessageClick(context: Context, inboxMessage: InboxMessage): Boolean` |
| `HydraInboxCoreApi.getInstance()` | `getUnReadMessagesCount(context, UnReadCountListener)`, `fetchInboxMessages(context, OnMessagesAvailableListener)`, `deleteInboxMessage(context, inboxMessage)`, `trackInboxMessageClick(context, inboxMessage)`, `deleteAllInboxMessages(context)` |
