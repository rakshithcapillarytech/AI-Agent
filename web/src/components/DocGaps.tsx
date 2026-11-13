import { useState } from "react";
import { api } from "../api";
import type { DocGap } from "../types";
import styles from "./admin.module.css";
import { ui } from "./controls";

/** Things clients needed that the documentation doesn't cover, most-asked first. */
export function DocGaps({ gaps, onChange }: { gaps: DocGap[]; onChange: () => void }) {
  const [busy, setBusy] = useState<string | null>(null);
  const handle = async (gap: DocGap) => {
    setBusy(gap.question);
    try {
      await api.handleDocGaps(gap.ids);
      onChange();
    } finally {
      setBusy(null);
    }
  };

  if (gaps.length === 0) {
    return <p className={styles.empty}>No gaps reported. The assistant logs one whenever it says something isn't documented.</p>;
  }
  return (
    <ul className={styles.list}>
      {gaps.map((gap) => (
        <li key={gap.ids[0]} className={styles.card}>
          <p className={styles.summary}>{gap.question}</p>
          <div className={styles.actions}>
            <span className={styles.meta}>
              Asked {gap.count} time{gap.count === 1 ? "" : "s"} · {gap.sessions} client{gap.sessions === 1 ? "" : "s"}
            </span>
            <button type="button" className={`${ui.button} ${ui.small}`} disabled={busy === gap.question} onClick={() => handle(gap)}>
              Mark as documented
            </button>
          </div>
        </li>
      ))}
    </ul>
  );
}
