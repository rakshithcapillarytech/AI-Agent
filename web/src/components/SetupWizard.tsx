import { ArrowLeft, ArrowRight, Check, Info, Loader2 } from "lucide-react";
import { useEffect, useMemo, useRef, useState } from "react";
import {
  CUSTOMER_IDS,
  ENVIRONMENTS,
  MODULES,
  PLATFORMS,
  REGIONS,
  labelOf,
  platformShort,
} from "../lib/catalog";
import type { CustomerIdType, Environment, Module, Platform, Profile, Region } from "../types";
import { ChoiceCard, ChoiceGrid, Segmented, TextField, ui } from "./controls";
import styles from "./wizard.module.css";

type FirebaseAnswer = "yes" | "no" | "unsure";

interface Draft {
  company: string;
  name: string;
  email: string;
  goLive: string;
  platforms: { platform: Platform; firebase: FirebaseAnswer | null }[];
  modules: Module[];
  environment: Environment | null;
  region: Region | null;
  customerId: CustomerIdType | null;
}

const EMPTY: Draft = {
  company: "",
  name: "",
  email: "",
  goLive: "",
  platforms: [],
  modules: ["core"],
  environment: null,
  region: null,
  customerId: null,
};

const STEPS = ["Your company", "Your apps", "Features", "Account", "Review"] as const;

const FIREBASE_OPTIONS: { id: FirebaseAnswer; label: string }[] = [
  { id: "yes", label: "Yes" },
  { id: "no", label: "No" },
  { id: "unsure", label: "Not sure" },
];

/** Why the user can't continue from a step yet, or null when the step is complete. */
function blocker(step: number, draft: Draft): string | null {
  switch (step) {
    case 0:
      return draft.company.trim() ? null : "Enter your company name to continue.";
    case 1:
      if (draft.platforms.length === 0) return "Pick at least one app.";
      return draft.platforms.some((p) => p.firebase === null)
        ? "Answer the Firebase question for each app."
        : null;
    case 3:
      if (!draft.environment) return "Choose where you're setting this up.";
      if (!draft.region) return "Choose your region.";
      return draft.customerId ? null : "Choose how your customers sign in.";
    default:
      return null;
  }
}

function toProfile(draft: Draft): Profile {
  const contact = [draft.name.trim(), draft.email.trim() && `<${draft.email.trim()}>`]
    .filter(Boolean)
    .join(" ");
  return {
    company: draft.company.trim(),
    platforms: draft.platforms.map(({ platform, firebase }) => ({
      platform,
      config_mode: firebase === "yes" ? "firebase" : firebase === "no" ? "direct" : null,
    })),
    modules: draft.modules,
    environment: draft.environment,
    region: draft.region,
    customer_id_type: draft.customerId,
    contacts: contact ? [contact] : [],
    go_live_date: draft.goLive || null,
  };
}

interface SetupWizardProps {
  onStart: (profile: Profile, name: string) => Promise<void>;
}

