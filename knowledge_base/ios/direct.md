---
platform: ios
config_mode: direct
sdk_package: HydraCore   # plus HydraPushNotification, HydraPushNotificationServiceExtension, HydraInAppMessage, HydraInboxCore, HydraInboxUI; private repo https://github.com/Capillary/hydra-sdk-ios-packages (SPM / Xcode / CocoaPods)
sdk_version: 1.7.5-preprod.12   # minimum for gamification, Beta for UAT/POC (gamification-ios; Integration document p.91). ios-sdk-getting-started: SDK 1.7.0 or above, framework table at 1.7.4
modules_covered: [core, push, inbox_api, inbox_ui, gamification]
modules_missing: [inapp, visitor, multi_account]
sources: ["Integration document _ Experience+ pp.88–99 (Hydra iOS SDK Integration Doc, without firebase)", "Capillary developer docs (docs.capillarytech.com): ios-sdk, ios-sdk-getting-started (updated 2026-08-14); install-sdk, initialise-ios-sdk, ios-sdk-api-reference, configure-push-notifications, rich-push-notifications, configure-notification-center_ios, set-up-source-account-ios, configure-gateway-ios (updated 2026-03-04); gamification-ios (updated 2026-08-18)"]
owner: TBD
last_verified: null
review_status: draft   # drafted from the source docs; not yet SME-verified
---
# iOS (without Firebase)

"Without Firebase" means the SDK settings (Account Id, Base URL, SSL key, Org Id, gamification values) are passed in code. **Push still goes through Firebase Cloud Messaging (FCM)**, so an app that wants push also adds the Firebase SDK and `GoogleService-Info.plist` (Modules → Push).

## Coverage
| Module | Status |
|---|---|
| Core: install, init, customer/token updates, sign-up, sign-in, profile update, sign-out, behavioural events, log levels | Documented (Swift) |
| Push: APNs → Firebase, FCM token, AppDelegate forwarding, Notification Service Extension, rich push, CTA handling, opt-in flags | Documented (Swift); some sample code is inconsistent (Gaps inline) |
| Inbox: `HydraInboxCore` API and `HydraInboxUI` Notification Center, App Groups | Documented (Swift); some API examples disagree (Gap inline) |
| Gamification: auto campaigns, screen reporting, Capillary token, Banner / Embedded / Loyalty views | Documented (Swift UIKit, SwiftUI, Objective-C) |
| Gamification delegate, UI suppression | Not documented for this mode |
| In-App (`HydraInAppMessage`) | Framework and one forwarding call only; no setup |
| Visitor, multi-account | Not documented |

## Requirements
- Hydra iOS SDK `{{sdk_version}}` or later (minimum for gamification; Beta for UAT/POC).
- Minimum deployment target: **iOS 13.0** (the Podfile uses `platform :ios, '13.0'`).
- Supported: iPhone (iOS) and iPad (iPadOS).
- Xcode 14 or later (stated for installing through Xcode), a valid iOS project, internet access.
- Swift. `HydraConfiguration` and `Hydra.generate(...)` are Swift-only; an Objective-C app needs a small Swift file for initialisation (step 3).

> ⚠️ Gap: Swift and CocoaPods versions, and a minimum Firebase SDK version for push, aren't documented. Ask a Capillary engineer.

## Prerequisites
See `_shared/prerequisites.md`.
- **Client gives Capillary:** iOS bundle ID (`{{bundle_id}}`). Capillary registers it in the MAPP_SDK source account's **Bundle Name** (as `ios:{{bundle_id}}`; one source account can hold both apps, e.g. `android:<applicationId>;ios:{{bundle_id}}`). For push, Capillary also needs the app's Firebase project (FCM Project ID, FCM service-account email) and sets up the iOS push gateways (`_shared/push.md`).
- **Capillary gives client:** Account Id, Base URL, SSL public key, Org Id, Gamification Key, Gamification Region, Gamification URL (optional). In this mode they are passed straight into `HydraConfiguration` as values.
- **Repo access:** the SDK installs from the private repo `https://github.com/Capillary/hydra-sdk-ios-packages`; request access from Capillary's access team. You then need GitHub credentials with access to it, or a GitHub username + Personal Access Token (PAT) with access to it. The PAT stays on the client's machine; never share it in chat.
- **Push only:** an Apple developer account (APNs key) and a Firebase project with an iOS app registered for `{{bundle_id}}`.
- Sample app for testing the integration and APIs: `https://github.com/Capillary/HydraSampleApp`.

> ⚠️ Gap: the required PAT scopes aren't documented. Ask a Capillary engineer.

## Steps

### 1. Authenticate to the private repo
The SDK is in a private GitHub repo. Use one option.

**Option A: GitHub credentials in Xcode**
1. Open Xcode.
2. Go to **Xcode → Settings (Preferences) → Accounts**.
3. Add your GitHub account.
4. Ensure the account has access to `Capillary/hydra-sdk-ios-packages`.

**Option B: username + PAT.** Use this as the package URL. Fill it in locally; any file containing it holds the token in plain text:

```text
https://<GITHUB_USERNAME>:<PERSONAL_ACCESS_TOKEN>@github.com/Capillary/hydra-sdk-ios-packages.git
```

### 2. Install the SDK
Frameworks (add the ones for the modules you use):

| Framework | Purpose |
|---|---|
| `HydraCore` | Base for all others: network, persistence, logging, event reporting. Bundles HydraGamification (enabled by configuration). |
| `HydraPushNotification` | Push: receiving and handling notifications, analytics, delivery receipt (DLR) events |
| `HydraPushNotificationServiceExtension` | Goes in the Notification Service Extension target: modifies notifications before display (rich push) |
| `HydraInAppMessage` | In-app messages shown as popups |
| `HydraInboxCore` | Stores received notifications locally for the Notification Center |
| `HydraInboxUI` | The pre-built Notification Center UI |

Use any one of the three methods.

**Option A: Swift Package Manager**

