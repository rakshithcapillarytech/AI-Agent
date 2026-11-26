---
updatedAt: 2026-11-12T09:54:09.000Z
agentTools:
  projectIndex: https://docs.capillarytech.com/llms.txt
---

# Configure Notification Center

This page provides information about notification center and how to configure it.

The Notification Center is a feature in the SDK that provides a central place for users to view and manage all of their push notifications. The Notification Center is a UI element that is displayed within the app. It contains a list of all of the push notifications that the user has received. The user can tap on a notification to open the corresponding app.

The Notification Center helps with the following:

* **Centralized Management:** Users access a centralized hub for all push notifications, ensuring organization and control over their app interactions.
* **Enhanced Accessibility:** Notifications are no longer buried in cluttered bars; users can manage them efficiently, leading to a seamless experience.
* **Increased Engagement:** Clear and accessible notifications promote active engagement, allowing users to respond promptly to social interactions, promotions, and achievements.
* **Improved customer satisfaction:** The Notification Center will help to improve customer satisfaction by making the app more useful and engaging
* **Metrics**: Enables to track the number of users who open the Notification Center, the number of push notifications that are viewed in the Notification Center, and the number of push notifications that are deleted from the Notification Center

  ## Use Case: Retail Loyalty Program

  **Scenario:**\
  A retail company operates a loyalty program where customers earn points for each purchase. This program offers exclusive promotions and discounts to reward loyal customers. The app sends push notifications to users, notifying them of earned points and offering special discounts.
  **Issue:**
  Many users miss out on these discounts due to cluttered notification bars filled with messages from various apps. They frequently clear their notification bars without noticing the discounts, resulting in missed opportunities.
  **Solution:**
  Introducing a Notification Center within the app resolves this issue. Users can conveniently access all loyalty program notifications in one location. Here, they can easily view their accumulated points and available discounts. This streamlined approach enhances user engagement and loyalty.

# Installing notification center

You can install the notification center using (a) Version catalog or (b) Artifact.

## Installing using version catalog

