---
platform: ios
config_mode: direct
sdk_package: HydraCore   # from the private repo https://github.com/Capillary/hydra-sdk-ios-packages (SPM / Xcode / CocoaPods)
sdk_version: 1.7.5-preprod.12   # "Required Version", Beta for UAT/POC (p.91)
modules_covered: [core, gamification]
modules_missing: [push, inapp, inbox_api, inbox_ui, visitor, multi_account]
sources: ["Integration document _ Experience+ pp.88–99 (Hydra iOS SDK Integration Doc, without firebase)"]
owner: TBD
last_verified: null
review_status: draft   # drafted from the source doc; not yet SME-verified
---
# iOS (without Firebase)

## Coverage
| Module | Status in this mode |
|---|---|
| Core: install, initialisation, sign-in, sign-out, custom events | Documented. Initialisation, sign-in, sign-out and events are shown in Swift only (no SwiftUI or Objective-C variants) |
| Gamification: automatic campaigns, screen reporting, Capillary token, Banner / Embedded / Loyalty views | Documented in Swift (UIKit), SwiftUI and Objective-C |
| Gamification delegate callbacks, gamification UI suppression | Not documented in this guide |
| Push and rich notifications (`HydraPushNotification`, `HydraPushNotificationServiceExtension`) | Pods appear in the CocoaPods Podfile only. No setup steps, and the guide doesn't say whether push works without Firebase |
| In-App messaging (`HydraInAppMessage`) | Pod appears in the Podfile only. No setup steps |
| Inbox / Notification Center (`HydraInboxCore`, `HydraInboxUI`) | Pods appear in the Podfile only. No setup steps |
| Visitor flow, multi-account | Not documented |

## Requirements
- SDK version: `{{sdk_version}}` (Beta for UAT/POC).
- Read access to the private GitHub repository `https://github.com/Capillary/hydra-sdk-ios-packages` (see Prerequisites).
- Xcode, with one of these package managers: Swift Package Manager (`Package.swift`), Xcode's package manager, or CocoaPods.
- The source's Podfile declares `platform :ios, '13.0'` and `use_frameworks!` (p.91). The guide doesn't otherwise state a minimum iOS version.

> ⚠️ Gap: the source doesn't state the minimum iOS deployment target (beyond the Podfile line), or the Xcode, Swift or CocoaPods versions. Ask a Capillary engineer before giving numbers.

## Prerequisites
See `_shared/prerequisites.md` for the common exchange. For this platform and mode:
- **Client gives Capillary:** the iOS bundle ID (`{{bundle_id}}`). Capillary's app team registers the app.
- **Capillary gives client:**
  - Account Id
  - Base URL
  - SSL public key
  - Org Id
  - Gamification Key
  - Gamification Region
  - Gamification URL (optional)
- **Repository access:** access to `https://github.com/Capillary/hydra-sdk-ios-packages`, requested from Capillary's access team. You then need **either**:
  - GitHub credentials (a GitHub account) with access to the `hydra-sdk-ios-packages` repository, **or**
  - a GitHub username plus a Personal Access Token (PAT) with access to the repository.
- **Token safety:** the PAT stays on the client's machine. Never paste it into chat or share it with anyone, Capillary included.

> ⚠️ Gap: the source doesn't state which scopes the PAT needs. Ask a Capillary engineer.

## Steps

### 1. Authenticate to the private SDK repository
The Hydra SDK is hosted in a private GitHub repository. Use one of these two options.

**Option A: GitHub credentials in Xcode**
1. Open Xcode.
2. Go to **Xcode → Settings (Preferences) → Accounts**.
3. Add your GitHub account.
4. Make sure the account has access to the `Capillary/hydra-sdk-ios-packages` repository.

**Option B: GitHub username and Personal Access Token.** Use this repository URL:

```text
https://<GITHUB_USERNAME>:<PERSONAL_ACCESS_TOKEN>@github.com/Capillary/hydra-sdk-ios-packages.git
```

The client replaces `<GITHUB_USERNAME>` and `<PERSONAL_ACCESS_TOKEN>` locally. **The token stays on the client's machine.** Any file that contains this URL, such as the Podfile in step 2, contains the token in plain text.

