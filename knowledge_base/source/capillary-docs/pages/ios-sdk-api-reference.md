---
updatedAt: 2026-03-04T06:05:34.000Z
agentTools:
  projectIndex: https://docs.capillarytech.com/llms.txt
---

# API Reference for Event Tracking and User Lifecycle Management

The Capillary iOS SDK APIs provide you with the capability to perform various actions, including customer registrations, customer logins, and more. These APIs can also be used for reporting to track events such as customer registrations, customer logins, and more.

There are 2 types of events:

1. **Standard events** - These events are configured in the SDK and cannot be removed.  With Capillary SDK, you can record user-specific information such as their username, first name, last name, email, mobile number, and other custom information, along with system information, in the events. This information can then be used to run campaigns based on user segregation at different levels.
2. **Behavioural events** - The events resource also allows you to create behavioural events to track any other important user interactions for your business. For example, events such as forgot password, cart abandonment, etc. These events can be further defined by event attributes such as price, quantity, and category. These events need to be configured in your org settings.
   For behavioural events, you need to do configuration in the Hydraconfig and organisation settings.

# User Management and Account Configuration

## Sign In

This API can be used to sign in a user to the platform and report when a user signs in.

```swift
public func reportUserSignIn(data: UserSignInGenerator, customData: Attributes)
```

* `UserSignInGenerator`: This object holds the necessary basic information. You can generate this object by organizing the required information into a suitable container or object that adheres to the `UserSignInGenerator` protocol.
* `customData` (Optional): This allows adding any extra information or custom data associated with the event being reported. The custom data should be added in the format of a`Dictionary<String, Any>`.

| Parameters | Type       | Description                                                      | Mandatory/Optional |
| :--------- | :--------- | :--------------------------------------------------------------- | :----------------- |
| customerId | String     | Unique identifier of the user                                    | Mandatory          |
| firstName  | String     | User first name                                                  | Mandatory          |
| lastName   | String     | User last name                                                   | Mandatory          |
| email      | String     | User email address                                               | Optional           |
| phone      | String     | User mobile number                                               | Mandatory          |
| customData | Dictionary | Additional information associated with the event being reported. | Optional           |

**Example 1:** SignIn event with  empty`customData`parameter.

```swift
let userSignInData = UserDetails(customerId: "customer-id",firstName: "first-name", lastName: "last-name", email: "email@goodemail.com", phone: "xxxxxxxx")
hydraCore.reportUserSignIn(data: userSignInData, customData: [:])
```

**Example 2:** SignIn event with `customData`attributes age and gender. This allows for the logging of specific attributes related to the user's age and gender during the user sign-in report.

```swift
let userSignInData = UserDetails(customerId: "customer-id",firstName: "first-name", lastName: "last-name", email: nil, phone: "xxxxxxxx")
hydraCore.reportUserSignIn(data: userSignInData, customData: [“Age”: “25”, “Gender”: “Male”])
```

**Example 3:** SignIn event with `customData`attributes age, gender and email.

```swift
let userSignInData = UserDetails(customerId: "customer-id",firstName: "first-name", lastName: "last-name", email: "email@goodemail.com", phone: "xxxxxxxx")
hydraCore.reportUserSignIn(data: userSignInData, customData: [“Age”: “25”, “Gender”: “Male”])
```

***

## Sign Up

This API can be used to register a user to the platform and report when a user registers.

```swift
public func reportUserSignUp(data: UserSignUpGenerator, customData: Attributes)
```

* `UserSignUpGenerator`: This object holds the necessary basic information. You can generate this object by organizing the required information into a suitable container or object that adheres to the `UserSignUpGenerator` protocol.
* `customData` (Optional): This allows adding any extra information or custom data associated with the event being reported. The custom data should be added in the format of a`Dictionary<String, Any>`.

| Parameters | Type       | Description                                                      | Mandatory/Optional |
| :--------- | :--------- | :--------------------------------------------------------------- | :----------------- |
| customerId | String     | Unique identifier of the user                                    | Mandatory          |
| firstName  | String     | User first name                                                  | Mandatory          |
| lastName   | String     | User last name                                                   | Mandatory          |
| email      | String     | User email address                                               | Optional           |
| phone      | String     | User mobile number                                               | Mandatory          |
| customData | Dictionary | Additional information associated with the event being reported. | Optional           |

**Example 1:** SignUp event with empty`customData`parameter.

```swift
let userSignUpData = UserDetails(customerId: "customer-id",firstName: "first-name", lastName: "last-name", email: "email@goodemail.com", phone: "xxxxxxxx")
hydraCore.reportUserSignUp(data: userSignUpData, customData: [:])
```

**Example 2:** SignUp event with  `customData`attributes age and gender. This allows for the logging of specific attributes related to the user's age and gender during the user sign-in report.

