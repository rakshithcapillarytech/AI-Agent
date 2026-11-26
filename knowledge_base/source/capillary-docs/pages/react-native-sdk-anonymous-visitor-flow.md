---
updatedAt: 2026-11-12T06:08:47.000Z
agentTools:
  projectIndex: https://docs.capillarytech.com/llms.txt
---

# Anonymous/Visitor Flow

Track anonymous visitors and identify them later with the Hydra class in your React Native app.

The SDK supports an anonymous "visitor" flow through the [Hydra](https://docs.capillarytech.com/docs/react-native-sdk-api-reference#hydra-class-apis) class. A user can move through the following states: `none`, then `visitor` (anonymous), then `merged` or `legacyRegistered` (identified), then `signedOut`.

This flow requires the Org Id that you get from the apps team. For details, see [Getting Started](https://docs.capillarytech.com/docs/react-native-sdk-getting-started). You configure the Org Id through the initialiser that you set up in [Installing iOS SDK](https://docs.capillarytech.com/docs/react-native-sdk-install#installing-ios-sdk) and [Installing Android SDK](https://docs.capillarytech.com/docs/react-native-sdk-install#installing-android-sdk).

# Using the visitor flow

1. Use [Hydra.isVisitorFlowEnabled()](https://docs.capillarytech.com/docs/react-native-sdk-api-reference#is-visitor-flow-enabled) to check whether the visitor flow is turned on for your account.
2. Use [Hydra.getCurrentUserState()](https://docs.capillarytech.com/docs/react-native-sdk-api-reference#get-current-user-state) to get the current [UserState](https://docs.capillarytech.com/docs/react-native-sdk-api-reference#userstate).
3. Use [Hydra.getVisitorDetails()](https://docs.capillarytech.com/docs/react-native-sdk-api-reference#get-visitor-details) to get the current [HydraVisitorInfo](https://docs.capillarytech.com/docs/react-native-sdk-api-reference#hydravisitorinfo) object (`visitorId`).
4. Subscribe to the visitor-flow lifecycle events on [HydraNativeEventEmitter](https://docs.capillarytech.com/docs/react-native-sdk-api-reference#sdk-event-tracking):
   * [setConfigFetchedCallback](https://docs.capillarytech.com/docs/react-native-sdk-api-reference#get-callback-when-config-is-fetched-visitor-flow)
   * [setLegacyFlowReadyCallback](https://docs.capillarytech.com/docs/react-native-sdk-api-reference#get-callback-when-legacy-flow-is-ready)
   * [setVisitorSessionReadyCallback](https://docs.capillarytech.com/docs/react-native-sdk-api-reference#get-callback-when-visitor-session-is-ready)
   * [setUserStateChangedCallback](https://docs.capillarytech.com/docs/react-native-sdk-api-reference#get-callback-when-user-state-changes)

The flow also uses `Hydra.identify()`, `Hydra.reset()`, and `Hydra.track()`. For details, see [React Native Setup Overview](https://docs.capillarytech.com/docs/react-native-sdk-setup-overview).