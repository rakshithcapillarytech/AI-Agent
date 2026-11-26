---
updatedAt: 2026-11-17T05:59:58.000Z
agentTools:
  projectIndex: https://docs.capillarytech.com/llms.txt
---

# Configure Firebase

This section provides information on setting up a Firebase project for the Web SDK.

<Callout icon="📘" theme="info">
  ### Note

  This page is only needed if you're using **Remote Config bootstrap**, and/or **push notifications**. If you're using direct-config bootstrap (the default — see [Initialise SDK — Configuration bootstrap](https://docs.capillarytech.com/docs/web-sdk-initialisation#configuration-bootstrap)) without push notifications, skip this entire page — no Firebase project is required. Just get your `accountId`/`baseURL`/`orgId` from the Capillary team and pass them directly to `HydraSDK.initialize()`.
</Callout>

## Step 1: Create a Firebase Project

1. Go to <https://console.firebase.google.com/>
2. Click **"Add project"**

<Image src="https://files.readme.io/7b494d3a96dbe1611a7e9844f608d746e4164807fa1ae7b5a2622b9071fce8c7-create_project_1.png" align="center" width="85%" border={true} />

or

<Image src="https://files.readme.io/99deab94c0b48ee31dfb9328519434775a9ed6719a49684c8c334b4d68a8910e-create_project_2.png" align="center" width="85%" border={true} />

3. Enter a project name (e.g., `my-app-analytics`)

<Image src="https://files.readme.io/07f1330f49578cdaafb8c5157a9d638d67b780e9842b2d678d613c96d061119f-enter_project_name.png" align="center" width="85%" border={true} />

<br />

4. Enable Google Analytics if desired (recommended)

<Image src="https://files.readme.io/bc8649965ee67d40fa2f544c0173d03a6ffa307b69b6a0620cbc93305ce833c9-enable_google_analytics.png" align="center" width="85%" border={true} />

5. Click **"Create project"**

<Image src="https://files.readme.io/03f01e698ea298066944df95b6401af98ca2d20eb4456c6116dd3224e777977f-click_create_project.png" align="center" width="85%" border={true} />

## Step 2: Register a Web App

1. In the project dashboard, click the **Web icon** (`</>`)

<Image src="https://files.readme.io/f96e9fc497fbec1aa6e39840e34a0a32966733c74fb2bf45b70239e18603173e-web_icon_click.png" align="center" width="85%" border={true} />

2. Enter an app nickname (e.g., `My Web App`)
3. Optionally check **"Also set up Firebase Hosting"**
4. Click **"Register app"**

<Image src="https://files.readme.io/b63c511e3666cc56788b781f4a35acc881b5b6d59c8a9a1d9d6c8f92d1fa9244-web_app_name.png" align="center" width="85%" border={true} />

5. **Copy the Firebase config object** — you will need every value from it

```javascript
const firebaseConfig = {
  apiKey: "AIzaSyC...",
  authDomain: "my-project.firebaseapp.com",
  databaseURL: "https://my-project-default-rtdb.firebaseio.com",
  projectId: "my-project",
  storageBucket: "my-project.appspot.com",
  messagingSenderId: "123456789",
  appId: "1:123456789:web:abcdef123456",
  measurementId: "G-XXXXXXXXXX", // only if Analytics is enabled
};
```

<Image src="https://files.readme.io/f46a5e527fde043eb05b904c591cb706cda55a5fabdc986da138c1c5a9c3ecce-copy_firebase_config_object.png" align="center" width="85%" border={true} />

<Image src="https://files.readme.io/16afc616213fd47bad06b6aa117747d77f7b35d27b0a540497eb80cf2f3c039d-install_firebase_cli.png" align="center" width="85%" border={true} />

<Image src="https://files.readme.io/b4e8c61445ffbd69f9a8eee2ac5a6533fb4ca5d222d8f12e5a17db55ca9cfed3-deploy_firebase_hosting.png" align="center" width="85%" border={true} />

## Step 3: Set Up Remote Config

<Callout icon="📘" theme="info">
  ### Note

  Only required for **Remote Config bootstrap**. Skip this step for direct-config bootstrap.
</Callout>

1. In the left sidebar, go to **Remote Config**

<Image src="https://files.readme.io/ef83d48d63793da818f2e0863d66c95d2f13916eac5676799b68539dff2db5d8-remote_config.png" align="center" width="85%" border={true} />

2. Click **"Create configuration"** → **"Add parameter"**

<Image src="https://files.readme.io/064cc6c4a2f97ecece9196932167e3b94d46d2069302033789cbce81f7ebfbfa-create_remote_config_configuration.png" align="center" width="85%" border={true} />

3. Set **Parameter key** (e.g., `hydra_sdk_config`) — this becomes your `remoteConfigKey`

4) Set **Default value** to this JSON (replace values with your Capillary credentials):

```json
{
  "accountId": "YOUR_ACCOUNT_ID",
  "baseURL": "https://api.example.capillarytech.com",
  "orgId": "YOUR_ORG_ID",
  "gamificationWriteKey": "wk_live_xxxxxxxxxx",
  "gamificationRegion": "us",
  "gamificationBaseUrl": "https://api-us.customerglu.com"
}
```

<Image src="https://files.readme.io/4e68bb5828b849844b8720c3344253c84c2b94bd36a1b5dddd1be22e0b1c40e0-add_remote_parameter.png" align="center" width="85%" border={true} />

<br />

5. Click **"Save"** then **"Publish changes"**

<Image src="https://files.readme.io/f8b43abb992b420033075b78818e9f0d2f77e77cb857f3b0df89fd263ba06008-publish_changes_2.png" align="center" width="85%" border={true} />

<Callout icon="⚠️" theme="warn">
  ### Important

  `accountId`, `baseURL`, and `orgId` are required. If any are missing, `HydraSDK.initialize()` will fail silently in Remote Config bootstrap mode.
</Callout>

## Step 4: Generate a VAPID Key

<Callout icon="📘" theme="info">
  ### Note

  Only required for **push notifications**.
</Callout>

1. Go to **Project Settings** → **Cloud Messaging** tab

<Image src="https://files.readme.io/38d9af20b8e485c2dfbbf2ec0aacffd38f4256b282d38185348847dee52a682c-project_settings.png" align="center" width="85%" border={true} />

<Image src="https://files.readme.io/b5ebfb0f444374d7e3f1c5ff9b3bda6b956e47c0a98278a6c483958dd3a8e1d3-cloud_messaging_tab.png" align="center" width="85%" border={true} />

<br />

2. Scroll to **Web configuration** → **Web Push certificates**

<Image src="https://files.readme.io/3989cd88c08278f7bd24384fc95662eb61d71a3b601167297801081009ec60f6-webpush_certificate.png" align="center" width="85%" border={true} />

3. Click **"Generate key pair"**

<Image src="https://files.readme.io/aa19cfe77cd84b6914d8242cb45212ff7881d76a47596a0c736b4c04c17cbfe9-generate_key_pair.png" align="center" width="85%" border={true} />

4. Copy the VAPID key — this goes into `notifications.vapidKey`. See [Configure Push Notifications](https://docs.capillarytech.com/docs/push-notification-web).

<Image src="https://files.readme.io/17191eed62bb3f5347044a61d0fc9fd0c9ecaa0b882aecf4abad4b31ca8e17f9-vapid_key.png" align="center" width="85%" border={true} />

## Step 5: Enable Required Firebase Services

| Service       | Steps                               |
| ------------- | ----------------------------------- |
| Remote Config | Confirm your parameter is published |

<Image src="https://files.readme.io/a4b9911a3b93a46c27b87c3649763adc4655d34d0279ad79678296eff39b5f5a-confirm_published.png" align="center" width="85%" border={true} />

<br />

Once your Firebase project is ready, continue to [Configure Push Notifications](https://docs.capillarytech.com/docs/push-notification-web) to add the service worker, or back to [Initialise SDK](https://docs.capillarytech.com/docs/web-sdk-initialisation) if you're only using Remote Config bootstrap without push.

<br />