### 2. Install the SDK
Use **any one** of the three methods below.

**Option A: Swift Package Manager (`Package.swift`)**

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

> ⚠️ Source doc correction: the source's `Package.swift` snippet says `.upToNextMajor(from: "1.1.0")` (p.90) vs the Required Version 1.7.5-preprod.12 stated in "1. Hydra SDK Version" (p.91). This file uses `{{sdk_version}}`. *Pending SME confirmation.*

> ⚠️ Gap: the snippet adds the package but doesn't show which product(s) to add to the app target's dependencies. Ask a Capillary engineer.

**Option B: Xcode**
1. Open your project in Xcode.
2. Select **File → Add Packages…**
3. Enter the repository URL, or the PAT URL from step 1 if you use that option.
4. Choose the version (`{{sdk_version}}`, see step 3) or branch.
5. Click **Add Package**.
6. Select the required Hydra frameworks.
7. Click **Add Package** again.
8. Import the required framework, for example `import HydraCore`.

> ⚠️ Gap: the source names only `HydraCore` as an example. It doesn't list the frameworks to select in step 6, or say which framework provides the gamification APIs. Ask a Capillary engineer.

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

Run `pod install`, then open the generated `.xcworkspace`.

> ⚠️ Source doc correction: in the source's Podfile, `private_repo = '...'` is assigned **inside** the `target 'YourAppTargetName' do … end` block (p.91). The second `target` block then uses `private_repo`, but in Ruby a local variable assigned inside one block isn't visible in another, so that block would hit an undefined-variable error. The Podfile above moves the assignment above both targets, so both blocks can use it. *Pending SME confirmation.*

> ⚠️ Source doc correction: this guide is "without firebase", yet its Podfile (p.91) includes `HydraPushNotification` and `HydraPushNotificationServiceExtension`, plus a separate Notification Service Extension target. The guide documents no push setup and doesn't say whether push is available without Firebase. Ask a Capillary engineer which pods a direct-mode app actually needs. *Pending SME confirmation.*

> ⚠️ Gap: the Podfile pins no version, so how to select `{{sdk_version}}` with CocoaPods isn't stated. Ask a Capillary engineer.

### 3. Use the required SDK version
Add the Hydra iOS SDK version to the application. The required version is **`{{sdk_version}}`** (Beta for UAT/POC).

> ⚠️ Source doc correction: this guide requires 1.7.5-preprod.12 from the repository `hydra-sdk-ios-packages` (pp.89–91) vs the Gamification iOS Integration Guide in the same document, which gives a minimum of 1.7.5-preprod.10 from `https://github.com/Capillary/hydra-ios-sdk-spm.git` (p.26). Use this guide's values for direct mode until an SME confirms. *Pending SME confirmation.*

### 4. Initialise the SDK
Swift. The comments map each source variable to the value Capillary provides:

```swift
do {
    let hydraConfig = try HydraConfiguration(
        accountID: accountID,                         // {{account_id}}
        server: .genericServer(apiBaseURL, sslKey, [0, 5, 10, 30, 120]),   // apiBaseURL = {{base_url}}, sslKey = {{ssl_public_key}}
        orgID: orgId,                                 // {{org_id}}
        gamificationWriteKey: gamificationWriteKey,   // {{gamification_key}}
        gamificationRegion: gamificationRegion,       // {{gamification_region}}
        gamificationBaseURL: gamificationBaseURL)     // {{gamification_base_url}} (optional)

    hydra = try Hydra.generate(with: hydraConfig, remoteLogLevel: .debug)
} catch let error {
    Logger.error(error.localizedDescription)
}
```

- `hydra` is the SDK instance. Every later step calls it (`hydra.reportUserSignIn(...)`, `hydra.gamificationScreenAppeared(...)` …).
- `remoteLogLevel: .debug` is the log level the source uses.
- Allowed gamification region values are listed in `_shared/prerequisites.md`.

> ⚠️ Gap: the third argument of `.genericServer(...)`, `[0, 5, 10, 30, 120]`, isn't explained anywhere in the source. Keep it exactly as given; don't guess its meaning. Ask a Capillary engineer.

