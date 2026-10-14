import { Plus } from "lucide-react";
import { type RecentSession, dayGroup, relativeTime } from "../lib/recent";
import styles from "./layout.module.css";

interface SidebarProps {
  recent: RecentSession[];
  activeId: string | null;
  onNew: () => void;
  onOpen: (id: string) => void;
}

const GROUPS = ["Today", "Yesterday", "Earlier"] as const;

export function Sidebar({ recent, activeId, onNew, onOpen }: SidebarProps) {
  return (
    <aside className={styles.sidebar} aria-label="Onboardings">
      <div className={styles.brand}>
        <div className={styles.brandName}>
          Experience<b>+</b> Copilot
        </div>
        <div className={styles.brandSub}>Integration assistant</div>
      </div>

      <button type="button" className={styles.newButton} onClick={onNew}>
        <Plus size={18} strokeWidth={2.4} />
        New onboarding
      </button>

      <div className={styles.sessionList}>
        {recent.length === 0 && (
          <>
            <div className={styles.sectionLabel}>Your onboardings</div>
            <p className={styles.emptyList}>Onboardings you start will appear here.</p>
          </>
        )}
        {GROUPS.map((group) => {
          const items = recent.filter((s) => dayGroup(s.createdAt) === group);
          if (items.length === 0) return null;
          return (
            <section key={group}>
              <div className={styles.sectionLabel}>
                <span>{group}</span>
                <span>{items.length}</span>
              </div>
              {items.map((session) => (
                <button
                  type="button"
                  key={session.id}
                  className={`${styles.sessionItem} ${session.id === activeId ? styles.sessionItemActive : ""}`}
                  onClick={() => onOpen(session.id)}
                  aria-current={session.id === activeId ? "page" : undefined}
                >
                  <span className={styles.sessionTitle}>{session.title}</span>
                  <span className={styles.sessionMeta}>
                    <span>
                      {session.environment && (
                        <span className={styles.envTag}>{session.environment.toUpperCase()} · </span>
                      )}
                      {session.meta}
                    </span>
                    <span>{relativeTime(session.createdAt)}</span>
                  </span>
                </button>
              ))}
            </section>
          );
        })}
      </div>

      <div className={styles.sidebarFooter}>Capillary Technologies · Experience+</div>
    </aside>
  );
}