```swift
let userSignUpData = UserDetails(customerId: "customer-id",firstName: "first-name", lastName: "last-name", email: nil, phone: "xxxxxxxx")
hydraCore.reportUserSignUp(data: userSignUpData, customData: [“Age”: “25”, “Gender”: “Male”])
```

**Example 3:** SignUp event with `customData`attributes age, gender and email.

```swift
let userSignUpData = UserDetails(customerId: "customer-id",firstName: "first-name", lastName: "last-name", email: "email@goodemail.com", phone: "xxxxxxxx")
hydraCore.reportUserSignUp(data: userSignUpData, customData: [“Age”: “25”, “Gender”: “Male”])
```

***

## User profile update

This API can be used to update a user's profile and report when a user has updated their profile.

```swift
public func reportUserProfileUpdate(data: UserProfileUpdateGenerator, customData: Attributes, subscriptions: [Any]? = nil)
```

* `UserProfileUpdateGenerator`: This object holds the necessary basic information. You can generate this object by organizing the required information into a suitable container or object that adheres to the `UserProfileUpdateGenerator` protocol.
* `customData` (Optional): This allows adding any extra information or custom data associated with the event being reported. The custom data should be added in the format of a`Dictionary<String, Any>`.

| Parameters    | Type       | Description                                                      | **Mandatory/Optional** |
| :------------ | :--------- | :--------------------------------------------------------------- | :--------------------- |
| customerId    | String     | Unique identifier of the user                                    | Mandatory              |
| firstName     | String     | User first name                                                  | Optional               |
| lastName      | String     | User last name                                                   | Optional               |
| email         | String     | User email address                                               | Optional               |
| phone         | String     | User mobile number                                               | Optional               |
| customData    | Dictionary | Additional information associated with the event being reported. | Optional               |
| subscriptions | Array      | The subscriptions list for the logged in user.                   | Optional               |

**Example 1:** User profile update event with  empty`customData` parameter.

```swift
let userProfileUpdateData = UserDetails(customerId: "customer-id",firstName: "first-name", lastName: "last-name", email: "email@goodemail.com", phone: "xxxxxxxx")
hydraCore.reportUserProfileUpdate(data: userProfileUpdateData, customData: [:])
```

**Example 2:** User profile update with `customData`attributes age and gender. This allows for the logging of specific attributes related to the user's age and gender during the user sign-in report.

```swift
let userProfileUpdateData = UserDetails(customerId: "customer-id",firstName: "first-name", lastName: "last-name", email: "email@goodemail.com", phone: "xxxxxxxx")
hydraCore.reportUserProfileUpdate(data: userProfileUpdateData, customData: [“Age”: “25”, “Gender”: “Male”])
```

**Example 3:** User profile update event with `subscription` parameter.

```swift
var subscriptions: [HydraSubscription] = []
var subscription: HydraSubscription = HydraSubscription(channel: "EMAIL", priority: "BULK", type: "OPTIN")
 subscriptions.append(subscription)
 subscription = HydraSubscription(channel: "PUSH", priority: "BULK", type: "OPTIN")
 subscriptions.append(subscription)
let userProfileUpdateData = UserDetails(customerId: "customer-id",firstName: "first-name", lastName: "last-name", email: "email@goodemail.com", phone: "xxxxxxxx")
hydraCoreSDK.reportUserProfileUpdate(data: userProfileUpdateData, customData: [:], subscriptions: subscriptions)
```

***

## Sign Out

This API can be used to sign out a user and report when a user has signed out.

```swift
public func reportUserSignOut(customData: [String: Any])
```

To log sign-out events, you can call the API without providing any data. This action removes all the user-related basic information, such as first name and mobile number, that was previously provided in the session.

**Example**

```swift
hydraCore.reportUserSignOut(customData: [:])
```

***

# User Event Tracking

These events can be used to track user actions throughout the application. These events are valid only if the SDK receives the `SignIn` or `SignUp `events. Events are Invalid if they are called after a `SignOut` event. In order to track these events, users have to pass event names (NotNull or NonEmpty) and attributes (optional).

The API below enables the application to send the custom events:

```swift
public func reportBehavioralEvent(name: String, customAttributes attributes: Attributes) 
```

| Parameter   | Type       | Description                              | Mandatory/Optional |
| :---------- | :--------- | :--------------------------------------- | :----------------- |
| event\_name | String     | Name of the event                        | Compulsory         |
| attributes  | Dictionary | The custom attributes map for the events | Optional           |

**Example**:

```swift
hydraCore.reportBehavioralEvent(name: "event-name",
                                                        customAttributes: ["additional-info" : "additional-details",
                                                                                      ["additional-info" : "additional-details"])
```

***

<br />