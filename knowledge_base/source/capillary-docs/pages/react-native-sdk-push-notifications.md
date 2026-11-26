---
updatedAt: 2026-11-12T06:08:47.000Z
agentTools:
  projectIndex: https://docs.capillarytech.com/llms.txt
---

# Configure Push Notifications

Push notifications are turned on by default. Make sure `enable_push_notification` is set to `true` (or omitted, because `true` is the default) in `PROJECT_ROOT/capillary/hydra-config.json`. For details, see [The hydra-config.json file](https://docs.capillarytech.com/docs/react-native-sdk-install#the-hydra-configjson-file). If you set it to `false`, the SDK skips Firebase registration entirely and none of the following steps are required.

# Configuring push notifications for Android

Follow these steps to configure push notifications for your Android project:

1. Add the following class path in `dependencies classpath` in the `android/build.gradle` file:
   ```
   'com.google.gms:google-services:4.4.2'
   ```
2. In `android/app/build.gradle`, apply the following plugin at the top of the file, where other plugins are initialized:
   ```gradle
   apply plugin: "com.google.gms.google-services"
   ```
3. Set `hydra_notification_color` to a color of your choice in `PROJECT_ROOT/capillary/hydra-config.json`. Android uses this color as the notification tint.
4. Add an image named `hydra_notification_small_icon` in `PROJECT_ROOT/capillary/icons`. Create these folders in your project root folder if they don't exist. The image can be PNG, JPG, or JPEG, but PNG is recommended. Android requires this image as the small notification icon.

# Configuring push notifications for iOS

Follow these steps to configure push notifications for your iOS project:

1. Ensure you have added the Push Notification capability for your app identifier on the [Apple Developer website](https://developer.apple.com/).
2. In your Xcode project settings for your application target, add the following capabilities under Signing & Capabilities:
   * Push Notification
   * Background Modes, with Background fetch and Remote notifications enabled.
3. Set up rich notifications. This step is mandatory for push notifications to function correctly on iOS. For detailed steps, see Configuring rich notifications for iOS.

## Configuring rich notifications for iOS

Follow these steps to configure rich push notifications for your iOS project.

1. Go to your project settings in Xcode and add a new target and select Notification Service Extension from the available templates. This adds a Notification Service Extension to your project.

   <Image align="center" className="border" border={true} width="80% " src="https://files.readme.io/425ac7aca18db38c8f1fc3e5739a15d70f8b50b44cc27c7b1954ab71fbf49fa5-image.png" />
2. When configuring the new target, Xcode will append the `ProductName` of your main target to its bundle identifier to create the bundle identifier for this extension. You must add this extension bundle identifier on the [Apple Developer website](https://developer.apple.com).

<Image align="center" className="border" border={true} width="80% " src="https://files.readme.io/4e6b398bdee413ff26531398ea311e4577c6edceb10649a457b6c64286fde377-image.png" />

3. Select the language as `Objective-C`if your `AppDelegate` is Objective-C and `Swift` if your AppDelegate is Swift.

   <Image align="center" className="border" border={true} width="80% " src="https://files.readme.io/02b47dde83d3360d459dac5d69b941cdda4ef07a490b2bf87ba14d5f7ae20c25-image.png" />
4. Add the `App Groups` capability in `Signing & Capabilities` for both your main application target and the new extension target. You will need to create and add a group in both targets. The group name must follow the format `group.<runner_target_bundle_id>.hydra`, where `<runner_target_bundle_id>` is replaced with the actual bundle identifier of your main application target. This App group also needs to be added on the [Apple Developer website](https://developer.apple.com) for both app identifiers.
5. In your ios/Podfile, add `extension_pods` within the target block for your new extension target, as shown here:

   ```ruby
   target 'HydraRichNotification' do
    extension_pods
   end
   ```

   If you set `$RNHydraUseSPM = true` in your Podfile, `extension_pods` does nothing. CocoaPods can't reach app extension targets with `spm_dependency`, which only wires Swift Package Manager products onto pod targets, not onto targets in the Xcode project of your app. Add the SDK to the extension target directly in Xcode instead:

   1. Select your app project (not Pods), go to **File** > **Add Package Dependencies**, and enter `https://github.com/Capillary/hydra-ios-sdk-spm.git`. Pin the exact version from `HYDRA_SPM_REQUIREMENT` in `node_modules/@capillarytech/react-native-hydra-lib/scripts/HydraPods.rb`, so the extension uses the same SDK version as your app.
   2. Select the extension target, go to **General** > **Frameworks, Libraries, and Embedded Content**, and add the `HydraPushNotificationServiceExtension` product.
6. Install the pods again by opening your terminal, changing the current working directory to your project's ios folder, and running the command:
   ```shell
   pod install
   ```
7. Replace the entire code `NotificationService.mm`(Objective-C) or `NotificationService.swift` (Swift) with the following code:
   ```objectivec
   #import "NotificationService.h"
   #import "HydraPushNotificationServiceExtension/HydraPushNotificationServiceExtension.h"
   @implementation NotificationService
   HydraRemoteNotificationService* service;
   -(id)init{
     self = [super init];
     service = [[HydraRemoteNotificationService alloc] init];
     return  self;
     
   }
   - (void)didReceiveNotificationRequest:(UNNotificationRequest *)request withContentHandler:(void (^)(UNNotificationContent * _Nonnull))contentHandler {
     [service didReceiveNotificationRequest:request withContentHandler:contentHandler];
   }
   - (void)serviceExtensionTimeWillExpire {
     [service serviceExtensionTimeWillExpire];
   }
   @end
   ```
   ```swift
   import UserNotifications
   import HydraPushNotificationServiceExtension
   class NotificationService: UNNotificationServiceExtension {
       let service:HydraRemoteNotificationService = .init()
       
       override func didReceive(_ request: UNNotificationRequest, withContentHandler contentHandler: @escaping (UNNotificationContent) -> Void) {
           service.didReceive(request, withContentHandler: contentHandler)
       }
       
       override func serviceExtensionTimeWillExpire() {
           service.serviceExtensionTimeWillExpire()
       }
   }
   ```

# Using the push APIs and events in React Native

Use the following APIs and events in your React Native code:

* Ask for permission using [HydraPushNotification.requestPermission()](https://docs.capillarytech.com/docs/react-native-sdk-api-reference#request-permission-for-push-notifications).
* Get the FCM token in one of two ways:
  * Register [addTokenAvailableListener](https://docs.capillarytech.com/docs/react-native-sdk-api-reference#get-callback-when-a-new-fcm-token-is-available) on `HydraNativeEventEmitter` to receive the token when it becomes available.
  * Call [HydraPushNotification.getFCMToken()](https://docs.capillarytech.com/docs/react-native-sdk-api-reference#get-fcm-token) to fetch the token on demand.
* Update push preferences. Call [HydraCore.updatePushPreferences](https://docs.capillarytech.com/docs/react-native-sdk-api-reference#update-user-push-preferences) with the signed-in `customerId` and a [HydraPushPreferences](https://docs.capillarytech.com/docs/react-native-sdk-api-reference#hydrapushpreferences) object to control whether the user receives promotional and transactional push notifications.
* Register event listeners. Use `HydraNativeEventEmitter` (call `getInstance()` first) to register for push-related events:
  * **Non-Hydra notification:** [addNonHydraNotificationReceivedListener](https://docs.capillarytech.com/docs/react-native-sdk-api-reference#get-callback-when-non-hydra-notification-is-received) fires when a non-Hydra push is received. [addNonHydraNotificationClickedListener](https://docs.capillarytech.com/docs/react-native-sdk-api-reference#get-callback-when-non-hydra-notification-is-clicked) fires when a non-Hydra push is tapped.
  * **Hydra notification:**
    * [addHydraNotificationReceivedListener](https://docs.capillarytech.com/docs/react-native-sdk-api-reference#get-callback-when-a-hydra-notification-is-received) fires when a Hydra push is received. For example, use it to refresh your notification list.
    * [addHydraNotificationShownListener](https://docs.capillarytech.com/docs/react-native-sdk-api-reference#callback-when-hydra-notification-is-shown) fires when a Hydra notification is shown in the system notification tray.
    * [addHydraNotificationClickedListener](https://docs.capillarytech.com/docs/react-native-sdk-api-reference#get-a-callback-for-notification-click) fires when a Hydra push or its CTA is tapped, when a notification is tapped in the built-in notification center, or when a CTA is tapped on an SDK-rendered in-app message. For example, use it to redirect to a deep link or an external link.
    * [addHydraNotificationDismissedListener](https://docs.capillarytech.com/docs/react-native-sdk-api-reference#callback-when-user-dismisses-a-hydra-notification) fires when the user dismisses a Hydra notification in the system notification tray.
* Unsubscribe. Use [removeListener](https://docs.capillarytech.com/docs/react-native-sdk-api-reference#remove-an-added-listener) to unregister any subscription, such as the FCM token listener or the event listeners.
* **Android, custom actions:** Register [addHandleCustomActionListener](https://docs.capillarytech.com/docs/react-native-sdk-api-reference#get-callback-for-a-notification-custom-action-android-only) to receive the payload when the user taps a notification CTA with a custom action.
* **Android, your own `FirebaseMessagingService`:** If you set `enable_hydra_sdk_firebase_registration` to `false`, pass each new FCM token to Hydra with [HydraPushNotification.passFCMToken(token)](https://docs.capillarytech.com/docs/react-native-sdk-api-reference#pass-fcm-token-android-only).
* **Opening external links:** If you also use Gamification, open external links with [HydraPushNotification.openExternalUrl(url)](https://docs.capillarytech.com/docs/react-native-sdk-api-reference#open-external-url) instead of the React Native `Linking.openURL(url)`. For details, see the warning in [Configure Gamification](https://docs.capillarytech.com/docs/gamification-react-native).