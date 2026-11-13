import { Check, X } from "lucide-react";
import { useState } from "react";
import { ApiError, api } from "../api";
import type { IssueDraft } from "../types";
import styles from "./admin.module.css";
import { ui } from "./controls";

const PLATFORMS = ["android", "ios", "react-native", "flutter", "web"];

function DraftCard({ draft, onDone }: { draft: IssueDraft; onDone: (id: string, note: string) => void }) {
  const p = draft.payload;
  const [fields, setFields] = useState({
    error_signature: p.error_signature,
    root_cause: p.root_cause,
    fix: p.fix,
    platform: p.platform ?? "",
    config_mode: p.config_mode ?? "",
  });
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const set = (key: keyof typeof fields) => (e: { target: { value: string } }) =>
    setFields((f) => ({ ...f, [key]: e.target.value }));

  const run = async (action: () => Promise<string>) => {
    setBusy(true);
    setError(null);
    try {
      onDone(draft.id, await action());
    } catch (e) {
      setError(e instanceof ApiError ? e.message : "Couldn't save. Try again.");
      setBusy(false);
    }
  };

  const id = `draft-${draft.id}`;
  return (
    <li className={styles.card}>
      <p className={styles.meta}>
        From a resolved conversation{p.step ? ` at ${p.step}` : ""}. Shared across clients once approved, so remove
        anything specific to one client.
      </p>
      <div className={styles.row}>
        <div>
          <label className={styles.label} htmlFor={`${id}-platform`}>Platform</label>
          <select id={`${id}-platform`} value={fields.platform} onChange={set("platform")} disabled={busy}>
            <option value="">Choose…</option>
            {PLATFORMS.map((x) => (
              <option key={x}>{x}</option>
            ))}
          </select>
        </div>
        <div>
          <label className={styles.label} htmlFor={`${id}-mode`}>Applies to</label>
          <select id={`${id}-mode`} value={fields.config_mode} onChange={set("config_mode")} disabled={busy}>
            <option value="">Both modes</option>
            <option value="firebase">With Firebase</option>
            <option value="direct">Without Firebase</option>
          </select>
        </div>
      </div>
      <label className={styles.label} htmlFor={`${id}-sig`}>Symptom or error text</label>
      <input id={`${id}-sig`} value={fields.error_signature} onChange={set("error_signature")} disabled={busy} />
      <label className={styles.label} htmlFor={`${id}-cause`}>Cause</label>
      <textarea id={`${id}-cause`} rows={3} value={fields.root_cause} onChange={set("root_cause")} disabled={busy} />
      <label className={styles.label} htmlFor={`${id}-fix`}>Fix</label>
      <textarea id={`${id}-fix`} rows={3} value={fields.fix} onChange={set("fix")} disabled={busy} />
      {p.tried.length > 0 && (
        <details>
          <summary>Fixes tried in the conversation ({p.tried.length})</summary>
          <ul className={styles.tried}>
            {p.tried.map((t, i) => (
              <li key={i}>{t}</li>
            ))}
          </ul>
        </details>
      )}
      <div className={styles.actions}>
        <button
          type="button"
          className={`${ui.button} ${ui.small}`}
          disabled={busy}
          onClick={() => run(async () => (await api.rejectIssueDraft(draft.id), "Rejected."))}
        >
          <X size={15} /> Reject
        </button>
        <button
          type="button"
          className={`${ui.button} ${ui.primary}`}
          disabled={busy}
          onClick={() => run(async () => `Published as ${(await api.approveIssueDraft(draft.id, fields)).file}`)}
        >
          <Check size={15} /> Approve and publish
        </button>
      </div>
      {error && <p role="alert" className={styles.error}>{error}</p>}
    </li>
  );
}

/** Fixes clients confirmed, drafted by the agent. Approving writes a file in knowledge_base/issues/. */
export function IssueDrafts({ drafts, onChange }: { drafts: IssueDraft[]; onChange: () => void }) {
  const [notes, setNotes] = useState<string[]>([]);
  const done = (_id: string, note: string) => {
    setNotes((n) => [note, ...n]);
    onChange();
  };
  return (
    <>
      {notes.length > 0 && <p className={styles.note} role="status">{notes[0]} Commit the new file to git to keep it.</p>}
      {drafts.length === 0 ? (
        <p className={styles.empty}>No drafts waiting. They appear when the assistant resolves a client's problem.</p>
      ) : (
        <ul className={styles.list}>
          {drafts.map((d) => (
            <DraftCard key={d.id} draft={d} onDone={done} />
          ))}
        </ul>
      )}
    </>
  );
}