```swift file=Package.swift
import PackageDescription

let package = Package(
    name: "<ProjectName>",
    dependencies: [
        .package(
            url: "https://github.com/Capillary/hydra-sdk-ios-packages",
            .upToNextMajor(from: "{{sdk_version}}")
        )
    ]
)
```

> ⚠️ Correction: ✅ Use `.upToNextMajor(from: "{{sdk_version}}")` (the required/minimum version: Integration document p.91, gamification-ios). ❌ Don't use `upToNextMajor(from: "1.1.0")` (Package.swift snippet in install-sdk and Integration document p.90). *Pending SME confirmation.*

> ⚠️ Correction: ✅ Use the repo `https://github.com/Capillary/hydra-sdk-ios-packages` and minimum version 1.7.5-preprod.12 (install-sdk, gamification-ios). ❌ Don't use `https://github.com/Capillary/hydra-ios-sdk-spm.git` or 1.7.5-preprod.10 (Integration document, Gamification iOS guide p.26). *Pending SME confirmation.*

**Option B: Xcode**
1. Open your project in Xcode.
2. Select **File → Add Packages…**
3. Enter `https://github.com/Capillary/hydra-sdk-ios-packages` (or the PAT URL from step 1), or pick it from recently added packages.
4. Under **Dependency Rule**, choose the version (`{{sdk_version}}`) or branch. Leaving the version blank selects the latest. Xcode shows the package's dependencies: check they don't conflict with your project's.
5. Under **Add to project**, select your project.
6. Click **Add Package**, select the frameworks you need (table above), and click **Add Package** again.
7. Import the framework where you use it, e.g. `import HydraCore`.

**Option C: CocoaPods**

```ruby file=Podfile
platform :ios, '13.0'
use_frameworks!

private_repo = 'https://<GITHUB_USERNAME>:<PERSONAL_ACCESS_TOKEN>@github.com/Capillary/hydra-sdk-ios-packages.git'

target 'YourAppTargetName' do
  pod 'HydraCore', :git => private_repo
  pod 'HydraPushNotification', :git => private_repo
  pod 'HydraPushNotificationServiceExtension', :git => private_repo
  pod 'HydraInAppMessage', :git => private_repo
  pod 'HydraInboxCore', :git => private_repo
  pod 'HydraInboxUI', :git => private_repo
end

target 'YourNotificationServiceExtensionTargetName' do
  pod 'HydraPushNotificationServiceExtension', :git => private_repo
end
```

Run `pod install` (or `pod install --repo-update`) and open the generated `.xcworkspace`. The git approach needs the URL on every pod; with a private Spec Repo for your organisation you can use the `source` directive and plain pod names instead.

> ⚠️ Correction: ✅ Use `private_repo = '…'` above both `target` blocks, as shown. ❌ Don't use it inside `target 'YourAppTargetName' do` (Podfile in install-sdk and Integration document p.91): Ruby hides it from the second target. *Pending SME confirmation.*

> ⚠️ Correction: ✅ Use only the pod lines shown. ❌ Don't paste the uncommented line `Ensure you are using the correct source or git URL` from the install-sdk Podfile; it is a comment missing its `#`. *Pending SME confirmation.*

> ⚠️ Gap: no Podfile shows how to pin `{{sdk_version}}`. Ask a Capillary engineer.

### 3. Initialise the SDK
Initialise in `AppDelegate`, inside `application(_:didFinishLaunchingWithOptions:)` (create the method if it isn't there). Create one SDK instance per application.

```swift file=AppDelegate.swift
do {
    let hydraConfig = try HydraConfiguration(
        accountID: accountID,                         // {{account_id}}
        server: .genericServer(apiBaseURL, sslKey, [0, 5, 10, 30, 120]),   // apiBaseURL = {{base_url}}, sslKey = {{ssl_public_key}}, [..] = retryDelays
        orgID: orgId,                                 // {{org_id}}
        gamificationWriteKey: gamificationWriteKey,   // {{gamification_key}}
        gamificationRegion: gamificationRegion,       // {{gamification_region}}
        gamificationBaseURL: gamificationBaseURL)     // {{gamification_base_url}} (optional if gamificationRegion is provided)

    hydra = try Hydra.generate(with: hydraConfig)
} catch let error {
    Logger.error(error.localizedDescription)
}
```

`hydra` is the SDK instance used by every later step; the docs also call it `hydraCore`, `hydraCoreSDK` or `hydraSDK`. Region values: see `_shared/prerequisites.md`.

Full `generate` signature (initialise-ios-sdk):

```swift
static public func generate(with configuration: ConfigurationGenerator,
                                geoData: GeographicDataGenerator? = nil,
                                supportsPushNotifications: Bool = false,
                                deviceScreenInfo: DeviceScreenInfo? = nil) throws -> Hydra
```

| Parameter | Type | Description | Mandatory/Optional |
|---|---|---|---|
| configuration (`HydraConfiguration`) | `ConfigurationGenerator` | Object conforming to `ConfigurationGenerator` | Mandatory |
| `geoData` | `GeographicDataGenerator` | User's geographic details: `country: String?`, `city: String?`, `countryCode: String?`, `timeZone: String` | Optional |
| `supportsPushNotifications` | `Bool` | Device's push notification settings | Mandatory (per the docs' table, although it defaults to `false`) |
| `deviceScreenInfo` | `DeviceScreenInfo` | `screenWidth: Int`, `screenHeight: Int` (both mandatory when passed) | Optional |

The initialise-ios-sdk example passes `GeoData(country: "country", countryCode: "country-code", city: "city", timeZone: "timezone")`, `DeviceScreenInfo(screenHeight: 00, screenWidth: 00)` and `supportsPushNotifications: true`.

**SwiftUI:** use the same `HydraConfiguration` / `Hydra.generate(...)` code; there is no separate SwiftUI initialiser. Call it once, e.g. from your `App` struct's `init()`.

**Objective-C:** `HydraConfiguration` and `Hydra.generate(...)` are Swift-only. Add a small Swift file that runs this initialisation once, and let your Objective-C code run after it. Screen reporting, `setCapToken` and the banner/embed/loyalty views have Objective-C methods on `HydraGamificationUI`.

