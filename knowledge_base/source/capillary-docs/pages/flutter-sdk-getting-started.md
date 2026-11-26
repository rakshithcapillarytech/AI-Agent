---
updatedAt: 2026-11-12T06:11:18.000Z
agentTools:
  projectIndex: https://docs.capillarytech.com/llms.txt
---

# Getting Started

This document helps you integrate the [`capillary_hydra`](https://pub.dev/packages/capillary_hydra) Flutter plugin package, published on pub.dev, in your Flutter apps.

# Prerequisites

| Platform    | Version                 |
| ----------- | ----------------------- |
| **Flutter** | >= 3.3.0 (Dart >= 3.0)  |
| **iOS**     | >= 15.0                 |
| **Android** | >= API 23 (Android 6.0) |

Before you get started, you need to register your app with the Capillary apps team. For registration, you need to provide these credentials:

* Bundle id for your iOS App
* ApplicationId for your Android App
* App signature (SHA256) from your Android app signing report

When you provide these credentials to our apps team, they will register the app with our system and provide you these details:

* Account Id
* Base url (End point)
* SSL public key

**If you plan to use the Anonymous/Visitor Flow**, you will additionally need this detail from the apps team:

* Org Id

**If you plan to use Gamification** (banners, embeds, loyalty widgets), you will additionally need these details from the apps team:

* Gamification Key
* Gamification Region
* Gamification Base Url

# Getting Started

1. Register your app on Firebase by following [this link](https://support.google.com/appsheet/answer/10104995?hl=en). Download `google-services.json` and `GoogleService-Info.plist`. Don't make any code changes suggested while generating these files.

2. It's mandatory to get Account Id, SSL public key, Base Url (End point), and Remote log level from a remote configuration tool (CMS tool). By default the SDK fetches these from Firebase Remote Config — add these 4 parameters in the Firebase console with these exact names:

   * `hydra_account_id`
   * `hydra_base_url`
   * `hydra_ssl_public_key`
   * `hydra_remote_log_level`

   **If you also want to use the Anonymous/Visitor Flow**, add this parameter:

   * `hydra_org_id`

   **If you also want to use Gamification**, add these 3 parameters:

   * `hydra_gamification_key`
   * `hydra_gamification_region`
   * `hydra_gamification_base_url`

   If your app uses more than one Hydra account (e.g. one per region), see [Multi-Hydra account setup](https://docs.capillarytech.com/docs/flutter-sdk-advanced-setup#multi-hydra-account-setup) for how to add a key set per account.

   You can also use other CMS tools, or pass the values directly. In that case, use a different initializer on iOS and Android — see [Other initializers](https://docs.capillarytech.com/docs/flutter-sdk-advanced-setup#other-initializers). The Remote log level can be set from 0 to 5, more details in [HydraLogLevel](https://docs.capillarytech.com/docs/flutter-sdk-api-reference#hydraloglevel).

3. There's an example app on the [`capillary_hydra` pub.dev page](https://pub.dev/packages/capillary_hydra/example) you can refer to while integrating.