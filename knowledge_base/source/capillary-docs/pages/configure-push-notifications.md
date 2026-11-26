---
updatedAt: 2026-11-16T05:54:42.000Z
agentTools:
  projectIndex: https://docs.capillarytech.com/llms.txt
---

# Configure Push Notifications

This page provides you with information on push notifications and how to configure it.

Push notifications are alerts that appear on a user's screen when an update occurs on the mobile app. The notification appears even if the user is not using the mobile app. They are useful for delivering timely and personalised content to users and can be an effective way to increase user engagement with your app.

The HydraPushNotification framework, along with HydraCore, enables your application to receive and handle push notifications sent via the Capillary platform. The framework also records data related to notifications and can be used for analytics. It also handles reporting of delivery and interaction events (DLRs).

You need to integrate the below frameworks to enable the push notifications:

* HydraPushNotification
* HydraPushNotificationServiceExtension

Capillary SDK sends push notifications to users using [Firebase Cloud Messaging](https://firebase.google.com/docs/cloud-messaging/) (FCM). Firebase Cloud Messaging is a service that allows you to send notifications to your applications and receive information from them.

To configure APNS Push notifications with Firebase, perform the following:

1. Download APNs key
   1. Log into your Apple developer account.
   2. Navigate to **Certificates, Identifiers and Profiles**.
   3. Click **Keys** and then click  the “+” button in the top right corner.
   4. In the **Name** field, enter a name for your APNs Auth Key.
   5. Select Apple Push Notification Service (APNs).
   6. Click **Continue**.
   7. Verify the information and click **Confirm**.
   8. Click **Download** to download your auth key file. Copy and save the Key ID.

> 📘 Note
>
> You can only download the file once. Make sure you save this file properly and create a backup for later. Do not rename the file. You can also use APNs certificate. For more information see [Apple developer guide](https://developer.apple.com/documentation/usernotifications/setting_up_a_remote_notification_server/establishing_a_token-based_connection_to_apns).

2. Add the APNs key/certificate to the Firebase
   1. In the Firebase Console, go to your project settings.
   2. Select the **Cloud Messaging** tab.
   3. Click on **iOS app configuration**.
   4. Upload your APNs authentication key or certificate. For more information, see [Firebase documentation](https://firebase.google.com/docs/cloud-messaging/ios/client#upload_your_apns_authentication_key).

3. Create a service account key for Capillary

   The Capillary backend needs a Firebase service-account private key to send notifications through FCM. Your iOS app doesn't need this key and must never contain it. For information on how to create and share the key, see [Configure Firebase](https://docs.capillarytech.com/docs/configure-firebase).

4. Add the Firebase configuration file to project
   1. Download the **GoogleService-Info.plist file** for your app.
   2. Open your Xcode project.
   3. Drag and drop the GoogleService-Info.plist file into your project.\
      Make sure that the file is added to your app's target.\
      For more information on **GoogleService-Info.plist file** and on adding it to your Firebase project, see [Firebase documentation](https://firebase.google.com/docs/ios/setup#add-config-file).

# Initialisation

To initialise the push notifications, perform the following:

## Install Firebase SDK and set up push notifications in your app

1. In your Xcode project, open your app's `AppDelegate.swift `file.
2. Import the Firebase and FirebaseMessaging.
3. In the `didFinishLaunchingWithOptions` method, add the following code to initialise Firebase:

```swift
import Firebase
import FirebaseMessaging


func application(_ application: UIApplication, didFinishLaunchingWithOptions launchOptions: [UIApplication.LaunchOptionsKey: Any]?) -> Bool {
        FirebaseApp.configure()
        Messaging.messaging().delegate = self


        // Add any additional configuration code or other setup here


        return true
}

```

## Initialise NotificationCore

1. Initialise `HydraPushNotification` object. Use below API:
   ```swift
   let notificationCore:NotificationCore = NotificationCore.shared
   ```
2. Pass the HydraCore object created previously.

```swift
notificationCore.update(sdk: hydraCoreSDK)
```

## Trigger HydraPushNotification APIs from AppDelegates

The `HydraPushNotification` class is responsible for implementing APIs that respond to the life cycle methods of the application, including the AppDelegate protocols. To ensure the smooth functioning of `HydraPushNotification`, the application should trigger the following methods from their appropriate locations:

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

## Send FCM token to SDK

From AppDelegate's `didReceiveRegistrationToken`, send the received token to the SDK using the HydraCore object created previously.

```swift
extension AppDelegate:MessagingDelegate{
    func messaging(_ messaging: Messaging, didReceiveRegistrationToken fcmToken: String?) {
        if let fcmToken = fcmToken {
            Logger.info("FCM Token is \(fcmToken)")
            hydraCoreSDK.update(interfaceID: fcmToken)

        }
    }
}
```

**Example:**

```swift
class AppDelegate: UIResponder, UIApplicationDelegate {
    private var notificationCore:NotificationCore
    func application(_ application: UIApplication, didFinishLaunchingWithOptions launchOptions: [UIApplication.LaunchOptionsKey: Any]?) -> Bool {
        self.notificationCore.application(application, didFinishLaunchingWithOptions: launchOptions)
    }
    
}
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

# Customise and modify push notifications

You can integrate `HydraPushNotificationExtensionService` framework to` UNNotificationServiceExtension`  to customise and modify incoming remote notifications before they are displayed to the user.  Perform the following:

## 1. Create a push notification service extension target

To create a service extension target:

1. In Xcode, from the **File** menu, click **New** and select **Target**.

<Image align="center" border={true} src="https://files.readme.io/4bea20c-Select_target.png" className="border" />

2. Select **Notification Service Extension**.

<Image align="center" border={true} src="https://files.readme.io/c6a2b32-Select_Service_Extension.png" className="border" />

3. Enter a name for the extension target and add it to the project.

For more information on service extension, see [UNNotificationServiceExtension documentation](https://developer.apple.com/documentation/usernotifications/unnotificationserviceextension).

## 2. Add `HydraPushNotificationServiceExtension` framework to extension target

Add `HydraPushNotificationServiceExtension` framework to **Frameworks and Libraries** of notification service extension.

<Image align="center" border={true} src="https://files.readme.io/7ad65fe-Add_framework.png" className="border" />

## 3. Make changes to the`UNNotificationServiceExtension` class

Import `HydraPushNotificationServiceExtension` and call the API from this framework. See the code snippet below.

```swift
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

# Gateway configuration

To enable mAPP SDK Channel and the push notifications, the team setting up the firebase account for the brand must raise a ticket with the gateways team with details requested by them.