> ⚠️ Gap: the initialise-ios-sdk page shows a different configuration: `ConfigurationGenerator` with `accountID` (mandatory), `customerId` (mandatory: phone/email/external ID) and `server` (optional), example `HydraConfiguration(accountID: "account-id", customerId: "customer-id", server: .server1)` called without `try`. The gamification-ios page and the Integration document use `accountID` / `server: .genericServer(...)` / `orgID` / gamification arguments with no `customerId`. Which initialiser the current SDK has, and whether apps with push must pass `supportsPushNotifications: true`, isn't settled. Ask a Capillary engineer.

> ⚠️ Gap: the Integration document (p.92) calls `Hydra.generate(with: hydraConfig, remoteLogLevel: .debug)`; the public `generate` signature has no `remoteLogLevel` parameter (remote logging is set with `updateRemoteLogLevel`, step 10). Ask a Capillary engineer which is current. The units of the retry delays (`[0, 5, 10, 30, 120]`) aren't stated either.

### 4. Keep customer ID and tokens up to date
After initialisation you can set or update these on the instance:

```swift
hydraCore.update(customerID: "customer-id")       // whenever the customer ID changes in the app
hydraCore.update(deviceToken: "device-token")     // the device's push token, to keep receiving push
hydraCore.update(interfaceID: "FCM-Token")        // the FCM token (apps using Firebase for push); update whenever it changes
hydraCore.update(notificationSupport: true)       // enable / disable notification support
```

Promotional / transactional push opt-in (defined by the SDK on `UserDefaults`, default `false`):

```swift
func setPromotionalPushOpted(status: Bool = false)
func setTransactionalPushOpted(status: Bool = false)
```

The docs call them as `UserDefaults.standard.setPromotionalPushOpted(status:)` and `UserDefaults.standard.setTransactionalPushOpted(status:)`.

### 5. Report user sign-up or sign-in
`customerId` must match the Account Linking Identifier in Capillary CRM (see `_shared/prerequisites.md`).

```swift
public func reportUserSignUp(data: UserSignUpGenerator, customData: Attributes)
public func reportUserSignIn(data: UserSignInGenerator, customData: Attributes)
```

| Field | Type | Mandatory/Optional |
|---|---|---|
| `customerId` | String | Mandatory (unique identifier of the user) |
| `firstName` | String | Mandatory |
| `lastName` | String | Mandatory |
| `email` | String | Optional (pass `nil` if absent) |
| `phone` | String | Mandatory |
| `customData` | `Dictionary<String, Any>` | Optional (pass `[:]` if none) |

```swift
let userSignInData = UserDetails(customerId: "customer-id",firstName: "first-name", lastName: "last-name", email: "email@goodemail.com", phone: "xxxxxxxx")
hydraCore.reportUserSignIn(data: userSignInData, customData: [:])

let userSignUpData = UserDetails(customerId: "customer-id",firstName: "first-name", lastName: "last-name", email: nil, phone: "xxxxxxxx")
hydraCore.reportUserSignUp(data: userSignUpData, customData: ["Age": "25", "Gender": "Male"])
```

### 6. Report a profile update
```swift
public func reportUserProfileUpdate(data: UserProfileUpdateGenerator, customData: Attributes, subscriptions: [Any]? = nil)
```

