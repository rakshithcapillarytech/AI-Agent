---
updatedAt: 2026-03-04T06:05:34.000Z
agentTools:
  projectIndex: https://docs.capillarytech.com/llms.txt
---

# Configure Notification Inbox

This page provides information about notification inbox and how to configure it.

The Hydra SDK provides a Notification Inbox feature, allowing users to view a history of relevant push notifications received within the app. This uses the HydraInboxCore and HydraInboxUI frameworks.

The Notification Inbox helps with the following:

* **Centralized Management:** Users access a centralized hub for all push notifications, ensuring organization and control over their app interactions.
* **Enhanced Accessibility:** Notifications are no longer buried in cluttered bars; users can manage them efficiently, leading to a seamless experience.
* **Increased Engagement:** Clear and accessible notifications promote active engagement, allowing users to respond promptly to social interactions, promotions, and achievements.
* **Improved customer satisfaction:** The Notification Inbox will help to improve customer satisfaction by making the app more useful and engaging
* **Metrics**: Enables to track the number of users who open the Notification Inbox, the number of push notifications that are viewed in the Notification Inbox, and the number of push notifications that are deleted from the Notification Inbox

  ## Use Case: Retail Loyalty Program

  **Scenario:**\
  A retail company operates a loyalty program where customers earn points for each purchase. This program offers exclusive promotions and discounts to reward loyal customers. The app sends push notifications to users, notifying them of earned points and offering special discounts.
  **Issue:**
  Many users miss out on these discounts due to cluttered notification bars filled with messages from various apps. They frequently clear their notification bars without noticing the discounts, resulting in missed opportunities.
  **Solution:**
  Introducing a Notification Center within the app resolves this issue. Users can conveniently access all loyalty program notifications in one location. Here, they can easily view their accumulated points and available discounts. This streamlined approach enhances user engagement and loyalty.

# Prerequisites

1. **Notification Management:**\
   The Inbox relies on the core SDK and push handling.  To enable and support the Notification Center's functionality, developers must integrate two frameworks.
   * HydraPushNotification
   * HydraPushNotificationServiceExtension\
     Ensure they are initialized and push delegate methods are forwarded correctly.
2. **App Groups (Mandatory):**\
   The Inbox feature requires App Groups to be configured correctly to allow data sharing (notification storage) between the main app and the Notification Service Extension (which often saves the incoming notification).

   > ❗️ Make sure that the same App Group ID is enabled for all the targets where the Capillary SDK is utilized.

### Set up App group ID

To set up an App Group ID for the main application, from **TARGETS**, select your App Target, navigate to the **Signing & Capabilities** tab and perform the following:

i.  Enable **App Groups** for your app target and choose an App Group ID. If you don't have one, create a new one with the format `group.{your_bundle_id}.hydra`.

ii. Enable **Background mode** and select/enable **Remote Notification**.

iii. Turn on the **Push Notifications** capability for your app.

<Image align="center" className="border" border={true} src="https://files.readme.io/fad705a-iOS_SDK_App_group_identifier.png" />

To set up an App Group ID for the Push Notification Extension Target, from **TARGETS**, select your App Target, navigate to the **Signing & Capabilities** tab and perform the changes as shown in the image below:

<Image align="center" className="border" border={true} src="https://files.readme.io/01c6356-Push_notification_extension_target.png" />

**NOTE:** The App Group ID must precisely match the name of the main application.

# Initialisation

Initialize `InboxCore` and `InboxUICore` after `HydraCore` and `NotificationCore`.

```
// In your AppDelegate

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
        // ... (as shown before) ...

        // --- Initialize Inbox Core ---
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
                print("Hydra Inbox Core Initialized Successfully!")
                
                // --- Initialize Inbox UI ---
                // Configure UI (Default example)
                let inboxUIConfig = HydraInboxUIConfiguration(
                    unreadMessageConfigType: .defaultUnreadConfiguration, // Style for unread items
                    readMessageConfigType: .defaultReadConfiguration,   // Style for read items
                    // Optional: Configure empty state text/font
                    // notificationsNotFoundConfiguration: HydraInboxEmptyNotificationsConfiguration(...), 
                    placeholderImage: UIImage(named: "notification-placeholder") // Optional
                )
                
                inboxUI = InboxUICore(with: inboxCore!, configuration: inboxUIConfig)
                print("Hydra Inbox UI Initialized Successfully!")
                
            } catch let error {
                print("Error Initializing Hydra Inbox Core/UI: \(error.localizedDescription)")
            }
        } else {
             print("Error: Cannot initialize Inbox without HydraCore config.")
        }
        
        // --- Rest of AppDelegate setup ---
        // ...

        return true
    }
    
    // ... other AppDelegate methods
}
```

