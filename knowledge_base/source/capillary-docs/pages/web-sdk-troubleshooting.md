---
updatedAt: 2026-11-17T07:26:50.000Z
agentTools:
  projectIndex: https://docs.capillarytech.com/llms.txt
---

# Validation, Troubleshooting & Rollback

Validate your Web SDK integration, troubleshoot common issues, and roll back if needed.

Run all 6 checks after completing setup and before going to production.

# Validation & smoke testing

### 1. SDK initializes without errors

Open the browser console. A successful init at `debugLevel: "NONE"` produces no output. To see verbose logs temporarily, set `debugLevel: "DEBUG"` — directly in the `initialize()` call if using direct-config bootstrap, or in your Remote Config JSON (then republish) if using Remote Config bootstrap.

<Callout icon="⚠️" theme="warn">
  ### Important

  If you still don't see debug-level output after setting `"DEBUG"`: check your browser DevTools console's own log-level filter. Chromium-based DevTools classify `console.debug()` calls under a separate **"Verbose"** level (distinct from Info/Warnings/Errors), which is often unchecked by default. Look for a "Default levels" dropdown near the top of the Console panel and enable **Verbose**, this is a DevTools display setting, not something the SDK controls.
</Callout>

### 2. Page view tracking

Call `sdkService.trackPageView()` (see [API Reference](https://docs.capillarytech.com/docs/web-sdk-api-reference#pageview--page-views)). Verify the event appears as an outbound POST to your `baseURL` in the Network tab.

### 3. Custom event tracking

Call `sdkService.trackEvent("test_event", { source: "smoke_test" })`. Confirm the event reaches the Capillary API.

### 4. User identification

Call `sdkService.identifyUser(...)` (see [API Reference — identify()](https://docs.capillarytech.com/docs/web-sdk-api-reference#identify)). Verify the user profile is created or updated in your Capillary environment.

### 5. Logout / reset

Call `sdkService.reset()`. Verify user context is cleared and subsequent tracking is anonymous.

### 6. User consent toggle

Call `sdkService.disableTracking()` then `sdkService.enableTracking()`.

# Common errors & fixes

| Error                                                                  | Likely cause                                                                                                                                | Fix                                                                                                                                                                                                                                                            |
| ---------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `initialize()` throws (direct-config) / fails silently (Remote Config) | `accountId`, `baseURL`, or `orgId` missing                                                                                                  | Direct-config bootstrap throws a synchronous `Error` immediately from `initialize()` — add the missing field(s) to the call. Remote Config bootstrap fails silently (the fetch error is only logged) — add the missing field(s) to Remote Config and republish |
| Events not reaching API                                                | `baseURL` incorrect, or (Remote Config bootstrap) Remote Config not published                                                               | Verify `baseURL` value; if using Remote Config bootstrap, confirm it's published                                                                                                                                                                               |
| Push notifications not working                                         | Service worker not found or wrong VAPID key                                                                                                 | Confirm `serviceWorkerPath` matches actual file location; regenerate VAPID key if needed                                                                                                                                                                       |
| Service worker 404 / not registering                                   | File not served at the expected path                                                                                                        | Confirm `firebase-messaging-sw.js` is in `public/` and reachable at `https://yourapp/firebase-messaging-sw.js`; check `serviceWorkerPath` matches                                                                                                              |
| `self.firebase is undefined` in SW console                             | `importScripts` failed or Firebase config placeholders not replaced                                                                         | Confirm network access to `gstatic.com`; replace all `YOUR_*` values in the service worker                                                                                                                                                                     |
| Notification icon missing                                              | `/logo192.png` fallback file does not exist                                                                                                 | Add `logo192.png` to `public/`, or change the fallback icon paths in the service worker                                                                                                                                                                        |
| DLR events not recorded                                                | Old service worker cached                                                                                                                   | Unregister the old worker (DevTools → Application → Service Workers → Unregister) and reload                                                                                                                                                                   |
| SDK not initializing on app load                                       | `initialize()` called inside a lifecycle hook                                                                                               | Move `sdkService.initialize()` to module top level                                                                                                                                                                                                             |
| TypeScript import errors                                               | Package types not resolved                                                                                                                  | Ensure `cap-hydra-web-sdk` is in `dependencies` and `node_modules` is up to date                                                                                                                                                                               |
| Gamification entry points not appearing                                | `gamificationWriteKey`, `gamificationRegion`, or `gamificationBaseUrl` missing (from Remote Config, or from the direct `initialize()` call) | Add all three fields directly, or to Remote Config and republish, depending on bootstrap mode; confirm values with the Capillary team                                                                                                                          |
| Loyalty embed iframe not rendering                                     | `<div id="{embedId}">` not present in the DOM at render time                                                                                | Confirm the `id` matches the `embedId` provided; element must exist before or shortly after `identify()`                                                                                                                                                       |
| Set `debugLevel: "DEBUG"` but still only seeing normal-level output    | Browser DevTools console filters `console.debug()` calls under a "Verbose" level, unchecked by default                                      | Enable "Verbose" in the Console panel's log-level filter (a DevTools setting, not an SDK config)                                                                                                                                                               |

For push-notification browser compatibility, see the [Browser Support Matrix](https://docs.capillarytech.com/docs/push-notification-web#browser-support-matrix).

# Rollback Procedure

If the SDK causes issues in production:

1. **Disable tracking immediately** — call `sdkService.disableTracking()` via a feature flag or emergency toggle
2. **Remove the SDK service import** from your app entry point to stop initialization
3. **Uninstall the package:**

```bash
npm uninstall cap-hydra-web-sdk
# or: yarn remove / pnpm remove / bun remove
```

4. **Clear IndexedDB** in affected browsers if stale data is a concern (DevTools → Application → IndexedDB)
5. **Notify the Capillary team** with error details for investigation

***

*For credentials or support, contact the Capillary team directly.*

<br />