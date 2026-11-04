import { Check, Circle, Minus } from "lucide-react";
import type { PrereqItem } from "../types";
import styles from "./session.module.css";

const DONE = new Set(["provided", "verified", "not_applicable"]);

const GROUPS: { owner: PrereqItem["owner"]; label: string }[] = [
  { owner: "client", label: "You do or provide" },
  { owner: "capillary", label: "Capillary sends you" },
];

function StatusIcon({ status }: { status: PrereqItem["status"] }) {
  if (status === "not_applicable") return <Minus size={12} strokeWidth={3} aria-label="Doesn't apply" />;
  if (DONE.has(status)) return <Check size={12} strokeWidth={3} aria-label="Done" />;
  return <Circle size={8} strokeWidth={0} fill="currentColor" aria-label="To do" />;
}

/** The client's prerequisites, built from their profile; the agent records progress in the chat. */
export function Checklist({ items }: { items: PrereqItem[] }) {
  if (items.length === 0) {
    return <p className={styles.contextEmpty}>Your checklist appears once your setup details are confirmed.</p>;
  }
  const done = items.filter((i) => DONE.has(i.status)).length;

  return (
    <div className={styles.checklist}>
      <div className={styles.checklistMeter} role="progressbar" aria-valuemin={0} aria-valuemax={items.length} aria-valuenow={done}>
        <span style={{ width: `${(done / items.length) * 100}%` }} />
      </div>
      <p className={styles.checklistCount}>
        {done} of {items.length} done · tell the assistant when you finish one
      </p>
      {GROUPS.map(({ owner, label }) => {
        const group = items.filter((i) => i.owner === owner);
        if (group.length === 0) return null;
        return (
          <div key={owner}>
            <h4 className={styles.checklistGroup}>{label}</h4>
            <ul className={styles.checklistItems}>
              {group.map((item) => {
                const isDone = DONE.has(item.status);
                return (
                  <li key={item.id} className={isDone ? styles.checkDone : undefined}>
                    <details>
                      <summary>
                        <span className={styles.checkIcon}>
                          <StatusIcon status={item.status} />
                        </span>
                        <span className={styles.checkTitle}>
                          {item.title}
                          {item.value && <code className={styles.checkValue}>{item.value}</code>}
                          {item.blocking && !isDone && owner === "client" && (
                            <span className={styles.checkTag}>Before coding</span>
                          )}
                        </span>
                      </summary>
                      <p className={styles.checkHow}>{item.how}</p>
                    </details>
                  </li>
                );
              })}
            </ul>
          </div>
        );
      })}
    </div>
  );
}
