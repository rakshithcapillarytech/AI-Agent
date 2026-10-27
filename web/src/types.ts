// Mirrors the backend's IntegrationProfile and session payloads (app/graph/state.py, app/api/main.py).

export type Platform = "android" | "ios" | "react-native" | "flutter" | "web";
export type ConfigMode = "firebase" | "direct";
export type Module =
  | "core"
  | "push"
  | "inapp"
  | "inbox_api"
  | "inbox_ui"
  | "visitor"
  | "gamification"
  | "multi_account";
export type Phase = "discovery" | "prerequisites" | "integration" | "verification" | "done";
export type Environment = "uat" | "production";
export type Region = "IN" | "US" | "ME";
export type CustomerIdType = "mobile" | "email" | "externalId" | "InTouchUserId" | "FCMToken";

export interface PlatformDetails {
  platform: Platform;
  /** null means "not sure"; the agent asks about it in the chat. */
  config_mode: ConfigMode | null;
}

export interface Profile {
  company: string | null;
  platforms: PlatformDetails[];
  modules: Module[];
  environment: Environment | null;
  region: Region | null;
  customer_id_type: CustomerIdType | null;
  contacts: string[];
  go_live_date: string | null;
  confirmed?: boolean;
}

export interface ChatMessage {
  role: "user" | "assistant";
  text: string;
  /** "setup" is the opening message generated from the setup wizard. */
  kind: "setup" | "chat";
  status?: "streaming" | "error";
}

export interface SessionState {
  phase: Phase;
  profile: Partial<Profile>;
  loaded_files: string[];
  messages: ChatMessage[];
  /** True once every app's config mode is known, so the downloadable guide can be built. */
  guide_ready: boolean;
}