export function SetupWizard({ onStart }: SetupWizardProps) {
  const [step, setStep] = useState(0);
  const [draft, setDraft] = useState<Draft>(EMPTY);
  const [submitting, setSubmitting] = useState(false);
  const [submitError, setSubmitError] = useState<string | null>(null);
  const card = useRef<HTMLElement>(null);

  // On a new step, bring the card's top back into view if it has scrolled above the fold.
  useEffect(() => {
    const el = card.current;
    if (el && el.getBoundingClientRect().top < 0) el.scrollIntoView({ block: "start", behavior: "smooth" });
  }, [step]);

  const update = (changes: Partial<Draft>) => setDraft((d) => ({ ...d, ...changes }));
  const stepBlocker = blocker(step, draft);
  const isLast = step === STEPS.length - 1;
  const hasUnsure = draft.platforms.some((p) => p.firebase === "unsure");

  const togglePlatform = (platform: Platform) =>
    update({
      platforms: draft.platforms.some((p) => p.platform === platform)
        ? draft.platforms.filter((p) => p.platform !== platform)
        : [...draft.platforms, { platform, firebase: null }],
    });

  const setFirebase = (platform: Platform, firebase: FirebaseAnswer) =>
    update({ platforms: draft.platforms.map((p) => (p.platform === platform ? { ...p, firebase } : p)) });

  const toggleModule = (module: Module) => {
    const on = draft.modules.includes(module);
    let modules = on ? draft.modules.filter((m) => m !== module) : [...draft.modules, module];
    // The ready-made inbox screen is built on the inbox, so they go together.
    if (!on && module === "inbox_ui" && !modules.includes("inbox_api")) modules = [...modules, "inbox_api"];
    if (on && module === "inbox_api") modules = modules.filter((m) => m !== "inbox_ui");
    update({ modules });
  };

  const next = async () => {
    if (stepBlocker) return;
    if (!isLast) {
      setStep(step + 1);
      return;
    }
    setSubmitting(true);
    setSubmitError(null);
    try {
      await onStart(toProfile(draft), draft.name.trim());
    } catch {
      setSubmitError("We couldn't start your onboarding. Check that the server is running, then try again.");
      setSubmitting(false);
    }
  };

  const reviewRows = useMemo(
    () => [
      { label: "Company", value: draft.company || "—", step: 0 },
      { label: "Contact", value: [draft.name, draft.email].filter(Boolean).join(" · ") || "—", step: 0 },
      {
        label: "Apps",
        value:
          draft.platforms
            .map((p) => {
              const firebase = p.firebase === "yes" ? "uses Firebase" : p.firebase === "no" ? "no Firebase" : "Firebase: not sure";
              return `${platformShort(p.platform)} (${firebase})`;
            })
            .join(", ") || "—",
        step: 1,
      },
      { label: "Features", value: draft.modules.map((m) => labelOf(MODULES, m)).join(", "), step: 2 },
      { label: "Where", value: labelOf(ENVIRONMENTS, draft.environment), step: 3 },
      { label: "Region", value: labelOf(REGIONS, draft.region), step: 3 },
      { label: "Customers sign in with", value: labelOf(CUSTOMER_IDS, draft.customerId), step: 3 },
      { label: "Target go-live", value: draft.goLive || "—", step: 0 },
    ],
    [draft],
  );

  return (
    <section ref={card} className={styles.card} aria-label="Set up a new onboarding">
      <ol className={styles.stepper}>
        {STEPS.map((label, index) => (
          <li
            key={label}
            className={`${styles.stepItem} ${index === step ? styles.stepCurrent : ""} ${index < step ? styles.stepDone : ""}`}
            aria-current={index === step ? "step" : undefined}
          >
            <span className={styles.stepDot}>{index < step ? <Check size={12} strokeWidth={3} /> : index + 1}</span>
            <span className={styles.stepLabel}>{label}</span>
          </li>
        ))}
      </ol>

      <div className={styles.body}>
        {step === 0 && (
          <>
            <StepIntro title="Who are we helping today?" text="We'll use this to personalise your onboarding." />
            <div className={styles.fieldGrid}>
              <TextField label="Company name" value={draft.company} onChange={(company) => update({ company })} placeholder="e.g. Demo Retail" />
              <TextField label="Your name" value={draft.name} onChange={(name) => update({ name })} placeholder="e.g. Priya Sharma" optional />
              <TextField label="Work email" type="email" value={draft.email} onChange={(email) => update({ email })} placeholder="you@company.com" optional />
              <TextField label="Target go-live date" type="date" value={draft.goLive} onChange={(goLive) => update({ goLive })} optional />
            </div>
          </>
        )}

        {step === 1 && (
          <>
            <StepIntro title="Which apps do you want to connect?" text="Pick everything you'd like to connect. You can choose more than one." />
            <ChoiceGrid label="Apps">
              {PLATFORMS.map((p) => (
                <ChoiceCard
                  key={p.id}
                  label={p.label}
                  hint={p.hint}
                  icon={p.icon}
                  selected={draft.platforms.some((x) => x.platform === p.id)}
                  onToggle={() => togglePlatform(p.id)}
                />
              ))}
            </ChoiceGrid>

            {draft.platforms.length > 0 && (
              <div className={styles.followUp}>
                <div className={styles.followUpHead}>
                  <h3>Does each app use Firebase?</h3>
                  <p>
                    Firebase is a Google service many apps use for notifications and settings. If you don't know, choose
                    “Not sure” and we'll work it out together.
                  </p>
                </div>
                {draft.platforms.map(({ platform, firebase }) => (
                  <div key={platform} className={styles.followUpRow}>
                    <span>{labelOf(PLATFORMS, platform)}</span>
                    <Segmented
                      label={`Does the ${labelOf(PLATFORMS, platform)} use Firebase?`}
                      value={firebase}
                      options={FIREBASE_OPTIONS}
                      onChange={(answer) => setFirebase(platform, answer)}
                    />
                  </div>
                ))}
              </div>
            )}
          </>
        )}

        {step === 2 && (
          <>
            <StepIntro title="What would you like to use?" text="Choose the features you need. You can add more later." />
            <ChoiceGrid label="Features">
              {MODULES.map((m) => (
                <ChoiceCard
                  key={m.id}
                  label={m.label}
                  hint={m.hint}
                  icon={m.icon}
                  selected={draft.modules.includes(m.id)}
                  onToggle={() => toggleModule(m.id)}
                  lockedBadge={m.id === "core" ? "Always included" : undefined}
                />
              ))}
            </ChoiceGrid>
          </>
        )}

        {step === 3 && (
          <>
            <StepIntro title="A few account details" text="Your Capillary contact can help if you're unsure about any of these." />
            <h3 className={styles.groupTitle}>Where are you setting this up?</h3>
            <ChoiceGrid label="Environment">
              {ENVIRONMENTS.map((e) => (
                <ChoiceCard key={e.id} role="radio" label={e.label} hint={e.hint} icon={e.icon} selected={draft.environment === e.id} onToggle={() => update({ environment: e.id })} />
              ))}
            </ChoiceGrid>
            <h3 className={styles.groupTitle}>Which region is your Capillary account in?</h3>
            <ChoiceGrid label="Region">
              {REGIONS.map((r) => (
                <ChoiceCard key={r.id} role="radio" label={r.label} hint={r.hint} selected={draft.region === r.id} onToggle={() => update({ region: r.id })} />
              ))}
            </ChoiceGrid>
            <h3 className={styles.groupTitle}>How do your customers sign in?</h3>
            <p className={styles.groupHint}>This must match the “Account Linking Identifier” set in Capillary CRM.</p>
            <ChoiceGrid label="Customer sign-in">
              {CUSTOMER_IDS.map((c) => (
                <ChoiceCard key={c.id} role="radio" label={c.label} hint={c.hint} selected={draft.customerId === c.id} onToggle={() => update({ customerId: c.id })} />
              ))}
            </ChoiceGrid>
          </>
        )}

        {step === 4 && (
          <>
            <StepIntro title="Check your details" text="Everything look right? You can change anything before you start." />
            <dl className={styles.review}>
              {reviewRows.map((row) => (
                <div key={row.label} className={styles.reviewRow}>
                  <dt>{row.label}</dt>
                  <dd>{row.value}</dd>
                  <button type="button" className={`${ui.button} ${ui.ghost} ${ui.small}`} onClick={() => setStep(row.step)}>
                    Edit
                  </button>
                </div>
              ))}
            </dl>
            {hasUnsure && (
              <p className={styles.note}>
                <Info size={16} /> You weren't sure about Firebase for some apps. The assistant will help you check
                first.
              </p>
            )}
          </>
        )}
      </div>

      <footer className={styles.footer}>
        <span className={styles.progress}>
          Step {step + 1} of {STEPS.length}
        </span>
        <div className={styles.footerActions}>
          {(submitError || stepBlocker) && <span className={styles.blocker}>{submitError ?? stepBlocker}</span>}
          {step > 0 && (
            <button type="button" className={ui.button} onClick={() => setStep(step - 1)} disabled={submitting}>
              <ArrowLeft size={16} /> Back
            </button>
          )}
          <button type="button" className={`${ui.button} ${ui.primary}`} onClick={next} disabled={!!stepBlocker || submitting}>
            {submitting ? (
              <>
                <Loader2 size={16} className={styles.spin} /> Starting…
              </>
            ) : isLast ? (
              <>
                Start onboarding <ArrowRight size={16} />
              </>
            ) : (
              <>
                Continue <ArrowRight size={16} />
              </>
            )}
          </button>
        </div>
      </footer>
    </section>
  );
}

function StepIntro({ title, text }: { title: string; text: string }) {
  return (
    <div className={styles.intro}>
      <h2>{title}</h2>
      <p>{text}</p>
    </div>
  );
}
