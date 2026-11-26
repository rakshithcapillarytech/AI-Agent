---
updatedAt: 2026-11-16T12:01:18.000Z
agentTools:
  projectIndex: https://docs.capillarytech.com/llms.txt
---

# Configure Firebase

This section helps you with information on configurations that you need to do on Firebase.

Capillary sends push notifications to your users through Firebase Cloud Messaging (FCM). To send them, the Capillary backend needs a service account in your Firebase project.

<Callout icon="📘" theme="info">
  ### Note

  Only the Capillary backend needs the service-account private key. Your Android app, iOS app, and website don't need it and must never contain it. Your apps use the standard public Firebase settings: `google-services.json` for Android, `GoogleService-Info.plist` for iOS, and the Firebase web configuration plus the VAPID public key for web.
</Callout>

## How Capillary uses the service account

The Capillary backend calls the FCM HTTP v1 API (`https://fcm.googleapis.com/v1/projects/<project-id>/messages:send`) through the Firebase Admin SDK, with the OAuth scope `https://www.googleapis.com/auth/firebase.messaging`. Capillary uses no other Firebase or Google Cloud service.

Google accepts a send request only with an OAuth 2.0 access token. The private key is what makes that token possible:

1. The Capillary backend builds a request that names your service account and the `firebase.messaging` scope.
2. The backend signs the request with the service account's private key.
3. Google checks the signature against the public key it has on file and returns an access token that lasts about an hour.
4. Capillary sends the notification with that token.

Without the private key, Google doesn't issue a token, so every send is rejected with 401 Unauthorized. Firebase configuration values can't replace the key.

## Configure Firebase

In the Google Firebase, perform the following:

1. Open [Google Firebase](https://console.firebase.google.com) and create the project. Refer to [Firebase documentation](https://firebase.google.com/docs/android/setup#create-firebase-project).
2. Set up cloud messaging. Refer to [Cloud messaging documentation](https://firebase.google.com/docs/cloud-messaging/android/client#java_1).

<Image align="center" className="border" border={true} src="https://files.readme.io/7df9c02-Messaging.png" />

3. Turn on the Firebase Cloud Messaging API (V1) for the project.
4. Create a dedicated service account for Capillary. Don't reuse an existing service account. Use a service account name that identifies its purpose and role in the project. For information on service account creation, see [Service account documentation](https://cloud.google.com/iam/docs/service-account-overview).

   Assign one of the following roles to the service account:

   * **Firebase Cloud Messaging API Admin** (`roles/firebasecloudmessaging.admin`). This role includes `cloudmessaging.messages.create`.
   * A custom role with only `cloudmessaging.messages.create`, if you want the tightest scope. For information on how to create a custom role, see [Custom role documentation](https://firebase.google.com/docs/projects/iam/roles).

   Don't use the Owner, Editor, or Firebase Admin roles. Capillary doesn't need them.

<Image align="center" className="border" border={true} src="https://files.readme.io/c49a5a5-Service_account.png" />

<Image align="center" className="border" border={true} src="https://files.readme.io/c046c9f-Service_account_created.png" />

5. Generate a new service account private key. This key lets the Capillary backend authenticate requests to FCM.

   It is recommended to use the key type as JSON.  This provides the key in a structured and easily readable key file in JSON format. For information on how to create the service account private key, refer to\
   [Service account key documentation](https://cloud.google.com/iam/docs/keys-create-delete).

<Image align="center" className="border" border={true} src="https://files.readme.io/ef7882e-Key.png" />

6. Share the key with Capillary using one of the following methods:

   * Use a one-time link from your enterprise password manager or secrets vault, such as 1Password or HashiCorp Vault. Restrict the link to the recipient's email address, set it to expire within 24 to 48 hours, and allow a single view.
   * Use a restricted link from your enterprise file-sharing platform, such as OneDrive or Google Drive. Share the link only with the recipient's email address, set an expiry date, and remove access after Capillary confirms the setup.

## Gateway Configuration

To enable mAPP SDK Channel and the push notifications, the team setting up the Firebase account for the brand must raise a ticket with the gateways team with details requested by them.