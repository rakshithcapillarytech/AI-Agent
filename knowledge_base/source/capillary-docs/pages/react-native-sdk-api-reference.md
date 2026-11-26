---
updatedAt: 2026-11-12T06:08:47.000Z
agentTools:
  projectIndex: https://docs.capillarytech.com/llms.txt
---

# API Reference for Event Tracking, Notifications, and User Lifecycle

# User Management, Account Configuration, and Event Tracking

## Check if Hydra SDK is initialized or not (on-demand)

```typescript
static isSdkInitialized(): Promise<boolean>;
```

**Returns**: `Promise<boolean>` which resolves to `true` if the Hydra SDK is initialized, `false` otherwise

**Usage**:

```typescript
HydraCore.isSdkInitialized()
  .then((isInitialized) => {
    console.log('Hydra Instance Status: ', isInitialized);
    if (isInitialized) {
      // perform any action based on the isInitialized status
    } else {
      // not yet initialized: register for the one-time result via addHydraSdkInitializationResultListener
      const hydraSdkInitializationResultSubscription =
        HydraNativeEventEmitter.getInstance().addHydraSdkInitializationResultListener(
          (result, message) => {}
        );
    }
  })
  .catch((error) => {
    console.error('Error checking Hydra initialization status:', error);
  });
```

> 📘 Note
>
> You can also register a one-time callback listener to retrieve the initialization status of Hydra, which is particularly helpful if you only need the status for initial API calls.

***

## Update User

This API can be used to update a user's profile and report when a user has updated their profile.

```typescript
static updateUser(
  userDetails: HydraUserDetails,
  customAttributes: Record<string, any> | null = null,
  subscriptions: Object[] | null = null
): Promise<boolean>;
```

### Parameters