## Initialisation Details

### InboxCoreConfiguration:

* hydraConfig: The shared `HydraConfiguration` instance.
* maximumNotificationCount (Optional Int): Limits the number of notifications stored locally per user. Defaults to 250 if not provided

### HydraInboxUIConfiguration:

* `unreadMessageConfigType` / `readMessageConfigType`: Define the appearance of list items. Options:
  * `.defaultUnreadConfiguration` / `.defaultReadConfiguration`: Use the SDK’s default styling.
  * `.customConfiguration`(`HydraInboxMessageConfigurator`): Provide your own object conforming to `HydraInboxMessageConfigurator` to customize fonts, colors, borders, etc. (see `HydraInboxMessageUIConfiguration` struct for properties).
  * `.customReactNativeConfiguration`(`HydraInboxMessageReactNativeUIConfigurator`): Provide configuration using string representations (e.g., hex colors) suitable for cross-platform frameworks.
* `notificationsNotFoundConfiguration` (Optional `HydraInboxEmptyNotificationsConfigurator`): Customize the text and font displayed when the inbox is empty.
* `placeholderImage` (Optional `UIImage`): Image shown while notification images are loading.

# Displaying the Notification Center

The `HydraInboxUI` framework provides a pre-built view controller.

```
// Example: In a UIViewController that has a button to open the inbox

import UIKit
import HydraInboxUI // Import HydraInboxUI

class HomeViewController: UIViewController {

    // Assuming you have access to the initialized inboxUI instance 
    // (e.g., via AppDelegate singleton or dependency injection)
    var inboxUI: InboxUICore? 

    override func viewDidLoad() {
        super.viewDidLoad()
        // Get the inboxUI instance (example using AppDelegate)
        if let appDelegate = UIApplication.shared.delegate as? AppDelegate {
            self.inboxUI = appDelegate.inboxUI
        }
    }

    @IBAction func inboxButtonTapped(_ sender: Any) {
        guard let inboxUI = self.inboxUI, let navController = self.navigationController else {
            print("Inbox UI not available or not embedded in a Navigation Controller")
            return
        }
        
        // Option 1: Let the SDK push the view controller
        inboxUI.showNotificationCenter(with: navController)
        
        // Option 2: Get the view controller and push it manually
        // let inboxVC = inboxUI.getNotificationCenter()
        // navController.pushViewController(inboxVC, animated: true)
        
        // Option 3: Get the SwiftUI View (if integrating into a SwiftUI hierarchy)
        // let inboxSwiftUIView = inboxUI.notificationCenterSwiftUIView()
        // // Embed inboxSwiftUIView in your SwiftUI view...
    }
}
```