Only `customerId` is mandatory; `firstName`, `lastName`, `email`, `phone`, `customData` and `subscriptions` (the logged-in user's subscription list) are optional.

```swift
var subscriptions: [HydraSubscription] = []
var subscription: HydraSubscription = HydraSubscription(channel: "EMAIL", priority: "BULK", type: "OPTIN")
subscriptions.append(subscription)
subscription = HydraSubscription(channel: "PUSH", priority: "BULK", type: "OPTIN")
subscriptions.append(subscription)
let userProfileUpdateData = UserDetails(customerId: "customer-id",firstName: "first-name", lastName: "last-name", email: "email@goodemail.com", phone: "xxxxxxxx")
hydraCoreSDK.reportUserProfileUpdate(data: userProfileUpdateData, customData: [:], subscriptions: subscriptions)
```

### 7. Report user sign-out
Removes the user's details (first name, mobile number, …) from the session.

```swift
let customAttributes = ["key1": "value1", "key2": "value2"]
// customData: Dictionary containing extra information that application want to send to the server along with this event

hydra.reportUserSignOut(customData: customAttributes)   // or customData: [:]
```

### 8. Report custom behavioural events
Events count only after a sign-in or sign-up has been reported, and are invalid after a sign-out. The name must be non-empty; attributes are optional. Behavioural events must also be configured in the Hydra config and the organisation settings.

```swift
public func reportBehavioralEvent(name: String, customAttributes attributes: Attributes)
```

```swift
let customAttributes = ["key1": "value1", "key2": "value2"]
hydra.reportBehavioralEvent(name:"custom_eventname", customAttributes: customAttributes)
```

### 9. Report the current screen (required for gamification)
Mandatory for screen-targeted campaigns: campaign visibility and eligibility depend on the reported screen.

Swift (UIKit), in each view controller:

```swift
override func viewDidAppear(_ animated: Bool) {
    super.viewDidAppear(animated)

    hydra.gamificationScreenAppeared("SampleScreenName")
}

override func viewWillDisappear(_ animated: Bool) {
    super.viewWillDisappear(animated)

    hydra.gamificationScreenDisappeared("SampleScreenName")
}
```

SwiftUI, applied directly to the screen's view (it reports appear/disappear automatically):

```swift
SampleView()
    .gamificationScreen("SampleScreenName")
```

> ⚠️ Correction: ✅ Use the modifier on the screen's own view, `SampleView().gamificationScreen("SampleScreenName")` (gamification-ios). ❌ Don't use `HydraGamificationUI().gamificationScreen("SampleScreenName")` (Integration document p.93). *Pending SME confirmation.*

Objective-C:

```objc
- (void)viewDidAppear:(BOOL)animated {
    [super viewDidAppear:animated];

    [HydraGamificationUI reportScreen:@"SampleScreenName"];
}

- (void)viewWillDisappear:(BOOL)animated {
    [super viewWillDisappear:animated];

    [HydraGamificationUI reportScreenDisappeared:@"SampleScreenName"];
}
```

### 10. Set log levels (optional)
| Level | Console | Remote sync |
|---|---|---|
| `error` | Problem occurred; app may continue | Only error logs |
| `warning` | Potential issue | Warning and error |
| `info` | General operation info | Info, warning and error |
| `debug` | Detailed debugging info | All logs |
| `none` | No console logs | No logs synced |

```swift
func updateConsoleLogLevel(level: LogLevel)   // default: debug
func updateRemoteLogLevel(level: LogLevel)    // default: none
```

> ⚠️ Gap: the docs' examples for both APIs are `Logger.updateLogLevel(level: .critical)`, which matches neither method name, and `.critical` isn't in the level table. Ask a Capillary engineer for the exact call.

### 11. Set the Capillary token (required for Loyalty View)
Set the Capillary B2B short-lived token **before** a Loyalty View mounts; without a valid token the view renders empty. Token source: `_shared/prerequisites.md`.

Swift / SwiftUI:

```swift
hydra.setCapToken(token)
```

Objective-C:

```objc
[HydraGamificationUI setCapToken:token];
```

## Modules

### Push
`HydraPushNotification` + `HydraPushNotificationServiceExtension`, with `HydraCore`. Capillary sends push through **FCM**, which delivers to iOS through APNs. The server side (what must match at Capillary, gateways, how to test, common problems) is in `_shared/push.md`.

#### 1. Apple and Firebase console setup
1. **APNs key.** Log into the Apple developer account → **Certificates, Identifiers and Profiles → Keys → +**. Name the key, select **Apple Push Notification Service (APNs)**, **Continue**, **Confirm**, **Download**. Copy and save the Key ID. The file downloads only once: back it up and don't rename it. An APNs certificate also works.
2. **Upload it to Firebase:** Firebase Console → project settings → **Cloud Messaging** → **iOS app configuration** → upload the APNs authentication key or certificate.
3. **`GoogleService-Info.plist`:** download it for your app and drag it into the Xcode project; make sure it is **added to the app's target**.

> ⚠️ Gap: configure-push-notifications also says to copy the **Server Key** from Cloud Messaging → iOS app configuration "for later", but never says who uses it. Ask a Capillary engineer whether it is still needed.

#### 2. Capabilities and App Group
In **TARGETS → your app target → Signing & Capabilities**:
1. Turn on **Push Notifications**.
2. Enable **Background Modes → Remote notifications**.
3. Enable **App Groups** and choose an App Group ID; if you have none, create one in the format `group.{{bundle_id}}.hydra`. Enable the **same App Group ID on every target that uses the Capillary SDK**, including the Notification Service Extension. The Inbox requires this.

> ⚠️ Gap: configure-notification-center_ios also says "The App Group ID must precisely match the name of the main application", which conflicts with the `group.{your_bundle_id}.hydra` format. Ask a Capillary engineer.

#### 3. Initialise Firebase and NotificationCore
```swift file=AppDelegate.swift
import Firebase
import FirebaseMessaging


func application(_ application: UIApplication, didFinishLaunchingWithOptions launchOptions: [UIApplication.LaunchOptionsKey: Any]?) -> Bool {
        FirebaseApp.configure()
        Messaging.messaging().delegate = self


        // Add any additional configuration code or other setup here


        return true
}
```

After creating the Hydra instance (step 3), create `NotificationCore` and pass it the instance:

```swift
let notificationCore:NotificationCore = NotificationCore.shared
notificationCore.update(sdk: hydraCoreSDK)
```

> ⚠️ Gap: how to add the Firebase SDK (`Firebase` / `FirebaseMessaging`) to the project isn't documented. Ask a Capillary engineer.

#### 4. Forward app delegate calls and the FCM token
`NotificationCore` (the `HydraPushNotification` class) exposes these lifecycle APIs, which the app must call from the matching places:

```swift
public func application(_ application: UIApplication,
                            didReceiveRemoteNotification userInfo: [AnyHashable: Any],
                            fetchCompletionHandler completionHandler: @escaping (UIBackgroundFetchResult) -> Void) -> ((UIBackgroundFetchResult) -> Void)

public func application(_ application: UIApplication,
                             didRegisterForRemoteNotificationsWithToken deviceToken: Data)

public  func application(_ application: UIApplication,
                             didFailToRegisterForRemoteNotificationsWithError error: Error)

public  func application(_ application: UIApplication,
                             didFinishLaunchingWithOptions launchOptions: [UIApplication.LaunchOptionsKey: Any]? = nil)
```

The docs' example (its `didFinishLaunchingWithOptions` also calls `self.notificationCore.application(application, didFinishLaunchingWithOptions: launchOptions)`):

```swift file=AppDelegate.swift
extension AppDelegate: UNUserNotificationCenterDelegate{
    func userNotificationCenter(_ center: UNUserNotificationCenter,
                                didReceive response: UNNotificationResponse,
                                withCompletionHandler completionHandler: @escaping () -> Void) {
        let userInfo = response.notification.request.content.userInfo
        Messaging.messaging().appDidReceiveMessage(userInfo)
        let result = notificationCore.userNotification(center: center, didReceive: response, withCompletionHandler: completionHandler)
        if result != nil {
                //developer can write custom code to handle as per their needs.
        }
    }
    func userNotificationCenter(_ center: UNUserNotificationCenter,
                                willPresent notification: UNNotification,
                                withCompletionHandler completionHandler: @escaping (UNNotificationPresentationOptions) -> Void) {
        let result = notificationCore.userNotification(center: center, willPresent: notification, withCompletionHandler: completionHandler)
        if result != nil {
                //developer can write custom code to handle as per their needs.
        }
    }
}


extension AppDelegate:MessagingDelegate{
    func messaging(_ messaging: Messaging, didReceiveRegistrationToken fcmToken: String?) {
        if let fcmToken = fcmToken {
            Logger.info("FCM_Token is \(fcmToken)")
            hydraCoreSDK.update(interfaceID: fcmToken)
        }
    }
}


extension AppDelegate {
    func application(_ application: UIApplication, didRegisterForRemoteNotificationsWithDeviceToken deviceToken: Data) {
        Messaging.messaging().apnsToken = deviceToken
        hydraCoreSDK.application(application, didRegisterForRemoteNotificationsWithToken: deviceToken)
    }


    func application(_ application: UIApplication, didFailToRegisterForRemoteNotificationsWithError error: Error) {
        print("Error occurred due to \(error.localizedDescription)")
    }


    func application(_ application: UIApplication,
                     didReceiveRemoteNotification userInfo: [AnyHashable : Any],
                     fetchCompletionHandler completionHandler: @escaping (UIBackgroundFetchResult) -> Void) {
        Messaging.messaging().appDidReceiveMessage(userInfo)
    _ = InAppMessagingCore.application(application, didReceiveRemoteNotification: userInfo, fetchCompletionHandler: completionHandler)

    }
}
```

> ⚠️ Gap: the push sample is inconsistent: the API list puts `didRegisterForRemoteNotificationsWithToken` on `NotificationCore`, but the example calls it on `hydraCoreSDK`; `didReceiveRemoteNotification` is forwarded only to `InAppMessagingCore`, not `NotificationCore`; and requesting notification permission, calling `registerForRemoteNotifications()` and setting `UNUserNotificationCenter`'s delegate aren't shown. Ask a Capillary engineer.

#### 5. Notification Service Extension (rich push)
Rich push (images, buttons) needs `HydraPushNotificationServiceExtension` in a Notification Service Extension target.
1. Xcode → **File → New → Target → Notification Service Extension** (iOS tab). Name it (e.g. `YourAppNotificationService`), **Finish**, and **Activate** the scheme if asked.
2. Add `HydraPushNotificationServiceExtension` to the extension target (**Frameworks and Libraries**):
   - SPM: **Project Settings → your project → Package Dependencies → `hydra-sdk-ios-packages`**, under **Targets** select the extension target and tick `HydraPushNotificationServiceExtension`.
   - CocoaPods: the extension target block in the Podfile (step 2), then `pod install`. The rich-push page's version:
     ```ruby file=Podfile
     target 'YourNotificationServiceExtensionTargetName' do
       use_frameworks!
       pod 'HydraPushNotificationServiceExtension', :git => 'https://github.com/Capillary/hydra-sdk-ios-packages.git' # Use your private repo URL if applicable
     end
     ```
3. Enable the same App Group as the app (Push step 2).
4. Replace the content of `NotificationService.swift` so Hydra handles the notification.

rich-push-notifications (subclass):

```swift file=NotificationService.swift
import UserNotifications
import HydraPushNotificationServiceExtension
import HydraCore // May be needed for Logger or other shared components

class NotificationService: HydraRemoteNotificationService {
// The HydraRemoteNotificationService superclass handles the core logic.
// You generally don't need to override didReceive or serviceExtensionTimeWillExpire
// unless you have very specific custom logic *in addition* to Hydra's processing.

override func didReceive(_ request: UNNotificationRequest, withContentHandler contentHandler: @escaping (UNNotificationContent) -> Void) {
    HydraCore.Logger.debug("NotificationService: didReceive called.") // Example logging
    super.didReceive(request, withContentHandler: contentHandler)
}

override func serviceExtensionTimeWillExpire() {
    HydraCore.Logger.debug("NotificationService: serviceExtensionTimeWillExpire called.") // Example logging
    super.serviceExtensionTimeWillExpire()
 }
}
```

configure-push-notifications (composition):

```swift file=NotificationService.swift
import UserNotifications
import Foundation
import HydraPushNotificationServiceExtension
class NotificationService: UNNotificationServiceExtension {
    let service:HydraRemoteNotificationService = .init()
    override func didReceive(_ request: UNNotificationRequest, withContentHandler contentHandler: @escaping (UNNotificationContent) -> Void) {
        service.didReceive(request, withContentHandler: contentHandler)
    }
    override func serviceExtensionTimeWillExpire() {
            // Called just before the extension will be terminated by the system.
            // Use this as an opportunity to deliver your "best attempt" at modified content, otherwise the original push payload will be used.
        service.serviceExtensionTimeWillExpire()
    }
}
```

> ⚠️ Gap: the two pages show different `NotificationService` patterns (subclass `HydraRemoteNotificationService` vs. hold one inside a `UNNotificationServiceExtension`). Use one, not both. Ask a Capillary engineer which is recommended.

How it works: when a notification with `mutable-content: 1` arrives while the app is in the background, iOS launches the extension; `HydraRemoteNotificationService.didReceive` parses the payload, downloads rich content (e.g. the image), attaches it, and calls `contentHandler` to show the modified notification.

#### 6. Handle CTA buttons
CTAs are defined in the push campaign on the Capillary platform. **Without a `HydraNotificationCallbackDelegate`, the SDK handles only `external`-type CTAs itself; all other CTA types are ignored.** Conform a class to `HydraNotificationCallbackDelegate` (in `HydraPushNotification`), implement `process(cta:notificationPayload:) -> Bool`, and set it on `NotificationCore.shared` (method name spelled as in the docs):

```swift
import HydraPushNotification

let actionHandler = NotificationActionHandler()

// In application(_:didFinishLaunchingWithOptions:), after notificationCore.update(sdk: hydraSDK):
notificationCore.setNotificationCallbackDelagte(delegate: actionHandler)

class NotificationActionHandler: HydraNotificationCallbackDelegate {
    func process(cta: HydraCore.CTA, notificationPayload payload: Any) -> Bool {
        switch cta.type {
        case CTAActionType.deepLink.rawValue:
            if cta.action == "myapp://products/promo" {
                // Navigate to specific screen
                return true  // Indicate we handled it
            } else {
                return false  // Let SDK try default handling (if any) or ignore
            }
        case CTAActionType.external.rawValue:
            if let url = URL(string: cta.action), UIApplication.shared.canOpenURL(url) {
                DispatchQueue.main.async {
                    UIApplication.shared.open(url, options: [:], completionHandler: nil)
                }
                return true
            } else {
                return false
            }
        default:
            return false  // Indicate we did not handle this type
        }
    }
}
```

`CTA` has `type`, `action`, `actionText`; `payload` is the original notification (cast to `[AnyHashable : Any]`). Return `true` if the app handled the action. Return `false` otherwise: for common types like `external_url` the SDK may try its default (e.g. open the URL); unhandled custom types are usually ignored.

### In-App
`HydraInAppMessage` shows in-app messages as popups. The push sample forwards `didReceiveRemoteNotification` to `InAppMessagingCore.application(application, didReceiveRemoteNotification: userInfo, fetchCompletionHandler: completionHandler)` (Push step 4), and the Inbox sample declares `var inAppCore: InAppMessagingCore?`.

> ⚠️ Gap: iOS in-app initialisation, configuration and callbacks aren't in the sources (the iOS in-app page, `in-app-messaging_ios`, wasn't provided; `in-app-messaging` covers Android only). Ask a Capillary engineer.

