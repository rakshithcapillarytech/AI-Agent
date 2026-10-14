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
| Module | Status |
|---|---|
| Core: install, init, sign-in, sign-out, custom events | Documented (init, sign-in/out, events in Swift only) |
| Gamification: auto campaigns, screen reporting, Capillary token, Banner / Embedded / Loyalty views | Documented (Swift UIKit, SwiftUI, Objective-C) |
| Gamification delegate, UI suppression | Not documented |
| Push, In-App, Inbox | Pods listed in the Podfile only; no setup |
| Visitor, multi-account | Not documented |

## Requirements
- Hydra iOS SDK `{{sdk_version}}` (Beta for UAT/POC).
- Xcode with Swift Package Manager or CocoaPods. The Podfile uses `platform :ios, '13.0'`.

> ⚠️ Gap: Xcode / Swift / CocoaPods versions and a confirmed minimum iOS target aren't documented. Ask a Capillary engineer.

## Prerequisites
See `_shared/prerequisites.md`.
- **Client gives Capillary:** iOS bundle ID (`{{bundle_id}}`). Capillary's app team registers the app.
- **Capillary gives client:** Account Id, Base URL, SSL public key, Org Id, Gamification Key, Gamification Region, Gamification URL (optional).
- **Repo access:** the SDK installs from the private repo `https://github.com/Capillary/hydra-sdk-ios-packages`; request access from Capillary's access team. You then need GitHub credentials or a username + Personal Access Token (PAT) with access to it. The PAT stays on the client's machine; never share it in chat.

> ⚠️ Gap: the required PAT scopes aren't documented. Ask a Capillary engineer.

## Steps

### 1. Authenticate to the private repo
The SDK is in a private GitHub repo. Use one option.

**Option A: GitHub credentials in Xcode**
1. Open Xcode.
2. Go to **Xcode → Settings (Preferences) → Accounts**.
3. Add your GitHub account.
4. Ensure the account has access to `Capillary/hydra-sdk-ios-packages`.

**Option B: username + PAT.** Fill in locally; any file containing this URL holds the token in plain text:

```text
https://<GITHUB_USERNAME>:<PERSONAL_ACCESS_TOKEN>@github.com/Capillary/hydra-sdk-ios-packages.git
```

### 2. Install the SDK
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

> ⚠️ Correction: ✅ Use `.upToNextMajor(from: "{{sdk_version}}")` (the Required Version, p.91). ❌ Don't use `.upToNextMajor(from: "1.1.0")` (Package.swift snippet, p.90). *Pending SME confirmation.*

**Option B: Xcode**
1. Open your project in Xcode.
2. Select **File → Add Packages…**
3. Enter the repository URL (or the PAT URL from step 1).
4. Choose the version (`{{sdk_version}}`) or branch.
5. Click **Add Package**.
6. Select the required Hydra frameworks.
7. Click **Add Package** again.
8. Import the required framework, e.g. `import HydraCore`.

> ⚠️ Gap: which frameworks to add (SPM target, Xcode step 6) isn't listed beyond `HydraCore`. Ask a Capillary engineer.

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

Run `pod install` and open the generated `.xcworkspace`.

> ⚠️ Correction: ✅ Use `private_repo = '…'` above both `target` blocks, as shown. ❌ Don't use it inside `target 'YourAppTargetName' do` (Podfile, p.91): Ruby hides it from the second target. *Pending SME confirmation.*

> ⚠️ Gap: the Podfile pins no version, and it adds push pods and a Notification Service Extension target although this guide documents no push without Firebase. Ask a Capillary engineer how to pin `{{sdk_version}}` and which pods direct mode needs.

### 3. Use the required SDK version
Required version: **`{{sdk_version}}`** (Beta for UAT/POC).

> ⚠️ Gap: the docs disagree on repo and version. This guide: `https://github.com/Capillary/hydra-sdk-ios-packages`, required 1.7.5-preprod.12 (pp.89–91). Gamification iOS guide: `https://github.com/Capillary/hydra-ios-sdk-spm.git`, minimum 1.7.5-preprod.10 (p.26). Use this guide's values for direct mode, and ask a Capillary engineer.

### 4. Initialise the SDK
Swift (comments map source variables to Capillary values):

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

`hydra` is the SDK instance used by every later step. Region values: see `_shared/prerequisites.md`.

> ⚠️ Gap: undocumented: what `[0, 5, 10, 30, 120]` means (keep as given), where in the app lifecycle to call this, argument types (e.g. region string or enum), how to omit the optional base URL, and SwiftUI / Objective-C init. Ask a Capillary engineer.

### 5. Report user sign-in
Swift (UIKit):

```swift
let userDetails = UserDetails(customerId: userName, firstName: firstName, lastName: lastName, email: email, phone: phone)

hydra.reportUserSignIn(data: userDetails, customData: customData)
```

`customerId` must match the Account Linking Identifier in Capillary CRM (see `_shared/prerequisites.md`).

> ⚠️ Gap: which `UserDetails` fields are required isn't documented. Ask a Capillary engineer.

### 6. Report user sign-out
Swift (UIKit):

```swift
let customAttributes = ["key1": "value1", "key2": "value2"]
// customData: Dictionary containing extra information that application want to send to the server along with this event

hydra.reportUserSignOut(customData: customAttributes)
```

### 7. Report the current screen (required for gamification)
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

SwiftUI (the modifier reports appear/disappear automatically):

