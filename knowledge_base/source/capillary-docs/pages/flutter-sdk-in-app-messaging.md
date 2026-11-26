---
updatedAt: 2026-11-12T06:11:18.000Z
agentTools:
  projectIndex: https://docs.capillarytech.com/llms.txt
---

# Configure In-App Messaging

# Configuring In-App Messaging

1. Add an image named `hydra_in_app_placeholder` in `capillary/icons`. Can be png, jpg, or jpeg. This image is used as a placeholder for in-app messages.
2. Set `enable_in_app_messaging` to `true` in `hydra-config.json` (see [hydra-config.json](https://docs.capillarytech.com/docs/flutter-sdk-install#hydra-configjson)).
3. **For iOS:**

   * In `AppDelegate.swift`, add this import at the top:

     ```swift
     import capillary_hydra_ios
     ```

   * Add this function:

     ```swift
     override func application(_ application: UIApplication, didReceiveRemoteNotification userInfo: [AnyHashable: Any], fetchCompletionHandler completionHandler: @escaping (UIBackgroundFetchResult) -> Void) {
         HydraNativeAPI.shared.application(application, didReceiveRemoteNotification: userInfo, fetchCompletionHandler: completionHandler)
     }
     ```