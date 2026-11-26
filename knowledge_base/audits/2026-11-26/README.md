# Audit: Capillary public docs vs our knowledge base (2026-11-26)

What was compared: 59 pages of the public developer docs (docs.capillarytech.com): the 55 pages in the "SDKs" branch of
`llms.txt`, plus the four in-app messaging pages that the index doesn't list (`in-app-messaging`, `in-app-messaging_ios`,
`react-native-sdk-in-app-messaging`, `flutter-sdk-in-app-messaging`). Against: the 10 platform guides, the shared guides, and the
files built from them (`requirements.yaml`, `prerequisites.yaml`, `faq.yaml`, `step_summaries/`, `step_modules.yaml`, evals, tests).

One report per platform, written by a separate reviewer who read every page of that platform in full:
[android](android.md) · [ios](ios.md) · [react-native](react-native.md) · [flutter](flutter.md) · [web](web.md).
Each has sections A (contradictions), B (missing), C (changed since 13 Nov), D (unused pages), E (problems in the docs themselves),
F (impact on derived files) and G (what was confirmed matching).

## Headline result
The guides do **not** fully match the current docs. Android and iOS differ the most (they were built from older copies of the pages);
Web changed a lot on 17 and 23 November; React Native and Flutter match closely.

Confirmed first-hand by reading the downloaded pages (not only by the reviewers):
- Android: the Maven group is `com.capillarytech` (we use `com.capillary`), the class packages are `com.capillarytech.hydra.*`
  (we use `com.capillary.hydra.*`), and the SDK version is `1.10.6` on 11 pages (we pin `1.9.22-beta02`).
- iOS: the SDK repository is public (`hydra-ios-sdk-spm`, "needs no GitHub account or personal access token"); minimum iOS 15.6 and Xcode 16.1
  (we say private repo with a token, iOS 13.0, Xcode 14); SDK version `1.10.6` (we pin `1.7.5-preprod.12`).
- Web: `pageView` options are `page_url`, `page_title`, `referrer`, `page_category` (we list `url`, `title`, `category`).
- Firebase push: a dedicated service account with `roles/firebasecloudmessaging.admin` (or a custom role with only
  `cloudmessaging.messages.create`), and the FCM API (V1) enabled. We have an older 11-permission list and "server key" Gaps.
- Gamification (all platforms, page dated 2026-11-23): a new "Game and CMS event payloads" section (seven events) and a four-field
  event mapping (`customerId`, `identifierType`, `source`, `accountId`). We have neither, and our Gap saying the payloads aren't
  documented is out of date.

## Open questions for a Capillary SME
1. Is `com.capillarytech` now the only published Android group, and is `1.10.6` the right version for every platform and module?
2. Does native Android still need a GitHub token? Android's install page uses GitHub Packages; the React Native and Flutter pages say the
   Android SDK comes from Maven Central with no credentials.
3. Who creates the gamification events and where (the docs give the field mapping but not the place)?
4. Which Firebase roles are really needed, and is the older 11-permission list still needed for anything?

## Limits of this audit
- There were no older copies of the pages, so "what changed since 13 Nov" is inferred from dates and from where our files differ.
- Findings marked medium or low confidence by the reviewers have not all been re-checked against the pages.
- The in-app pages for Web don't exist; the Android in-app page matches our guide apart from the group and version.
