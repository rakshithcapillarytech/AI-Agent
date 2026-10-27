import type { Profile, SessionState } from "./types";

const BASE = "/api";

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
  body: unknown,
  handlers: StreamHandlers,
  signal?: AbortSignal,
): Promise<void> {
  const response = await fetch(url, {
    method: "POST",
    headers: { "content-type": "application/json" },
    body: JSON.stringify(body),
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
  /** Same-origin URL of the session's downloadable Markdown guide (served as an attachment). */
  guideUrl: (id: string) => `${BASE}/sessions/${encodeURIComponent(id)}/guide`,

  createSession: () =>
    fetch(`${BASE}/sessions`, { method: "POST" }).then((r) => json<{ session_id: string }>(r)),

  getSession: (id: string) =>
    fetch(`${BASE}/sessions/${encodeURIComponent(id)}`).then((r) => json<SessionState>(r)),

  start: (id: string, profile: Profile, handlers: StreamHandlers, signal?: AbortSignal) =>
    streamTurn(`${BASE}/sessions/${encodeURIComponent(id)}/start`, { profile }, handlers, signal),

  send: (id: string, content: string, handlers: StreamHandlers, signal?: AbortSignal) =>
    streamTurn(`${BASE}/sessions/${encodeURIComponent(id)}/messages`, { content }, handlers, signal),
};