> ⚠️ Gap: the source doesn't say any of the following:
> - where in the app lifecycle to run this code;
> - where to declare and keep the `hydra` property;
> - the Swift types of `accountID`, `apiBaseURL`, `sslKey`, `orgId`, `gamificationRegion` and `gamificationBaseURL` (for example, whether the region is a string or an enum);
> - how to leave out the optional gamification base URL;
> - what other `remoteLogLevel` values exist, or which one to use in production;
> - what `Logger` is (an SDK type or the sample app's own logger).
>
> No Objective-C or SwiftUI initialisation is given. Ask a Capillary engineer.

### 5. Report user sign-in
Swift (UIKit):

```swift
let userDetails = UserDetails(customerId: userName, firstName: firstName, lastName: lastName, email: email, phone: phone)

hydra.reportUserSignIn(data: userDetails, customData: customData)
```

`customerId` must match the Account Linking Identifier configured in Capillary CRM (see `_shared/prerequisites.md`).

> ⚠️ Gap: the source doesn't say which `UserDetails` fields are required and which are optional, or the type of `customData`. The sign-out step describes `customData` as a dictionary. Ask a Capillary engineer.

### 6. Report user sign-out
Swift (UIKit):

```swift
let customAttributes = ["key1": "value1", "key2": "value2"]
// customData: Dictionary containing extra information that application want to send to the server along with this event

hydra.reportUserSignOut(customData: customAttributes)
```

### 7. Report the current screen (required for gamification)
HydraGamification uses screen information to decide when and where to show campaigns. **Screen reporting is mandatory for screen-targeted campaigns.** Campaign visibility and eligibility depend on the currently reported screen.

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

SwiftUI:

```swift
HydraGamificationUI().gamificationScreen("SampleScreenName")
```

The `gamificationScreen` modifier reports screen appearance and disappearance automatically. No manual lifecycle callbacks are needed.

> ⚠️ Source doc correction: this guide's SwiftUI sample applies the modifier to `HydraGamificationUI()` (p.93). The Gamification iOS Integration Guide in the same document applies it to the screen's own view instead: `SampleView().gamificationScreen("SampleScreenName")` (p.28). Elsewhere `HydraGamificationUI` is used only as an Objective-C class with class methods. *Pending SME confirmation.*

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

> ⚠️ Gap: the source doesn't say how screen names must match campaign configuration, or which import Objective-C files need to use `HydraGamificationUI`. Ask a Capillary engineer.

### 8. Report custom behavioural events
Swift (UIKit):

```swift
let customAttributes = ["key1": "value1", "key2": "value2"]
hydra.reportBehavioralEvent(name: "custom_eventname", customAttributes: customAttributes)
```

### 9. Set the Capillary token (required for Loyalty View)
A new public API supports the Loyalty View. Set the Capillary B2B short-lived token **before** a Loyalty View is displayed. Where the token comes from is described in `_shared/prerequisites.md`.

Swift:

```swift
hydra.setCapToken(token)
```

SwiftUI:

```swift
hydra.setCapToken(token)
```

Objective-C:

```objc
[HydraGamificationUI setCapToken:token];
```

**Important** (from the source, p.95):
- The Capillary token must be set before the Loyalty View renders.
- Without a valid token, loyalty content may not appear.

## Modules

### Push
The Podfile (step 2) lists `HydraPushNotification` and `HydraPushNotificationServiceExtension`, plus a Notification Service Extension target.
> ⚠️ Gap: no push or rich-notification setup is documented for this mode, and the guide doesn't say whether push works without Firebase. Ask a Capillary engineer.

### In-App
The Podfile (step 2) lists `HydraInAppMessage`.
> ⚠️ Gap: no further setup steps are documented for this mode. Ask a Capillary engineer.

### Inbox
The Podfile (step 2) lists `HydraInboxCore` and `HydraInboxUI`.
> ⚠️ Gap: no further setup steps are documented for this mode. Ask a Capillary engineer.

### Visitor
> ⚠️ Gap: not documented for this mode. Ask a Capillary engineer.

### Gamification
**Automatic experiences.** Once configured (steps 4 and 7, plus step 9 for Loyalty), Hydra handles these campaign types with no extra code. It evaluates campaign eligibility and shows content when it applies.
- Floating Button campaigns
- Popup campaigns
- Bottom Sheet campaigns

**Custom UI components** (optional). To show gamification content inside the app's own screens, use the views below. For each view:
1. Pass a unique view ID.
2. Register a height callback.
3. Update the view height dynamically.

The IDs (`{{banner_id}}`, `{{embed_id}}`, `{{loyalty_id}}`) are the entry-point IDs from Capillary (see `_shared/prerequisites.md`). The source writes them as constants (`BANNER_ID`, `EMBED_ID`, `LOYALTY_ID`) and doesn't state their type. In the UIKit / Objective-C samples, `bannerHeightConstraint` / `heightConstraint` are the host view's own height constraints.

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
GamificationEmbedView(
    embedId: {{embed_id}}
)
```

Objective-C:

```objc
UIView *embed =
[HydraGamificationUI embedViewWithEmbedId:{{embed_id}}
                                onHeight:^(CGFloat height) {
    self.heightConstraint.constant = height;
}];
```

*Loyalty View.* Set the Capillary token first (step 9). In the source, the Loyalty View's parameter label is `embedId:` / `EmbedId:`, not a loyalty-specific label. Keep it as shown.

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
GamificationLoyaltyView(
    embedId: {{loyalty_id}}
)
```

Objective-C:

```objc
UIView *loyalty =
[HydraGamificationUI loyaltyViewWithEmbedId:{{loyalty_id}}
                                  onHeight:^(CGFloat height) {
    self.heightConstraint.constant = height;
}];
```

> ⚠️ Gap: this guide documents no gamification delegate (lifecycle, campaign, analytics or deeplink callbacks) and no API to suppress automatic gamification UI. The Gamification iOS Integration Guide in the same document describes `HydraGamificationDelegate` and `setGamificationSuppressed(_:)` (pp.30–33). It doesn't say whether they apply in direct mode. Ask a Capillary engineer before using them here.

## Verification
**SDK initialisation.** `HydraConfiguration(...)` and `Hydra.generate(with:remoteLogLevel:)` are both called with `try` inside the `do / catch` from step 4. If either throws, the `catch` block logs `error.localizedDescription` and initialisation has failed. The source doesn't describe what a successful initialisation looks like beyond no error being thrown.

**Expected result** (from the source, p.99): after the required steps, HydraGamification campaigns appear in the app automatically:
- Floating Buttons
- Bottom Sheets
- Popups

If the optional UI components were added, Banner, Embedded and Loyalty content also appears inside the app's screens.

**Required checklist** (from the source, p.98; Hydra configuration items adjusted, see the correction below):
- Updated to the latest Hydra iOS SDK version (required: `{{sdk_version}}`).
- Gamification region, key and (optional) base URL passed to `HydraConfiguration` as `gamificationRegion`, `gamificationWriteKey` and `gamificationBaseURL` (step 4).
- Screen names reported (step 7).
- Capillary token set with `setCapToken(...)` (required for Loyalty View).

Optional: Banner View, Embedded View, Loyalty View added.

> ⚠️ Source doc correction: the source checklist (p.98) says "Add `hydra_gamification_region` / `hydra_gamification_key` / `hydra_gamification_base_url` (Optional)". Those are Firebase Remote Config key names, as used by the Firebase-mode gamification guide (p.27). In this mode there's no Remote Config: the values go into `HydraConfiguration` (step 4). *Pending SME confirmation.*

> ⚠️ Gap: the source gives no formal verification procedure. There are no expected log lines, no callbacks confirming initialisation or gamification readiness, and no dashboard checks for sign-in, sign-out or events. Ask a Capillary engineer which Xcode console output to look for with `remoteLogLevel: .debug`.

## Known Issues

**Swift Package Manager, Xcode or CocoaPods can't fetch the Hydra SDK**
- Cause: the SDK lives in the private repository `Capillary/hydra-sdk-ios-packages`. Fetching fails without GitHub credentials, or a username + PAT, that have access to it.
- Fix:
  1. Request repository access from Capillary's access team.
  2. Then either add the GitHub account in **Xcode → Settings → Accounts**, or use the PAT URL (step 1).

*From the source doc (prerequisites and installation, pp.89–90).*

**Screen-targeted campaigns don't appear**
- Cause: the current screen isn't reported. Campaign visibility and eligibility depend on the currently reported screen.
- Fix: report screens as in step 7.

*From the source doc (p.94).*

**Loyalty View shows no content**
- Cause: the Capillary B2B token wasn't set, or wasn't valid, before the Loyalty View rendered.
- Fix: call `setCapToken(...)` before rendering the Loyalty View (step 9).

*From the source doc (p.95).*

## API Reference

**Configuration and initialisation**

| API | Purpose |
|---|---|
| `HydraConfiguration(accountID:server:orgID:gamificationWriteKey:gamificationRegion:gamificationBaseURL:)` | Builds the SDK configuration (`throws`) |
| `.genericServer(apiBaseURL, sslKey, [0, 5, 10, 30, 120])` | `server:` value carrying the Base URL and SSL public key. The integer array is unexplained in the source |
| `Hydra.generate(with:remoteLogLevel:)` | Creates the Hydra instance (`throws`). The source passes `remoteLogLevel: .debug` |

**User and event reporting**

| API | Purpose |
|---|---|
| `UserDetails(customerId:firstName:lastName:email:phone:)` | User details for sign-in |
| `hydra.reportUserSignIn(data:customData:)` | Reports sign-in |
| `hydra.reportUserSignOut(customData:)` | Reports sign-out, with an optional custom-data dictionary |
| `hydra.reportBehavioralEvent(name:customAttributes:)` | Reports a custom behavioural event |

**Screen reporting**

| API | Purpose |
|---|---|
| `hydra.gamificationScreenAppeared(_:)` | Reports that a screen appeared (Swift, UIKit) |
| `hydra.gamificationScreenDisappeared(_:)` | Reports that a screen disappeared (Swift, UIKit) |
| `.gamificationScreen(_:)` | SwiftUI modifier. Reports appearance and disappearance automatically (see the step 7 correction) |
| `[HydraGamificationUI reportScreen:]` | Reports that a screen appeared (Objective-C) |
| `[HydraGamificationUI reportScreenDisappeared:]` | Reports that a screen disappeared (Objective-C) |

**Capillary token**

| API | Purpose |
|---|---|
| `hydra.setCapToken(_:)` / `[HydraGamificationUI setCapToken:]` | Sets the Capillary B2B short-lived token for the Loyalty View |

**Gamification views**

| API | Purpose |
|---|---|
| `hydra.gamificationBannerView(bannerId:) { height in … }` | Banner view with a height callback (Swift, UIKit) |
| `GamificationBannerView(bannerId:)` | Banner view (SwiftUI) |
| `[HydraGamificationUI bannerViewWithBannerId:onHeight:]` | Returns a `UIView *` banner (Objective-C) |
| `hydra.gamificationEmbedView(embedId:) { height in … }` | Embedded view with a height callback (Swift) |
| `GamificationEmbedView(embedId:)` | Embedded view (SwiftUI) |
| `[HydraGamificationUI embedViewWithEmbedId:onHeight:]` | Returns a `UIView *` embedded view (Objective-C) |
| `hydra.gamificationLoyaltyView(embedId:) { height in … }` | Loyalty view with a height callback (Swift) |
| `GamificationLoyaltyView(embedId:)` | Loyalty view (SwiftUI) |
| `[HydraGamificationUI loyaltyViewWithEmbedId:onHeight:]` | Returns a `UIView *` loyalty view (Objective-C) |

**Packages**

| Package | Notes |
|---|---|
| SPM / Xcode: `https://github.com/Capillary/hydra-sdk-ios-packages` | Products to select aren't listed, apart from the `import HydraCore` example |
| CocoaPods pods (`:git => private_repo`) | `HydraCore`, `HydraPushNotification`, `HydraPushNotificationServiceExtension`, `HydraInAppMessage`, `HydraInboxCore`, `HydraInboxUI`; also `HydraPushNotificationServiceExtension` in the Notification Service Extension target |
