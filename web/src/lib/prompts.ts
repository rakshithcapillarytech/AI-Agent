// Copy-paste prompts for the client's own AI assistant, used together with the downloadable
// guide. The opening "setup" paragraph is personalised from the profile; the rest is fixed.
import type { Platform, Profile } from "../types";
import { CUSTOMER_IDS, ENVIRONMENTS, MODULES, REGIONS, labelOf, platformShort } from "./catalog";

export type PromptKind = "setup" | "debug";

const PLATFORM_NAMES: Record<Platform, string> = {
  android: "Android (native)",
  ios: "iOS (native)",
  flutter: "Flutter",
  "react-native": "React Native",
  web: "Website",
};

const RULES = [
  "1. Use the attached guide as your only source for SDK facts: method names, config keys, versions, file locations and the order of steps. Copy names exactly as written. Don't use outside knowledge of this SDK.",
  "2. \"⚠️ Correction\" lines: always use the ✅ value, never the ❌ value.",
  "3. \"⚠️ Gap\" lines, or anything the guide doesn't cover: say so plainly and tell me to confirm it with my Capillary contact. Don't guess.",
  "4. Values in {{double braces}} come from Capillary or from my project. Never invent them; tell me which value goes where.",
  "5. Never ask me for secrets (GitHub tokens, private keys, API keys).",
];

const DEBUG_RULES = [
  RULES[0],
  "2. \"⚠️ Correction\" lines: always use the ✅ value, never the ❌ value. Check these first; they mark known mistakes in the original documentation.",
  "3. \"⚠️ Gap\" lines, or anything the guide doesn't cover: say so plainly. Don't guess.",
  "4. Values in {{double braces}} come from Capillary or from my project. Never invent them.",
  "5. Never ask me for secrets. If I paste a token or key by mistake, tell me to remove it and rotate it.",
];

function setupLines(profile: Partial<Profile>): string[] {
  const apps = (profile.platforms ?? []).map((p) => {
    const mode =
      p.config_mode === "firebase"
        ? "with Firebase Remote Config"
        : p.config_mode === "direct"
          ? "without Firebase Remote Config"
          : "not sure whether it uses Firebase";
    return `${PLATFORM_NAMES[p.platform]}, ${mode}`;
  });
  const appLines =
    apps.length === 1 ? [`- App: ${apps[0]}`] : apps.map((app, i) => `- App ${i + 1}: ${app}`);
  const region = profile.region ? `${labelOf(REGIONS, profile.region)} (${profile.region})` : "not given";
  const features = (profile.modules ?? []).map((m) => labelOf(MODULES, m)).join(", ") || "not given";

  return [
    ...appLines,
    `- Features: ${features}`,
    `- Environment: ${profile.environment ? labelOf(ENVIRONMENTS, profile.environment) : "not given"}, region ${region}`,
    `- Customers sign in with: ${profile.customer_id_type ? labelOf(CUSTOMER_IDS, profile.customer_id_type) : "not given"}`,
  ];
}

export function buildPrompt(kind: PromptKind, profile: Partial<Profile>): string {
  const company = profile.company?.trim() || "our company";
  const example = profile.platforms?.[0] ? platformShort(profile.platforms[0].platform) : "Platform";

  if (kind === "setup") {
    return [
      `I'm integrating Capillary's Hydra SDK (Experience+) for ${company}. Our setup:`,
      ...setupLines(profile),
      "",
      "I've attached our integration guide as a Markdown file. It covers only this setup. Act as an experienced engineer and walk me through the integration.",
      "",
      "Rules:",
      ...RULES,
      "",
      "How to guide me:",
      "- First, list the prerequisites from the guide that I need before writing code, grouped by who provides them: me, or Capillary.",
      "- Then take me through the setup steps in the guide's order, one or two steps at a time. For each step, give me the exact code or config and the file it goes in.",
      "- After each step, tell me how to check it worked, then wait for me to confirm before moving on.",
      `- Cite the guide section you're using, e.g. (${example} › Steps › 3).`,
      "",
      "Where I am right now:",
      '[e.g. "Starting from scratch", or "Done up to adding the package, now on the next step"]',
    ].join("\n");
  }

  return [
    `I'm integrating Capillary's Hydra SDK (Experience+) for ${company} and I've hit a problem. Our setup:`,
    ...setupLines(profile),
    "",
    "I've attached our integration guide as a Markdown file. It covers only this setup. Act as an experienced engineer and help me find and fix the cause.",
    "",
    "Rules:",
    ...DEBUG_RULES,
    "",
    "How to debug:",
    "1. If anything is missing, ask for it before diagnosing: the exact error, logs, the relevant code or config, and my SDK, tool and OS versions. Ask only for what you actually need.",
    "2. List the likely causes, most likely first. For each, quote the part of the guide it relies on and say why it fits my symptoms.",
    "3. Give me the fix as exact steps or code, and the file it goes in.",
    "4. Tell me how to confirm it's fixed.",
    "5. If nothing in the guide explains it, say so and write a short summary I can send to my Capillary contact: setup, symptom, error, what we've tried.",
    "",
    "The problem:",
    "[Describe what's happening and what you expected. Paste the exact error message, plus any relevant code or logs.]",
  ].join("\n");
}