**Design Reference:** For detailed design and mockups, refer to the [Figma design](https://www.figma.com/design/XZHO6EOIeb4RnPFdhcTIkp/SDK-%7C-Notification-centre-enhancements?node-id=74-33608\&node-type=FRAME\&t=NvJcBai6WEcb6Pv1-0) .

# **Handling Interactions**

Similar to In-App Messaging, user interactions within the default Notification Center UI (tapping a notification to view details/perform primary action, tapping CTA buttons, deleting notifications) are **handled automatically by the`HydraInboxUI` framework**.

* It uses the underlying `InboxCore` instance to:
  * Mark notifications as read (handleNotification(action: .read)).
  * Delete notifications (`handleNotification(action: .delete)` or `handleDeleteAllNotifications`).
  * Trigger CTA actions (`performNotificationAction` or `performNotificationExpandableCtaAction`).
* The UI automatically refreshes when data changes.

# **Updating UI for Unread Count (e.g., Badge on a Bell Icon)**

You often need to display an indicator (like a badge) when there are unread notifications.

1. **Fetch Count:** `Use inboxCore.getUnreadNotificationCount { ... }` to get the current count asynchronously.
2. **Listen for Changes:** Implement the `HydraInboxUIProtocol` and set your class as the delegate using `inboxUI.setHydraInboxUIDelegate(delegate: self)`. The `refreshNotificationList()` method will be called whenever the inbox data changes (new message, read, delete).

   ```
   // Example: In your HomeViewController (or wherever the bell icon is)
   import HydraInboxCore // Import Core for the protocol

   class HomeViewController: UIViewController, HydraInboxUIProtocol {

       @IBOutlet weak var inboxBadgeLabel: UILabel! // Example UI element
       @IBOutlet weak var inboxButton: UIButton!
       
       var inboxUI: InboxUICore? 
       var inboxCore: InboxCore? // Need core instance to fetch count

       override func viewDidLoad() {
           super.viewDidLoad()
           if let appDelegate = UIApplication.shared.delegate as? AppDelegate {
               self.inboxUI = appDelegate.inboxUI
               self.inboxCore = appDelegate.inboxCore
               
               // Set self as the delegate to listen for changes
               self.inboxUI?.setHydraInboxUIDelegate(delegate: self)
           }
           updateInboxBadge()
       }
       
       override func viewWillAppear(_ animated: Bool) {
           super.viewWillAppear(animated)
           // Refresh badge when view appears, in case changes happened while away
           updateInboxBadge()
       }

       func updateInboxBadge() {
           inboxCore?.getUnreadNotificationCount { [weak self] count in
               DispatchQueue.main.async {
                   self?.inboxBadgeLabel.isHidden = (count == 0)
                   self?.inboxBadgeLabel.text = "\(count)"
                   // Add animation or other UI updates as needed
               }
           }
       }

       // MARK: - HydraInboxUIProtocol Delegate

       func refreshNotificationList() {
           // This method is called by the SDK when inbox data changes.
           // Update the badge count.
           print("Inbox delegate received refreshNotificationList call.")
           updateInboxBadge()
       }
       
       @IBAction func inboxButtonTapped(_ sender: Any) {
          // ... (Show inbox code from previous example) ...
          // Optionally, mark badge as 0 immediately when opened
          // inboxBadgeLabel.isHidden = true 
       }
   }
   ```

# **Building a Custom Inbox UI**

If the pre-built `HydraInboxUI` doesn’t meet your needs, you can build a completely custom UI using only `HydraInboxCore`:

1. Initialize `InboxCore` as shown before.
2. Fetch Data: Use `inboxCore.getNotifications { ... }` to get the `[HydraNotificationPayload]` array.
3. Display Data: Use the fetched data to populate your custom `UITableView`, `UICollectionView`, or SwiftUI `List`.
4. Handle Actions: In your custom UI, when a user taps or swipes:
   * Call `inboxCore.performNotificationAction(notification:)` for taps on the main item.
   * Call `inboxCore.performNotificationExpandableCtaAction(notification:cta:)` for secondary button taps.
   * Call `inboxCore.handleNotification(notification:action:completion:)` with `.read` when a notification is viewed/tapped, and with `.delete` when deleted.
5. **Refresh UI:** Use the `HydraInboxUIProtocol` delegate (`setHydraInboxUIDelegate`) to listen for `refreshNotificationList()` calls and update your custom UI accordingly. Fetch the latest data using `getNotifications` within the delegate method.

# API Usage

## HydraInboxCore

### **getUnreadNotificationCount()**

Use this API to retrieve the count of unread notifications using the instance of **InboxCore**. This method returns an integer value.

**Example:** In the example below, we have set a badge icon on the bell image if there is one or more unread notification(s):

```
guard let inboxCore Application Manager sharedObj inboxCore else
{
  return
}
if inboxCore getUnread NotificationCount() > 0
{
notificationButton setImage Ullmage system Name: "bell.badge" for normal
} 
else 
{
  notificationButton setImage Ullmage system Name: "bell" for normal
}

```

### **getNotifications()**

Use this API to get the available notifications. This method returns an array of **HydraNotificationPayload** objects. The configuration provided while initializing the InboxCore instance is used. For more information, refer to the [HydraInboxCoreConfigGenerator](https://docs.capillarytech.com/docs/configure-notification-center_ios#hydrainboxcore) section.

**Example:**

```swift
val notifications: List<HydraNotificationPayload> = inboxCore.getNotifications()
```

## **handleNotification(notification: HydraNotificationPayload, action: HydraNotificationAction)**

This API communicates the action taken on the notification to the SDK. The action should be an enum of type **HydraNotificationAction**.

There are two type of actions:

* Use `.read` when the user clicks on the notification, and
* `.delete` when the user wants to delete the notification.

Example:

```swift
inboxCore.handleNotification(notification.notification, HydraNotificationAction.READ)
```

#### **handleDeleteAllNotifications()**

This API deletes all notifications associated with the current user from the database. Returns `true` if all notifications were deleted successfully, otherwise `false`.

Example:

```swift
if (inboxCore.handleDeleteAllNotifications()) {
    Logger.info("Delete all notifications succeeded")
} else {
    Logger.error("Delete all notifications failed")
}
```

### **performNotificationAction(notification: HydraNotificationPayload)**

Use this API to perform the action associated with the notification when the user clicks on it.

Example:

```swift
inboxCore.performNotificationAction(notification.notification)
```

### **setHydraInboxUIDelegate(delegate: HydraInboxUIProtocol?)**

Use this API to set the delegate of **InboxCore**. The delegate is notified of changes in the database, such as insertion, deletion, or updates of notifications. The view displaying the Notification Center should implement the **HydraInboxUIProtocol** and use this method.

The Notification Center view can implement the `func refreshNotificationList()` to update the UI and refresh the notifications.

Example:

```swift


extension NotificationListViewModel: HydraInboxUIProtocol

{ func refreshNotificationList()
                                                         
{
DispatchQueue.main.async
  { [weak self] in self?.refresh()
}
}
}
```

## **HydraInboxUI**

To show Notification Center, an Application Developer can use either

* `showNotificationCenter(with navigationController: UINavigationController)`\
  OR
* `getNotificationCenter() `API

#### **showNotificationCenter(with navigationController: UINavigationController)**

Use this API to push Notification Center created by the SDK in the given navigationController.

Example:

```swift
inboxUI.showNotificationCenter(with = navigationController)
```

### **getNotificationCenter()**

Use this API to obtain the Notification Center created by the SDK. The application can then decide whether to push or present this Notification Center.

Example:

```swift
val notificationCenterViewController = inboxUI.getNotificationCenter()
navigationController.pushViewController(notificationCenterViewController, animated = true)
```

#### **setHydraInboxUIDelegate(delegate: HydraInboxUIProtocol)**

Use this API to set the delegate of **InboxUICore**. This delegate is also passed internally to the **InboxCore** delegate. By doing so, changes notified by **InboxCore** are directly passed to this delegate.

Example:

For instance, if you have a bell icon on the Home screen that should show a badge when there are unread notifications, set the delegate of **InboxUICore** on the Home screen using this method. Implement the **refreshNotificationList()** method in the Home screen to update the bell icon accordingly:

```swift
override func viewWillAppear(_ animated: Bool) {
        super.viewWillAppear(animated)
        updateNotificationBellIcon()
       self.inboxUI.setInboxUIDelegate(delegate: self)
}
@objc private func updateNotificationBellIcon() {
        guard let inboxCore = ApplicationManager.sharedObj.inboxCore else {
            return
        }
        if inboxCore.getUnreadNotificationCount() > 0 {
            notificationButton.setImage(UIImage(systemName: "bell.badge"), for: .normal)
        } else {
            notificationButton.setImage(UIImage(systemName: "bell"), for: .normal)
        }
    }


extension HomeViewController: HydraInboxUIProtocol {
    func refreshNotificationList() {
        DispatchQueue.main.async { [weak self] in
            self?.updateNotificationBellIcon()
        }
    }
}

```

***