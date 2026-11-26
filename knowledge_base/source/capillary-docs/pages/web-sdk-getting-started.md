---
updatedAt: 2026-11-17T10:32:06.000Z
agentTools:
  projectIndex: https://docs.capillarytech.com/llms.txt
---

# Getting Started

This guide provides an overview about Capillary's Web SDK.

Capillary Hydra WebSDK (`cap-hydra-web-sdk`) provides event tracking, user identification, [push notifications](https://docs.capillarytech.com/docs/push-notification-web), and [gamification](https://docs.capillarytech.com/docs/gamification-web).

The SDK provides:

* **Event Tracking** — custom behavioral events and page views
* **User Identification** — link anonymous visitors to known users
* **Push Notifications** — browser-based push via Firebase Cloud Messaging
* **User Consent Controls** — enable/disable tracking at runtime
* **Gamification** — auto-renders campaigns and entry points (icon buttons, modals, banners, embeds) after user signin; configured entirely from the gamification dashboard
* **Loyalty Embeds** — injects loyalty iframe views into host-provided placeholder divs; token-authenticated via `setCapToken`

The SDK is a singleton initialized once at module load time. It internally queues all calls until ready — no manual readiness guards are needed.

**Package:** `cap-hydra-web-sdk`

**SDK version:** `1.10.6`

**Covers:** Installation, configuration, validation, troubleshooting, and rollback — supports both direct-config bootstrap (default, no Firebase) and Remote Config bootstrap

## Browser support

See the [Browser Support Matrix](https://docs.capillarytech.com/docs/push-notification-web#browser-support-matrix) on the Push Notifications page.

# Release channels

| Channel                                | When to use                                                      |
| -------------------------------------- | ---------------------------------------------------------------- |
| **Production** (`@latest`) — *default* | production environments — stable, fully tested releases          |
| **Beta** (`@beta`)                     | pre-release testing — latest features before the next stable cut |

# Integration roadmap

To integrate your web app with the Capillary Web SDK, perform the below steps:

1. [Install the SDK](https://docs.capillarytech.com/docs/web-sdk-install)
2. [Initialise the SDK](https://docs.capillarytech.com/docs/web-sdk-initialisation) — choose direct-config (default) or Remote Config bootstrap
3. [Configure Firebase](https://docs.capillarytech.com/docs/configure-firebase-web) — only if using push notifications or Remote Config bootstrap
4. [Configure push notifications](https://docs.capillarytech.com/docs/push-notification-web) — only if needed
5. [Configure gamification](https://docs.capillarytech.com/docs/gamification-web) — only if needed
6. [Review the API reference](https://docs.capillarytech.com/docs/web-sdk-api-reference)
7. [Validate your integration](https://docs.capillarytech.com/docs/web-sdk-troubleshooting) before going to production