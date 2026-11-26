---
updatedAt: 2026-03-25T09:19:20.000Z
agentTools:
  projectIndex: https://docs.capillarytech.com/llms.txt
---

# API Reference for Event Tracking and User Lifecycle Management

The Capillary Android SDK APIs provide you with the capability to perform various actions, including customer registrations, customer logins, and more. These APIs can also be used for reporting to track events such as customer registrations, customer logins, and more.

There are 2 types of events:

1. **Standard events** - These events are configured in the SDK and cannot be removed.  With Capillary SDK, you can record user-specific information such as their username, first name, last name, email, mobile number, and other custom information, along with system information, in the events. This information can then be used to run campaigns based on user segregation at different levels.
2. **Behavioural events** - The events resource also allows you to create behavioural events to track any other important user interactions for your business. For example, events such as forgot password, cart abandonment etc. These events can be further defined by event attributes such as price, quantity, and category. These events need to be configured in your org settings.
   For behavioural events, you need to do configuration in the Hydraconfig and organisation settings.

# User Management and Account Configuration

The SDK offers four event-tracking APIs for recording for reporting user action events. These APIs enable you to recognize visitors, monitor events, generate events dynamically, and track the activities of users, including any properties that describe their actions. This information can be used to gain insights into user behaviour and create campaigns based on user segmentation at different levels. For example, with the user event data, you can send welcome messages to customers through e-mail or offer different offers based on user age, gender etc.

The SDK has the below standard event tracking APIs:

1. Sign In
2. Sign Up
3. User Update
4. Sign Out

Each user in the app should have a unique identifier (cuid) associated with their account. Provide this identifier whenever a user signs up or signs in. This enables cross-device and cross-platform tracking, leading to improved behavioural and demographic data quality.

### Sign In

This API can be used to sign in a user to the platform and report when a user signs in.

```kotlin
fun pushUserSignin(  
   cuid: String,  
   firstName: String? = null,  
   lastName: String? = null,  
   email: String? = null,  
   phone: String? = null,  
   customData: Map\<String, Any>? = null  
)
```
```java
public void pushUserSignin(String cuid, String firstName, String lastName, String email, String phone, Map<String, Object> customData) {
    // Function body
}
```

| Parameter  | Type   | Description                                            | Optional/Mandatory |
| ---------- | ------ | ------------------------------------------------------ | ------------------ |
| cuid       | String | Identifier for the user, either phone/email/externalId | Mandatory          |
| firstName  | String | First name of the user                                 | Optional           |
| lastName   | String | Last name of the user                                  | Optional           |
| email      | String | Email address of the user                              | Optional           |
| phone      | String | Phone number of the user                               | Optional           |
| customData | Map    | Map of custom attributes for the user                  | Optional           |

**Example:**

1. User push sign-in event to SDK with optional details.
   ```kotlin
   hydraAPI?.pushUserSignin(  
      "9000090000",  
      "Henry",  
      "Williams",  
      "henrywill@gmail.com",  
      "9000090000",  
      mapOf("Age" to "25","Gender" to "Male"))
   ```
   ```java
   if (hydraAPI != null) {
       hydraAPI.pushUserSignin(
           "9000090000",
           "Henry",
           "Williams",
           "henrywill@gmail.com",
           "9000090000",
           Map.of("Age", "25", "Gender", "Male")
       );
   }
   ```
2. User push sign-in event to SDK without optional details.
   ```kotlin
   hydraAPI?.pushUserSignin(  
      "9000090000",  
      "",  
      "",  
      "",  
      "",  
      emptyMap()  
   )
   ```
   ```java
   if (hydraAPI != null) {
       hydraAPI.pushUserSignin(
           "9000090000",
           "",
           "",
           "",
           "",
           Collections.emptyMap()
       );
   }
   ```

### Sign up

This API can be used to register a user to the platform and report when a user registers.

