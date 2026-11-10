import { LifeBuoy, Send } from "lucide-react";
import { useCallback, useEffect, useState } from "react";
import { api } from "../api";
import type { Escalation } from "../types";
import styles from "./admin.module.css";
import { PageHeader } from "./PageHeader";
import { ui } from "./controls";

function EscalationCard({ item, onAnswer }: { item: Escalation; onAnswer: (id: string, text: string) => Promise<void> }) {
  const [answer, setAnswer] = useState("");
  const [sending, setSending] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const c = item.context;

  const send = async () => {
    setSending(true);
    setError(null);
    try {
      await onAnswer(item.id, answer.trim());
    } catch {
      setError("Couldn't send. Try again.");
      setSending(false);
    }
  };

  return (
    <li className={styles.card}>
      <div className={styles.cardHead}>
        <b>{c.company || "Unknown company"}</b>
        <span className={styles.meta}>
          {c.apps.join(", ")} · {c.environment ?? "?"} · {c.region ?? "?"} · phase: {c.phase ?? "?"}
        </span>
      </div>
      <p className={styles.summary}>{item.summary}</p>
      {c.step && <p className={styles.meta}>Current step: {c.step}</p>}
      {c.tried.length > 0 && (
        <div>
          <p className={styles.label}>Already tried</p>
          <ul className={styles.tried}>
            {c.tried.map((t, i) => (
              <li key={i}>{t}</li>
            ))}
          </ul>
        </div>
      )}
      <details>
        <summary>Recent conversation</summary>
        <ul className={styles.thread}>
          {c.recent_messages.map((m, i) => (
            <li key={i}>
              <b>{m.role === "client" ? "Client" : "Assistant"}:</b> {m.text}
            </li>
          ))}
        </ul>
      </details>
      <label className={styles.label} htmlFor={`answer-${item.id}`}>
        Your answer (the assistant relays it to the client)
      </label>
      <textarea id={`answer-${item.id}`} rows={4} value={answer} onChange={(e) => setAnswer(e.target.value)} disabled={sending} />
      <div className={styles.actions}>
        <a className={styles.link} href={`?session=${encodeURIComponent(item.session_id)}`} target="_blank" rel="noreferrer">
          Open client chat
        </a>
        <button type="button" className={`${ui.button} ${ui.primary}`} disabled={sending || !answer.trim()} onClick={send}>
          <Send size={15} /> {sending ? "Sending… this can take a minute" : "Send answer"}
        </button>
      </div>
      {error && <p role="alert" className={styles.error}>{error}</p>}
    </li>
  );
}

/** Engineers' queue: sessions paused on "talk to a human". Opened with /?admin=1 (no login yet). */
export function AdminView() {
  const [items, setItems] = useState<Escalation[] | null>(null);
  const [error, setError] = useState<string | null>(null);

  const load = useCallback(async () => {
    try {
      setItems(await api.listEscalations());
      setError(null);
    } catch {
      setItems(null);
      setError("Couldn't reach the server.");
    }
  }, []);

  useEffect(() => {
    void load();
  }, [load]);

  const answer = async (id: string, text: string) => {
    await api.answerEscalation(id, text);
    setItems((current) => current?.filter((i) => i.id !== id) ?? null);
  };

  return (
    <>
      <PageHeader title="Escalations" subtitle="Clients waiting for an engineer" />
      <div className={styles.page}>
        {items === null ? (
          <p className={styles.empty}>{error ?? "Loading…"}</p>
        ) : items.length === 0 ? (
          <p className={styles.empty}>
            <LifeBuoy size={18} /> Nothing waiting. New requests appear here when a client asks for a human.
            <button type="button" className={`${ui.button} ${ui.small}`} onClick={load}>
              Refresh
            </button>
          </p>
        ) : (
          <ul className={styles.list}>
            {items.map((item) => (
              <EscalationCard key={item.id} item={item} onAnswer={answer} />
            ))}
          </ul>
        )}
      </div>
    </>
  );
}
