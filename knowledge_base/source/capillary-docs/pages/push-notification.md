---
updatedAt: 2026-11-16T05:54:42.000Z
agentTools:
  projectIndex: https://docs.capillarytech.com/llms.txt
---

# Configure Push Notifications

This page provides you with information on push notifications and how to configure it.

Push notifications are alerts that appear on a user's screen when an update occurs on the mobile app. The notification appears even if the user is not using the mobile app. They are useful for delivering timely and personalised content to users and can be an effective way to increase user engagement with your app.

Capillary SDK sends push notifications to Android users using [Firebase Cloud Messaging](https://firebase.google.com/docs/cloud-messaging/) (FCM).

# Prerequisite

The Capillary backend needs a Firebase service-account private key to send notifications to your users through FCM. Your app doesn't need this key and must never contain it. For information on how to create and share the key, see [Configure Firebase](https://docs.capillarytech.com/docs/configure-firebase).

# Configuring FCM for push notifications

Push registration can be handled by the application or Capillary SDK. Specific configurations are required based on whether SDK or the application performs the below two steps.

## Requesting notification runtime permission (Android 13+)

From Android 13 onwards, by default, push notifications are disabled for mobile applications. The applications have to explicitly ask permission from the end user to allow push notifications.

Capillary SDK provides helper APIs to show the permission request to the end-user for enabling notifications. Use the below API to show the permission request dialog to the user.\
This API automatically tracks the response and sets up the required notification channel.

`HydraPushApi.getInstance().requestPushPermission(context)`

## Configuring push registration - App handles the push notification

1. By default, Capillary SDK attempts to register for push tokens. If the mobile application manages the push notification, you must opt out of SDK's token registration. To opt-out, use the below settings:

```kotlin
val hydraConfig = HydraConfig.Builder(
   applicationContext,
   accountId = "123"
)
   .fcmConfig(FcmConfig(false))
   .build()
HydraAPI.instanceWithConfig(applicationContext, hydraConfig)
```
```java
FcmConfig fcmConfig = new FcmConfig(false);

HydraConfig hydraConfig = new HydraConfig.Builder(applicationContext)
        .setAccountId("123")
        .setFcmConfig(fcmConfig)
        .build();

HydraAPI.instanceWithConfig(applicationContext, hydraConfig);

```

2. Pass the push token to the SDK\
   If you already have a Firebase Messaging Service registered, you can pass New Token generated from
   `onNewToken` method and pass to Capillary SDK via `HydraFirebaseAPI.getInstance().passPushToken`. Use the below function:

   ```kotlin
   override fun onNewToken(token: String) {  
      HydraFirebaseAPI.getInstance().passPushToken(applicationContext, token)  
   }
   ```
   ```java
   @Override
   public void onNewToken(String token) {
       HydraFirebaseAPI.getInstance().passPushToken(applicationContext, token);
   }

   ```

   In addition, make sure that you pass the latest token every time to continue receiving push notifications when the previous token changes.\
   The token changes in the following scenarios:

   * The app is restored on a new device
   * The user uninstalls/reinstalls the app
   * The user clears app data.
3. Pass the push payload to the SDK

   If you already have a Firebase Messaging Service registered, you can pass `RemoteMessage` objects to SDK via `HydraFirebaseApi.passPushPayload()` from the `onMessageReceived() `in the Firebase receiver. Before passing the payload to the SDK, make sure that the payload is from the Hydra platform using the `isFromHydraPlatform()` helper API provided by the SDK.

   Example: User passing the hydra push payload to the SDK

```kotlin
if (HydraPushApi.getInstance().isFromHydraPlatform(remoteMessage.data)) {  
   HydraFirebaseAPI.getInstance().passPushPayload(applicationContext, remoteMessage.data)  
}
```
```java
if (HydraPushApi.getInstance().isFromHydraPlatform(remoteMessage.getData())) {
    HydraFirebaseAPI.getInstance().passPushPayload(applicationContext, remoteMessage.getData());
}

```

## Configuring push registration - SDK handles the push notification

To make Capillary SDK handle push token registration,

1. Enable SDK's token registration. Set the`FcmConfig(true)` at `fcmConfig` method.

```kotlin
val hydraConfig = HydraConfig.Builder(  
   applicationContext,  
   accountId = "123"  
)  
   .fcmConfig(FcmConfig(true))  
   .build()  
HydraAPI.instanceWithConfig(applicationContext, hydraConfig)
```
```java
HydraConfig hydraConfig = new HydraConfig.Builder(applicationContext)
        .setAccountId("123")
        .setFcmConfig(new FcmConfig(true))
        .build();

HydraAPI.instanceWithConfig(applicationContext, hydraConfig);

```

2. Add HydraFirebaseMessagingService to your manifest. Capillary SDK manages Firebase Messaging internally using the`HydraFirebaseMessagingService`.

```xml
<service
   android:name="com.capillarytech.hydra.firebase.HydraFirebaseMessagingService"
   android:exported="false">
   <intent-filter>
       <action android:name="com.google.firebase.MESSAGING_EVENT" />
   </intent-filter>
</service>
```
```xml
<service
   android:name="com.capillarytech.hydra.firebase.HydraFirebaseMessagingService"
   android:exported="false">
   <intent-filter>
       <action android:name="com.google.firebase.MESSAGING_EVENT" />
   </intent-filter>
</service>
```

# Configuring push notification

Set notification options (small icon, color, multiple notification handling). Use the following function:

```kotlin
val hydraConfig = HydraConfig.Builder(
   applicationContext,
   accountId = "123"
)
   .notificationConfig(
       NotificationConfig(
           smallIcon = R.drawable.small_icon,
           notificationColor = R.color.teal_200,
           isMultipleNotificationInDrawerEnabled = true,
       )
   )
   .build()
HydraAPI.instanceWithConfig(applicationContext, hydraConfig)
```
```java
NotificationConfig notificationConfig = new NotificationConfig(
    R.drawable.small_icon,
    R.color.teal_200,
    true
);

HydraConfig hydraConfig = new HydraConfig.Builder(applicationContext)
        .setAccountId("123")
        .setNotificationConfig(notificationConfig)
        .build();

HydraAPI.instanceWithConfig(applicationContext, hydraConfig);

```

| Parameter                             | Description                                                                                                                                                                                                 |
| :------------------------------------ | :---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| smallIcon                             | Resource-id for the notification small icon                                                                                                                                                                 |
| notificationColor                     | Icon colour for the notification                                                                                                                                                                            |
| isMultipleNotificationInDrawerEnabled | By default, SDK shows multiple notifications i.e. `isMultipleNotificationInDrawerEnabled` is true. If you want the app to show a single notification, set `isMultipleNotificationInDrawerEnabled` as false. |

## Push notification delivery and campaign TTL

If a push notification is not delivered to a device in real time (for example, because the device is offline, the FCM token is stale, or there are connectivity issues), the SDK uses a Pull mechanism to deliver the notification the next time the user opens the app. The system enforces a campaign Time-to-Live (TTL), which determines how long an undelivered notification remains eligible for delivery, including through the Pull mechanism. By default, the campaign TTL is 15 days, but you can configure this value at the organization level. If a notification remains within its configured TTL, it can still be delivered when the app is opened, even if the associated campaign has already ended. After the TTL expires, the notification is discarded and is no longer delivered. The TTL applies to all push notifications, including both promotional and transactional messages.

# Implementing Callback listeners

To make sure that you receive callbacks, even when the application is running in the background, listeners should be added in the `onCreate()` method of the application class. Capillary SDK provides the below listeners to hook into:

## Push notification callback

To receive a push callback, the application must register a `HydraPushNotificationListener` .

> 📘 Note
>
> It is mandatory to add the push notification callback listener once the SDK is initialized.

To perform push callback, implement the `HydraPushNotificationListener` and register for callback using `HydraPushAPI.getInstance().registerPushNotificationListener`.

Example: User implementing `HydraPushNotificationListener` to receive the push notification callback from the Hydra SDK.

```kotlin
class ApplicationPushMessageListener: HydraPushNotificationListener {
    private val TAG = HydraPushNotificationListener::class.java.name

    override fun onNotificationReceived(context: Context, payload: Bundle) {
        super.onNotificationReceived(context, payload)
    }

    override fun onNotificationShown(context: Context, payload: Bundle) {
        super.onNotificationShown(context, payload)
    }

    override fun onNotificationClick(context: Context, payload: NotificationPayload, cta: CTA ? ): Boolean {
        return super.onNotificationClick(context, payload, cta)
    }
    override fun onNotificationDismissed(context: Context, payload: Bundle) {
        super.onNotificationDismissed(context, payload)
    }
    override fun handleCustomAction(context: Context, payload: Bundle) {
        super.handleCustomAction(context, payload)
    }
}
```

Register the above callback in the `onCreate` of your application class after initialization of HydraAPI

In the above callback method, “onNotificationClick” returns Boolean to which application can return either true or false. If the function returns false, the action will be taken by the SDK and if returned true then custom action can be taken by the client app.

```kotlin
HydraPushApi.getInstance()
    .registerPushNotificationListener(ApplicationPushMessageListener())
```
```java
HydraPushApi.getInstance()
   .registerPushNotificationListener(new ApplicationPushMessageListener());
```

## Token callback

When Hydra SDK handles push registration, it optionally provides a callback to the application whenever a new token is registered or the token is refreshed.\
To get the token callback, implement the `TokenAvailableListener` and register it using `HydraFirebaseAPI.getInstance().addTokenListener`.

**Example:** User implementing `TokenAvailableListener` to receive the callback from the Capillary SDK

```kotlin
class ApplicationTokenListener : TokenAvailableListener {
   private val TAG = ApplicationTokenListener::class.java.name

   override fun onTokenAvailable(token: Token) {
       Log.w(TAG, "Application Token $token")
   }
}

```
```java
import android.util.Log;
import com.capillarytech.hydra.sdk.entity.Token;
import com.capillarytech.hydra.sdk.listeners.TokenAvailableListener;

public class ApplicationTokenListener implements TokenAvailableListener {
    private static final String TAG = ApplicationTokenListener.class.getName();

    @Override
    public void onTokenAvailable(Token token) {
        Log.w(TAG, "Application Token " + token);
    }
}

```

Register the above callback in the `onCreate` of your application class

```kotlin
HydraFirebaseAPI.getInstance().addTokenListener(ApplicationTokenListener())
```
```java
HydraFirebaseAPI.getInstance().addTokenListener(new ApplicationTokenListener());
```

## NonHydra payload callback

To receive a callback when a push payload is received for a server other than the Capillary platform, you can implement the `NonHydraPushListener` and register for the callback using:

```kotlin
HydraFirebaseAPI.getInstance().addNonHydraPushListener()
```
```java
HydraFirebaseAPI.getInstance().addNonHydraPushListener(new NonHydraPushListener() {
    @Override
    public void onNonHydraPushReceived(RemoteMessage remoteMessage) {
        // Handle the non-Hydra push notification here
    }
});

```

**Example:** User implementing `NonHydraPushListener` to receive the callback from the Capillary SDK.

```kotlin
class ApplicationPayloadListener : NonHydraPushListener {  
   override fun onPushReceived(remoteMessage: RemoteMessage) {  
       val pushNotificationPayload = remoteMessage.data  
       Log.w(TAG, "Application Push Payload $pushNotificationPayload")  
   }  
}
```
```java
import android.util.Log;
import com.google.firebase.messaging.RemoteMessage;
import com.capillarytech.hydra.firebase.NonHydraPushListener;

public class ApplicationPayloadListener implements NonHydraPushListener {
    private static final String TAG = ApplicationPayloadListener.class.getName();

    @Override
    public void onPushReceived(RemoteMessage remoteMessage) {
        String pushNotificationPayload = remoteMessage.getData().toString();
        Log.w(TAG, "Application Push Payload " + pushNotificationPayload);
    }
}

```

**Example:** Register the above callback in the `onCreate` of your application class

```kotlin
HydraFirebaseAPI.getInstance().addNonHydraPushListener(ApplicationPayloadListener())
```
```java
HydraFirebaseAPI.getInstance().addNonHydraPushListener(new ApplicationPayloadListener());

```

# Call to action

Calls To Action (CTA) are the deep links or URIs where users land when they click on the push message. You can add CTAs when you create your push campaign on the dashboard. They are divided into two categories:

1. Primary CTA
2. Non-primary CTA.

## Primary CTA

A push message can have only one primary CTA which performs an action when the user taps on the content of the push notification. This action can either direct the user to a particular URI in the browser or a deep link. If you do not configure any URI or deep link for primary CTA, then the user will be redirected to your application's launcher activity upon tapping the push notification.

## Non-primary CTA

You can add a maximum of 3 non-primary CTAs in a push notification. Each of the CTA triggers a specific action when the user taps on the corresponding button.

## Deeplink

A deep link is a type of hyperlink that takes you directly to a specific page within the app or website instead of the homepage. Capillary SDK supports URL-based deep linking. To create a push campaign, you can enter any valid URL on your dashboard  such as an` http / https` lnk or a valid custom URL like `cap://handleDeeplink/1234`. The SDK then sends this URL as part of an intent to the application. To receive the intent as shown below the application must add the intent filters to its manifest file.

```xml
<activity android:name=".SignUpActivity" android:exported="true">
<!--            Example with path prefix, port and path suffix for deep linking-->

   <!--            url example: cap://checkdeeplink:888/anythingsuffix-->

   <!--            url example: cap://checkdeeplink:888/prefixanything-->

<intent-filter>
       <action android:name="android.intent.action.VIEW" />
       <category android:name="android.intent.category.DEFAULT" />
       <category android:name="android.intent.category.BROWSABLE" />
        <data
           android:host="checkdeeplink"
           android:pathPrefix="/prefix"
           android:pathSuffix="suffix"
           android:port="888"
           android:scheme="cap" />
   </intent-filter>
</activity>
```

# Rich push notification

Rich push notifications enable you to engage with users using fancy push notification templates built to work with Capillary SDK. This feature is available from Hydra SDK version 1.2.0 and RichNotification version 1.0.0.

There are two ways to install rich push notifications:

* Installation using catalog
* Installation using artifact

## Installing using catalog

The recommended approach for integration is through a Version Catalog. For more information, refer to the documentation [Installing with version catalog](https://docs.capillarytech.com/docs/installing-sdk#/installing-with-version-catalog). After you configure the catalog, perform the following:

1. Add the dependency in the `app/build.gradle` file as shown below:

```kotlin
dependencies {
    // ...
    implementation("hydra.richnotification")
}

```
```groovy
dependencies {
…
 implementation("hydra.richnotification")
}
```

## Installing using Artifact

To install rich notifications using Artifact, perform the following:

1. Add the dependency in the `app/build.gradle` file as shown below:

```kotlin
dependencies {
    // ...
    implementation("com.capillarytech:hydra-richnotification:1.10.6")
}

```
```groovy
dependencies {
…
 implementation("com.capillarytech:hydra-richnotification:1.10.6")
}
```