```kotlin
fun pushUserSignup(  
   cuid: String,  
   firstName: String,  
   lastName: String,  
   email: String,  
   phone: String,  
   customData: Map\<String, Any>?,
   subscriptions: List<Any>?
)
```
```java
public void pushUserSignup(String cuid, String firstName, String lastName, String email, String phone, Map<String, Object> customData) {
    // Function body
}
```

| Parameter     | Type   | Description                                                                            | Optional/Mandatory |
| ------------- | ------ | -------------------------------------------------------------------------------------- | ------------------ |
| cuid          | String | phone/email/externalId                                                                 | Mandatory          |
| firstName     | String | User first name                                                                        | Mandatory          |
| lastName      | String | User last Name                                                                         | Mandatory          |
| email         | String | User email address                                                                     | Mandatory          |
| phone         | String | User mobile number                                                                     | Mandatory          |
| customData    | Map    | The attribute map which needs to be set for the user.                                  | Optional           |
| subscriptions | List   | List of subscriptions which include channel, accountId, priority, type and sourcename. | Optional           |

**Example:**

1. User push sign-up event to  SDK with all optional details

   ```kotlin
   hydraAPI?.pushUserSignup(
      "9000090000",
      "Henry",
      "Williams",
      "henrywill@gmail.com",
      "9000090000",
      mapOf("Age" to "25","Gender" to "Male")
   )
   ```
   ```java
   if (hydraAPI != null) {
       hydraAPI.pushUserSignup(
           "9000090000",
           "Henry",
           "Williams",
           "henrywill@gmail.com",
           "9000090000",
           Map.of("Age", "25", "Gender", "Male")
       );
   }

   ```
2. User push sign-up event to  SDK without optional details
   ```kotlin
   hydraAPI?.pushUserSignup(  
      "9000090000",  
      "",  
      "",  
      "",  
      "",  
      emptyMap()  
   )
   ```
   ```java
   if (hydraAPI != null) {
       hydraAPI.pushUserSignup(
           "9000090000",
           "",
           "",
           "",
           "",
           Collections.emptyMap()
       );
   }
   ```

### User update

This API can be used to update a user's profile and report when a user has updated their profile.

```kotlin
fun pushUserUpdate(  
   cuid: String,  
   firstName: String? = null,  
   lastName: String? = null,  
   email: String? = null,  
   phone: String? = null,  
   customData: Map\<String, Any>? = null  
)
```
```java
public void pushUserUpdate(String cuid, String firstName, String lastName, String email, String phone, Map<String, Object> customData) {
    // Function body
}
```

| Parameter  | Type   | Description                                          | Optional/Mandatory |
| ---------- | ------ | ---------------------------------------------------- | ------------------ |
| cuid       | String | phone/email/externalId                               | Mandatory          |
| firstName  | String | User first Name                                      | Optional           |
| lastName   | String | User Last Name                                       | Optional           |
| email      | String | User Email address                                   | Optional           |
| phone      | String | User mobile number                                   | Optional           |
| customData | Map    | The attribute map which needs to be set for the user | Optional           |

**Example:**

1. User push update event to SDK with optional details
   ```kotlin
   hydraAPI?.pushUserUpdate(  
      "9000090000",  
      "Henry",  
      "Williams",  
      "henrywill@gmail.com",  
      "9000090000",  
      mapOf("Age" to "25","Gender" to "Male")  
   )
   ```
   ```java
   if (hydraAPI != null) {
       hydraAPI.pushUserUpdate(
           "9000090000",
           "Henry",
           "Williams",
           "henrywill@gmail.com",
           "9000090000",
           Map.of("Age", "25", "Gender", "Male")
       );
   }
   ```
2. User push update event to  SDK without optional details
   ```kotlin
   hydraAPI?.pushUserUpdate(  
      "9000090000",  
      "",  
      "",  
      "",  
      "",  
      emptyMap()  
   )
   ```
   ```java
   if (hydraAPI != null) {
       hydraAPI.pushUserUpdate(
           "9000090000",
           "",
           "",
           "",
           "",
           Collections.emptyMap()
       );
   }
   ```

