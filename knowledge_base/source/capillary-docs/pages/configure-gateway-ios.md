---
updatedAt: 2026-03-04T06:05:34.000Z
agentTools:
  projectIndex: https://docs.capillarytech.com/llms.txt
---

# Configure gateway

The Capillary Gateway configuration involves collaboration between the Mobile Capillary App Team, Gateway team, and the Sustenance Team.

The App Team generates the client token and project ID details, which are then incorporated into the Data Pipeline Management Gateway (DPMG) by the Sustenance Team. Additionally, credit files (data related to credit transactions such as points and rewards based on defined criteria) in JSON format for various platforms (android-trans, android-bulk, iOS-trans, iOS-bulk) are processed.

1. The App Team provides client token and project ID details required for Capillary Gateway setup, to the Sustenance team.
2. Verification of Existing Entries:
   1. The Sustenance Team checks if corresponding entries exist for the root organization (orgId=0) in the DPMG.
   2. If entries do not exist, proceed to step 3. Otherwise, use the existing IDs.
3. Adding New Entries to DPMG:
   1. Utilize the provided client token and project ID details to create new entries in the DPMG.
   2. Review and confirm configuration details such as host names, service URLs, authentication credentials, and message settings, as per the information provided in the [table](https://docs.capillarytech.com/reference/configure-gateway#capillary-gateway-configuration-details).
   3. Follow the insert statement provided in the hotswap link for inserting new entries.
   4. Ensure that the IDs in gateway\_org\_configs match with the gateway\_id in the DPMG.
4. Server Restart Request:
   1. After completing the setup and configuration process, request a server restart from the Engage side.
   2. This ensures that any changes made to the Capillary Gateway configurations take effect.

## Capillary Gateway Configuration Details

| id   | org\_id | short\_name       | host\_name | full\_name | username | password | connection\_properties | service\_ip | service\_url                          | status\_check\_url | message\_class | message\_priority | channel\_count | status | is\_private | status\_check\_type | properties                                                 | start\_time         | end\_time           | auto\_update\_time  |
| ---- | ------- | ----------------- | ---------- | ---------- | -------- | -------- | ---------------------- | ----------- | ------------------------------------- | ------------------ | -------------- | ----------------- | -------------- | ------ | ----------- | ------------------- | ---------------------------------------------------------- | ------------------- | ------------------- | ------------------- |
| 2066 | 0       | fcmios\_bulk      | fcmios     | fcm        | test     | test     | {}                     | 127.0.0.1   | <https://fcm.googleapis.com/fcm/send> |                    | IOS            | BULK              | 5              | ACTIVE | 0           | PUSH                | `{"scopes":["campaign"]}`                                  | 1970-01-01 00:00:00 | 2100-01-01 00:00:00 | 2020-09-29 14:40:15 |
| 2067 | 0       | fcmios\_trans     | fcmios     | fcm        | test     | test     | {}                     | 127.0.0.1   | <https://fcm.googleapis.com/fcm/send> |                    | IOS            | HIGH              | 5              | ACTIVE | 0           | PUSH                | `{"scopes":["optout","otp","highvoltrans","transaction"]}` | 1970-01-01 00:00:00 | 2100-01-01 00:00:00 | 2020-09-29 14:40:15 |
| 2068 | 0       | fcmandroid\_bulk  | fcmandroid | fcm        | test     | test     | {}                     | 127.0.0.1   | <https://fcm.googleapis.com/fcm/send> |                    | ANDROID        | BULK              | 5              | ACTIVE | 0           | PUSH                | `{"scopes":["campaign"]}`                                  | 1970-01-01 00:00:00 | 2100-01-01 00:00:00 | 2022-07-11 11:56:34 |
| 2069 | 0       | fcmandroid\_trans | fcmandroid | fcm        | test     | test     | {}                     | 127.0.0.1   | <https://fcm.googleapis.com/fcm/send> |                    | ANDROID        | HIGH              | 5              | ACTIVE | 0           | PUSH                | `{"scopes":["optout","otp","highvoltrans","transaction"]}` | 1970-01-01 00:00:00 | 2100-01-01 00:00:00 | 2020-09-29 14:40:15 |