1. Configure version catalog. For more information, see [Configure version catalog](https://docs.capillarytech.com/docs/installing-sdk#/installing-with-version-catalog).
2. Add the dependency in the `app/build.gradle` file:

```groovy
dependencies {
…
 implementation("hydra.inbox.core")
 implementation("hydra.inbox.ui")
}

```

## Installing directly using artifact

Add the following dependency in the `app/build.gradle file`:

```groovy
dependencies {  
…  
 implementation("com.capillarytech:hydra-inbox-core:1.10.6")  
 implementation("com.capillarytech:hydra-inbox-ui:1.10.6")  
}
```

# Setting up fallback images for the notification center

During the initiation of the SDK, the application should define a <Glossary>Fallback image</Glossary> using the provided configuration. This image will display if the SDK encounters issues while downloading the image from a specific notification's payload.

Create an instance of the `NotificationCenterConfig`

```kotlin
NotificationCenterConfig(@DrawableRes val defaultImage: Int)
```
```java
public class NotificationCenterConfig {
    private int defaultImage;

    public NotificationCenterConfig(int defaultImage) {
        this.defaultImage = defaultImage;
    }

    public int getDefaultImage() {
        return defaultImage;
    }
}
```

| Parameter    | Type | Description                                | Mandatory/Optional |
| ------------ | ---- | ------------------------------------------ | ------------------ |
| defaultImage | int  | Resource ID of the fallback drawable image | Mandatory          |

Define the below configuration while initializing the SDK:

```kotlin
val hydraConfig = HydraConfig.Builder(
   applicationContext,
   accountId = "123"
)
   .notificationCenterConfig(NotificationCenterConfig(R.drawable.notification_center_fallback))
.build()

HydraAPI.instanceWithConfig(applicationContext, hydraConfig)
```
```java
HydraConfig hydraConfig = new HydraConfig.Builder(
    applicationContext,
    "123"
)
    .notificationCenterConfig(new NotificationCenterConfig(R.drawable.notification_center_fallback))
    .build();

HydraAPI.instanceWithConfig(applicationContext, hydraConfig);
```

# Integrating the default notification center

When your app integrates the HydraInboxCore and HydraInboxUI frameworks, you can opt to use the default notification Center UI by either launching the SDK-provided Activity or including the provided Fragment.

## Using activity

The activity is preconfigured within the SDK's manifest file and can be initiated using the code snippet below.

```kotlin
val inboxActivity = Intent(this, InboxActivity::class.java)  
startActivity(inboxActivity)
```
```java
Intent inboxActivity = new Intent(this, InboxActivity.class);
startActivity(inboxActivity);

```

## Using fragment

To incorporate the InboxFragment provided by the SDK into your app's activity, follow these steps. For information on adding a Fragment to an Activity, refer to the [Google documentation on Fragments](https://developer.android.com/guide/fragments).

**Example:**

```kotlin
private fun attachFragment() {  
   try {  
       supportFragmentManager.beginTransaction().replace(  
           R.id.hydraInboxFragmentFrameLayout,  
           InboxFragment(),  
           "inboxFragment"  
       ).commit()  
   } catch (e: Exception) {  
       Logger.v("loadInboxMessageFragment(): ")  
   }  
}
```
```java
private void attachFragment() {
    try {
        getSupportFragmentManager()
            .beginTransaction()
            .replace(
                R.id.hydraInboxFragmentFrameLayout,
                new InboxFragment(),
                "inboxFragment"
            )
            .commit();
    } catch (Exception e) {
        Logger.v("loadInboxMessageFragment(): ");
    }
}

```

# API Usage - HydraInboxCore

The **HydraInboxCore** API provides various functions to interact with notifications and messages using the instance of **InboxCore**.

## 1. getUnreadNotificationCount

Use this API to retrieve the count of unread notifications using the instance of **InboxCore**.

### Method:

**Kotlin:**

```kotlin
fun getUnReadMessagesCount(
    context: Context,
    listener: UnReadCountListener
)
```
```java
public void getUnReadMessagesCount(
    Context context,
    UnReadCountListener listener
)
```

#### Parameters:

| Parameter | Type                | Description        | Mandatory/Optional |
| --------- | ------------------- | ------------------ | ------------------ |
| context   | Context             | Activity’s Context | Mandatory          |
| listener  | UnReadCountListener | Listener's Object  | Mandatory          |

### Implementation:

```kotlin
HydraInboxCoreApi.getInstance().getUnReadMessagesCount(
    this,
    object : UnReadCountListener {
        override fun onCountAvailable(unReadMessagesCount: Int) {
            // Handle the unread message count
        }
    }
)
```
```java
HydraInboxCoreApi.getInstance().getUnReadMessagesCount(
    this,
    new UnReadCountListener() {
        @Override
        public void onCountAvailable(int unReadMessagesCount) {
            // Handle the unread message count
        }
    }
);
```

## 2. fetchInboxMessages

This API fetches available notifications for the current user using the instance of **InboxCore**.

### Method:

```kotlin
fun fetchInboxMessages(
    context: Context,
    listener: OnMessagesAvailableListener
)
```
```java
public void fetchInboxMessages(
    Context context,
    OnMessagesAvailableListener listener
)
```

#### Parameters:

| Parameter | Type                        | Description        | Mandatory/Optional |
| --------- | --------------------------- | ------------------ | ------------------ |
| context   | Context                     | Activity’s Context | Mandatory          |
| listener  | OnMessagesAvailableListener | Listener's Object  | Mandatory          |

## 3. deleteInboxMessages

Use this API to delete an inbox message using the instance of **InboxCore**.

### Method:

```kotlin
fun deleteInboxMessage(
    context: Context,
    inboxMessage: InboxMessage
)
```
```java
public void deleteInboxMessage(
    Context context,
    InboxMessage inboxMessage
)
```

#### Parameters:

| Parameter    | Type         | Description                     | Mandatory/Optional |
| ------------ | ------------ | ------------------------------- | ------------------ |
| context      | Context      | Activity’s Context              | Mandatory          |
| inboxMessage | InboxMessage | Object of the message to delete | Mandatory          |

## 4. trackInboxMessageClick

This API sends a Dlr event indicating that the user has clicked an inbox message using the instance of **InboxCore**.

### Method:

```kotlin
fun trackInboxMessageClick(
    context: Context,
    inboxMessage: InboxMessage
)
```
```java
public void trackInboxMessageClick(
    Context context,
    InboxMessage inboxMessage
)
```

#### Parameters:

| Parameter    | Type         | Description                   | Mandatory/Optional |
| ------------ | ------------ | ----------------------------- | ------------------ |
| context      | Context      | Activity’s Context            | Mandatory          |
| inboxMessage | InboxMessage | Object of the clicked message | Mandatory          |

## 5. deleteAllInboxMessages

This API deletes all inbox messages for the current user using the instance of **InboxCore**.

### Method:

```kotlin
fun deleteAllInboxMessages(
    context: Context
)
```
```java
public void deleteAllInboxMessages(
    Context context
)
```

#### Parameters:

| Parameter | Type    | Description        | Mandatory/Optional |
| --------- | ------- | ------------------ | ------------------ |
| context   | Context | Activity’s Context | Mandatory          |

# Configuring inbox message listeners

**InboxMessageListeners**

To receive callbacks for inbox messages, listeners should be added in the *onCreate()* of the Application class. Hydra offers the following listeners to hook into:\
**Inbox Message Callback**
Application has to register an `InboxMessageListener` to receive in-app message Callbacks.

> 📘 It is mandatory to add this listener once the hydra sdk is initialized to avail custom action for inbox message click.

To get the inbox message callback implement the OnMessageClickListener and register for the callback using HydraInboxUIHelper.getInstance().registerOnMessageClickListener

**Example:** User implementing **OnMessageClickListener** to receive the inbox message callback from the Hydra SDK.

```kotlin
class ApplicationMessageClickListener : OnMessageClickListener {  
  override fun onMessageClick(context: Context, inboxMessage: InboxMessage): Boolean {  
       return super.onMessageClick(context, cta)  
   }  
}
```
```java
public class ApplicationMessageClickListener implements OnMessageClickListener {
    @Override
    public boolean onMessageClick(Context context, InboxMessage inboxMessage) {
        return super.onMessageClick(context, inboxMessage);
    }
}
```

Register the above callback in the onCreate of your application class after initialization of HydraApi

In the above callback method, “onMessageClick” returns Boolean to which application can return either true or false. If the function returns false, the action will be taken by the SDK and if returned true then custom action can be taken by the client app.

```kotlin
HydraInboxUIHelper.getInstance()
   .registerOnMessageClickListener(ApplicationMessageClickListener())
```
```java
HydraInboxUIHelper.getInstance()
   .registerOnMessageClickListener(new ApplicationMessageClickListener());
```

<br />

***

# Customizing default notification center

The SDK provides various UI customization options to ensure the notification center seamlessly integrates with the overall app design.

## Inheriting app theme:

The notification center (InboxActivity) automatically inherits your app's default theme for a cohesive look.\
For example, if your application is configured with the following theme:

```xml
<style name="Theme.XYZ" parent="Theme.MaterialComponents.DayNight.NoActionBar">
   <!-- Primary brand color. -->
   <item name="colorPrimary">@color/purple_500</item>
   <item name="colorPrimaryVariant">@color/purple_700</item>
   <item name="colorOnPrimary">@color/white</item>
   <!-- Secondary brand color. -->
   <item name="colorSecondary">@color/teal_200</item>
   <item name="colorSecondaryVariant">@color/teal_700</item>
   <item name="colorOnSecondary">@color/white</item>
   <!-- Status bar color. -->
   <item name="android:statusBarColor">?attr/colorPrimaryVariant</item>
   <item name="android:windowBackground">@android:color/white</item> …. </style>

```

Then, your app will feature a white window background and a purple app bar, resulting in an appearance similar to the screenshots provided below:

<Image align="center" className="border" border={true} src="https://files.readme.io/951aa73-Default_theme.png" />

With the UI customization options, you can override this style and customize various UI elements.

## Customization options:

You can customize various UI elements by overriding specific styles in your app's resources:

### Customizing toolbar style

* To customize the title and navigation icon in the toolbar, override the InboxToolbarStyle with the following customization:

```xml
<style name="HydraInboxToolbarStyle" parent="Theme.AppCompat">
   <item name="android:textColorSecondary">@color/hydra_inbox_toolbar_text_color</item>
   <item name="android:textColorPrimary">@color/hydra_inbox_toolbar_text_color</item>
   <item name="android:fontFamily">@font/roboto</item>
   <item name="android:textSize">@dimen/hydra_inbox_toolbar_font_size</item>
   <item name="android:textStyle">bold</item>
   <item name="android:background">@color/hydra_inbox_toolbar_background_color</item>
   <item name="android:navigationIcon">@drawable/ic_menu_black_24dp</item>
</style>

```

* To customize the unread messages count in the toolbar, override the InboxToolbarTextStyle with the following customization:

```xml
<style name="HydraInboxToolbarTextStyle">
   <item name="android:textColor">@color/hydra_inbox_toolbar_text_color</item>
   <item name="android:fontFamily">@font/roboto</item>
   <item name="android:textSize">@dimen/hydra_inbox_toolbar_font_size</item>
   <item name="android:textStyle">bold</item>
</style>

```

* To customize the "CLEAR ALL" button in the toolbar, override the InboxToolbarButtonStyle with the following customization:
* ```xml
  <style name="HydraInboxToolbarButtonStyle">
     <item name="android:textColor">@color/hydra_inbox_toolbar_button_color</item>
     <item name="android:fontFamily">@font/roboto</item>
     <item name="android:textSize">@dimen/hydra_inbox_toolbar_button_size</item>
     <item name="android:textStyle">normal</item>
  </style>

  ```

### Customizing inbox message style

Any message displayed in the notification center can be in either the unread state or the read state. To distinguish between the two, the SDK provides distinct styles for each entity as follows:

### Background color:

**Unread state:**

```xml
<color name="hydra_unread_message_background_color">#FFFFFF</color>

```

**Read state:**

```xml
<color name="hydra_read_message_background_color">#FFFFFF</color>
```

### Title style:

**Unread state:**

```xml
<style name="HydraUnReadInboxTitleTextStyle">
   <item name="android:textSize">@dimen/hydra_inbox_title_font_size</item>
   <item name="android:textColor">@color/hydra_inbox_title_color</item>
   <item name="android:fontFamily">@font/roboto</item>
   <item name="android:textStyle">bold</item>
   <item name="android:maxLines">2</item>
</style>
```

**Read state:**

```xml
<style name="HydraReadInboxTitleTextStyle">
   <item name="android:textSize">@dimen/hydra_inbox_title_font_size</item>
   <item name="android:textColor">@color/hydra_inbox_title_color</item>
   <item name="android:fontFamily">@font/roboto</item>
   <item name="android:textStyle">normal</item>
   <item name="android:maxLines">2</item>
</style>
```

### Summary style:

**Unread state:**

```xml
<style name="HydraUnReadInboxMessageTextStyle">
   <item name="android:textSize">@dimen/hydra_inbox_message_font_size</item>
   <item name="android:textColor">@color/hydra_inbox_message_color</item>
   <item name="android:fontFamily">@font/roboto</item>
   <item name="android:textStyle">bold</item>
   <item name="android:maxLines">3</item>
</style>
```

**Read state:**

```xml
<style name="HydraReadInboxMessageTextStyle">
   <item name="android:textSize">@dimen/hydra_inbox_message_font_size</item>
   <item name="android:textColor">@color/hydra_inbox_message_color</item>
   <item name="android:fontFamily">@font/roboto</item>
   <item name="android:textStyle">normal</item>
   <item name="android:maxLines">3</item>
</style>
```

### Timestamp style:

**Unread state:**

```xml
<style name="HydraUnReadInboxMessageTimeStyle">
   <item name="android:textSize">@dimen/hydra_inbox_time_font_size</item>
   <item name="android:textColor">@color/hydra_inbox_time_color</item>
   <item name="android:fontFamily">@font/roboto</item>
   <item name="android:textStyle">bold</item>
</style>
```

**Read state:**

```xml
<style name="HydraReadInboxMessageTimeStyle">
   <item name="android:textSize">@dimen/hydra_inbox_time_font_size</item>
   <item name="android:textColor">@color/hydra_inbox_time_color</item>
   <item name="android:fontFamily">@font/roboto</item>
   <item name="android:textStyle">bold</item>
</style>
```

### Customizing empty box style

To customize the appearance of the empty text box view when no notifications are available, override the InboxEmptyBoxTextStyle with the following customization:

```xml
<style name="HydraInboxEmptyBoxTextStyle">
   <item name="android:background">@color/hydra_inbox_transparent_color</item>
   <item name="android:textSize">@dimen/hydra_inbox_empty_box_text_size</item>
   <item name="android:textColor">@color/hydra_inbox_empty_box_message_color</item>
   <item name="android:fontFamily">@font/roboto</item>
   <item name="android:textStyle">normal</item>
</style>
```