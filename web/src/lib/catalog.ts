// Plain-English labels for everything the client picks or sees. Keep jargon out of `label`;
// technical names may appear in `hint` for the developer who later reads the summary.
import {
  Atom,
  BellRing,
  Building2,
  FlaskConical,
  Globe,
  Inbox,
  Layers,
  LayoutList,
  type LucideIcon,
  MessageSquare,
  Rocket,
  Smartphone,
  TabletSmartphone,
  Trophy,
  UserRound,
  Users,
} from "lucide-react";
import type { CustomerIdType, Environment, Module, Phase, Platform, Region } from "../types";

export interface Option<T extends string> {
  id: T;
  label: string;
  hint: string;
  icon?: LucideIcon;
}

export const PLATFORMS: Option<Platform>[] = [
  { id: "android", label: "Android app", hint: "Built natively for Android (Kotlin or Java)", icon: Smartphone },
  { id: "ios", label: "iPhone / iPad app", hint: "Built natively for iOS (Swift or Objective-C)", icon: TabletSmartphone },
  { id: "flutter", label: "Flutter app", hint: "One codebase for Android and iOS", icon: Layers },
  { id: "react-native", label: "React Native app", hint: "One codebase for Android and iOS", icon: Atom },
  { id: "web", label: "Website", hint: "A web app or website", icon: Globe },
];

export const MODULES: Option<Module>[] = [
  { id: "core", label: "User tracking", hint: "Know who your users are and what they do. Always included.", icon: Users },
  { id: "push", label: "Push notifications", hint: "Send messages to users' phones or browsers", icon: BellRing },
  { id: "inapp", label: "In-app messages", hint: "Show pop-up messages inside the app", icon: MessageSquare },
  { id: "inbox_api", label: "Notification inbox", hint: "Keep a history of messages users received", icon: Inbox },
  { id: "inbox_ui", label: "Ready-made inbox screen", hint: "A built-in screen that shows the inbox", icon: LayoutList },
  { id: "visitor", label: "Guest users", hint: "Track people before they sign in", icon: UserRound },
  { id: "gamification", label: "Gamification", hint: "Rewards, games and loyalty campaigns", icon: Trophy },
  { id: "multi_account", label: "Several brands in one app", hint: "One app serving more than one Capillary account", icon: Building2 },
];

export const ENVIRONMENTS: Option<Environment>[] = [
  { id: "uat", label: "Testing (UAT)", hint: "Try everything safely first", icon: FlaskConical },
  { id: "production", label: "Live (Production)", hint: "Real customers will use it", icon: Rocket },
];

export const REGIONS: Option<Region>[] = [
  { id: "IN", label: "India", hint: "IN" },
  { id: "US", label: "United States", hint: "US" },
  { id: "ME", label: "Middle East", hint: "ME" },
];

export const CUSTOMER_IDS: Option<CustomerIdType>[] = [
  { id: "mobile", label: "Mobile number", hint: "Customers sign in with their phone number" },
  { id: "email", label: "Email address", hint: "Customers sign in with their email" },
  { id: "externalId", label: "Your own customer ID", hint: "An ID from your own systems" },
  { id: "InTouchUserId", label: "Capillary user ID", hint: "The InTouch user ID from Capillary" },
  { id: "FCMToken", label: "Device token", hint: "The Firebase (FCM) token of the device" },
];

export const PHASES: { id: Phase; label: string; detail: string }[] = [
  { id: "discovery", label: "About your app", detail: "What you're connecting" },
  { id: "prerequisites", label: "Get ready", detail: "Accounts, keys and files" },
  { id: "integration", label: "Add the SDK", detail: "Step-by-step setup" },
  { id: "verification", label: "Check it works", detail: "Test before going live" },
  { id: "done", label: "All set", detail: "You're live" },
];

const PLATFORM_SHORT: Record<Platform, string> = {
  android: "Android",
  ios: "iOS",
  flutter: "Flutter",
  "react-native": "React Native",
  web: "Web",
};

export const labelOf = <T extends string>(options: Option<T>[], id: T | null | undefined) =>
  options.find((o) => o.id === id)?.label ?? "—";

export const platformShort = (p: Platform) => PLATFORM_SHORT[p];

export function phaseIndex(phase: Phase): number {
  return PHASES.findIndex((p) => p.id === phase);
}

/** Friendly name for a knowledge file path, e.g. "flutter/firebase.md" → "Flutter · with Firebase". */
export function guideLabel(path: string): string {
  const shared: Record<string, string> = {
    "_shared/overview.md": "Experience+ overview",
    "_shared/prerequisites.md": "Before you start",
    "_shared/firebase-setup.md": "Firebase setup",
  };
  if (shared[path]) return shared[path];
  const [platform, file] = path.split("/");
  const mode = file?.replace(".md", "") === "firebase" ? "with Firebase" : "without Firebase";
  return `${PLATFORM_SHORT[platform as Platform] ?? platform} · ${mode}`;
}