### Sign out

This API can be used to sign out a user and report when a user has signed out.

To log sign-out events, only the cuid is required. You can use the cuid to erase all previously logged user information such as firstName, mobile, etc.

**API function:**

```kotlin
fun pushUserSignOut(  
 cuid: String  
)
```
```java
public void pushUserSignOut(String cuid) {
    // Function body
}
```

| Parameter | Type   | Description            | Optional/Mandatory |
| --------- | ------ | ---------------------- | ------------------ |
| cuid      | String | phone/email/externalId | Mandatory          |

**Example:**

```kotlin
hydraAPI?.pushUserSignOut(  
   "9000090000",  
)
```
```java
if (hydraAPI != null) {
    hydraAPI.pushUserSignOut("9000090000");
}
```

### Pass user preferences

This API allows the application to track user preferences by passing settings in a User Preference object with the necessary information.

**API function:**

```kotlin
fun passUserPreferences(cuid: String,   userPreference: UserPreferences)
```

**Example:**

```kotlin
hydraAPI?.passUserPreferences(
   "9000090000", UserPreferences(promOpted, transOpted)
)
```
```java
public void passUserPreferences(String cuid, UserPreferences userPreference) {
    // Function body
}
```

#### Parameters

| Parameter        | Type   | Description                                                                       | Optional/Mandatory |
| :--------------- | :----- | :-------------------------------------------------------------------------------- | :----------------- |
| `cuid`           | String | Customer ID (phone/email/externalId). If null, uses the stored CUID from sign-in. | Optional           |
| `userPreference` | Object | Object containing `promPushOpted` and `transPushOpted` boolean values.            | Mandatory          |

##### UserPreferences Object

The `userPreferences` object contains two boolean properties:

| Property         | Type    | Description                                                                                                                                                                                |
| :--------------- | :------ | :----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `promPushOpted`  | Boolean | **Promotional Push Opt-in**: Set to `true` if user wants to receive promotional push notifications (marketing campaigns, offers, discounts). Set to `false` to opt out.                    |
| `transPushOpted` | Boolean | **Transactional Push Opt-in**: Set to `true` if user wants to receive transactional push notifications (order confirmations, shipping updates, account alerts). Set to `false` to opt out. |

# User Event Tracking

These events can be used to track user actions throughout the application. These events are valid only if the SDK receives the `SignIn` or `SignUp `events. Events are Invalid if they are called after a `SignOut` event. In order to track these events, users have to pass event names (NotNull or NonEmpty) and attributes (optional).

## Creating behavioural events

You need to create the desired behavioural events in the org settings.

