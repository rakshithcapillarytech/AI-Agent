---
updatedAt: 2026-03-25T09:19:20.000Z
agentTools:
  projectIndex: https://docs.capillarytech.com/llms.txt
---

# Initialise SDK

This section provides information on initialisation of the SDK.

To initialize the Capillary SDK,

1. Create an instance of the SDK for each application. This API needs to be called in the `onCreate() `of the application class with the `HydraConfig`. You can use this instance in your code to interact with the SDK.

2. ```kotlin
   fun instanceWithConfig(  
      context: Context, config: HydraConfig  
   ): HydraAPI
   ```
   ```java
   public HydraAPI instanceWithConfig(Context context, HydraConfig config) {
       // Function body goes here
   }
   ```

3. Provide configuration in the SDK using`HydraConfig`. The SDK accepts several parameters. The parameter accountId is mandatory. If accountID is not provided, the SDK throws an exception. All other parameters are optional.

   ```kotlin
   var accountId: String,  
   var baseURL: String?,  
   var sslPublicKey: String?,  
   var country: String?,  
   var city: String?,  
   var countryCode: String?,  
   var captureViewPortDetails: Boolean,  
   var isDisableAppLaunchedEvent: Boolean,  
   var debugLevel: Int,
   var remoteDebugLevel: Int,
   var fcmConfig:FcmConfig = defaultFcmConfig(),  
   val notificationConfig: NotificationConfig? = null
   ```
   ```java
   String accountId;
   String baseURL;
   String sslPublicKey;
   String country;
   String city;
   String countryCode;
   boolean captureViewPortDetails;
   boolean isDisableAppLaunchedEvent;
   int debugLevel;
   int remoteDebugLevel;
   FcmConfig fcmConfig = defaultFcmConfig();
   ```

4. Add the SDK initialization block in the `onCreate` callback of your application class as shown below:

   ```kotlin
   val hydraConfig = HydraConfig.Builder(  
      applicationContext,  
      accountId = "PARTNER_ACCOUNT_ID"  
   )  
      .debugLevel(LogType.VERBOSE)
      .remoteDebugLevel(LogType.DEBUG)
      .captureViewPortDetails(true)  
      .country("India")  
      .city("Pune")  
      .countryCode("91")  
      .baseURL("PARTNER_HYDRA_URL")  
      .sslPublicKey("PARTNER_SSL_PUBLIC_KEY_FOR_HYDRA_URL")  
      .build()
   ```
   ```java
   HydraConfig hydraConfig = new HydraConfig.Builder(applicationContext)
       .setAccountId("PARTNER_ACCOUNT_ID")
       .setDebugLevel(LogType.VERBOSE)
       .setRemoteDebugLevel(LogType.DEBUG)
       .setCaptureViewPortDetails(true)
       .setCountry("India")
       .setCity("Pune")
       .setCountryCode("91")
       .setBaseURL("PARTNER_HYDRA_URL")
       .setSslPublicKey("PARTNER_SSL_PUBLIC_KEY_FOR_HYDRA_URL")
       .build();
   ```

   | Parameter               | Type                      | Description                                                | Mandatory/Optional                   |
   | ----------------------- | ------------------------- | ---------------------------------------------------------- | ------------------------------------ |
   | accountId               | String                    | Account ID of the partner                                  | Mandatory                            |
   | .debugLevel             | LogType                   | Logging Config i.e. OFF(-1), INFO(0), DEBUG(1), VERBOSE(2) | Optional                             |
   | .remoteDebugLevel       | LogType                   | Remote Logging Config i.e. OFF(-1), INFO(0), DEBUG(1)      | Optional                             |
   | .captureViewPortDetails | Boolean                   | Capture ViewPort information                               | Optional                             |
   | .country                | String                    | Country name                                               | Optional                             |
   | .city                   | String                    | City name                                                  | Optional                             |
   | .countryCode            | String                    | Country code value                                         | Optional                             |
   | .baseURL                | String                    | Base URL of region                                         | Optional                             |
   | .sslPublicKey           | String                    | Valid SSL Public Key of URL                                | Optional                             |
   | .fcmConfig              | FcmConfig object          | Firebase Configuration                                     | Optional (If not using Firebase SDK) |
   | .notificationConfig     | NotificationConfig object | Notification Configuration                                 | Optional (If not using Firebase SDK) |

5. Create an instance of the `HydraAPI `with `HydraConfig`. Use the below functional call:\
   `HydraAPI.instanceWithConfig(applicationContext, hydraConfig)`

   | Parameter          | Type        | Description         | Optional/Mandatory |
   | :----------------- | :---------- | :------------------ | :----------------- |
   | applicationContext | Context     | Application context | Mandatory          |
   | hydraConfig        | HydraConfig | HydraConfig object  | Mandatory          |