### Inbox
`HydraInboxCore` (storage + API) and `HydraInboxUI` (pre-built Notification Center). Requires push (`HydraPushNotification` and `HydraPushNotificationServiceExtension` initialised, delegate methods forwarded) and the **same App Group on the app and extension targets** (Push steps 2 and 5).

**Initialise** `InboxCore` and `InboxUICore` after `HydraCore` and `NotificationCore`:

```swift file=AppDelegate.swift
import HydraInboxCore
import HydraInboxUI

class AppDelegate: UIResponder, UIApplicationDelegate {

    var hydraSDK: Hydra?
    let notificationCore = NotificationCore.shared
    var inAppCore: InAppMessagingCore?
    var inboxCore: InboxCore?
    var inboxUI: InboxUICore?

    func application(_ application: UIApplication, didFinishLaunchingWithOptions launchOptions: [UIApplication.LaunchOptionsKey: Any]?) -> Bool {

        // --- Initialize Hydra Core, Notification Core, In-App Messaging ---

        if let config = hydraSDK?.configuration() {
            let inboxCoreConfig = InboxCoreConfiguration(
                hydraConfig: config,
                maximumNotificationCount: 200 // Optional: Max messages stored per user
            )
            do {
                inboxCore = try InboxCore(
                    with: inboxCoreConfig,
                    configuredFor: .dev // Match environment
                )
                let inboxUIConfig = HydraInboxUIConfiguration(
                    unreadMessageConfigType: .defaultUnreadConfiguration, // Style for unread items
                    readMessageConfigType: .defaultReadConfiguration,   // Style for read items
                    // notificationsNotFoundConfiguration: HydraInboxEmptyNotificationsConfiguration(...),
                    placeholderImage: UIImage(named: "notification-placeholder") // Optional
                )
                inboxUI = InboxUICore(with: inboxCore!, configuration: inboxUIConfig)
            } catch let error {
                print("Error Initializing Hydra Inbox Core/UI: \(error.localizedDescription)")
            }
        } else {
             print("Error: Cannot initialize Inbox without HydraCore config.")
        }
        return true
    }
}
```

