---
platform: android
config_mode: direct
sdk_package: com.capillarytech:hydra-core
sdk_version: 1.10.6
modules_covered: [core, inbox_api, inbox_ui, gamification]
modules_missing: [inapp, visitor, multi_account]
sources: ["Capillary developer docs (docs.capillarytech.com): gamification-android Option B and Game and CMS event payloads (updated 2026-11-23), android-sdk-getting-started (updated 2026-11-12), installing-sdk (updated 2026-11-12), set-up-source-account (updated 2026-11-12), in-app-messaging (updated 2026-11-12), configure-notification-center (updated 2026-11-12), sdk-initialisation (updated 2026-03-25), android-sdk-api-reference (updated 2026-03-25)", "Integration document _ Experience+ pp.100–112 (Hydra Android SDK Integration Guide, Without Firebase)"]
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
- Hydra SDK `{{sdk_version}}` or later. This is the minimum version for gamification (gamification-android) and the version the Getting Started table lists for every module.
- Gradle settings file using `dependencyResolutionManagement` (step 2).
- From Getting Started (android-sdk-getting-started): Android SDK version V21 or above (minSdk 21), targetSdkVersion 34, compileSdkVersion 34. (Its "Google Firebase account" prerequisite is for the Firebase integration, not this mode.)

> ⚠️ Correction: ✅ Use `1.10.6` as the SDK version (gamification-android: "Minimum SDK version: `1.10.6`"; installing-sdk and android-sdk-getting-started also use `1.10.6`). ❌ Don't use `1.9.22-beta02`, labelled Beta for UAT/POC, which an older internal Integration document gave as the gamification minimum. *Pending SME confirmation: an SME should confirm that no UAT or POC build still needs a beta version.*

> ⚠️ Gap: AGP, Kotlin and exact Gradle versions aren't documented. Ask a Capillary engineer.

> ⚠️ Gap: the docs list `targetSdkVersion 34` and `compileSdkVersion 34` as prerequisites without saying whether newer levels are supported (app stores may ask for a newer target level). Ask a Capillary engineer before moving to a newer target level.

