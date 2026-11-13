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
  kind: "setup" | "chat" | "upload";
  status?: "streaming" | "error";
}

/** One prerequisites checklist entry (app/graph/state.py PrereqItem). */
export interface PrereqItem {
  id: string;
  title: string;
  owner: "client" | "capillary";
  status: "pending" | "provided" | "verified" | "not_applicable";
  /** Client items marked blocking must be done before integration starts. */
  blocking: boolean;
  value: string | null;
  how: string;
  source: string;
  /** Set when the client can upload this file and the system checks it. */
  validator: "google_services_json" | "google_service_info_plist" | null;
}

export interface SessionState {
  phase: Phase;
  profile: Partial<Profile>;
  loaded_files: string[];
  prerequisites: PrereqItem[];
  messages: ChatMessage[];
  /** True once every app's config mode is known, so the downloadable guide can be built. */
  guide_ready: boolean;
  /** "file › step" entries built when integration starts; `current_step` is the index in progress. */
  plan_steps: string[];
  current_step: number;
  /** Set while an engineer has been asked to help: the thread is paused until they answer. */
  escalation: { status: "open" } | null;
}

/** One hand-off waiting for an engineer (app/escalation/store.py). */
export interface Escalation {
  id: string;
  session_id: string;
  summary: string;
  status: "open" | "answered";
  created_at: string;
  context: {
    company: string | null;
    apps: string[];
    environment: string | null;
    region: string | null;
    phase: string | null;
    step: string | null;
    tried: string[];
    recent_messages: { role: "client" | "assistant"; text: string }[];
  };
}

/** A fix the client confirmed, drafted by the agent for review (app/learning/issues.py). */
export interface IssueDraft {
  id: string;
  session_id: string;
  status: "pending" | "approved" | "rejected";
  created_at: string;
  payload: {
    error_signature: string;
    root_cause: string;
    fix: string;
    platform: Platform | null;
    config_mode: ConfigMode | null;
    tried: string[];
    step: string | null;
  };
}

/** Something clients needed that the documentation doesn't cover, grouped by question. */
export interface DocGap {
  question: string;
  count: number;
  sessions: number;
  ids: string[];
  last_seen: string;
}

export type IssueEdit = Partial<Pick<IssueDraft["payload"], "error_signature" | "root_cause" | "fix">> & {
  platform?: string;
  config_mode?: string;
};