- `InboxCoreConfiguration`: `hydraConfig` (the shared `HydraConfiguration`); `maximumNotificationCount` (optional Int, notifications stored per user, **default 250**).
- `HydraInboxUIConfiguration`: `unreadMessageConfigType` / `readMessageConfigType` = `.defaultUnreadConfiguration` / `.defaultReadConfiguration`, `.customConfiguration(HydraInboxMessageConfigurator)` (fonts, colours, borders; see `HydraInboxMessageUIConfiguration`), or `.customReactNativeConfiguration(HydraInboxMessageReactNativeUIConfigurator)` (string values such as hex colours); `notificationsNotFoundConfiguration` (optional `HydraInboxEmptyNotificationsConfigurator`, empty-state text/font); `placeholderImage` (optional `UIImage`, shown while images load).

> ⚠️ Gap: the values for `InboxCore(with:configuredFor:)` other than `.dev` ("Match environment") aren't listed. Ask a Capillary engineer.

**Show the Notification Center** (needs a navigation controller for options 1–2):

```swift
inboxUI.showNotificationCenter(with: navController)                 // Option 1: SDK pushes it
let inboxVC = inboxUI.getNotificationCenter()                       // Option 2: push / present it yourself
navController.pushViewController(inboxVC, animated: true)
let inboxSwiftUIView = inboxUI.notificationCenterSwiftUIView()      // Option 3: SwiftUI view to embed
```

Taps, CTA buttons, mark-as-read and delete inside the pre-built UI are handled by `HydraInboxUI` automatically, and the list refreshes itself.

**Unread badge:** fetch the count with `inboxCore.getUnreadNotificationCount`, and listen for changes by conforming to `HydraInboxUIProtocol` and calling `inboxUI.setHydraInboxUIDelegate(delegate: self)`; the SDK then calls `refreshNotificationList()` on new, read or deleted messages (update UI on the main queue).

```swift
func updateInboxBadge() {
    inboxCore?.getUnreadNotificationCount { [weak self] count in
        DispatchQueue.main.async {
            self?.inboxBadgeLabel.isHidden = (count == 0)
            self?.inboxBadgeLabel.text = "\(count)"
        }
    }
}

// MARK: - HydraInboxUIProtocol
func refreshNotificationList() {
    updateInboxBadge()
}
```

