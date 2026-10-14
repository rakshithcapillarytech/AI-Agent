import { useCallback, useEffect, useState } from "react";
import { type StreamHandlers, api } from "../api";
import type { ChatMessage, Profile, SessionState } from "../types";

// Sessions whose /start call has been issued. Module-level so React StrictMode's dev-only
// double-mount can't start the same session twice.
const startedSessions = new Set<string>();

const CONNECTION_ERROR = "We couldn't reach the assistant. Check your connection, then try again.";

/**
 * One onboarding conversation: loads it, streams agent turns into `messages`, and re-syncs with
 * the server (the source of truth) after every turn.
 */
export function useConversation(id: string, startProfile?: Profile) {
  const [session, setSession] = useState<SessionState | null>(null);
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [busy, setBusy] = useState(false);
  const [loadError, setLoadError] = useState(false);

  const patchLast = (patch: (message: ChatMessage) => ChatMessage) =>
    setMessages((current) => [...current.slice(0, -1), patch(current[current.length - 1])]);

  const runTurn = useCallback(
    async (userMessage: ChatMessage, call: (handlers: StreamHandlers) => Promise<void>) => {
      setBusy(true);
      setMessages((current) => [
        ...current,
        userMessage,
        { role: "assistant", text: "", kind: "chat", status: "streaming" },
      ]);

      let failed = false;
      const fail = (text: string) => {
        failed = true;
        patchLast((m) => ({ ...m, text: m.text ? `${m.text}\n\n${text}` : text, status: "error" }));
      };
      try {
        await call({ onToken: (t) => patchLast((m) => ({ ...m, text: m.text + t })), onError: fail });
      } catch {
        fail(CONNECTION_ERROR);
      }

      try {
        const fresh = await api.getSession(id);
        setSession(fresh);
        // Keep the local error bubble (and its Retry) when the turn failed.
        if (!failed) setMessages(fresh.messages);
      } catch {
        if (!failed) patchLast((m) => ({ ...m, status: undefined }));
      }
      setBusy(false);
    },
    [id],
  );

  useEffect(() => {
    if (startProfile) {
      if (startedSessions.has(id)) return;
      startedSessions.add(id);
      setSession({ phase: "discovery", profile: startProfile, loaded_files: [], messages: [] });
      void runTurn({ role: "user", text: "", kind: "setup" }, (h) => api.start(id, startProfile, h));
      return;
    }

    let cancelled = false;
    api
      .getSession(id)
      .then((fresh) => {
        if (cancelled) return;
        setSession(fresh);
        setMessages(fresh.messages);
      })
      .catch(() => !cancelled && setLoadError(true));
    return () => {
      cancelled = true;
    };
    // Load once per session id; the start profile only matters on the first mount.
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [id]);

  const send = useCallback(
    (text: string) => runTurn({ role: "user", text, kind: "chat" }, (h) => api.send(id, text, h)),
    [id, runTurn],
  );

  /** Resend after a failed turn: the last chat message, or a nudge if the opening turn failed. */
  const retry = useCallback(() => {
    const lastUser = [...messages].reverse().find((m) => m.role === "user");
    setMessages((current) => current.slice(0, -2)); // drop the failed exchange; send() re-adds it
    const text = lastUser?.kind === "chat" ? lastUser.text : "Please start our onboarding.";
    void send(text);
  }, [messages, send]);

  return { session, messages, busy, loadError, send, retry };
}
