---
updatedAt: 2026-11-12T10:14:48.000Z
agentTools:
  projectIndex: https://docs.capillarytech.com/llms.txt
---

# Configure Rich Push Notifications

Hydra supports rich push notifications, allowing you to include images, buttons, and potentially other interactive elements directly in the notification interface.

Integrate the HydraPushNotificationServiceExtension framework into a Notification Service Extension target to enable rich push processing. To do this, follow these steps:

1. ## Add Notification Service Extension Target:

   1. In Xcode, go to **File** > **New** > **Target**
   2. Select **Notification Service Extension** under the iOS tab.
   3. Give it a product name (e.g., YourAppNotificationService).
   4. Select Finish. If prompted, activate the new scheme by selecting **Activate**.

2. ## Add Framework to Extension Target:

   1. Add the `HydraPushNotificationServiceExtension` framework to this *new* target using your preferred  manager:\
      **Swift Package Manager (SPM):**

      1. In **Project Settings** > **Your Project** > **Package Dependencies**, select `hydra-ios-sdk-spm`.
      2. Under **Targets**, select your Notification Service Extension target.
      3. Check the box next to `HydraPushNotificationServiceExtension`.\
         **CocoaPods:**
      4. Add the following to your Podfile:

         ```ruby
         target 'YourNotificationServiceExtensionTargetName' do  
           use_frameworks!  
           pod 'HydraPushNotificationServiceExtension', :git => 'https://github.com/Capillary/hydra-ios-sdk-spm.git'  
         end  
         ```

         2. Run `pod install`

3. ## Modify NotificationService.swift:

   1. Open the NotificationService.swift file in your Notification Service Extension target
   2. Replace its content with the following code to delegate handling to the Hydra SDK:

   ```
   import UserNotifications  
   import HydraPushNotificationServiceExtension  
   import HydraCore // May be needed for Logger or other shared components  

   class NotificationService: HydraRemoteNotificationService {
   // The HydraRemoteNotificationService superclass handles the core logic.  
   // You generally don't need to override didReceive or serviceExtensionTimeWillExpire  
   // unless you have very specific custom logic \*in addition\* to Hydra's processing.  
     
   override func didReceive(\_ request: UNNotificationRequest, withContentHandler contentHandler: @escaping (UNNotificationContent) \-\> Void) {  
       HydraCore.Logger.debug("NotificationService: didReceive called.") // Example logging  
       // Ensure App Group UserDefaults migration/setup runs if needed.   
       // Consider calling a setup function if HydraCore requires it for extensions.  
       // UserDefaults.standard.performMigrationIfNeeded() // If applicable in extension  
       super.didReceive(request, withContentHandler: contentHandler)  
   }  

   override func serviceExtensionTimeWillExpire() {  
       HydraCore.Logger.debug("NotificationService: serviceExtensionTimeWillExpire called.") // Example logging  
       super.serviceExtensionTimeWillExpire()  
    }
   }
   ```

## How it Works:

1. When a remote notification with `mutable-content: 1`flag arrives while the app is in the background, iOS launches your Notification Service Extension.
2. The `didReceive` method in `HydraRemoteNotificationService` is called.
3. The SDK parses the payload, identifies rich content (like image URLs), downloads the image, attaches it to the notification content, and then calls the `contentHandler` to display the modified notification.

# Handling Notification Actions (CTAs)

Push notifications can include Call-to-Action (CTA) buttons. A CTA is a button or link that encourages users to take the next step. Phrases like “Shop now” or “Learn more” guide users clearly and effectively toward the desired action.

To setup CTA handling for rich push notifications follow these steps:

1. Define CTAs: CTAs are typically defined when creating the push notification campaign on the Capillary platform.
2. Implement Delegate:\
   Your application needs to handle what happens when a user taps a CTA button.\
   If the application did not conform to protocol `HydraNotificationCallbackDelegate` , SDK will only be able to handle external type CTA on its own. All the other types of CTA will be ignored.

   1. Create a class (or use an existing one like your `AppDelegate` or a dedicated manager) that conforms to the `HydraNotificationCallbackDelegate` protocol (defined in `HydraPushNotification`).
   2. Implement the required `process(cta:notificationPayload:)` -> `Bool` method.
   3. Set the following delegate instance on the `NotificationCore.shared` instance:

      ```
      import HydraPushNotification

          // In your AppDelegate or where you initialize NotificationCore:

          let actionHandler = NotificationActionHandler() // Create an instance

          func application(_ application : UIApplication, didFinishLaunchingWithOptions launchOptions : [UIApplication.LaunchOptionsKey : Any] ?)->Bool {
        // ... initialization ...
        notificationCore
            .update(sdk: hydraSDK)

            // Set the delegate for handling CTAs
            notificationCore.setNotificationCallbackDelagte(delegate: actionHandler)

            // ... rest of setup ...
            return true
      }

      // Example Implementation (e.g., in AppDelegate or a dedicated manager)
      class NotificationActionHandler : HydraNotificationCallbackDelegate {
        func process(cta: HydraCore.CTA, notificationPayload payload: Any)->Bool {
          print(
              "Processing CTA: Type='\(cta.type)', Action='\(cta.action)', Text='\(cta.actionText)'")

              // Parse the payload if needed (it's passed as Any)
              if let userInfo =
                  payload as ? [AnyHashable : Any] {
            // You might extract more context from the original payload
            print("Original Payload: \(userInfo)")
          }

          // Handle different CTA types based on the 'action' string
          switch
            cta.type {
              case CTAActionType.deepLink.rawValue:
                // Handle deep linking based on the cta.action value
                print("Handling Deep Link: \(cta.action)") if cta.action ==
                    "myapp://products/promo" {
                  // Navigate to specific screen
                  // NotificationCenter.default.post(name: .navigateToPromoProducts,
                  // object: nil)
                  return true  // Indicate we handled it
                }
                else {
                  return false  // Let SDK try default handling (if any) or ignore
                }

              case CTAActionType.external.rawValue:
                print("Handling External URL: \(cta.action)")
                    // Attempt to open the URL using Hydra's helper or
                    // UIApplication.shared.open
                    if let url = URL(string: cta.action),
                           UIApplication.shared.canOpenURL(url) {
                  DispatchQueue.main.async {
                    UIApplication.shared.open(url, options: [:],
                                              completionHandler: nil)
                  }
                  return true  // Indicate we handled it
                }
                else {
                  return false
                }

              default:
                print(
                    "Unhandled CTA type: \(cta.type)") return false  // Indicate we did not handle this type
            }
        }
      }
      ```
3. Delegate Responsibilities:
   1. The `process` method receives the `CTA` object (containing `type`, `action`, `actionText`) and the original notification payload (Any).
   2. Your code needs to interpret the `cta.type` and `cta.action` to perform the desired task (e.g., navigate to a screen, open a URL, call an API).
   3. Return `true` if your app successfully handled the action.
   4. Return `false` if your app did not handle the action. If you return `false` for common types like `external_url`, the SDK might attempt a default behavior (like trying to open the URL itself). For unhandled custom types, returning `false` usually means the action is ignored.