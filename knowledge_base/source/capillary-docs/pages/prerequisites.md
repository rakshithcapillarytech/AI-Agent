---
updatedAt: 2026-11-17T06:02:49.000Z
agentTools:
  projectIndex: https://docs.capillarytech.com/llms.txt
---

# Prerequisites

Before you begin, make sure you have the following:

* Your Capillary `accountId`, `orgId`, and `baseURL` — obtained from the Capillary team
* A Firebase project — only required if you plan to use push notifications, or if you choose Remote Config bootstrap (see [Configuration bootstrap](https://docs.capillarytech.com/docs/web-sdk-initialisation#configuration-bootstrap)). Not required for the default direct-config bootstrap without push notifications.
* Gamification credentials (`gamificationWriteKey`, `gamificationRegion`, `gamificationBaseUrl`) — only required if enabling [gamification](https://docs.capillarytech.com/docs/gamification-web)
* <Anchor target="_blank" href="https://docs.capillarytech.com/docs/prerequisites#content-security-policy-csp-configuration">Content Security Policy (CSP) Configuration</Anchor>

  ***

  ## Content Security Policy (CSP) Configuration

  If your application enforces a Content Security Policy (CSP), allowlist the following domains so the SDK functions correctly. Add these to your existing directives rather than replacing them — the exact set needed depends on which features you use.

  `connect-src`

  * `https://*.capillarytech.com` — core API, gamification, and loyalty traffic (always required)
  * `https://*.googleapis.com`, `https://*.firebaseio.com`, `https://*.firebaseapp.com` — only if using Remote Config bootstrap and/or push notifications
  * `https://*.posthog.com` — SDK diagnostics (always required)
    `script-src`
  * `'self'`
  * `https://*.gstatic.com` — push notifications only (loads the Firebase Messaging scripts inside the service worker)
  * `https://*.posthog.com`
    `frame-src`
  * `https://*.capillarytech.com` — loyalty embeds and gamification iframe content types (CAMPAIGN, WALLET, NUDGE, PROGRAM, REWARD)
    `img-src`
  * `https://*.capillarytech.com` — loyalty embeds and the gamification STATIC content type
    `worker-src`
  * `'self'`, `blob:`, `data:` — required for posthog
    **Example:**

  ```
  connect-src 'self' https://*.capillarytech.com https://*.googleapis.com https://*.firebaseio.com https://*.firebaseapp.com https://*.posthog.com;
  script-src 'self' https://*.gstatic.com https://*.posthog.com;
  frame-src 'self' https://*.capillarytech.com;
  img-src 'self' https://*.capillarytech.com;
  worker-src 'self' blob: data:;
  ```

  > If you're not using Remote Config bootstrap, push notifications, or gamification/loyalty, only the `capillarytech.com` and `posthog.com` entries are needed.