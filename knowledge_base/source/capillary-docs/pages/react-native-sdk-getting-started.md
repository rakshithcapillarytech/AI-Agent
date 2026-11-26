---
updatedAt: 2026-11-12T06:08:47.000Z
agentTools:
  projectIndex: https://docs.capillarytech.com/llms.txt
---

# Getting Started

To use the Capillary Engagement platform on a React Native application, you need to set up the React Native Wrapper using the Native Hydra Android and iOS SDKs.

# Prerequisites

Before you start the integration, ensure you have the following prerequisites met:

| Platform         | Version                       |
| ---------------- | ----------------------------- |
| **React Native** | 0.77.0 or later               |
| **iOS**          | 15.0 or later                 |
| **Android**      | API 21 (Android 5.0) or later |
| **Node.js**      | 18.0.0 or later               |
| **targetSdk**    | 31 or later                   |
| **compileSdk**   | 31 or later                   |

* [ ] Register your application with the Capillary apps team by providing the following:

  * `Bundle Id` for your iOS app
  * `ApplicationId` for your Android app
  * App signature (SHA256) from your Android app signing report\
    After registering with the Capillary apps team, you will be provided the Account ID, base URL (endpoint), and SSL public key.

  If you plan to use the Anonymous/Visitor Flow, the apps team also provides:

  * Org Id

  If you plan to use Gamification (banners, embeds, loyalty widgets), the apps team also provides:

  * Gamification Key
  * Gamification Region
  * Gamification Base Url

* [ ] Set up Firebase for push notifications:
  * Register your application on Firebase. To register, refer to this [guide](https://support.google.com/appsheet/answer/10104995?hl=en).

  * Download the `google-services.json` file for Android and the `GoogleService-Info.plist` file for iOS from your Firebase project. Do not make any code changes suggested by Firebase at this stage.
  > 📘 Note
  >
  > You don't need Firebase if you don't use push notifications. To run Hydra without Firebase, see [Using Hydra without Firebase](https://docs.capillarytech.com/docs/react-native-sdk-advanced-setup#using-hydra-without-firebase) for the steps to skip.

* [ ] Get the Account ID, base URL (End point), SSL public key and Remote log level from the remote configuration tool (CMS tool).
  * **Using Firebase Remote Config:** Initialisers for iOS and Android are provided to fetch these parameters from the Firebase Remote Config. If you choose this method, add the following four parameters in the Firebase console. The names of these parameters must match exactly:

    * hydra\_account\_id
    * hydra\_base\_url
    * hydra\_ssl\_public\_key
    * hydra\_remote\_log\_level

    If you also want to use the Anonymous/Visitor Flow, add this parameter:

    * hydra\_org\_id

    If you also want to use Gamification, add these three parameters:

    * hydra\_gamification\_key
    * hydra\_gamification\_region
    * hydra\_gamification\_base\_url

    If your app uses more than one Hydra account, for example one for each region, see [Multi-Hydra account setup](https://docs.capillarytech.com/docs/react-native-sdk-advanced-setup#multi-hydra-account-setup) to add a set of keys for each account.
  * **Using other CMS tools:** If you prefer a different CMS tool, you must use alternative initialisers in iOS and Android. For details, see [Installing iOS SDK](https://docs.capillarytech.com/docs/react-native-sdk-install#installing-ios-sdk), [Installing Android SDK](https://docs.capillarytech.com/docs/react-native-sdk-install#installing-android-sdk), and [Other initializers](https://docs.capillarytech.com/docs/react-native-sdk-advanced-setup#other-initializers). Set the remote log level to a value from 0 to 5. For details, see [HydraLogLevel](https://docs.capillarytech.com/docs/react-native-sdk-api-reference#hydraloglevel).

# Sample app

Clone the examples demonstrating how to use the package in projects with different React Native versions and architectures from the following branches of the [react-native-hydra-lib](https://github.com/Capillary/react-native-hydra-lib)  repository:

* example\_rn72\_new\_arch
* example\_rn72\_old\_arch
* example\_rn74\_old\_arch
* example\_rn75\_old\_arch
* example\_rn76\_new\_arch
* example\_rn77\_new\_arch