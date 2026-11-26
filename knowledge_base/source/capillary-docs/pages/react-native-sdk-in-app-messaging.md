---
updatedAt: 2026-11-12T06:08:47.000Z
agentTools:
  projectIndex: https://docs.capillarytech.com/llms.txt
---

# Configure In-App Messaging

# Configuring In-App Messaging

You can turn on and configure in-app messages within your application for both iOS and Android. To configure in-app messaging, follow these steps:

1. Add an image named `hydra_in_app_placeholder` in `PROJECT_ROOT/capillary/icons`. Create these folders in your project root folder if they don't exist. The image can be PNG, JPG, or JPEG, but PNG is recommended. The SDK uses this image as a placeholder for in-app messages.
2. Set `enable_in_app_messaging` to `true` in `PROJECT_ROOT/capillary/hydra-config.json`.