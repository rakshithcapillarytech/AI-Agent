---
updatedAt: 2026-11-12T11:01:29.000Z
agentTools:
  projectIndex: https://docs.capillarytech.com/llms.txt
---

# Getting Started

This guide provides information on how to integrate your mobile apps with Capillary iOS SDK.

Capillary SDK provides you with essential analytics capabilities and helps you engage better with your users through, [push notifications](https://docs.capillarytech.com/docs/configure-push-notifications) ,  [notification inbox](https://docs.capillarytech.com/update/docs/configure-notification-center_ios#/) and [in-app messaging](https://docs.capillarytech.com/docs/in-app-messaging_ios).

The SDK consists of the following frameworks:

* **HydraCore** - This framework is the base for all other frameworks. The framework provides various infrastructure modules such as network, data persistence and log management, and in addition, also provides API(s) for Analytics(Event) reporting.
* **HydraPushNotification** -This framework helps in the following:
  * Simplifying the integration of push/remote notifications for all Capillary customers
  * Enabling the delivery of notifications
  * Ccapturing and reporting data for analytics
  * Ensuring the posting of DLR (Delivery Receipt) events at all stages.
* **HydraPushNotificationServiceExtension** - This can be integrated with the notification content extension of the host application and enables customising and modifying the original notifications before it is presented to the user.  Its key responsibility is to dynamically update a notification UI based on the payload.
* **HydraInAppMessage** - This enables to display in-app messages using popup notifications.
* **HydraInboxCore** - Manages all remote notifications received by the application and stores them locally to display in the Notification Center.
* **HydraInboxUI** - Populates the Notification Center with all remote notifications received by the application.

# Prerequisites

* iOS SDK version 1.10.6 or above
* Minimum deployment version (iOS): 15.6

# Supported platforms

* Mobile(iOS)
* Tablet(iPadOS)

# iOS SDK Version and Size

| SDK library                           | Version | Size   |
| :------------------------------------ | :------ | :----- |
| HydraCore                             | 1.10.6  | 9.6 MB |
| HydraInAppMessage                     | 1.10.6  | 3.5 MB |
| HydraPushNotification                 | 1.10.6  | 2.1 MB |
| HydraPushNotificationServiceExtension | 1.10.6  | 2.7 MB |
| HydraInboxUI                          | 1.10.6  | 2.4 MB |
| HydraInboxCore                        | 1.10.6  | 1.5 MB |

To integrate your mobile apps with Capillary iOS SDK, perform the following steps:

* [Install SDK](https://docs.capillarytech.com/docs/install-sdk)
* [Initialise SDK](https://docs.capillarytech.com/docs/initialise-ios-sdk)
* [Configure iOS SDK API](https://docs.capillarytech.com/docs/ios-sdk-api-reference)
* [Configure push notifications](https://docs.capillarytech.com/docs/configure-push-notifications)
* [Configure gamification (Experience+)](https://docs.capillarytech.com/docs/gamification-ios)