## Prerequisites
Common exchange: `_shared/prerequisites.md`. For this mode:
- **Source account:** the CSM / project manager configures it in *Organisation settings > Omni Channel Settings > Channel Configurations > MAPP_SDK* (set-up-source-account). The Android fields are the bundle name (the app's package name, from the app developer) and the **App signature** ("required only for Android apps"; from the app developer). One source account can serve both iOS and Android: enter both bundle names in the Bundle name field, separated by a semicolon (for example `android:com.capillarytech.product.android.one;ios:com.capillarytech.product.ios.x`).
- **Client gives Capillary:** the Android application ID (package name), and the app signature (SHA256 from the signing report; see the Gap below).
- **Capillary gives client:** Account Id (the Source Account Id of your MAPP_SDK account), Base URL (specific to your Capillary cluster), SSL Public Key, Org Id, Gamification Key, Gamification Region (`IN`, `US` or `ME`), Gamification URL (optional).
- **Repository access** (request from Capillary's access team): read access to `https://github.com/Capillary/hydra-sdk-android-maven`, plus a GitHub username and a Personal Access Token (PAT) with the **`read:packages`** scope.
- **Behavioural events** you send with `pushEvent` must first be created in Capillary: *Organisation settings > Master Data Management > Data Model > Behavioural events*.

> ⚠️ Gap: the source-account page (set-up-source-account) says the App signature is required for Android, but the install guides (android-sdk-getting-started and the gamification page's Option B prerequisites) name only the application ID. A mismatch stops the SDK (`_shared/prerequisites.md`). Send the signature with the application ID and confirm with Capillary.

> ⚠️ Gap: set-up-source-account says "Source Account Id - Displays the service account id. This is auto-generated." The Source Account Id is the value you pass as `accountId`; it is not a Firebase service account. Ask a Capillary engineer if this is unclear.

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

> ⚠️ Gap: this block follows the gamification page (gamification-android), which loads `github.properties` with `Properties()` before using it. The `maven { ... }` snippet on the install page (installing-sdk) isn't copy-pasteable: it uses an undefined `props`, curly quotes around the key names, an angle-bracket URL, Groovy `url "..."` inside a block labelled Kotlin, and a misaligned `password` line. Ask a Capillary engineer if the block above doesn't authenticate.

### 3. Add the SDK dependencies
Only `hydra-core` is required. Use the SDK version `{{sdk_version}}` (the minimum for gamification, and the version the docs show for every module).

> **Important:** do NOT add the `com.google.gms.google-services` plugin, Firebase dependencies or `google-services.json`.

```groovy file=app/build.gradle
dependencies {
    // Hydra Core (required)
    implementation "com.capillarytech:hydra-core:{{sdk_version}}"

    // In-app messaging (optional)
    implementation "com.capillarytech:hydra-inapp:{{sdk_version}}"

    // Inbox / Notification Center (optional)
    implementation "com.capillarytech:hydra-inbox-core:{{sdk_version}}"
    implementation "com.capillarytech:hydra-inbox-ui:{{sdk_version}}"

    // Gamification (optional)
    implementation "com.capillarytech:hydra-gamification:{{sdk_version}}"
    implementation "com.capillarytech:hydra-gamification-ui:{{sdk_version}}"
}
```

```kotlin file=app/build.gradle.kts
dependencies {
    // Hydra Core (required)
    implementation("com.capillarytech:hydra-core:{{sdk_version}}")

    // In-app messaging (optional)
    implementation("com.capillarytech:hydra-inapp:{{sdk_version}}")

    // Inbox / Notification Center (optional)
    implementation("com.capillarytech:hydra-inbox-core:{{sdk_version}}")
    implementation("com.capillarytech:hydra-inbox-ui:{{sdk_version}}")

    // Gamification (optional)
    implementation("com.capillarytech:hydra-gamification:{{sdk_version}}")
    implementation("com.capillarytech:hydra-gamification-ui:{{sdk_version}}")
}
```

> ⚠️ Gap: the standard install page (installing-sdk) also adds AndroidX libraries (`androidx.core:core`, `androidx.appcompat:appcompat`, `androidx.lifecycle:lifecycle-process`, versions shown only as `xxx`); this mode's guide doesn't list them, though step 9 uses `ProcessLifecycleOwner`. Ask a Capillary engineer whether and at which versions to add them.

> ⚠️ Gap: the gamification page says HydraGamification is bundled in HydraCore (Option A: no extra dependency), yet its Option B (above) adds `hydra-gamification` and `hydra-gamification-ui`. The Getting Started module table lists neither of these two artifacts (nor `hydra-mi-push-kit`) and has no catalog entry for them. Ask a Capillary engineer whether the two gamification artifacts are needed in this mode, and whether the without-Firebase guide is the one to follow.

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

> ⚠️ Gap: sdk-initialisation marks `.baseURL` and `.sslPublicKey` as "Optional", but the other pages (and Capillary's hand-over of these values) treat them as values you must pass. Pass both.

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
Map<String, Object> customData = new HashMap<>();
customData.put("Age", "25");
customData.put("Gender", "Male");

if (hydraAPI != null) {
    hydraAPI.pushUserSignup(
        "9000090000",
        "Henry",
        "Williams",
        "henrywill@gmail.com",
        "9000090000",
        customData
    );
}
```

`pushUserUpdate(...)` takes the same six arguments (only `cuid` mandatory). Signatures: API Reference.

> ⚠️ Gap: the API reference's Java samples write the attributes with `Map.of("Age", "25", "Gender", "Male")`; this guide uses `HashMap` instead. `Map.of` needs Android API 30 or higher, while the docs set minSdk 21, so it can crash older devices with `NoSuchMethodError`. Ask a Capillary engineer if you need the docs' form.

The Kotlin `pushUserSignup` also accepts an optional `subscriptions` list (the Java signature has none). The API reference lists only its keys (channel, accountId, priority, type and sourcename). The source-account page (set-up-source-account) shows this sample entry for an Android app; `accountId` is the Source Account Id of your MAPP_SDK account:

```json
{
    "channel": "ANDROID",
    "accountId": "~2024ba96",
    "priority": "BULK",
    "type": "OPTIN",
    "sourceName": "MAPP_SDK"
}
```

> ⚠️ Gap: the docs show this only as a JSON payload, not as Kotlin code for building the `subscriptions` list. The key is `sourcename` in the API reference and `sourceName` in the sample, and the channel value is `ANDROID` here but `iOS` (mixed case) in the iOS sample. Ask a Capillary engineer for the exact form your SDK version expects.

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

> ⚠️ Gap: the API reference's behavioural-event samples also put `"event_name"` and `"customerId"` inside the attributes map, and its text says behavioural events need configuration "in the Hydraconfig" as well as in org settings, but it shows no such `HydraConfig` setting. Whether those two keys must be repeated in the attributes, and what to configure in `HydraConfig`, isn't documented. Ask a Capillary engineer.

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
Add `hydra-inapp` (step 3). The In-App page (in-app-messaging) says the feature is available from Capillary SDK 1.4.0 and supports the Header, Footer, Popup and Interstitial layouts. Its configuration (`InAppConfig`, the mandatory click listener, `triggerInAppOnLaunch`) is in `android/firebase.md` › Modules › In-App.

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
  <com.capillarytech.hydra.gamification.ui.entrypoints.BannerView
      android:id="@+id/{{banner_id}}"
      android:layout_width="match_parent"
      android:layout_height="wrap_content" />
  ```
- **Embed View:** in this mode it needs explicit binding via `bindEmbedView()`.
  ```xml
  <com.capillarytech.hydra.gamification.ui.entrypoints.EmbedWebView
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
  <com.capillarytech.hydra.gamification.ui.entrypoints.LoyaltyEmbedView
      android:id="@+id/{{loyalty_id}}"
      android:layout_width="match_parent"
      android:layout_height="match_parent" />
  ```
  > ⚠️ Gap: which API response returns the Loyalty `embedId` isn't documented. Ask a Capillary engineer.

**Gamification events (Game and CMS event payloads).** Experience+ sends seven events (gamification-android, "Game and CMS event payloads"). The docs show no app code for them; they matter when you create the events in Capillary (field mapping below). Rules for every payload: `cuid` is **required**; `event_name` is always sent; payloads are flat JSON (no nested objects); numbers are sent as numbers, not strings. All other attributes are optional.

| Event | Flow | Fires when | Attributes besides `cuid` and `event_name` |
|---|---|---|---|
| `game_open` | Game | A game entry surface opens or launches the game | `campaign_id`, `game_type`, `entry_surface`, `embed_id`, `entry_point_id`, `entry_point_location`, `deep_link_url`, `hyper_link_url` |
| `game_viewed` | Game | The game UI is rendered and visible | `campaign_id`, `game_type`, `load_time_ms` (number) |
| `game_played` | Game | The user's first real interaction (spin, scratch, tap, select) | `campaign_id`, `game_type` |
| `game_completed` | Game | The game ends: won, lost, completed or abandoned | `campaign_id`, `game_type`, `total_time_ms` (number) |
| `reward_seen` | Game | The user views the reward (reveal screen or wallet) | `reward_id`, `campaign_id`, `reward_type` |
| `content_open` | CMS | A CMS surface (widget, banner or full page) is opened | `content_surface` |
| `content_viewed` | CMS | The CMS content is rendered and visible | `page_id`, `content_surface`, `load_time_ms` (number) |

Documented values: `entry_surface` is `popup`, `floating_icon`, `modal` or `banner_embedded` (`embed_id` applies to `banner_embedded` only); `game_type` includes `spinthewheel`, `scratchcard`, `slotmachine`, `quiz`, `memorygame`, `giftbox`, `streak`, `multistep`, `referral` (not exhaustive); `reward_type` includes `points`, `coupons`, `cashback`, `discount`, `freebie`, `buyXgetY`, `noReward` (not exhaustive); `content_surface` is `widget`, `banner` or `full_page`. `campaign_id` is the join key across game and reward events. Sample payload:

```json
{
  "cuid": "stringxxx",
  "event_name": "game_viewed",
  "campaign_id": "camp_44",
  "game_type": "spinthewheel",
  "load_time_ms": 850
}
```

**Field mapping.** When you create the events in Capillary, map these four event-creation fields. **All four are required.**

| Event-creation field | Maps from |
|---|---|
| `customerId` | `cuid` from the event payload (on every event) |
| `identifierType` | The login identifier you pass to the SDK: `mobile`, `email` or `externalId` |
| `source` | `SDK` |
| `accountId` | The SDK account ID (`{{account_id}}`) |

> ⚠️ Gap: the docs don't say where in Capillary you create these events or how the payload reaches them. Ask a Capillary engineer.

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

**Gradle can't resolve `com.capillarytech:hydra-core` (401/403 from `maven.pkg.github.com`)** — derived from the prerequisites, not a reported case.
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
| `pushUserSignup(cuid: String, firstName: String, lastName: String, email: String, phone: String, customData: Map<String, Any>?, subscriptions: List<Any>?)` | Registration; `customData`, `subscriptions` (channel, accountId, priority, type, sourcename; sample in step 7) optional. The Java signature has no `subscriptions` |
| `pushUserUpdate(cuid: String, firstName: String? = null, lastName: String? = null, email: String? = null, phone: String? = null, customData: Map<String, Any>? = null)` | Profile update |
| `pushUserSignOut(cuid: String)` | Sign-out (step 6 Gap) |
| `passUserPreferences(cuid: String, userPreference: UserPreferences)` | Push opt-in preferences: `UserPreferences(promPushOpted: Boolean, transPushOpted: Boolean)`; null `cuid` uses the stored CUID |
| `pushEvent(eventName: String, attributes: Map<String, Any>? = null)` | Custom event |
| `setCapToken(token)` | Capillary B2B token for Loyalty View |
| `getGamificationManager()` | Manager passed to `GamificationUIManager` |
| `GamificationUIManager(manager, context)` | `.onScreenChanged(activity, name)`, `.onActivityDestroyed(activity)`, `.onAppForegrounded()`, `.onAppBackgrounded()`, `.bindEmbedView(view, entryPointId, owner)` |
| Views (`com.capillarytech.hydra.gamification.ui.entrypoints`) | `BannerView`, `EmbedWebView`, `LoyaltyEmbedView` |
| Gamification events | `game_open`, `game_viewed`, `game_played`, `game_completed`, `reward_seen`, `content_open`, `content_viewed`; map `cuid`→`customerId`, `identifierType`, `source` (SDK), `accountId` (Modules › Gamification) |
| `NotificationCenterConfig(@DrawableRes defaultImage: Int)` | Inbox fallback image (mandatory parameter) |
| `InboxActivity`, `InboxFragment` | Default Notification Center UI |
| `HydraInboxUIHelper.getInstance().registerOnMessageClickListener(listener)` | `OnMessageClickListener.onMessageClick(context: Context, inboxMessage: InboxMessage): Boolean` |
| `HydraInboxCoreApi.getInstance()` | `getUnReadMessagesCount(context, UnReadCountListener)`, `fetchInboxMessages(context, OnMessagesAvailableListener)`, `deleteInboxMessage(context, inboxMessage)`, `trackInboxMessageClick(context, inboxMessage)`, `deleteAllInboxMessages(context)` |