| Parameter        | Type                                                                                                    | Required/Optional | Description                                                                                                            |
| ---------------- | ------------------------------------------------------------------------------------------------------- | ----------------- | ---------------------------------------------------------------------------------------------------------------------- |
| userDetails      | [HydraUserDetails](https://docs.capillarytech.com/docs/react-native-sdk-api-reference#hydrauserdetails) | required          | [Read more about this class here](https://docs.capillarytech.com/docs/react-native-sdk-api-reference#hydrauserdetails) |
| customAttributes | Record\<string, any>                                                                                    | optional          | You can pass custom attributes that can be used for analytics                                                          |
| subscriptions    | Object\[]                                                                                               | optional          | List of Subscriptions which include channel, accountId, priority, type and sourcename                                  |

**Returns**: `Promise<boolean>` indicating if update was successfully requested

**Usage**:

```typescript
HydraCore.updateUser(userDetails, customAttributesObj, subscriptionsObj)
  .then((res: any) => {
    console.log('HydraCore.updateUser', res);
  })
  .catch((err: any) => {
    console.log('HydraCore.updateUser', err);
  });
```

***

## Update Geo Config

This API can be used to update a user's geo config and report when a user has updated their geo config.

```typescript
static updateGeoConfig(geoConfig: HydraGeoConfig): Promise<boolean>;
```

### Parameters

| Parameter | Type                                                                                                | Required/Optional | Description                                                                                                          |
| --------- | --------------------------------------------------------------------------------------------------- | ----------------- | -------------------------------------------------------------------------------------------------------------------- |
| geoConfig | [HydraGeoConfig](https://docs.capillarytech.com/docs/react-native-sdk-api-reference#hydrageoconfig) | required          | [Read more about this class here](https://docs.capillarytech.com/docs/react-native-sdk-api-reference#hydrageoconfig) |

**Returns**: `Promise<boolean>` indicating if geo config update was successful

**Usage**:

```typescript
HydraCore.updateGeoConfig(geoConfig).then((updateRequested) => {
  console.log('Geo config update requested = ', updateRequested);
}).catch((err: any) => {
  console.log('HydraCore.updateGeoConfig', err);
});
```

***

## Update User Push Preferences

This API can be used to update a user's push preference and report when a user has updated their push preference.

```typescript
static updatePushPreferences(
  customerId: string,
  preferences: HydraPushPreferences
): Promise<boolean>;
```

### Parameters

| Parameter   | Type                                                                                                            | Required/Optional | Description                                                                                                                |
| ----------- | --------------------------------------------------------------------------------------------------------------- | ----------------- | -------------------------------------------------------------------------------------------------------------------------- |
| customerId  | string                                                                                                          | required          | Customer id of the user to update push preferences                                                                         |
| preferences | [HydraPushPreferences](https://docs.capillarytech.com/docs/react-native-sdk-api-reference#hydrapushpreferences) | required          | [Read more about this class here](https://docs.capillarytech.com/docs/react-native-sdk-api-reference#hydrapushpreferences) |

**Returns**: `Promise<boolean>` indicating if preferences update was successful

**Usage**:

```typescript
HydraCore.updatePushPreferences(customerId, pushPreferences)
  .then((res: any) => {
    console.log('HydraCore.updatePushPreferences success', res);
  })
  .catch((err: any) => {
    console.log('HydraCore.updatePushPreferences error', err);
  });
```

***

## Configure Hydra account settings

This API can be used to configure the Hydra account settings for the user.

```typescript
static setHydraAccountConfig(
   hydraAccountConfig: HydraAccountConfig
 ): Promise<boolean>;
```

### Parameters

| Parameter          | Type                                                                                                        | Required/Optional | Description                                                                                                                                                                                                                                                                     |
| ------------------ | ----------------------------------------------------------------------------------------------------------- | ----------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| hydraAccountConfig | [HydraAccountConfig](https://docs.capillarytech.com/docs/react-native-sdk-api-reference#hydraaccountconfig) | required          | Read more about this class [here](https://docs.capillarytech.com/docs/react-native-sdk-api-reference#hydraaccountconfig), including the optional `orgId` (Anonymous/Visitor Flow) and `gamificationKey`, `gamificationRegion`, and `gamificationBaseUrl` (Gamification) fields. |

**Returns**: `Promise<boolean>` which resolves to `true` once the SDK has switched to this account. Use it in a [multi-Hydra account setup](https://docs.capillarytech.com/docs/react-native-sdk-advanced-setup#multi-hydra-account-setup), and call it after the SDK has initialized and before `Hydra.identify`.

**Usage**:

```typescript
HydraCore.setHydraAccountConfig(hydraAccountConfig)
  .then((res: any) => {
    console.log('HydraCore.setHydraAccountConfig success', res);
  })
  .catch((err: any) => {
    console.log('HydraCore.setHydraAccountConfig error', err);
  });
```

***

## Configure Firebase remote configuration keys

This API can be used to configure the Firebase Remote configuration keys.

```typescript
static setFirebaseRemoteConfigKeys(
   remoteConfigKeys: HydraFirebaseRemoteConfigKeys
 ): Promise<boolean>;
```

### Parameters

| Parameter        | Type                                                                                                                              | Required/Optional | Description                                                                                                                                                                                                                                                                                                           |
| ---------------- | --------------------------------------------------------------------------------------------------------------------------------- | ----------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| remoteConfigKeys | [HydraFirebaseRemoteConfigKeys](https://docs.capillarytech.com/docs/react-native-sdk-api-reference#hydrafirebaseremoteconfigkeys) | required          | Read more about this class [here](https://docs.capillarytech.com/docs/react-native-sdk-api-reference#hydrafirebaseremoteconfigkeys), including the optional `keyForOrgId` (Anonymous/Visitor Flow) and `keyForGamificationKey`, `keyForGamificationRegion`, and `keyForGamificationBaseUrl` (Gamification) key names. |

**Returns**: `Promise<boolean>` which resolves to `true` once the SDK has switched to the account these keys point to. Use it in a [multi-Hydra account setup](https://docs.capillarytech.com/docs/react-native-sdk-advanced-setup#multi-hydra-account-setup), and call it after the SDK has initialized and before `Hydra.identify`.

**Usage**:

```typescript
HydraCore.setFirebaseRemoteConfigKeys(remoteConfigKeys)
  .then((res: any) => {
    console.log('HydraCore.setFirebaseRemoteConfigKeys success', res);
  })
  .catch((err: any) => {
    console.log('HydraCore.setFirebaseRemoteConfigKeys error', err);
  });
```

***

## Deprecated HydraCore APIs

These APIs are still exported for backward compatibility but are deprecated. Don't use them in new code. They might be removed in a future major release.

| Deprecated                                         | Use instead                                                  |
| -------------------------------------------------- | ------------------------------------------------------------ |
| `HydraCore.signUp(userDetails, customAttributes)`  | [`Hydra.identify(userDetails, customAttributes)`](#identify) |
| `HydraCore.signIn(userDetails, customAttributes)`  | [`Hydra.identify(userDetails, customAttributes)`](#identify) |
| `HydraCore.signOut(customerId)`                    | [`Hydra.reset(customerId)`](#reset)                          |
| `HydraCore.reportUserEvent(eventName, attributes)` | [`Hydra.track(eventName, attributes)`](#track)               |

***

# Hydra class APIs

## Identify

```typescript
static identify(
  userDetails: HydraUserDetails,
  customAttributes: Record<string, any> | null = null
): Promise<boolean>;
```

### Parameters

| Parameter        | Type                                  | Required/Optional | Description                                                    |
| ---------------- | ------------------------------------- | ----------------- | -------------------------------------------------------------- |
| userDetails      | [HydraUserDetails](#hydrauserdetails) | required          | Identifies the current visitor as a known user.                |
| customAttributes | Record\<string, any>                  | optional          | You can pass custom attributes that can be used for analytics. |

**Returns**: `Promise<boolean>` indicating if identify was successfully requested

**Usage**:

```typescript
Hydra.identify(userDetails, customAttributesObj)
  .then((res) => console.log('Hydra.identify success', res))
  .catch((err) => console.log('Hydra.identify error', err));
```

***

## Track

```typescript
static track(
  eventName: string,
  attributes: Record<string, any> | null = null
): Promise<boolean>;
```

### Parameters

| Parameter  | Type                 | Required/Optional | Description                                                 |
| ---------- | -------------------- | ----------------- | ----------------------------------------------------------- |
| eventName  | string               | required          | Name of the event you want to report.                       |
| attributes | Record\<string, any> | optional          | List of key value pairs for additional data with the event. |

**Returns**: `Promise<boolean>` indicating if the event was successfully reported

**Usage**:

```typescript
Hydra.track('product_viewed', { productId: 'abc123' })
  .then((res) => console.log('Hydra.track success', res))
  .catch((err) => console.log('Hydra.track error', err));
```

***

## Reset

```typescript
static reset(customerId: string): Promise<boolean>;
```

### Parameters

| Parameter  | Type   | Required/Optional | Description                       |
| ---------- | ------ | ----------------- | --------------------------------- |
| customerId | string | required          | Customer id of the user to reset. |

**Returns**: `Promise<boolean>` indicating if reset was successfully requested

**Usage**:

```typescript
Hydra.reset(customerId)
  .then((res) => console.log('Hydra.reset success', res))
  .catch((err) => console.log('Hydra.reset error', err));
```

***

## Get Current User State

```typescript
static getCurrentUserState(): Promise<UserState | null>;
```

**Returns**: `Promise<UserState | null>` which resolves to the current [UserState](#userstate) enum value, or null

**Usage**:

```typescript
Hydra.getCurrentUserState().then((state) => {
  console.log('Current user state - ', state);
});
```

***

## Get Visitor Details

```typescript
static getVisitorDetails(): Promise<HydraVisitorInfo | null>;
```

**Returns**: `Promise<HydraVisitorInfo | null>` which resolves to a [HydraVisitorInfo](#hydravisitorinfo) object (`visitorId`), or null

**Usage**:

```typescript
Hydra.getVisitorDetails().then((info) => {
  console.log('Visitor details - ', info);
});
```

***

## Is Visitor Flow Enabled

```typescript
static isVisitorFlowEnabled(): Promise<boolean>;
```

**Returns**: `Promise<boolean>` which resolves to a boolean indicating whether the anonymous visitor flow is turned on for this account

**Usage**:

```typescript
Hydra.isVisitorFlowEnabled().then((enabled) => {
  console.log('Visitor flow enabled - ', enabled);
});
```

***

## Gamification Screen Appeared and Disappeared

```typescript
static gamificationScreenAppeared(screenName: string): Promise<void>;
static gamificationScreenDisappeared(screenName: string): Promise<void>;
```

### Parameters

| Parameter  | Type   | Required/Optional | Description                                                                                              |
| ---------- | ------ | ----------------- | -------------------------------------------------------------------------------------------------------- |
| screenName | string | required          | Name of the screen to track for gamification screen views. Pass the **same** `screenName` to both calls. |

**Usage**:

```typescript
Hydra.gamificationScreenAppeared('HomeScreen');
// ... later, when the screen unmounts:
Hydra.gamificationScreenDisappeared('HomeScreen');
```

***

## Set Cap Token

```typescript
static setCapToken(token: string): Promise<void>;
```

### Parameters

| Parameter | Type   | Required/Optional | Description       |
| --------- | ------ | ----------------- | ----------------- |
| token     | string | required          | CAP token to set. |

**Usage**:

```typescript
Hydra.setCapToken(token);
```

***

## Gamification Suppression

```typescript
static setGamificationSuppressed(suppressed: boolean): Promise<void>;
static isGamificationSuppressed(): Promise<boolean>;
```

### Parameters

| Parameter  | Type    | Required/Optional | Description                                                                          |
| ---------- | ------- | ----------------- | ------------------------------------------------------------------------------------ |
| suppressed | boolean | required          | `true` to stop gamification campaigns from being shown, `false` to allow them again. |

**Returns**: `setGamificationSuppressed` resolves once the value is applied. `isGamificationSuppressed` resolves to the current value. Both **reject** if the Hydra SDK is not initialized yet, so a rejection means suppression was not applied (or the value is unknown), not that it is `false`.

**Usage**:

```typescript
// for example, while the user is in checkout
Hydra.setGamificationSuppressed(true);
// ... later
Hydra.setGamificationSuppressed(false);

Hydra.isGamificationSuppressed().then((suppressed) => {
  console.log('Gamification suppressed - ', suppressed);
});
```

***

## Theme Mode

```typescript
static setThemeMode(mode: ThemeMode): Promise<void>;
static getThemeMode(): Promise<ThemeMode>;
```

### Parameters

| Parameter | Type                    | Required/Optional | Description                |
| --------- | ----------------------- | ----------------- | -------------------------- |
| mode      | [ThemeMode](#thememode) | required          | Theme mode for Hydra's UI. |

**Returns**: `setThemeMode` resolves once the mode is applied, and rejects if the SDK is not initialized or the mode is invalid. `getThemeMode` resolves to the current [ThemeMode](#thememode).

**Usage**:

```typescript
import { Hydra, ThemeMode } from '@capillarytech/react-native-hydra-lib';

Hydra.setThemeMode(ThemeMode.dark);

Hydra.getThemeMode().then((mode) => {
  console.log('Theme mode - ', mode);
});
```

***

# Managing Push Notifications

## Get FCM Token

This API can be used to get the FCM token and report when the token is retrieved.

```typescript
static getFCMToken(): Promise<string>;
```

**Returns**: `Promise<string>` containing FCM token (throws error if unavailable)

**Usage**:

```typescript
HydraPushNotification.getFCMToken().then((token) => {
  console.log('FCM Token - ', token);
}).catch((err: any) => {
  console.log('HydraPushNotification.getFCMToken', err);
});
```

***

## Request Permission for Push notifications

This API can be used to request permission for push notifications from the user and report when the push permission has been granted.

```typescript
static requestPermission(): Promise<boolean>;
```

**Returns**: `Promise<boolean>` indicating if permission was granted. It can also throw an error.

**Usage**:

```typescript
HydraPushNotification.requestPermission()
  .then((status) => {
    console.log('Notification permission status - ', status);
  })
  .catch((err: any) => {
    console.log('HydraPushNotification.requestPermission', err);
  });
```

***

## Open External URL

```typescript
static openExternalUrl(url: string): Promise<void>;
```

### Parameters

| Parameter | Type   | Required/Optional | Description                                                                              |
| --------- | ------ | ----------------- | ---------------------------------------------------------------------------------------- |
| url       | string | required          | External URL to open, for example when you handle a notification or CTA action yourself. |

**Usage**:

```typescript
HydraPushNotification.openExternalUrl('https://example.com');
```

***

## Pass FCM Token (Android only)

```typescript
static passFCMToken(token: string): Promise<void>;
```

Call this on Android whenever `enable_hydra_sdk_firebase_registration` is `false` in `hydra-config.json`, meaning Hydra isn't fetching the FCM token itself. On iOS, this call resolves immediately and does nothing.

> 📘 Note
>
> Gamification needs this call on Android. With `enable_hydra_sdk_firebase_registration` set to `false`, Gamification doesn't work properly until you pass a token. Call `passFCMToken` **after the SDK has initialized**. It rejects before that. Use the real FCM token if your app has one. If it doesn't, for example when you [use Hydra without Firebase](https://docs.capillarytech.com/docs/react-native-sdk-advanced-setup#using-hydra-without-firebase), a dummy token is fine.

There are two cases:

* **Your app owns the `FirebaseMessagingService`:** pass every new FCM token (for example from `onNewToken`, or from `@react-native-firebase/messaging`) so Hydra can deliver push notifications and Gamification works.
* **No Firebase and no push:** pass a dummy token once, after initialization, so Gamification works.

### Parameters

| Parameter | Type   | Required/Optional | Description                                                            |
| --------- | ------ | ----------------- | ---------------------------------------------------------------------- |
| token     | string | required          | The device's FCM token, or any non-empty dummy string if there's none. |

**Returns**: `Promise<void>`. On Android, it rejects if the SDK has not been initialized yet.

**Usage, real token**:

```typescript
import messaging from '@react-native-firebase/messaging';

if (Platform.OS === 'android') {
  const token = await messaging().getToken();
  await HydraPushNotification.passFCMToken(token);
}
```

**Usage, dummy token after initialization**:

```typescript
const passToken = () => {
  if (Platform.OS === 'android') {
    HydraPushNotification.passFCMToken('hydra-dummy-token');
  }
};

const isInitialized = await HydraCore.isSdkInitialized();
if (isInitialized) {
  passToken();
} else {
  const subscription =
    HydraNativeEventEmitter.getInstance().addHydraSdkInitializationResultListener(
      (success) => {
        if (success) passToken();
        HydraNativeEventEmitter.getInstance().removeListener(subscription);
      }
    );
}
```

***

# Managing the Notification Inbox

## Get list of Hydra Notifications

This API can be used to get the list of notifications.

```typescript
static async getInboxMessages(): Promise<HydraNotification[]>;
```

**Returns**: `Promise<HydraNotification[]>`

**Usage**:

```typescript
HydraInbox.getInboxMessages().then((messages) => {
  if (messages.length > 0) {
    console.log('Inbox message first - ', messages[0]);
  } else {
    console.log('No messages in inbox');
  }
});
```

***

## Get Unread Hydra Notifications Count

This API can be used to get the number of unread notifications.

```typescript
static getUnreadMessagesCount(): Promise<number>;
```

**Returns**: `Promise<number>` with unread count

**Usage**:

```typescript
HydraInbox.getUnreadMessagesCount().then((count) => {
  console.log('Unread count - ', count);
});
```

***

## Mark a Hydra Notification as read

This API can be used to mark a notification as read and report when a notification has been marked as read.

```typescript
static markInboxMessageAsRead(
  hydraNotification: HydraNotification
): Promise<boolean>;
```

### Parameters

| Parameter         | Type                                                                                                                          | Required/Optional | Description                                                                                                                                                                                      |
| ----------------- | ----------------------------------------------------------------------------------------------------------------------------- | ----------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| hydraNotification | [HydraNotification](https://docs.capillarytech.com/docs/react-native-sdk-api-reference#managing-notification-data-structures) | required          | Hydra Notification to mark as read from the list of Hydra Notification obtained [here](https://docs.capillarytech.com/docs/react-native-sdk-api-reference#managing-notification-data-structures) |

**Returns**: `Promise<boolean>` indicating success

**Usage**:

```typescript
HydraInbox.markInboxMessageAsRead(hydraNotification).then((res) => {
  console.log('Marked as read - ', res);
});
```

***

## Delete a Hydra Notification

This API can be used to delete a notification and report when a notification has been deleted.

```typescript
static deleteInboxMessage(
  hydraNotification: HydraNotification
): Promise<boolean>;
```

### Parameters

| Parameter         | Type                                                                                                                          | Required/Optional | Description                                                                                                                                                                                |
| ----------------- | ----------------------------------------------------------------------------------------------------------------------------- | ----------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| hydraNotification | [HydraNotification](https://docs.capillarytech.com/docs/react-native-sdk-api-reference#managing-notification-data-structures) | required          | Hydra Notification to delete from the list of Hydra Notification obtained [here](https://docs.capillarytech.com/docs/react-native-sdk-api-reference#managing-notification-data-structures) |

**Returns**: `Promise<boolean>` indicating success

**Usage**:

```typescript
HydraInbox.deleteInboxMessage(hydranotification).then((deleted) => {
  console.log('Deleted message - ', deleted);
});
```

***

## Delete all Hydra Notifications

This API can be used to delete all notifications and report when all notifications have been deleted.

```typescript
static deleteAllInboxMessages(): Promise<boolean>;
```

**Returns**: `Promise<boolean>` indicating success

**Usage**:

```typescript
HydraInbox.deleteAllInboxMessages().then((deleted) => {
  console.log('All messages deleted - ', deleted);
});
```

***

# Managing the In-App Notification Centre

## Show In-Built Notification Centre

This API can be used to show the built-in notification centre.

```typescript
static showNotificationCenter(): Promise<void>;
```

**Usage**:

```typescript
HydraInboxUI.showNotificationCenter();
```

***

## Hide In-Built Notification Centre if Showing

This API can be used to hide the built-in notification centre.

```typescript
static hideNotificationCenterIfShowing(): Promise<void>;
```

**Usage**:

```typescript
HydraInboxUI.hideNotificationCenterIfShowing().then(() => {
  console.log('Notification Center hidden');
});
```

***

# SDK Event Tracking

## Get Singleton Instance

This API can be used to get the singleton instance.

```typescript
static getInstance(): HydraNativeEventEmitter;
```

**Returns**: Singleton Instance of HydraNativeEventEmitter to invoke all other functions of this class

**Usage**:

```typescript
HydraNativeEventEmitter.getInstance();
```

***

## Get callback for Hydra SDK initialization result

This API can be used to get the result of initialisation.

```typescript
HydraNativeEventEmitter.addHydraSdkInitializationResultListener(
  listener: (success: boolean, errorMessage: string | null) => void
): EmitterSubscription;
```

### Parameters

| Parameter | Type                                                     | Required/Optional | Description                                                                                                                                                             |
| --------- | -------------------------------------------------------- | ----------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| listener  | (success: boolean, errorMessage: string \| null) => void | required          | A function which accepts a boolean if the initialization was successful or not, the function also has an optional string to pass errorMessage when initialization fails |

**Returns**: subscription object of type EmitterSubscription, this should be saved if you want to remove the listener later

**Usage**:

```typescript
const hydraSdkIntializationResultSubscription =
  HydraNativeEventEmitter.getInstance().addHydraSdkInitializationResultListener(
    (result, message) => {}
  );
```

> 📘 Note
>
> You can check the initialization status of the SDK on demand using the [isSdkInitialized](#check-if-hydra-sdk-is-initialized-or-not-on-demand) function. This is particularly useful when your API calls depend on the initialization state of Hydra. You can call this function at any time.

***

## Get callback when a new FCM token is available

This API can be used to get a callback and report when a new FCM token is available.

```typescript
HydraNativeEventEmitter.addTokenAvailableListener(
  listener: (token: string) => void
): EmitterSubscription;
```

### Parameters

| Parameter | Type                    | Required/Optional | Description                                               |
| --------- | ----------------------- | ----------------- | --------------------------------------------------------- |
| listener  | (token: string) => void | required          | A function which accepts a string parameter for FCM token |

**Returns**: subscription object of type EmitterSubscription, this should be saved if you want to remove the listener later

**Usage**:

```typescript
const tokenAvailableSubscription =
  HydraNativeEventEmitter.getInstance().addTokenAvailableListener(
    (token) => {
      console.log('>>> onTokenAvailable:', token);
    }
  );
```

***

## Get callback when Non Hydra Notification is received

This API can be used to get a callback when a non-Hydra push notification is received.

```typescript
HydraNativeEventEmitter.addNonHydraNotificationReceivedListener(
  listener: (notification: NonHydraNotification) => void
): EmitterSubscription;
```

### Parameters

| Parameter | Type                                         | Required/Optional | Description                                                                          |
| --------- | -------------------------------------------- | ----------------- | ------------------------------------------------------------------------------------ |
| listener  | (notification: NonHydraNotification) => void | required          | A function which accepts a NonHydraNotification parameter for received notification. |

**Usage**:

```typescript
const nonHydraNotificationReceivedSubscription =
  HydraNativeEventEmitter.getInstance().addNonHydraNotificationReceivedListener(
    (notification: NonHydraNotification) => {
      console.log(
        '>>>>>>> Non-Hydra Notification received >>>>>> ',
        notification
      );
    }
  );
```

***

## Get callback when Non Hydra Notification is clicked

This API can be used to get a callback when a non-Hydra push notification is tapped.

```typescript
HydraNativeEventEmitter.addNonHydraNotificationClickedListener(
  listener: (notification: NonHydraNotification) => void
): EmitterSubscription;
```

**Usage**:

```typescript
const nonHydraNotificationClickedSubscription =
  HydraNativeEventEmitter.getInstance().addNonHydraNotificationClickedListener(
    (notification: NonHydraNotification) => {
      console.log(
        '>>>>>>> Non-Hydra Notification clicked >>>>>> ',
        notification
      );
    }
  );
```

***

## Get callback when a Hydra Notification is received

This API can be used to get a callback and report when a new notification is received.

```typescript
HydraNativeEventEmitter.addHydraNotificationReceivedListener(
  listener: (notification: HydraNotification) => void
): EmitterSubscription;
```

### Parameters

| Parameter | Type                                      | Required/Optional | Description                                                                      |
| --------- | ----------------------------------------- | ----------------- | -------------------------------------------------------------------------------- |
| listener  | (notification: HydraNotification) => void | required          | A function which accepts a HydraNotification parameter for received notification |

**Returns**: subscription object of type EmitterSubscription, this should be saved if you want to remove the listener later

**Usage**:

```typescript
const notificationReceivedSubscription = HydraNativeEventEmitter.getInstance().addHydraNotificationReceivedListener((notification : HydraNotification) => {
  console.log('>>>>>>> Notification received >>>>>> ', notification);
});
```

***

## Get a callback for notification click

This API can be used to get a callback and report when a notification is clicked.

```typescript
HydraNativeEventEmitter.addHydraNotificationClickedListener(
  listener: (notification: HydraNotification | null, cta: HydraNotificationCta | null) => void
): EmitterSubscription;
```

### Parameters

| Parameter | Type                                                                                 | Required/Optional | Description                                                                                                                                                                                                         |
| --------- | ------------------------------------------------------------------------------------ | ----------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| listener  | (notification: HydraNotification \| null, cta: HydraNotificationCta \| null) => void | required          | A function which accepts an optional HydraNotification and an optional [HydraNotificationCta](https://docs.capillarytech.com/docs/react-native-sdk-api-reference#hydranotificationcta) for the CTA that was clicked |

**Returns**: subscription object of type EmitterSubscription, this should be saved if you want to remove the listener later

**Usage**:

```typescript
function onHydraNotificationClicked(
  notification: HydraNotification | null,
  cta: HydraNotificationCta | null
) {
  console.log('>>>>>>>>> onHydraNotificationClicked', notification, 'cta', cta);
  if (!cta?.action) {
    return;
  }
  if (cta.type === HydraNotificationCtaType.external) {
    HydraPushNotification.openExternalUrl(cta.action);
  } else if (cta.type === HydraNotificationCtaType.deepLink) {
    console.log('DeepLink clicked', cta.action);
  }
}

const notificationClickedSubscription = HydraNativeEventEmitter.getInstance().addHydraNotificationClickedListener( onHydraNotificationClicked );
```

***

## Callback when Hydra Notification is Shown

This API can be used to get a callback and report when a notification token is shown.

```typescript
HydraNativeEventEmitter.addHydraNotificationShownListener(
  listener: (notification: HydraNotification) => void
): EmitterSubscription;
```

### Parameters

| Parameter | Type                                      | Required/Optional | Description                                                                   |
| --------- | ----------------------------------------- | ----------------- | ----------------------------------------------------------------------------- |
| listener  | (notification: HydraNotification) => void | required          | A function which accepts a HydraNotification parameter to show a notification |

**Returns**: subscription object of type EmitterSubscription, this should be saved if you want to remove the listener later

**Usage**:

```typescript
const notificationShownSubscription =
  HydraNativeEventEmitter.getInstance().addHydraNotificationShownListener(
    (notification: HydraNotification) => {
      console.log('>>>>>>>>> onHydraNotificationShown', notification);
    }
  );
```

***

## Callback when user dismisses a hydra notification

This API can be used to get a callback and report when a user dismisses a notification.

```typescript
HydraNativeEventEmitter.addHydraNotificationDismissedListener(
  listener: (notification: HydraNotification) => void
): EmitterSubscription;
```

### Parameters

| Parameter | Type                                      | Required/Optional | Description                                                                         |
| --------- | ----------------------------------------- | ----------------- | ----------------------------------------------------------------------------------- |
| listener  | (notification: HydraNotification) => void | required          | A function which accepts a HydraNotification parameter for a dismissed notification |

**Returns**: subscription object of type EmitterSubscription, this should be saved if you want to remove the listener later

**Usage**:

```typescript
const notificationDismissedSubscription = HydraNativeEventEmitter.getInstance().addHydraNotificationDismissedListener(
  (notification: HydraNotification) => {
    console.log('>>>>>>>>> onHydraNotificationDismissed', notification);
  }
);
```

***

## Callback when In-Built notification center is dismissed

This API can be used to get a callback and report when a user dismisses the in-built notification center.

```typescript
HydraNativeEventEmitter.addNotificationCenterDismissedListener(
  listener: () => void
): EmitterSubscription;
```

### Parameters

| Parameter | Type       | Required/Optional | Description                       |
| --------- | ---------- | ----------------- | --------------------------------- |
| listener  | () => void | required          | A function without any parameters |

**Returns**: subscription object of type EmitterSubscription, this should be saved if you want to remove the listener later

**Usage**:

```typescript
const notificationCenterDismissedSubscription =
  HydraNativeEventEmitter.getInstance().addNotificationCenterDismissedListener(
    () => {
      console.log('>>>>>>> Notification center dismissed >>>>>>');
    }
  );
```

***

## Callback when the inbox is updated

This API can be used to get a callback and report when the inbox is updated.

```typescript
HydraNativeEventEmitter.addInboxUpdatedListener(
  listener: () => void
): EmitterSubscription;
```

### Parameters

| Parameter | Type       | Required/Optional | Description                       |
| --------- | ---------- | ----------------- | --------------------------------- |
| listener  | () => void | required          | A function without any parameters |

**Returns**: subscription object of type EmitterSubscription, this should be saved if you want to remove the listener later

**Usage**:

```typescript
const inboxUpdatedSubscription =
  HydraNativeEventEmitter.getInstance().addInboxUpdatedListener(() => {
    console.log('>>>>>>> Inbox updated >>>>>>');
  });
```

***

## Get callback when config is fetched (visitor flow)

```typescript
setConfigFetchedCallback(listener: (isVisitorFlowEnabled: boolean) => void): EmitterSubscription;
```

### Parameters

| Parameter | Type                                    | Required/Optional | Description                                                                                            |
| --------- | --------------------------------------- | ----------------- | ------------------------------------------------------------------------------------------------------ |
| listener  | (isVisitorFlowEnabled: boolean) => void | required          | Fired once remote config has been fetched, indicating whether the anonymous visitor flow is turned on. |

**Usage**:

```typescript
HydraNativeEventEmitter.getInstance().setConfigFetchedCallback(
  (isVisitorFlowEnabled) => {
    console.log('Visitor flow enabled - ', isVisitorFlowEnabled);
  }
);
```

***

## Get callback when legacy flow is ready

```typescript
setLegacyFlowReadyCallback(listener: () => void): EmitterSubscription;
```

**Usage**:

```typescript
HydraNativeEventEmitter.getInstance().setLegacyFlowReadyCallback(() => {
  console.log('Legacy flow ready');
});
```

***

## Get callback when visitor session is ready

```typescript
setVisitorSessionReadyCallback(listener: () => void): EmitterSubscription;
```

**Usage**:

```typescript
HydraNativeEventEmitter.getInstance().setVisitorSessionReadyCallback(() => {
  console.log('Visitor session ready');
});
```

***

## Get callback when user state changes

```typescript
setUserStateChangedCallback(listener: (userState: UserState | null) => void): EmitterSubscription;
```

### Parameters

| Parameter | Type                                   | Required/Optional | Description                                                                                   |
| --------- | -------------------------------------- | ----------------- | --------------------------------------------------------------------------------------------- |
| listener  | (userState: UserState \| null) => void | required          | Fired whenever the user's state transitions (none/visitor/merged/legacyRegistered/signedOut). |

**Usage**:

```typescript
HydraNativeEventEmitter.getInstance().setUserStateChangedCallback(
  (userState) => {
    console.log('User state changed - ', userState);
  }
);
```

***

## Get callback when the height of a gamification view changes

```typescript
addGamificationViewHeightChangedListener(listener: (height: number, entryPointId: string) => void): EmitterSubscription;
```

### Parameters

| Parameter | Type                                           | Required/Optional | Description                                                                                                        |
| --------- | ---------------------------------------------- | ----------------- | ------------------------------------------------------------------------------------------------------------------ |
| listener  | (height: number, entryPointId: string) => void | required          | Fired when the height of a gamification banner/embed/loyalty view changes, for example to auto-size the container. |

**Usage**:

```typescript
HydraNativeEventEmitter.getInstance().addGamificationViewHeightChangedListener(
  (height, entryPointId) => {
    console.log('Gamification view height changed - ', height, entryPointId);
  }
);
```

***

## Get callback for a notification custom action (Android only)

```typescript
addHandleCustomActionListener(listener: (payload: string) => void): EmitterSubscription;
```

### Parameters

| Parameter | Type                      | Required/Optional | Description                                                                                                          |
| --------- | ------------------------- | ----------------- | -------------------------------------------------------------------------------------------------------------------- |
| listener  | (payload: string) => void | required          | Fired when the user taps a Hydra notification CTA with a custom action, with the action payload. Not emitted on iOS. |

**Usage**:

```typescript
HydraNativeEventEmitter.getInstance().addHandleCustomActionListener(
  (payload) => {
    console.log('Custom action - ', payload);
  }
);
```

***

## Get callback when gamification requests a deep link

```typescript
addGamificationDeeplinkListener(listener: (url: string) => void): EmitterSubscription;
```

### Parameters

| Parameter | Type                  | Required/Optional | Description                                                                                   |
| --------- | --------------------- | ----------------- | --------------------------------------------------------------------------------------------- |
| listener  | (url: string) => void | required          | Fired when a gamification campaign asks the app to open a deep link. Route `url` in your app. |

**Usage**:

```typescript
HydraNativeEventEmitter.getInstance().addGamificationDeeplinkListener((url) => {
  // for example, hand off to your navigation or linking handler
  console.log('Gamification deep link - ', url);
});
```

***

## Get callback when a gamification event is triggered

```typescript
addGamificationEventTriggerListener(
  listener: (name: string, payload: Record<string, any>) => void
): EmitterSubscription;
```

### Parameters

| Parameter | Type                                                  | Required/Optional | Description                                                                             |
| --------- | ----------------------------------------------------- | ----------------- | --------------------------------------------------------------------------------------- |
| listener  | (name: string, payload: Record\<string, any>) => void | required          | Fired when a gamification campaign/game triggers a named event, with its event payload. |

**Usage**:

```typescript
HydraNativeEventEmitter.getInstance().addGamificationEventTriggerListener(
  (name, payload) => {
    console.log('Gamification event triggered - ', name, payload);
  }
);
```

***

## Get callback for gamification analytics events

```typescript
addGamificationAnalyticsEventListener(
  listener: (name: string, payload: Record<string, any>) => void
): EmitterSubscription;
```

### Parameters

| Parameter | Type                                                  | Required/Optional | Description                                                                                                    |
| --------- | ----------------------------------------------------- | ----------------- | -------------------------------------------------------------------------------------------------------------- |
| listener  | (name: string, payload: Record\<string, any>) => void | required          | Fired for analytics events emitted by gamification UI, for example to forward them to your own analytics tool. |

**Usage**:

```typescript
HydraNativeEventEmitter.getInstance().addGamificationAnalyticsEventListener(
  (name, payload) => {
    console.log('Gamification analytics event - ', name, payload);
  }
);
```

***

## Remove an added listener

This API can be used to get a callback and report when an added listener is removed.

```typescript
HydraNativeEventEmitter.removeListener(
  emitterSubscription: EmitterSubscription
): void;
```

### Parameters

| Parameter           | Type                | Required/Optional | Description                                    |
| ------------------- | ------------------- | ----------------- | ---------------------------------------------- |
| emitterSubscription | EmitterSubscription | required          | Subscription returned when adding the listener |

**Returns**: void

**Usage**:

```typescript
HydraNativeEventEmitter.getInstance().removeListener(
  inboxUpdatedSubscription
);
```

***

## Remove all listeners for an event

```typescript
removeAllListeners(eventType: HydraNativeEvent): void;
```

### Parameters

| Parameter | Type                                  | Required/Optional | Description                                  |
| --------- | ------------------------------------- | ----------------- | -------------------------------------------- |
| eventType | [HydraNativeEvent](#hydranativeevent) | required          | Event whose listeners should all be removed. |

**Usage**:

```typescript
HydraNativeEventEmitter.getInstance().removeAllListeners(
  HydraNativeEvent.onInboxUpdated
);
```

***

# Managing User Data Structures

## HydraUserDetails

This class stores the user's details.

```typescript
constructor HydraUserDetails(
  customerId: string,
  firstName?: string | null,
  lastName?: string | null,
  email?: string | null,
  phone?: string | null
): HydraUserDetails;
```

### Parameters

| Parameter  | Type   | Required/Optional | Description                                                                                                                                                                                                                                                                 |
| ---------- | ------ | ----------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| customerId | string | required          | customerId can be mobile, email, InTouchUserId, externalId or FCMToken. It depends on how your app is configured on capillary CRM dashboard in `Organisation settings -> Omni Channel Settings -> Channel Configurations -> MAPP_SDK` Look for `Account Linking Identifier` |
| firstName  | string | optional          | First name of the user                                                                                                                                                                                                                                                      |
| lastName   | string | optional          | Last name of the user                                                                                                                                                                                                                                                       |
| email      | string | optional          | Email of the user                                                                                                                                                                                                                                                           |
| phone      | string | optional          | Phone number of the user                                                                                                                                                                                                                                                    |

**Usage**:

```typescript
const userDetails = new HydraUserDetails(
  '8888888888',
  'FirstName',
  'LastName',
  'hydra.test@capillarytech.com',
  '918888888888',
);
```

***

## HydraGeoConfig

This class stores the geo config details of a user.

```typescript
constructor HydraGeoConfig(
  city: string,
  country: string,
  countryCode: string,
  timezone?: string | null
): HydraGeoConfig;
```

### Parameters

| Parameter   | Type   | Required/Optional | Description                    |
| ----------- | ------ | ----------------- | ------------------------------ |
| city        | string | required          | City of the user               |
| country     | string | required          | Country of the user            |
| countryCode | string | required          | Country code for mobile number |
| timezone    | string | optional          | User's timezone                |

**Usage**:

```typescript
const geoConfig = new HydraGeoConfig(
  'Bangalore',
  'India',
  'IN',
  'Asia/Kolkata'
);
```

***

## HydraPushPreferences

This class stores the push preference details of a user.

```typescript
constructor HydraPushPreferences(
  promPushOpted: boolean,
  transPushOpted: boolean
): HydraPushPreferences;
```

### Parameters

| Parameter      | Type    | Required/Optional | Description                                     |
| -------------- | ------- | ----------------- | ----------------------------------------------- |
| promPushOpted  | boolean | required          | Enable/disable promotional push notifications   |
| transPushOpted | boolean | required          | Enable/disable transactional push notifications |

**Usage**:

```typescript
const pushPreferences = new HydraPushPreferences(
  true,
  true
);
```

***

## HydraLogLevel

This enumeration defines the constants used to set the console and remote log levels in hydra configuration. The higher level includes all the levels below.

```typescript
enum HydraLogLevel {
  off = 0,
  error = 1,
  warn = 2,
  info = 3,
  debug = 4,
  verbose = 5,
}
```

***

## HydraAccountConfig

This is a model class used to update user's account configurations, including optional Anonymous/Visitor Flow and Gamification fields.

```typescript
constructor HydraAccountConfig(
  accountId: string,
  baseUrl: string,
  sslPublicKey: string,
  remoteDebugLevel: HydraLogLevel = HydraLogLevel.off,
  orgId?: string,
  gamificationKey?: string,
  gamificationRegion?: string,
  gamificationBaseUrl?: string
): HydraAccountConfig;
```

### Parameters

| Parameter           | Type                            | Required/Optional | Description                                                                           |
| ------------------- | ------------------------------- | ----------------- | ------------------------------------------------------------------------------------- |
| accountId           | string                          | required          | Account id of the hydra account config                                                |
| baseUrl             | string                          | required          | baseUrl of the hydra account config                                                   |
| sslPublicKey        | string                          | required          | sslPublicKey of the hydra account config                                              |
| remoteDebugLevel    | [HydraLogLevel](#hydraloglevel) | required          | Log level (e.g. HydraLogLevel.off, HydraLogLevel.verbose). Default: HydraLogLevel.off |
| orgId               | string                          | optional          | Org Id, required for the Anonymous/Visitor Flow                                       |
| gamificationKey     | string                          | optional          | Gamification Key, required for Gamification                                           |
| gamificationRegion  | string                          | optional          | Gamification Region, required for Gamification                                        |
| gamificationBaseUrl | string                          | optional          | Gamification Base Url, required for Gamification                                      |

**Usage**:

```typescript
const hydraAccountConfig = new HydraAccountConfig(
  accountId,
  baseUrl,
  sslPublicKey,
  remoteDebugLevel,
  orgId,
  gamificationKey,
  gamificationRegion,
  gamificationBaseUrl
);
```

***

## HydraFirebaseRemoteConfigKeys

This is a model class used to update a user's remote account configurations, including optional Anonymous/Visitor Flow and Gamification key names.

```typescript
constructor HydraFirebaseRemoteConfigKeys(
  keyForAccountId: string,
  keyForBaseUrl: string,
  keyForSsl: string,
  keyForRemoteDebugLevel: string,
  keyForOrgId?: string,
  keyForGamificationKey?: string,
  keyForGamificationRegion?: string,
  keyForGamificationBaseUrl?: string
): HydraFirebaseRemoteConfigKeys;
```

### Parameters

| Parameter                 | Type   | Required/Optional | Description                                                                                   |
| ------------------------- | ------ | ----------------- | --------------------------------------------------------------------------------------------- |
| keyForAccountId           | string | required          | Firebase config Key for your applicable hydra AccountId                                       |
| keyForBaseUrl             | string | required          | Firebase config Key for your applicable hydra BaseUrl                                         |
| keyForSsl                 | string | required          | Firebase config Key for your applicable hydra SSL                                             |
| keyForRemoteDebugLevel    | string | required          | Firebase config Key for your applicable hydra RemoteDebugLevel                                |
| keyForOrgId               | string | optional          | Firebase config Key for your applicable hydra Org Id, required for the Anonymous/Visitor Flow |
| keyForGamificationKey     | string | optional          | Firebase config Key for your applicable Gamification Key                                      |
| keyForGamificationRegion  | string | optional          | Firebase config Key for your applicable Gamification Region                                   |
| keyForGamificationBaseUrl | string | optional          | Firebase config Key for your applicable Gamification Base Url                                 |

**Usage**:

```typescript
const remoteConfigKeys = new HydraFirebaseRemoteConfigKeys(
  'ind_hydra_account_id',
  'ind_hydra_base_url',
  'ind_hydra_ssl_public_key',
  'ind_hydra_remote_log_level',
  'ind_hydra_org_id',
  'ind_hydra_gamification_key',
  'ind_hydra_gamification_region',
  'ind_hydra_gamification_base_url'
);
```

***

## UserState

This enumeration represents the current state of the user in the anonymous/visitor flow.

```typescript
enum UserState {
  none = 'none',
  legacyRegistered = 'legacyRegistered',
  visitor = 'visitor',
  merged = 'merged',
  signedOut = 'signedOut',
}
```

***

## HydraVisitorInfo

This class represents the current anonymous visitor's identifier.

```typescript
class HydraVisitorInfo {
  visitorId: string;
}
```

***

## ThemeMode

This enumeration is used with [Hydra.setThemeMode / getThemeMode](#theme-mode).

```typescript
enum ThemeMode {
  none = 'NONE',
  auto = 'AUTO',
  light = 'LIGHT',
  dark = 'DARK',
}
```

***

## HydraNativeEvent

This enumeration lists the event names emitted by [HydraNativeEventEmitter](#sdk-event-tracking). You only need it for [removeAllListeners](#remove-all-listeners-for-an-event). Use the typed `add…Listener` and `set…Callback` methods to subscribe.

```typescript
enum HydraNativeEvent {
  onTokenAvailable = 'onTokenAvailable',
  onNonHydraNotificationReceived = 'onNonHydraNotificationReceived',
  onNonHydraNotificationClicked = 'onNonHydraNotificationClicked',
  onHydraNotificationReceived = 'onHydraNotificationReceived',
  onHydraNotificationClicked = 'onHydraNotificationClicked',
  onHydraNotificationShown = 'onHydraNotificationShown',
  onHydraNotificationDismissed = 'onHydraNotificationDismissed',
  handleCustomAction = 'handleCustomAction',
  onNotificationCenterDismissed = 'onNotificationCenterDismissed',
  onInboxUpdated = 'onInboxUpdated',
  onHydraSdkInitializationResult = 'onHydraSdkInitializationResult',
  onHydraInAppMessage = 'onHydraInAppMessage',
  onConfigFetchedCallback = 'onConfigFetchedCallback',
  onLegacyFlowReady = 'onLegacyFlowReady',
  onVisitorSessionReady = 'onVisitorSessionReady',
  onUserStateChanged = 'onUserStateChanged',
  onGamificationViewHeightChanged = 'onGamificationViewHeightChanged',
  gamificationAnalyticsEvent = 'gamificationAnalyticsEvent',
  gamificationDeeplink = 'gamificationDeeplink',
  gamificationEventTrigger = 'gamificationEventTrigger',
}
```

***

# Managing Notification Data Structures

## HydraNotification Structure

This class stores the structure for a notification.

```typescript
class HydraNotification {
  readonly cuid: string | null;
  readonly scope: string | null;
  readonly campaignId: string | null;
  readonly variationId: string | null;
  readonly senderId: string | null;
  readonly senderSource: string | null;
  readonly custom: string | null;
  readonly customData: Record<string, any> | null;
  readonly priority: string | null;
  readonly validity: string | null;
  readonly messageId: string | null;
  readonly gateway: HydraNotificationGateway | null;
  readonly body: HydraNotificationBody | null;
  readonly expandableDetails: HydraNotificationExpandedDetails | null;
  readonly isRead: boolean | null;
  readonly imageIdentifier: string | null;
  readonly accountId: string | null;
  readonly channelId: string | null;
  readonly payload: string | null;
  readonly createdAt: Date | null;
  readonly isExpanded: boolean | null;
  readonly isMessageEllipsized: boolean | null;
  readonly isTitleEllipsized: boolean | null;
  readonly showArrow: boolean | null;
}
```

## HydraNotificationBody

This class stores the body for a notification.

```typescript
class HydraNotificationBody {
  readonly title: string | null;
  readonly message: string | null;
  readonly cta: HydraNotificationCta | null;
  readonly image: string | null;
}
```

## HydraNotificationCta

This class stores the call to action (CTA) for a notification.

```typescript
class HydraNotificationCta {
  readonly type: HydraNotificationCtaType | null;
  readonly action: string | null;
  readonly actionText: string | null;
}
```

## HydraNotificationCtaType Enum

This class stores the call to action (CTA) type for a notification.

```typescript
enum HydraNotificationCtaType {
  external,
  deepLink,
  rating,
  feedback,
  appRating,
  unknown,
}
```

## HydraNotificationExpandedDetails

This class stores the expanded details for a notification.

```typescript
class HydraNotificationExpandedDetails {
  readonly ctas: HydraNotificationCta[] | null;
  readonly message: string | null;
  readonly image: string | null;
  readonly style: string | null;
}
```

## HydraNotificationGateway Enum

This class stores the gateway details for a notification.

```typescript
enum HydraNotificationGateway {
  fcm,
  xiaomi,
  unknown,
}
```

## NonHydraNotification Structure

This class stores the structure for a non-Hydra notification.

```typescript
class NonHydraNotification {
  readonly title: string | null;
  readonly body: string | null;
  readonly icon: string | null;
  readonly imageUrl: string | null;
  readonly data: Record<string, any> | null;
}
```