**Custom inbox UI** (only `HydraInboxCore`): fetch `[HydraNotificationPayload]` with `inboxCore.getNotifications { ... }`; on tap call `inboxCore.performNotificationAction(notification:)`; on a secondary button `inboxCore.performNotificationExpandableCtaAction(notification:cta:)`; call `inboxCore.handleNotification(notification:action:completion:)` with `.read` when viewed and `.delete` when deleted; `handleDeleteAllNotifications()` deletes all of the current user's notifications (returns `true` on success); refresh from `refreshNotificationList()` by calling `getNotifications` again.

> ⚠️ Gap: the inbox page's API examples disagree with its own guide: `getUnreadNotificationCount()` returning an Int vs. a completion closure; `getNotifications()` shown in Kotlin syntax vs. a closure; `handleNotification(notification.notification, HydraNotificationAction.READ)` vs. `handleNotification(notification:action:completion:)` with `.read`; `performNotificationAction(notification.notification)` without a label; `setInboxUIDelegate(delegate:)` vs. `setHydraInboxUIDelegate(delegate:)`. Use the signatures above and check them in Xcode; ask a Capillary engineer if they don't compile.

### Visitor
> ⚠️ Gap: not documented for this mode. Ask a Capillary engineer.

### Gamification
HydraGamification is bundled in `HydraCore`; no extra framework. Configure it with the gamification arguments of `HydraConfiguration` (step 3): `gamificationWriteKey` is mandatory, and at least one of `gamificationRegion` / `gamificationBaseURL` is required, otherwise HydraGamification stays disabled. If the base URL is set it is used directly; otherwise Hydra resolves it from the region. Then report screens (step 9) and, for the Loyalty View, set the token (step 11).

**Automatic experiences.** Floating button, popup and bottom sheet campaigns appear automatically on reported screens, based on targeting rules in the Gamification dashboard. No UI code is needed.

**Embeddable views (optional).** For each view: pass a unique ID (entry-point IDs from Capillary), register a height callback, and update your container's height when it fires.

*Banner View*

Swift (UIKit):
```swift
let bannerView = hydra.gamificationBannerView(
    bannerId: {{banner_id}}
) { height in
    self.bannerHeightConstraint.constant = height
}
```

SwiftUI:
```swift
GamificationBannerView(bannerId: {{banner_id}})
```

Objective-C:
```objc
UIView *banner =
[HydraGamificationUI bannerViewWithBannerId:{{banner_id}}
                                  onHeight:^(CGFloat height) {
    self.heightConstraint.constant = height;
}];
```

*Embedded View*

Swift:
```swift
let embedView = hydra.gamificationEmbedView(
    embedId: {{embed_id}}
) { height in
    self.heightConstraint.constant = height
}
```

SwiftUI:
```swift
GamificationEmbedView(embedId: {{embed_id}})
```

Objective-C:
```objc
UIView *embed =
[HydraGamificationUI embedViewWithEmbedId:{{embed_id}}
                                onHeight:^(CGFloat height) {
    self.heightConstraint.constant = height;
}];
```

*Loyalty View* (set the token first, step 11; the parameter label is `embedId:` as shown)

Swift:
```swift
let loyaltyView = hydra.gamificationLoyaltyView(
    embedId: {{loyalty_id}}
) { height in
    self.heightConstraint.constant = height
}
```

SwiftUI:
```swift
GamificationLoyaltyView(embedId: {{loyalty_id}})
```

Objective-C:
```objc
UIView *loyalty =
[HydraGamificationUI loyaltyViewWithEmbedId:{{loyalty_id}}
                                  onHeight:^(CGFloat height) {
    self.heightConstraint.constant = height;
}];
```

> ⚠️ Gap: `HydraGamificationDelegate` and `setGamificationSuppressed(_:)` appear only in the Firebase-mode gamification guide of the Integration document (pp.30–33), not in gamification-ios; whether they work in direct mode isn't stated. Ask a Capillary engineer.

## Verification
- **Init:** an error thrown by `HydraConfiguration(...)` or `Hydra.generate(...)` is logged by the `catch` in step 3. Console logs default to `debug` (step 10).
- **Push:** the `MessagingDelegate` sample logs the FCM token (`FCM_Token is …`) and passes it to `update(interfaceID:)`; then follow `_shared/push.md` › Test the push flow. A rich push (image) shows the image only if the extension is set up (Push step 5).
- **Inbox:** the sample's `catch` prints `Error Initializing Hydra Inbox Core/UI: …` on failure; `refreshNotificationList()` fires when a new push is stored.
- **Gamification:** floating buttons, bottom sheets and popups appear on reported screens; Banner, Embedded and Loyalty content appears where those views were added.
- **Gamification checklist:** SDK at least `{{sdk_version}}`; gamification key plus region or base URL in `HydraConfiguration` (step 3); screens reported on appear and disappear (step 9); `setCapToken(...)` before a Loyalty View (step 11). Optional: Banner, Embedded, Loyalty views.

> ⚠️ Correction: ✅ Use `HydraConfiguration` arguments for the gamification values (step 3; gamification-ios Option B: literal values, no Remote Config). ❌ Don't use the Firebase Remote Config keys `hydra_gamification_region` / `hydra_gamification_key` / `hydra_gamification_base_url` (checklist, Integration document p.98; the gamification-ios checklist uses the same key names for both options). *Pending SME confirmation.*

> ⚠️ Gap: no SDK success log lines or dashboard checks are documented. Ask a Capillary engineer.

