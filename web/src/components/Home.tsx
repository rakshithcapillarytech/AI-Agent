import { ArrowRight } from "lucide-react";
import { PHASES } from "../lib/catalog";
import { type RecentSession, greeting, relativeTime } from "../lib/recent";
import type { Profile } from "../types";
import { ui } from "./controls";
import styles from "./home.module.css";
import { MarkTile } from "./MarkTile";
import { PageHeader } from "./PageHeader";
import { SetupWizard } from "./SetupWizard";

interface HomeProps {
  userName: string;
  recent: RecentSession[];
  onStart: (profile: Profile, name: string) => Promise<void>;
  onOpen: (id: string) => void;
}

export function Home({ userName, recent, onStart, onOpen }: HomeProps) {
  const firstName = userName.split(/\s+/)[0];

  return (
    <>
      <PageHeader title="Home" subtitle="Connect a new app, or pick up where you left off" />
      <div className={styles.scroll}>
        <div className={styles.content}>
          <div className={styles.eyebrowRow}>
            <span className={ui.eyebrow}>
              <MarkTile size={22} />
              Experience+ · Integration copilot
            </span>
            {recent.length > 0 && <span className={ui.pill}>{recent.length} onboardings</span>}
          </div>

          <h1 className={styles.greeting}>
            {greeting()}
            {firstName ? (
              <>
                , <span className={styles.name}>{firstName}</span>.
              </>
            ) : (
              "."
            )}
          </h1>
          <p className={styles.lede}>
            Tell us about your app, and we'll guide your team through connecting it to Capillary, step by step and in
            plain language.
          </p>

          <SetupWizard onStart={onStart} />

          <div className={styles.panels}>
            <section className={styles.panel} aria-labelledby="recent-title">
              <header className={styles.panelHeader}>
                <h2 id="recent-title">
                  Pick up where you left off <span className={styles.count}>{recent.length}</span>
                </h2>
              </header>
              {recent.length === 0 ? (
                <p className={styles.panelEmpty}>Your onboardings will appear here once you start one.</p>
              ) : (
                <ul className={styles.list}>
                  {recent.slice(0, 5).map((session) => (
                    <li key={session.id}>
                      <button type="button" className={styles.listItem} onClick={() => onOpen(session.id)}>
                        <span className={styles.initial}>{session.title[0]?.toUpperCase() ?? "?"}</span>
                        <span className={styles.listText}>
                          <span className={styles.listTitle}>{session.title}</span>
                          <span className={styles.listMeta}>
                            {session.environment && <b>{session.environment.toUpperCase()}</b>} {session.meta}
                          </span>
                        </span>
                        <span className={styles.listTime}>{relativeTime(session.createdAt)}</span>
                        <ArrowRight size={16} className={styles.listArrow} />
                      </button>
                    </li>
                  ))}
                </ul>
              )}
            </section>

            <section className={styles.panel} aria-labelledby="how-title">
              <header className={styles.panelHeader}>
                <h2 id="how-title">How it works</h2>
              </header>
              <ol className={styles.steps}>
                {PHASES.filter((p) => p.id !== "done").map((phase, index) => (
                  <li key={phase.id}>
                    <span className={styles.stepNumber}>{index + 1}</span>
                    <span>
                      <span className={styles.stepTitle}>{phase.label}</span>
                      <span className={styles.stepDetail}>{phase.detail}</span>
                    </span>
                  </li>
                ))}
              </ol>
            </section>
          </div>
        </div>
      </div>
    </>
  );
}
