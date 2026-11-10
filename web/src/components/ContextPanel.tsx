import { BookOpen, Check } from "lucide-react";
import { MODULES, PHASES, guideLabel, labelOf, phaseIndex, platformShort } from "../lib/catalog";
import type { SessionState } from "../types";
import { Checklist } from "./Checklist";
import { ui } from "./controls";
import { GuideDownload } from "./GuideDownload";
import { PromptCopy } from "./PromptCopy";
import { Steps } from "./Steps";
import styles from "./session.module.css";

interface ContextPanelProps {
  sessionId: string;
  session: SessionState;
  busy: boolean;
  onUpload: (file: File) => void;
}

export function ContextPanel({ sessionId, session, busy, onUpload }: ContextPanelProps) {
  const current = phaseIndex(session.phase);
  const profile = session.profile;

  return (
    <aside className={styles.context} aria-label="Onboarding details">
      <section>
        <h3 className={styles.contextTitle}>Your progress</h3>
        <ol className={styles.journey}>
          {PHASES.map((phase, index) => {
            const state = index < current ? "done" : index === current ? "current" : "todo";
            return (
              <li key={phase.id} className={styles[`journey_${state}`]} aria-current={state === "current" ? "step" : undefined}>
                <span className={styles.journeyDot}>{state === "done" && <Check size={11} strokeWidth={3} />}</span>
                <span>
                  <span className={styles.journeyLabel}>{phase.label}</span>
                  <span className={styles.journeyDetail}>{phase.detail}</span>
                </span>
              </li>
            );
          })}
        </ol>
      </section>

      <section>
        <h3 className={styles.contextTitle}>Your checklist</h3>
        <Checklist items={session.prerequisites ?? []} busy={busy} onUpload={onUpload} />
      </section>

      {(session.plan_steps ?? []).length > 0 && (
        <section>
          <h3 className={styles.contextTitle}>Your integration steps</h3>
          <Steps steps={session.plan_steps} current={session.current_step} />
        </section>
      )}

      <section className={styles.guideCard}>
        <h3 className={styles.contextTitle}>Use with your own AI</h3>
        <p>
          <b>First</b>, download the documentation for your exact setup as one file, and attach it in Claude, Cursor
          or ChatGPT.
        </p>
        <GuideDownload sessionId={sessionId} ready={session.guide_ready} variant="panel" />
        <PromptCopy profile={profile} ready={session.guide_ready} />
      </section>

      <section>
        <h3 className={styles.contextTitle}>Your setup</h3>
        <div className={styles.chips}>
          {(profile.platforms ?? []).map((p) => (
            <span key={p.platform} className={ui.pill}>
              {platformShort(p.platform)}
              {p.config_mode === "firebase" ? " · Firebase" : p.config_mode === "direct" ? " · no Firebase" : " · Firebase?"}
            </span>
          ))}
        </div>
        <div className={styles.chips}>
          {(profile.modules ?? []).map((m) => (
            <span key={m} className={styles.featureChip}>
              {labelOf(MODULES, m)}
            </span>
          ))}
        </div>
      </section>

      <section>
        <h3 className={styles.contextTitle}>Guides in use</h3>
        {session.loaded_files.length === 0 ? (
          <p className={styles.contextEmpty}>Guides load once your setup details are confirmed.</p>
        ) : (
          <ul className={styles.guides}>
            {session.loaded_files.map((path) => (
              <li key={path} title={path}>
                <BookOpen size={14} />
                {guideLabel(path)}
              </li>
            ))}
          </ul>
        )}
      </section>
    </aside>
  );
}