## Known Issues
| Symptom | Cause | Fix |
|---|---|---|
| SDK fetch fails (SPM / Xcode / CocoaPods) | No access to the private repo, or no credentials in Xcode / PAT in the URL | Request access from Capillary's access team; then step 1 |
| SPM resolves an old SDK | The docs' snippet uses `from: "1.1.0"` | Use `from: "{{sdk_version}}"` (step 2) |
| Objective-C code can't call `HydraConfiguration` / `Hydra.generate` | Both are Swift-only | Initialise from a small Swift file (step 3) |
| Events don't count | Reported before any sign-in / sign-up, or after sign-out | Report sign-in or sign-up first (steps 5, 8) |
| Push stops arriving after a token change | New FCM token not passed to the SDK | Call `update(interfaceID:)` from `messaging(_:didReceiveRegistrationToken:)` (Push step 4) |
| Rich push shows no image or buttons | No Notification Service Extension, framework not added to the extension target, or payload without `mutable-content: 1` | Push step 5 |
| Push CTA buttons (other than external URLs) do nothing | No `HydraNotificationCallbackDelegate` set | Set one with `setNotificationCallbackDelagte(delegate:)` (Push step 6) |
| Inbox doesn't store / show notifications | App Group missing or different between the app and extension targets, or push not initialised | Same App Group ID on every SDK target (Push step 2); initialise Inbox after `HydraCore` and `NotificationCore` |
| Screen-targeted campaigns don't appear | Current screen not reported | Report screens (step 9) |
| No gamification at all | Gamification key missing, or neither region nor base URL given | Pass key + region or base URL (step 3) |
| Loyalty View renders empty | Token missing or invalid before the view mounts | Call `setCapToken(...)` first (step 11) |
| Push never arrives although sign-in works | The app's Firebase project isn't the one registered at Capillary, APNs key not uploaded to Firebase, or the push gateway isn't set up yet | Push step 1; then `_shared/push.md` › Test the push flow and › Common problems |
| SDK log shows `Client Credentials Generation Failed` / `source not found` (400) | The app's registration at Capillary doesn't match the app. Documented only for the Android signature; whether a wrong bundle ID gives the same error isn't documented | Check the registered Bundle Name against your bundle ID and ask Capillary (`_shared/push.md`) |

## API Reference
| API | Purpose |
|---|---|
| `HydraConfiguration(accountID:server:orgID:gamificationWriteKey:gamificationRegion:gamificationBaseURL:)` | SDK config (`throws`) |
| `.genericServer(apiBaseURL, sslKey, retryDelays)` | `server:` value (Base URL, SSL key, retry delays) |
| `Hydra.generate(with:geoData:supportsPushNotifications:deviceScreenInfo:)` | Creates the `hydra` instance (`throws`); only `with:` is required in the examples |
| `hydra.update(customerID:)` / `update(deviceToken:)` / `update(interfaceID:)` / `update(notificationSupport:)` | Update customer ID, device token, FCM token, notification support |
| `UserDefaults.standard.setPromotionalPushOpted(status:)` / `setTransactionalPushOpted(status:)` | Promotional / transactional push opt status (default `false`) |
| `updateConsoleLogLevel(level:)` / `updateRemoteLogLevel(level:)` | Log levels `error`, `warning`, `info`, `debug`, `none` (defaults `debug` / `none`) |
| `UserDetails(customerId:firstName:lastName:email:phone:)` | User details for sign-up, sign-in, profile update |
| `hydra.reportUserSignUp(data:customData:)` / `reportUserSignIn(data:customData:)` | Sign-up / sign-in |
| `hydra.reportUserProfileUpdate(data:customData:subscriptions:)` | Profile update; `HydraSubscription(channel:priority:type:)` |
| `hydra.reportUserSignOut(customData:)` | Sign-out |
| `hydra.reportBehavioralEvent(name:customAttributes:)` | Custom event |
| `NotificationCore.shared` / `update(sdk:)` | Push core; pass the Hydra instance |
| `notificationCore.userNotification(center:didReceive:withCompletionHandler:)` / `userNotification(center:willPresent:withCompletionHandler:)` | Forward `UNUserNotificationCenterDelegate` calls |
| `notificationCore.setNotificationCallbackDelagte(delegate:)` | Register a `HydraNotificationCallbackDelegate` (`process(cta:notificationPayload:) -> Bool`) |
| `HydraRemoteNotificationService` (`didReceive(_:withContentHandler:)`, `serviceExtensionTimeWillExpire()`) | Notification Service Extension handling |
| `InAppMessagingCore.application(_:didReceiveRemoteNotification:fetchCompletionHandler:)` | Forward remote notifications to in-app |
| `InboxCoreConfiguration(hydraConfig:maximumNotificationCount:)` / `InboxCore(with:configuredFor:)` | Inbox core (`throws`) |
| `HydraInboxUIConfiguration(unreadMessageConfigType:readMessageConfigType:notificationsNotFoundConfiguration:placeholderImage:)` / `InboxUICore(with:configuration:)` | Inbox UI |
| `inboxUI.showNotificationCenter(with:)` / `getNotificationCenter()` / `notificationCenterSwiftUIView()` | Show the Notification Center |
| `inboxUI.setHydraInboxUIDelegate(delegate:)` + `HydraInboxUIProtocol.refreshNotificationList()` | Inbox change callback |
| `inboxCore.getUnreadNotificationCount`, `getNotifications`, `handleNotification(notification:action:completion:)` (`.read` / `.delete`), `handleDeleteAllNotifications()`, `performNotificationAction(notification:)`, `performNotificationExpandableCtaAction(notification:cta:)` | Inbox API (custom UI) |
| `hydra.gamificationScreenAppeared(_:)` / `gamificationScreenDisappeared(_:)` | Screen reporting (Swift) |
| `.gamificationScreen(_:)` | Screen reporting (SwiftUI modifier) |
| `[HydraGamificationUI reportScreen:]` / `reportScreenDisappeared:` | Screen reporting (Objective-C) |
| `hydra.setCapToken(_:)` / `[HydraGamificationUI setCapToken:]` | Capillary B2B token for Loyalty View |
| `hydra.gamificationBannerView(bannerId:)` / `GamificationBannerView(bannerId:)` / `bannerViewWithBannerId:onHeight:` | Banner (Swift / SwiftUI / ObjC) |
| `hydra.gamificationEmbedView(embedId:)` / `GamificationEmbedView(embedId:)` / `embedViewWithEmbedId:onHeight:` | Embedded (Swift / SwiftUI / ObjC) |
| `hydra.gamificationLoyaltyView(embedId:)` / `GamificationLoyaltyView(embedId:)` / `loyaltyViewWithEmbedId:onHeight:` | Loyalty (Swift / SwiftUI / ObjC) |
