---
updatedAt: 2026-10-20T04:53:32.000Z
agentTools:
  projectIndex: https://docs.capillarytech.com/llms.txt
---

# Configure In-app Messaging

This page provides you with information on In-app messaging feature.

The HydraInAppMessage framework enables the display of contextual messages (like popups, banners, feedback forms) to users while they are actively using your app. These are typically triggered by silent push notifications or specific user actions/events defined in campaigns.

# Prerequisites

* HydraPushNotification framework:  In-App Messaging relies on both the core SDK and the push notification framework for receiving triggers (often via silent push) and reporting interaction events. Ensure both are initialized and configured correctly, including forwarding delegate methods for `NotificationCore`.
* Push Capabilities: Your app needs the “Push Notifications” and “Background Modes” (with “Remote notifications” enabled) capabilities configured in Xcode.

# Integration

Add the HydraInAppMessage framework. This framework is responsible for processing in-app messages.

# Initialize InAppMessagingCore object

Initialize `InAppMessagingCore` after `HydraCore` and `NotificationCore` have been set up, typically in your `AppDelegate`

```swift
// In your AppDelegate

import HydraInAppMessage

    class AppDelegate : UIResponder, UIApplicationDelegate {
  var hydraSDK : Hydra? let notificationCore =
                     NotificationCore.shared var inAppCore : InAppMessagingCore
                 ?

                 func application(
                     _ application: UIApplication,
                     didFinishLaunchingWithOptions
                         launchOptions: [UIApplication.LaunchOptionsKey : Any]?)
                     ->Bool {
    // --- Initialize Hydra Core, Notification Core, In-App Messaging ---
    // ... (as shown before) ...

    // --- Initialize In-App Messaging Core ---
    if let
      config =
          hydraSDK?.configuration() {  // Get config from initialized HydraCore
        // Prepare In-App specific configuration
        let inAppConfig = HydraInAppMessageConfiguration(
            hydraConfig: config,
            notificationCore: notificationCore,  // Pass the NotificationCore
                                                 // instance
            appStoreId: "YOUR_APP_STORE_ID",     // Optional: Required for App
                                                 // Rating messages
            placeholderImage: UIImage(
                named: "default-placeholder")  // Optional: Placeholder for
                                               // images
            )

            do {
          inAppCore = try
            InAppMessagingCore(
                with: inAppConfig,
                environment:.dev,  // Match environment used for HydraCore
                applicationState: application.applicationState)
                print("Hydra In-App Messaging Initialized Successfully!")
        }
        catch let error {
          print(
              "Error Initializing Hydra In-App Messaging: \(error.localizedDescription)")
        }
      }
    else {
      print(
          "Error: Cannot initialize In-App Messaging without HydraCore config.")
    }

    // --- Rest of AppDelegate setup ---
    // ... (Register for push, forward delegate methods etc.) ...

    return true
  }

  // ... other AppDelegate methods (including forwarded push methods)
}
```

| Parameter          | Type                     | Mandatory | Description                                                                 |
| :----------------- | :----------------------- | :-------- | :-------------------------------------------------------------------------- |
| `hydraConfig`      | `ConfigurationGenerator` | Yes       | The same `HydraConfiguration` instance used for `HydraCore` initialization. |
| `notificationCore` | `NotificationCore?`      | Yes       | The shared instance of `NotificationCore`.                                  |
| `appStoreId`       | `String?`                | No        | Your application’s App Store ID. **Required** if using App Rating messages. |
| `placeholderImage` | `UIImage?`               | No        | An optional placeholder image to show while message images are loading.     |

**Example:**

```swift
let config = try HydraConfiguration(accountID: "AccountID", customerId: "CustomerID", server: .server1)
guard let hydra = try? Hydra.generate(with: config) else {
    Logger.error("Error in configuration generation")
    return nil
}
Logger.updateLogLevel(level: .critical)
do {
    let inAppConfig = HydraInAppMessageConfiguration(hydraConfig: config, notificationCore: notificationCore, appStoreId: "", placeholderImage: nil)
    inAppCore = try InAppMessagingCore(with: inAppConfig, environment: .dev)
} catch let error {
    print(error)
}

```

# How it Works:

* `InAppMessagingCore` automatically registers itself with `NotificationCore` to listen for silent push notifications tagged for in-app messages.
* When a relevant silent push arrives, the SDK parses the payload, stores the message details locally (using its internal database), and potentially downloads associated images.
* The SDK manages a queue of messages and observes the application state.
* When the app is active and conditions are met (e.g., an app launch message is received), the `InAppDisplayManager` attempts to display the highest priority message from the queue.

# InApp-supported layouts

<Image alt="App rating" align="center" border={true} src="https://files.readme.io/8b2d8a2-App_rating.png">
  App rating
</Image>

<Image alt="Feedback" align="center" border={true} src="https://files.readme.io/a3f22bb-Feedback.png">
  Feedback
</Image>

<Image alt="Footer" align="center" width="35% " border={true} src="https://files.readme.io/dc3b779-Footer.png">
  Footer
</Image>

<Image alt="Header" align="center" width="35% " border={true} src="https://files.readme.io/3bd3e08-Header.png">
  Header
</Image>

<Image alt="Interstitial" align="center" width="5px" border={true} src="https://files.readme.io/3ee7a54-INTERSTITIAL.png">
  Interstitial
</Image>

<Image alt="Pop up" align="center" width="25% " border={true} src="https://files.readme.io/5d334ab-POP_UP.png">
  Pop up
</Image>

<Image alt="Rating" align="center" border={true} src="https://files.readme.io/98965d8-Rating.png">
  Rating
</Image>

# Handling Interactions

User interactions with in-app messages (button taps, submitting ratings/feedback, closing the message) are handled automatically by the SDK.

* The internal `InAppDisplayManager` captures the interaction.
* It calls the appropriate `HydraCore` methods to:
  * Report interaction events (e.g., `inAppMessageClicked`, `inAppMessageDismissed`, `inAppMessageRating`, `inAppMessageFeedback`).
  * Perform associated actions (e.g., navigating deep links or opening external URLs via `hydraCore.performCTAAction`).
  * Dismiss the in-app message view.
* No specific delegate implementation is required from the app for standard in-app message interactions.

## User Logout

When a user logs out, it’s important to clear any pending in-app messages associated with them.\
Call this after `hydraSDK?.reportUserSignOut(...)`:\
`inAppCore?.userLoggedOut()`