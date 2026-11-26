---
updatedAt: 2026-11-12T06:08:47.000Z
agentTools:
  projectIndex: https://docs.capillarytech.com/llms.txt
---

# Configure Notification Center

This document outlines the steps to integrate Notification Center into your React Native project using the Hydra SDK. Follow the instructions below to enable and configure Notification Center for your application.

An In-App Notification Centre is a centralised hub within the dashboard, allowing you to stay updated on important events, actions, and announcements without leaving the app.

<Image align="center" border={false} caption="Notification centre on Android" src="https://files.readme.io/2b86f5234d7677edf82be916aeef2e4ddd01c2734a0fc93349ca063dc2acf1ae-image.png" width="60% " />

<Image align="center" border={false} caption="Notification centre on iOS" src="https://files.readme.io/0db981e45dc7eb95b7a16b91570b1d0951177fa090e23a6c1e4d3408d62e9a41-image.png" width="60% " />

# Configuring the Inbox API

Use the Inbox API to implement your own notification list in your app, for example a screen that shows notifications fetched from the SDK. The SDK stores notifications locally. You use the `HydraInbox` APIs to read, mark as read, and delete them.

1. Set `enable_inbox_api` to `true` in `PROJECT_ROOT/capillary/hydra-config.json`.

   > 📘 Note
   >
   > On iOS, you must also set up the Notification Service Extension and the App Group from [Configuring rich notifications for iOS](https://docs.capillarytech.com/docs/react-native-sdk-push-notifications#configuring-rich-notifications-for-ios) for the Inbox API to work.

2. In React Native, use [HydraInbox](https://docs.capillarytech.com/docs/react-native-sdk-api-reference#managing-the-notification-inbox) to work with the SDK notification database:
   * [getInboxMessages](https://docs.capillarytech.com/docs/react-native-sdk-api-reference#get-list-of-hydra-notifications): Fetch all inbox notifications.
   * [getUnreadMessagesCount](https://docs.capillarytech.com/docs/react-native-sdk-api-reference#get-unread-hydra-notifications-count): Get the unread count.
   * [markInboxMessageAsRead](https://docs.capillarytech.com/docs/react-native-sdk-api-reference#mark-a-hydra-notification-as-read): Mark one notification as read.
   * [deleteInboxMessage](https://docs.capillarytech.com/docs/react-native-sdk-api-reference#delete-a-hydra-notification): Delete one notification.
   * [deleteAllInboxMessages](https://docs.capillarytech.com/docs/react-native-sdk-api-reference#delete-all-hydra-notifications): Clear the inbox.

3. In React Native, register [addInboxUpdatedListener](https://docs.capillarytech.com/docs/react-native-sdk-api-reference#callback-when-the-inbox-is-updated) on `HydraNativeEventEmitter` to refresh the list when you use the Inbox APIs to show notifications in your UI. Alternatively, use [addHydraNotificationReceivedListener](https://docs.capillarytech.com/docs/react-native-sdk-api-reference#get-callback-when-a-hydra-notification-is-received) to refresh when a new Hydra push arrives.

# Configuring the Inbox UI

This allows you to use the native notification center UI included in Hydra SDK.

To turn on the Inbox UI, follow these steps:

1. Turn on the Inbox API by following step 1 under [Configuring the Inbox API](#configuring-the-inbox-api).
2. Set `enable_inbox_ui` to `true` in `PROJECT_ROOT/capillary/hydra-config.json`.
3. Add an image named `hydra_inbox_ui_placeholder` in `PROJECT_ROOT/capillary/icons`. Create these folders in your project root folder if they don't exist. The image can be PNG, JPG, or JPEG, but PNG is recommended. The SDK uses this image as a placeholder for notifications in the notification center.
4. In React Native, use [HydraInboxUI.showNotificationCenter()](https://docs.capillarytech.com/docs/react-native-sdk-api-reference#managing-the-in-app-notification-centre) to show the built-in notification center and `HydraInboxUI.hideNotificationCenterIfShowing()` to hide it. Register [addNotificationCenterDismissedListener](https://docs.capillarytech.com/docs/react-native-sdk-api-reference#callback-when-in-built-notification-center-is-dismissed) on `HydraNativeEventEmitter` for dismiss callbacks.

On iOS, `use_default_inbox_ui_config` controls the layout. It is `true` by default, which uses the SDK default notification center layout. To supply a custom `INBOX_UI_CONFIG`, set it to `false`. Inbox UI on Android uses the default configuration.