```swift
HydraGamificationUI().gamificationScreen("SampleScreenName")
```

> ⚠️ Gap: the docs disagree on the SwiftUI form. This guide applies the modifier to `HydraGamificationUI()` (p.93); the Gamification iOS guide applies it to the screen's own view, `SampleView().gamificationScreen("SampleScreenName")` (p.28). Ask a Capillary engineer.

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

### 8. Report custom behavioural events
Swift (UIKit):

```swift
let customAttributes = ["key1": "value1", "key2": "value2"]
hydra.reportBehavioralEvent(name:"custom_eventname", customAttributes: customAttributes)
```

### 9. Set the Capillary token (required for Loyalty View)
Set the Capillary B2B short-lived token **before** a Loyalty View renders; without a valid token, loyalty content may not appear. Token source: `_shared/prerequisites.md`.

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
> ⚠️ Gap: no push or rich-notification setup is documented beyond the Podfile pods. Ask a Capillary engineer.

### In-App
> ⚠️ Gap: no setup documented beyond the `HydraInAppMessage` pod. Ask a Capillary engineer.

### Inbox
> ⚠️ Gap: no setup documented beyond the `HydraInboxCore` / `HydraInboxUI` pods. Ask a Capillary engineer.

### Visitor
> ⚠️ Gap: not documented for this mode. Ask a Capillary engineer.

### Gamification
**Automatic experiences.** Once configured, Hydra shows Floating Button, Popup and Bottom Sheet campaigns with no extra code.

**Custom UI components (optional).** For each view: pass a unique view ID, register a height callback, update the view height dynamically. The IDs are entry-point IDs from Capillary; the height constraints are the host view's own.

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

*Loyalty View* (set the token first, step 9; the parameter label is `embedId:` as shown)

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

> ⚠️ Gap: `HydraGamificationDelegate` and `setGamificationSuppressed(_:)` appear only in the Firebase-mode gamification guide (pp.30–33); whether they work in direct mode isn't stated. Ask a Capillary engineer.

## Verification
- **Init:** an error thrown by `HydraConfiguration(...)` or `Hydra.generate(...)` is logged by the `catch` in step 4.
- **Result:** Floating Buttons, Bottom Sheets and Popups appear automatically; Banner, Embedded and Loyalty content appears where those views were added.
- **Checklist:** SDK `{{sdk_version}}`; gamification key, region, optional base URL in `HydraConfiguration` (step 4); screens reported (step 7); `setCapToken(...)` for Loyalty View. Optional: Banner, Embedded, Loyalty views.

> ⚠️ Correction: ✅ Use `HydraConfiguration` arguments for the gamification values (step 4). ❌ Don't use the Firebase Remote Config keys `hydra_gamification_region` / `hydra_gamification_key` / `hydra_gamification_base_url` (checklist, p.98). *Pending SME confirmation.*

> ⚠️ Gap: no success log lines, callbacks or dashboard checks are documented. Ask a Capillary engineer.

## Known Issues
| Symptom | Cause | Fix |
|---|---|---|
| SDK fetch fails (SPM / Xcode / CocoaPods) | No access to the private repo | Request access from Capillary's access team; then step 1 |
| Screen-targeted campaigns don't appear | Current screen not reported | Report screens (step 7) |
| Loyalty View shows no content | Token missing or invalid before render | Call `setCapToken(...)` first (step 9) |

## API Reference
| API | Purpose |
|---|---|
| `HydraConfiguration(accountID:server:orgID:gamificationWriteKey:gamificationRegion:gamificationBaseURL:)` | SDK config (`throws`) |
| `.genericServer(apiBaseURL, sslKey, [0, 5, 10, 30, 120])` | `server:` value (Base URL, SSL key) |
| `Hydra.generate(with:remoteLogLevel:)` | Creates the `hydra` instance (`throws`) |
| `UserDetails(customerId:firstName:lastName:email:phone:)` | Sign-in user details |
| `hydra.reportUserSignIn(data:customData:)` | Sign-in |
| `hydra.reportUserSignOut(customData:)` | Sign-out |
| `hydra.reportBehavioralEvent(name:customAttributes:)` | Custom event |
| `hydra.gamificationScreenAppeared(_:)` / `gamificationScreenDisappeared(_:)` | Screen reporting (Swift) |
| `.gamificationScreen(_:)` | Screen reporting (SwiftUI modifier) |
| `[HydraGamificationUI reportScreen:]` / `reportScreenDisappeared:` | Screen reporting (Objective-C) |
| `hydra.setCapToken(_:)` / `[HydraGamificationUI setCapToken:]` | Capillary B2B token for Loyalty View |
| `hydra.gamificationBannerView(bannerId:)` / `GamificationBannerView(bannerId:)` / `bannerViewWithBannerId:onHeight:` | Banner (Swift / SwiftUI / ObjC) |
| `hydra.gamificationEmbedView(embedId:)` / `GamificationEmbedView(embedId:)` / `embedViewWithEmbedId:onHeight:` | Embedded (Swift / SwiftUI / ObjC) |
| `hydra.gamificationLoyaltyView(embedId:)` / `GamificationLoyaltyView(embedId:)` / `loyaltyViewWithEmbedId:onHeight:` | Loyalty (Swift / SwiftUI / ObjC) |
| Pods (`:git => private_repo`) | `HydraCore`, `HydraPushNotification`, `HydraPushNotificationServiceExtension`, `HydraInAppMessage`, `HydraInboxCore`, `HydraInboxUI` |
