---
updatedAt: 2026-11-12T06:11:18.000Z
agentTools:
  projectIndex: https://docs.capillarytech.com/llms.txt
---

# Configure Notification Center

An In-App Notification Centre is a centralised hub within the mobile app's dashboard, allowing you to stay updated on important events, actions, and announcements without leaving the app.

<Image align="center" border={false} caption="Notification centre on Android" src="https://files.readme.io/2b86f5234d7677edf82be916aeef2e4ddd01c2734a0fc93349ca063dc2acf1ae-image.png" width="60% " />

<Image align="center" border={false} caption="Notification centre on iOS" src="https://files.readme.io/0db981e45dc7eb95b7a16b91570b1d0951177fa090e23a6c1e4d3408d62e9a41-image.png" width="60% " />

<br />

# Configuring the Inbox API

Use the Inbox API to build your app's own notification list. The SDK stores received notifications in a local database; you use `HydraInbox` to read, mark as read, and delete them.

1. Set `enable_inbox_api` to `true` in `hydra-config.json` (see [hydra-config.json](https://docs.capillarytech.com/docs/flutter-sdk-install#hydra-configjson)). On iOS, the Notification Service Extension and App Group from the rich notifications part of step 3 in [Configure Push Notifications](https://docs.capillarytech.com/docs/flutter-sdk-push-notifications) must also be set up.
2. **Flutter – HydraInbox APIs:** use [HydraInbox](https://docs.capillarytech.com/docs/flutter-sdk-api-reference#hydrainbox-class-apis) for `getInboxMessages`, `getUnreadInboxMessagesCount`, `markInboxMessageAsRead`, `deleteInboxMessage`, and `deleteAllInboxMessages`.
3. There's no dedicated "inbox updated" event — refresh your list from `onHydraNotificationReceived` or `onNotificationCenterDismissed` on your [HydraNativeEventHandler](https://docs.capillarytech.com/docs/flutter-sdk-api-reference#hydranativeeventhandler-class), or by calling `HydraInbox` on demand.

# Configuring the Inbox UI

If you want to use the notification center provided by the Hydra SDK, enable this.

1. Enable Inbox API — see [Inbox API](#configuring-the-inbox-api).
2. Set `enable_inbox_ui` to `true` in `hydra-config.json`.
3. Add an image named `hydra_inbox_ui_placeholder` in `capillary/icons`. Can be png, jpg, or jpeg.
4. **Flutter – HydraInboxUI APIs:** use [HydraInboxUI.showNotificationCenter()](https://docs.capillarytech.com/docs/flutter-sdk-api-reference#hydrainboxui-class-apis) to show the built-in notification center and [HydraInboxUI.hideNotificationCenterIfShowing()](https://docs.capillarytech.com/docs/flutter-sdk-api-reference#hydrainboxui-class-apis) to hide it. Override `onNotificationCenterDismissed` on your [HydraNativeEventHandler](https://docs.capillarytech.com/docs/flutter-sdk-api-reference#hydranativeeventhandler-class) for dismiss callbacks.