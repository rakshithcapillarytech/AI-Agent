import type { DocGap, Escalation, IssueDraft, IssueEdit, Profile, SessionState } from "./types";

const BASE = "/api";
const JSON_TYPE = "application/json";
/** The server refuses uploads above this (app/validators/upload.py MAX_UPLOAD_BYTES). */
export const MAX_UPLOAD_BYTES = 256 * 1024;

export class ApiError extends Error {
  constructor(
    message: string,
    readonly status?: number,
  ) {
    super(message);
  }
}

export interface StreamHandlers {
  onToken: (text: string) => void;
  onError: (message: string) => void;
}

async function json<T>(response: Response): Promise<T> {
  if (!response.ok) {
    throw new ApiError(`Request failed (${response.status})`, response.status);
  }
  return (await response.json()) as T;
}

/** POST and consume the server-sent events of one agent turn (`token`, `error`, `done`). */
async function streamTurn(
  url: string,
  body: BodyInit,
  contentType: string,
  handlers: StreamHandlers,
  signal?: AbortSignal,
): Promise<void> {
  const response = await fetch(url, {
    method: "POST",
    headers: { "content-type": contentType },
    body,
    signal,
  });
  if (!response.ok || !response.body) {
    throw new ApiError(`Request failed (${response.status})`, response.status);
  }

  const reader = response.body.pipeThrough(new TextDecoderStream()).getReader();
  let buffer = "";
  for (;;) {
    const { value, done } = await reader.read();
    if (done) break;
    buffer += value;
    const events = buffer.split("\n\n");
    buffer = events.pop() ?? "";
    for (const event of events) {
      const data = event.split("\n").find((line) => line.startsWith("data: "));
      if (!data) continue;
      const parsed = JSON.parse(data.slice("data: ".length)) as { type: string; text?: string };
      if (parsed.type === "token" && parsed.text) handlers.onToken(parsed.text);
      else if (parsed.type === "error") handlers.onError(parsed.text ?? "Something went wrong.");
    }
  }
}

export const api = {
  /** Admin queue: escalations waiting for an engineer. No login yet. */
  listEscalations: () => fetch(`${BASE}/admin/escalations`).then((r) => json<Escalation[]>(r)),

  /** Answer an escalation: the server resumes the paused session with it (can take a minute). */
  answerEscalation: (id: string, answer: string) =>
    fetch(`${BASE}/admin/escalations/${encodeURIComponent(id)}/answer`, {
      method: "POST",
      headers: { "content-type": JSON_TYPE },
      body: JSON.stringify({ answer }),
    }).then((r) => json<{ ok: boolean }>(r)),

  /** Drafts the agent wrote from fixes clients confirmed, waiting for review. */
  listIssueDrafts: () => fetch(`${BASE}/admin/issue-drafts`).then((r) => json<IssueDraft[]>(r)),

  /** Publish a draft (with the reviewer's edits). A draft that fails the gate throws with the reasons. */
  approveIssueDraft: async (id: string, edits: IssueEdit) => {
    const response = await fetch(`${BASE}/admin/issue-drafts/${encodeURIComponent(id)}/approve`, {
      method: "POST",
      headers: { "content-type": JSON_TYPE },
      body: JSON.stringify(edits),
    });
    if (response.status === 422) {
      const { detail } = (await response.json()) as { detail: string[] | string };
      throw new ApiError(Array.isArray(detail) ? detail.join(" ") : detail, 422);
    }
    return json<{ file: string }>(response);
  },

  rejectIssueDraft: (id: string) =>
    fetch(`${BASE}/admin/issue-drafts/${encodeURIComponent(id)}/reject`, { method: "POST" }).then((r) =>
      json<{ ok: boolean }>(r),
    ),

  listDocGaps: () => fetch(`${BASE}/admin/doc-gaps`).then((r) => json<DocGap[]>(r)),

  handleDocGaps: (ids: string[]) =>
    fetch(`${BASE}/admin/doc-gaps/handle`, {
      method: "POST",
      headers: { "content-type": JSON_TYPE },
      body: JSON.stringify({ ids }),
    }).then((r) => json<{ ok: boolean }>(r)),

  /** Same-origin URL of the session's downloadable Markdown guide (served as an attachment). */
  guideUrl: (id: string) => `${BASE}/sessions/${encodeURIComponent(id)}/guide`,

  createSession: () =>
    fetch(`${BASE}/sessions`, { method: "POST" }).then((r) => json<{ session_id: string }>(r)),

  getSession: (id: string) =>
    fetch(`${BASE}/sessions/${encodeURIComponent(id)}`).then((r) => json<SessionState>(r)),

  start: (id: string, profile: Profile, handlers: StreamHandlers, signal?: AbortSignal) =>
    streamTurn(`${BASE}/sessions/${encodeURIComponent(id)}/start`, JSON.stringify({ profile }), JSON_TYPE, handlers, signal),

  send: (id: string, content: string, handlers: StreamHandlers, signal?: AbortSignal) =>
    streamTurn(`${BASE}/sessions/${encodeURIComponent(id)}/messages`, JSON.stringify({ content }), JSON_TYPE, handlers, signal),

  /** Upload a checklist file as the raw body; the server checks it and the agent replies to the result. */
  uploadFile: (id: string, file: File, handlers: StreamHandlers, signal?: AbortSignal) =>
    streamTurn(
      `${BASE}/sessions/${encodeURIComponent(id)}/files?name=${encodeURIComponent(file.name)}`,
      file,
      "application/octet-stream",
      handlers,
      signal,
    ),
};
