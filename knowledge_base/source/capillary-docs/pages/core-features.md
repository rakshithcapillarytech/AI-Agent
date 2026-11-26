---
updatedAt: 2026-03-04T06:05:34.000Z
agentTools:
  projectIndex: https://docs.capillarytech.com/llms.txt
---

# Core Features

# **Analytics**

The Hydra SDK enables comprehensive tracking of user actions and attributes, allowing you to understand user behavior and segment your audience effectively.

All analytics methods are called on the Hydra instance obtained during initialization (e.g., hydraSDK).

## **Identifying Users (Sign Up / Sign In / Sign Out)**

It’s crucial to identify users when they log in or register to associate events correctly with their profiles.

### User Sign Up:

Call `reportUserSignUP` when a new user registers in your app.

1. Prepare user details

```swift
let userDetails \= UserDetails(
    customerId
    : "new\_user\_123",  // Required: Unique user identifier
      firstName
    : "New",  // Optional
      lastName
    : "User",  // Optional
      email
    : "[new.user@example.com](mailto:new.user@example.com)",  // Optional
      phone
    : "+15551234567")  // Optional
```

2. Add custom attributes (optional)

```swift
let customAttributes : [String:Any] =
                           ["registrationMethod":"Email",
                                "referralSource":"CampaignXYZ"] hydraSDK
                       ?.reportUserSignUP(data
                                          : userDetails, customData
                                          : customAttributes)
                        // IMPORTANT: Also update the SDK's customerId
                        // immediately after sign-up/sign-in
                        hydraSDK
                       ?.update(customerID
                                : "new_user_123")
```

### User Sign In:

Call `reportUserSignIn` when an existing user logs in.

1. Prepare user details (provide known details)

```swift
let userDetails = UserDetails(customerId
                              : "existing_user_456",  // Required
                                firstName
                              : "Existing", lastName
                              : "User", email
                              : "existing.user@example.com", phone
                              : "+15559876543")

```

2. Custom attributes relevant to sign-in (optional)

```swift
// Optional: Custom attributes relevant to sign-in
let customAttributes : [String:Any] = ["loginMethod":"Password"]

                       hydraSDK
                       ?.reportUserSignIn(data
                                          : userDetails, customData
                                          : customAttributes)
```

> ❗️ Note
>
> Update the SDK's customerId immediately after sign-up/sign-in using:
>
> ```
> hydraSDK?.update(customerID: "existing\_user\_456")
> ```

### User Sign Out:

Call reportUserSignOut when a user logs out. This clears the associated user data within the SDK’s context for subsequent events (until the next sign-in/sign-up).

Custom attributes relevant to sign-out (optional)

```swift
let customAttributes: [String: Any] = [
    "reason": "UserInitiated"
]


hydraSDK?.reportUserSignOut(customData: customAttributes)

```

> 📘 Note:
>
> * Update customerID to a guest ID or clear it if necessary using any of the following
>
> ```
> hydraSDK?.update(customerID: "GUEST\_ID")
> ```
> ```
> potentially hydraSDK?.update(customerID: "")
> ```
>
> * The `UserDetails` struct (conforming to `UserDetailsGenerator`) is used to pass user information. Ensure you provide at least the `customerId`.

### **Updating User Profile Attributes**

Use `reportUserProfileUpdate` to send updates to a user’s profile information or custom attributes at any time after they are identified.

1. Prepare updated user details (only include fields that changed or need setting)

```swift
let updatedUserDetails \=
    UserDetails(customerId
                : "existing\_user\_456",  // Required
                  firstName
                : "ExistingUpdated",
                  // lastName, email, phone can be omitted if not changing
                  ...)
```

2. Include any custom attributes to update or add

```
let customAttributes : \[String:Any\] \= \
    ["preferredLanguage":"fr",
             "loyaltyTier":"Gold",
        "lastPurchaseDate":Date()  // Ensure dates are properly formatted if needed  
\]
```

3. Update user subscriptions for example, newsletter opt-in/out (optional)

```
struct MySubscription : Codable{
  let channel : String let type : String  // e.g., "OPTIN" / "OPTOUT"
} let subscriptions : [MySubscription] =
                          [
                            MySubscription(channel
                                           : "EMAIL_NEWSLETTER", type
                                           : "OPTIN"),
                            MySubscription(channel
                                           : "SMS_PROMOTIONS", type
                                           : "OPTOUT")
                          ]

                      hydraSDK
                      ?.reportUserProfileUpdate(
                           data
                           : updatedUserDetails, customData
                           : customAttributes,
                             subscriptions
                           : subscriptions)  // Pass subscriptions if applicable
```

> 📘 Notes
>
> * The structure/format of subscription objects depends on your specific implementation.
> * Ensure the objects conform to Codable/Encodable or are valid JSON types.

### **Tracking Custom Behavioral Events**

Use `reportBehavioralEvent` to track any custom action a user performs within your app. This is essential for understanding engagement and triggering campaigns.

1. Example: Tracking product view
   ```
   let eventName \= "ProductViewed" let attributes : \[String:Any\] \= \
       ["productID":"SKU12345",
           "productName":"Hydra T-Shirt", "category":"Apparel", "price":29.99,
              "currency":"USD"  
   \] hydraSDK
       ?.reportBehavioralEvent(name
                               : eventName, customAttributes
                               : attributes)
   ```
2. Example: Tracking checkout step
   ```
   let checkoutEvent \= "CheckoutStepCompleted" let checkoutAttrs : \
       [String:Any\] \= \["stepNumber":2,
                            "stepName":"ShippingAddress", "cartValue":150.75  
   \] hydraSDK
       ?.reportBehavioralEvent(name
                               : checkoutEvent, customAttributes
                               : checkoutAttrs)
   ```
3. Example: Tracking a simple button click
   ```
   hydraSDK?.reportBehavioralEvent(name: "ShareButtonClicked", customAttributes: \[:\]) 
   //No extra attributes needed
   ```