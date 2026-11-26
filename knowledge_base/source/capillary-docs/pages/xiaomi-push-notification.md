---
updatedAt: 2026-11-12T09:54:09.000Z
agentTools:
  projectIndex: https://docs.capillarytech.com/llms.txt
---

# Xiaomi push notification (Push Amplification)

This page provides you with information on configuring push notifications on Chinese OEM devices.

> **Deprecation Notice:** This page documents the Xiaomi Mi Push integration which is currently deprecated. If you are starting a new integration, contact your Capillary CSM for the recommended push amplification approach.

Push notifications often go undelivered to some app users due to device-level restrictions on certain Chinese OEM devices. The Capillary Android SDK addresses this issue by sending push notifications through both Xiaomi Cloud Push and Firebase Cloud Messaging (FCM) push services, increasing the likelihood of successful delivery. If a message is successfully delivered through one of these push services, the notification from the other cloud service is suppressed. No priority is defined, and there are no changes to the current FCM flow. This ensures that users receive the push notification only once.

To prevent unnecessary additions to the application, separate modules for each push service are available. You can integrate the appropriate module based on the types of devices used by your application's users.

# Integrating Xiaomi Push SDK

Perform the following:

1. Register as a Xiaomi developer on the [Xiaomi website](https://global.developer.mi.com/home).
2. Create app. To create, Log into the console, click **Create App**, enter the required details and click **CREATE**.

   <Image align="center" className="border" border={true} width="60% " src="https://files.readme.io/f0be5dc-Register.png" />
3. Click on the App name and retrieve the app's Package name/App ID / AppKey / App Secret.\
   The App ID and App Key serve as the client's identity during client SDK initialization. The App Secret is authenticated for sending messages on the server-side.

   <Image align="center" className="border" border={true} src="https://files.readme.io/2ba8ea9-package_name.png" />
4. Log into the Mi Push Operational Console and enable Push.
5. Add dependency of the Mi SDK.

   1. Download the Mi SDK.
   2. Add the downloaded Mi SDK to the "libs" folder of the application module in your project.
   3. Include the following configuration in the `build.gradle` file of the app module:

      ```groovy
      android {
          repositories {
              flatDir {
                  dirs 'libs'
              }
          }
      }

      dependencies {
          implementation fileTree(include: ['*.aar'], dir: 'libs')
      }

      ```
   4. For the new project structure (applicable from the Android Gradle plugin version 7.0.0 and above), add the following in the `dependencyResolutionManagement` block of your `settings.gradle` file:

      ```groovy
      dependencyResolutionManagement {DependencyResolutionManagement it ->
          repositoriesMode.set(RepositoriesMode.FAIL_ON_PROJECT_REPOS)
          repositoriesMode.set(RepositoriesMode.PREFER_SETTINGS)
          
          repositories { RepositoryHandler it ->
              google()
              mavenCentral()
          }
      }

      ```

# Installing SDK

Perform the following:

1. Add the dependency files.\
   **Installing using version catalog:**
   This is the recommended method.
   1. Configure the catalog. For more information, refer to the [Version Catalog Installation](https://docs.capillarytech.com/docs/installing-sdk#/installing-with-version-catalog).
   2. Add the dependency in the `app/build.gradle` file.
      ```groovy
      dependencies {
          ...
          implementation("hydra.mipushkit")
      }
      ```
      **Installing using Artifact**\
      To install using artifact, add the following dependency in the `app/build.gradle` file:
   ```groovy
   dependencies {
   …
    implementation("com.capillarytech:hydra-mi-push-kit:1.10.6")
   }
   ```
2. Add the SDK files to the project.

   1. Download the helper class and broadcast receiver files from [here](https://github.com/Capillary/push-amp-plus).
   2. Create a package named `com.hydra.sdk.miPushKit` and paste the downloaded files into this package.
   3. Add Broadcast Receiver in AndroidManifest.xml file.

      ```xml
      <receiver
          android:name="com.hydra.sdk.miPushKit.MiBroadcastReciever"
          android:exported="false">

          <intent-filter>
              <action android:name="com.xiaomi.mipush.RECEIVE_MESSAGE" />
          </intent-filter>

          <intent-filter>
              <action android:name="com.xiaomi.mipush.MESSAGE_ARRIVED" />
          </intent-filter>

          <intent-filter>
              <action android:name="com.xiaomi.mipush.ERROR" />
          </intent-filter>

      </receiver>

      ```

# Initialise Xiaomi push

1. Locate the part of your code where the application comes to the foreground.
2. Insert the following code within that section:

   ```java
   MiPushHelper.initialiseMiPush(context, MI_APP_ID, MI_APP_KEY, Region);
   ```

where,

MI\_APP\_ID: The App-Id from the Mi Dashboard.\
MI\_APP\_KEY: The App-Key from the Mi Dashboard.
Region: The chosen region for Mi data residency.

## Handling Push within the Application (optional):

If you're handling token registration and notifications in your app's receiver, follow these steps:

1. Set the Data Region:

   1. Determine the region where Mi data resides using the`MiPushClient.getAppRegion(context)`API.
   2. Pass the region to the below API:

      ```java
      HydraMiPushApi.getInstance().setDataRegion(context, MiRegion.valueOf(region.toString()));  

      ```
2. Use the `passPushToken()` API and pass the push token to the SDK.

   ```java
   HydraMiPushApi.getInstance().passPushToken(context, pushToken);
   ```
3. Use the `isFromHydraPlatform()` helper API provided by the SDK and make sure that the payload is from the Capillary Hydra platform. After you confirm, pass the notification payload to the SDK.
   ```java
   HydraMiPushApi.getInstance().passPushPayload(context, pushPayload)
   ```

Example:

```java
if (HydraPushApi.getInstance().isFromHydraPlatform(remoteMessage)) {
   HydraMiPushApi.getInstance().passPushPayload(context, remoteMessage);
}
```