1. Navigate to  **Organisation settings > Master Data Management > Data Model > Behavioural events** and create desired behaviour events. For more information, see [Set behavioural events](https://docs.capillarytech.com/docs/behavioral-events).

<Image align="center" border={true} src="https://files.readme.io/ab478d0-Custom_event.png" className="border" />

> 📘 These events enable tracking user actions within the application and are only valid if the user has signed in or signed up with Capillary SDK.

## Adding behavioural events in Hydraconfig

The events that you created in the org settings need to be configured in the `HydraConfig` to send the events to the SDK.

**API function:**

```kotlin
fun pushEvent(  
   eventName: String,  
   attributes: Map\<String, Any>? = null  
)
```
```java
public void pushEvent(String eventName, Map<String, Object> attributes) {
    // Function body
}
```

| Parameter   | Type   | Description                                           | Mandatory/Optional |
| :---------- | :----- | :---------------------------------------------------- | :----------------- |
| event\_name | String | Event name                                            | Mandatory          |
| attributes  | Map    | The attribute map which needs to be set for the event | Optional           |

**Example:**

1. Review events to the SDK
   ```kotlin
   HydraAPI.getDefaultInstance(context = this)!!.pushEvent(
       "productReviewedMapp",
       mapOf(
           "event_name" to "productReviewedMapp",
           "customerId" to AppSharedPreferences.getInstance()
               .getStringSharedPreference(Constants.Pref.MOBILE_NUMBER, "null"),
           "customerReview"  to review,
           "productName" to productName
       )
   )
   ```
   ```java
   HydraAPI.getDefaultInstance(this).pushEvent(
       "productReviewedMapp",
       new HashMap<String, Object>() {{
           put("event_name", "productReviewedMapp");
           put("customerId", AppSharedPreferences.getInstance()
               .getStringSharedPreference(Constants.Pref.MOBILE_NUMBER, "null"));
           put("customerReview", review);
           put("productName", productName);
       }}
   );
   ```
2. Remove from cart event to SDK
   ```kotlin
   HydraAPI.getDefaultInstance(this@CartPageActivity)?.pushEvent(
       "removedFromCart",
       mapOf(
           "price" to clickedItem.amount,
           "skuCode" to clickedItem.sku,
           "quantity" to clickedItem.qty,
           "customerId" to AppSharedPreferences.getInstance().getStringSharedPreference(Constants.Pref.MOBILE_NUMBER,"null"),
           "event_name" to "removedFromCart"
       )
   )
   ```
   ```java
   HydraAPI.getDefaultInstance(this).pushEvent(
       "removedFromCart",
       new HashMap<String, Object>() {{
           put("price", clickedItem.getAmount());
           put("skuCode", clickedItem.getSku());
           put("quantity", clickedItem.getQty());
           put("customerId", AppSharedPreferences.getInstance().getStringSharedPreference(Constants.Pref.MOBILE_NUMBER, "null"));
           put("event_name", "removedFromCart");
       }}
   );
   ```
3. Page/Activity events to SDK

   ```kotlin
   hydraAPI?.pushEvent("Page/Activity successfully opened")
   ```
   ```java
   if (hydraAPI != null) {
       hydraAPI.pushEvent("Page/Activity successfully opened");
   }
   ```
4. Click events with some attributes to SDK
   ```kotlin
   hydraAPI?.pushEvent("button Click",
   mapOf("Username" to "Henry", "Age" to "25", "Gender" to "Male")
   )
   ```
   ```java
   if (hydraAPI != null) {
       hydraAPI.pushEvent("button Click",
           Map.of("Username", "Henry", "Age", "25", "Gender", "Male")
       );
   }
   ```
5. Customer cart details to SDK
   ```kotlin
   hydraAPI.pushEvent("add to cart",  
   mapOf("Book" to "Rich Dad Poor Dad", "Phone" to "Realme 10", "Earphones" to "Sony Earbuds")  
   )
   ```
   ```java
   hydraAPI.pushEvent(
       "add to cart",
       Map.of("Book", "Rich Dad Poor Dad", "Phone", "Realme 10", "Earphones", "Sony Earbuds")
   );
   ```

## Enable console log

Use this API to initialise Hydra’s console logger if the SDK initialises after app startup.

**API function:**

```kotlin
HydraAPI.initializeConsoleLogger(LogType.Debug)
```

| Parameter (parameters marked with \* are mandatory) | Type    | Description |
| :-------------------------------------------------- | :------ | :---------- |
| logLevel\*                                          | LogType | Log level   |

# Handling alarm permissions

Use this API to check if your app currently has the user’s permission to schedule alarms. If not, ask the user for permission and retrieve the current status of the alarm permission.

```kotlin Check if exact alarms are available
val canSchedule = AlarmPermissionUtils.canScheduleExactAlarms(context)
```
```kotlin Request exact alarm permission (Android 12+)
AlarmPermissionUtils.requestExactAlarmPermission(context)
```
```kotlin Log current permission status for debugging
AlarmPermissionUtils.logExactAlarmStatus(context)
```
```kotlin Check if exact alarms are supported but not granted
if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.S) {
    if (!AlarmPermissionUtils.canScheduleExactAlarms(context)) {
        // Optionally guide users to grant permission for better carousel timing
        AlarmPermissionUtils.requestExactAlarmPermission(context)
    }
}
```