---
updatedAt: 2026-11-12T06:08:47.000Z
agentTools:
  projectIndex: https://docs.capillarytech.com/llms.txt
---

# React Native Setup Overview

1. For a multi-Hydra account setup, you must use one of the following methods to initialise the Hydra SDK from the React Native side when switching Hydra accounts for a given user. You can set Hydra account details in two ways:
   * When fetching Hydra account values yourself, use [setHydraAccountConfig](https://docs.capillarytech.com/docs/react-native-sdk-api-reference#configure-hydra-account-settings).
   * When you are using Firebase Remote Config, use [setFirebaseRemoteConfigKeys](https://docs.capillarytech.com/docs/react-native-sdk-api-reference#configure-firebase-remote-configuration-keys).\
     If you have a single-Hydra account setup, no action is required.\
     Call one of these methods **before** you call `Hydra.identify`. For details, see [Multi-Hydra account setup](https://docs.capillarytech.com/docs/react-native-sdk-advanced-setup#multi-hydra-account-setup).

2. Use the [Hydra](https://docs.capillarytech.com/docs/react-native-sdk-api-reference#hydra-class-apis) class to register or identify the user. Call [Hydra.identify(userDetails, customAttributes)](https://docs.capillarytech.com/docs/react-native-sdk-api-reference#identify). The customerId is required and must match the configuration on the Capillary CRM dashboard. For the anonymous visitor flow, see [Anonymous/Visitor Flow](https://docs.capillarytech.com/docs/react-native-sdk-anonymous-visitor-flow).

3. `HydraCore.signUp`, `HydraCore.signIn`, `HydraCore.signOut` and `HydraCore.reportUserEvent` are deprecated. Use [Hydra.identify](https://docs.capillarytech.com/docs/react-native-sdk-api-reference#identify), [Hydra.reset](https://docs.capillarytech.com/docs/react-native-sdk-api-reference#reset) and [Hydra.track](https://docs.capillarytech.com/docs/react-native-sdk-api-reference#track) instead.

4. The [HydraPushNotification](https://docs.capillarytech.com/docs/react-native-sdk-api-reference#hydrapushnotification-class-apis) class provides static functions for push notifications: [requestPermission](https://docs.capillarytech.com/docs/react-native-sdk-api-reference#request-permission-for-push-notifications) and [getFCMToken](https://docs.capillarytech.com/docs/react-native-sdk-api-reference#get-fcm-token). To receive push notifications, you can ask for permission using [requestPermission](https://docs.capillarytech.com/docs/react-native-sdk-api-reference#request-permission-for-push-notifications).

5. Use [getFCMToken](https://docs.capillarytech.com/docs/react-native-sdk-api-reference#get-fcm-token) to get the FCM token. You can also add the listener using [addTokenAvailableListener](https://docs.capillarytech.com/docs/react-native-sdk-api-reference#get-callback-when-a-new-fcm-token-is-available) API in HydraNativeEventEmitter to get it when it is available.

6. The HydraCore class includes additional functions:
   1. Use [updateUser](https://docs.capillarytech.com/docs/react-native-sdk-api-reference#update-user) to update the user details you set with `Hydra.identify`.
   2. Use [updateGeoConfig](https://docs.capillarytech.com/docs/react-native-sdk-api-reference#update-geo-config) to update users' geo configuration, such as city, country and countryCode.
   3. Use [updatePushPreferences](https://docs.capillarytech.com/docs/react-native-sdk-api-reference#update-user-push-preferences) to update push notification preferences and enable or disable promotional and transactional push notifications.

7. The Hydra class includes additional functions:
   1. Use [Hydra.reset(customerId)](https://docs.capillarytech.com/docs/react-native-sdk-api-reference#reset) to reset or sign out the current user.
   2. Use [Hydra.track(eventName, attributes)](https://docs.capillarytech.com/docs/react-native-sdk-api-reference#track) to report custom user actions, such as a product viewed, an item added to the cart, a purchase, or a screen or section viewed, with optional attributes. Capillary uses this data for analytics and segmentation.

8. Use the HydraInbox class to manage them with functions like [getInboxMessages](https://docs.capillarytech.com/docs/react-native-sdk-api-reference#get-list-of-hydra-notifications), [getUnreadMessagesCount](https://docs.capillarytech.com/docs/react-native-sdk-api-reference#get-unread-hydra-notifications-count), [markInboxMessageAsRead](https://docs.capillarytech.com/docs/react-native-sdk-api-reference#mark-a-hydra-notification-as-read), [deleteInboxMessage](https://docs.capillarytech.com/docs/react-native-sdk-api-reference#delete-a-hydra-notification), and [deleteAllInboxMessages](https://docs.capillarytech.com/docs/react-native-sdk-api-reference#delete-all-hydra-notifications). The Hydra SDK has a database of the Hydra notifications and doesn't save any non-Hydra notifications. These APIs allow you to implement your UI for Notification Centre.

9. Use the [HydraInboxUI](https://docs.capillarytech.com/docs/react-native-sdk-api-reference#/managing-the-in-app-notification-centre) class functions: [showNotificationCenter](https://docs.capillarytech.com/docs/react-native-sdk-api-reference#/show-in-built-notification-centre) and [hideNotificationCenterIfShowing](https://docs.capillarytech.com/docs/react-native-sdk-api-reference#/hide-in-built-notification-centre-if-showing) to use the built-in notification centre from the Hydra plugin.

10. The [HydraNativeEventEmitter](https://docs.capillarytech.com/docs/react-native-sdk-api-reference#/sdk-event-tracking) class allows you to register listeners for different events from the SDK.

11. Use [getInstance](https://docs.capillarytech.com/docs/react-native-sdk-api-reference#/get-singleton-instance) API to get the singleton instance.

12. Use [addHydraNotificationReceivedListener](https://docs.capillarytech.com/docs/react-native-sdk-api-reference#/get-callback-when-a-hydra-notification-is-received) when a Hydra notification is received.

13. Use [addHydraNotificationClickedListener](https://docs.capillarytech.com/docs/react-native-sdk-api-reference#get-a-callback-for-notification-click) to receive a callback when a Hydra push notification or its CTA is tapped, when a notification is tapped in the built-in notification centre, or when a CTA is tapped on an SDK-rendered in-app message.

14. Use [addHydraNotificationShownListener](https://docs.capillarytech.com/docs/react-native-sdk-api-reference#callback-when-hydra-notification-is-shown) to receive a callback when a Hydra notification is shown in the system notification tray.

15. Use [addHydraNotificationDismissedListener](https://docs.capillarytech.com/docs/react-native-sdk-api-reference#callback-when-user-dismisses-a-hydra-notification) when the user dismisses a Hydra notification in the system notification tray.

16. Use [addNotificationCenterDismissedListener](https://docs.capillarytech.com/docs/react-native-sdk-api-reference#callback-when-in-built-notification-center-is-dismissed) to get the callback when the Hydra in-built notification centre is dismissed by the user.

17. Use [addInboxUpdatedListener](https://docs.capillarytech.com/docs/react-native-sdk-api-reference#callback-when-the-inbox-is-updated) when the Hydra notification database is updated.

18. Use [addNonHydraNotificationReceivedListener](https://docs.capillarytech.com/docs/react-native-sdk-api-reference#get-callback-when-non-hydra-notification-is-received) and [addNonHydraNotificationClickedListener](https://docs.capillarytech.com/docs/react-native-sdk-api-reference#get-callback-when-non-hydra-notification-is-clicked) when a non-Hydra push notification is received or tapped.

19. Use [addHandleCustomActionListener](https://docs.capillarytech.com/docs/react-native-sdk-api-reference#get-callback-for-a-notification-custom-action-android-only) on Android to receive the payload when the user taps a notification CTA with a custom action.

20. Use [removeListener](https://docs.capillarytech.com/docs/react-native-sdk-api-reference#remove-an-added-listener) API to remove a listener.

21. On Android, if you set `enable_hydra_sdk_firebase_registration` to `false`, pass each new FCM token to Hydra with [HydraPushNotification.passFCMToken(token)](https://docs.capillarytech.com/docs/react-native-sdk-api-reference#pass-fcm-token-android-only). If you also use Gamification, open external links with [HydraPushNotification.openExternalUrl(url)](https://docs.capillarytech.com/docs/react-native-sdk-api-reference#open-external-url) instead of `Linking.openURL(url)`.

22. For Gamification, the Hydra class includes functions to report screens, set the Capillary token, suppress campaigns, and set the theme mode. For details, see [Configure Gamification](https://docs.capillarytech.com/docs/gamification-react-native).

23. Configure log levels. Console log level is used for logging in the Xcode console and LogCat. Remote log level is used to save the logs in the backend. Both log levels use integers from 0 to 5, where 0 turns off the logs and 5 is verbose. For details, see [HydraLogLevel](https://docs.capillarytech.com/docs/react-native-sdk-api-reference#hydraloglevel).

* Set the console log level in `hydra-config.json` using `console_log_level`.
* The remote log level comes from `hydra_remote_log_level` in Firebase Remote Config, or from the remote-config object you pass to the initialiser.