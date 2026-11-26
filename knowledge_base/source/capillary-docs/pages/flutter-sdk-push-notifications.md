---
updatedAt: 2026-11-12T06:11:18.000Z
agentTools:
  projectIndex: https://docs.capillarytech.com/llms.txt
---

# Configure Push Notifications

# Configuring push notifications

1. Create a folder named `icons` inside `capillary/` if it doesn't already exist, and add an image named `hydra_notification_small_icon` (png, jpg, or jpeg — png recommended). This is the small icon shown in the notification drawer.

2. Set `hydra_notification_color` in `capillary/hydra-config.json` (see [hydra-config.json](https://docs.capillarytech.com/docs/flutter-sdk-install#hydra-configjson)). This is used on Android.

3. **For iOS:**

   * Make sure Push Notification capability is added to your app identifier on [developer.apple.com](https://developer.apple.com).
   * In Xcode project settings for your app target, add these capabilities under Signing & Capabilities: Push Notification, and Background Modes with Background fetch and Remote notifications enabled.
   * **Rich notifications are mandatory.** Set up a Notification Service Extension and wire it to Hydra:

     * Add a Notification Service Extension: in Xcode, go to your project settings and add a new target for this. Xcode will append the extension's product name to your main target's bundle id to derive its bundle id — add that new bundle id on [developer.apple.com](https://developer.apple.com).

     * Add **App Groups** capability in Signing & Capabilities for both your main target and this extension target, using the same group in both, in the form `group.<runner_target_bundle_id>.hydra`. Create this App Group on developer.apple.com for both identifiers.

     * If Swift Package Manager is enabled for your project, skip this step. Otherwise, in `ios/Podfile`, add `extension_pods` inside your new extension target (e.g. `HydraRichNotification`):

       ```ruby
       target "HydraRichNotification" do
         use_frameworks!
         extension_pods
       end
       ```

       Then run `pod install` again as in step 3 of [Setting up iOS](https://docs.capillarytech.com/docs/flutter-sdk-install#setting-up-ios).

     * Replace the entire contents of `NotificationService.swift` with:

       ```swift
       import UserNotifications
       import HydraPushNotificationServiceExtension

       class NotificationService: UNNotificationServiceExtension {
           let service: HydraRemoteNotificationService = .init()

           override func didReceive(_ request: UNNotificationRequest, withContentHandler contentHandler: @escaping (UNNotificationContent) -> Void) {
               service.didReceive(request, withContentHandler: contentHandler)
           }

           override func serviceExtensionTimeWillExpire() {
               service.serviceExtensionTimeWillExpire()
           }
       }
       ```

4. **For Android:** the Firebase setup in [Setting up Android](https://docs.capillarytech.com/docs/flutter-sdk-install#setting-up-android) (steps 1–2) is all that's needed.

5. **Flutter – push APIs and events:**
   * Ask for permission using [HydraPushNotification.requestPermission()](https://docs.capillarytech.com/docs/flutter-sdk-api-reference#2-request-permission-for-push-notifications). Call it before you can receive push.
   * Get the FCM token on demand with [HydraPushNotification.getFCMToken()](https://docs.capillarytech.com/docs/flutter-sdk-api-reference#1-get-fcm-token), or receive it via `onTokenAvailable` on your [HydraNativeEventHandler](https://docs.capillarytech.com/docs/flutter-sdk-api-reference#hydranativeeventhandler-class).
   * **Update push preferences:** call [HydraCore.updatePushPreferences](https://docs.capillarytech.com/docs/flutter-sdk-api-reference#3-update-user-push-preferences) with the signed-in `customerId` and a [HydraPushPreferences](https://docs.capillarytech.com/docs/flutter-sdk-api-reference#hydrapushpreferences) object to control whether the user receives promotional and transactional push notifications.
   * **Event callbacks** on your [HydraNativeEventHandler](https://docs.capillarytech.com/docs/flutter-sdk-api-reference#hydranativeeventhandler-class), registered with [HydraNativeEvents.addEventHandler](https://docs.capillarytech.com/docs/flutter-sdk-api-reference#hydranativeevent-class-apis):
     * **Hydra notification:** `onHydraNotificationReceived`, `onHydraNotificationShown`, `onHydraNotificationClicked` (a push or its CTA tapped, a notification tapped in the built-in notification center, or a CTA tapped on an in-app message) and `onHydraNotificationDismissed`.
     * **Non-Hydra notification:** `onNonHydraNotificationReceived` and `onNonHydraNotificationClicked`.
   * **Unsubscribe:** use [removeEventHandler](https://docs.capillarytech.com/docs/flutter-sdk-api-reference#hydranativeevent-class-apis) or [removeAllEventHandlers](https://docs.capillarytech.com/docs/flutter-sdk-api-reference#hydranativeevent-class-apis).
   * **Android – your app gets FCM tokens itself** (e.g. with `firebase_messaging`): pass each new token to Hydra with [HydraPushNotification.passFCMToken](https://docs.capillarytech.com/docs/flutter-sdk-api-reference#3-pass-fcm-token-android-only).