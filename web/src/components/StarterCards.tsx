import { ArrowRight, CircleCheck, ClipboardList, type LucideIcon, TriangleAlert, Wrench } from "lucide-react";
import styles from "./session.module.css";

interface Starter {
  category: string;
  icon: LucideIcon;
  tone: "green" | "blue" | "magenta" | "orange";
  text: string;
  /** Sent as-is, or (with `prefill`) placed in the composer for the user to finish. */
  prompt: string;
  prefill?: boolean;
}

const STARTERS: Starter[] = [
  {
    category: "Before you start",
    icon: ClipboardList,
    tone: "green",
    text: "What do we need to prepare before we start?",
    prompt: "What do we need to prepare before we start?",
  },
  {
    category: "Setup steps",
    icon: Wrench,
    tone: "blue",
    text: "Walk us through the setup steps, one at a time.",
    prompt: "Walk us through the setup steps, one at a time.",
  },
  {
    category: "Errors & fixes",
    icon: TriangleAlert,
    tone: "magenta",
    text: "We're seeing an error and need help fixing it.",
    prompt: "We're seeing this error: ",
    prefill: true,
  },
  {
    category: "Testing",
    icon: CircleCheck,
    tone: "orange",
    text: "How do we check that everything is working?",
    prompt: "How do we check that everything is working?",
  },
];

interface StarterCardsProps {
  onSend: (text: string) => void;
  onPrefill: (text: string) => void;
}

export function StarterCards({ onSend, onPrefill }: StarterCardsProps) {
  return (
    <section className={styles.starters} aria-labelledby="starters-title">
      <h2 id="starters-title" className={styles.startersTitle}>
        Start from a common question
      </h2>
      <div className={styles.starterGrid}>
        {STARTERS.map(({ category, icon: Icon, tone, text, prompt, prefill }) => (
          <button
            key={category}
            type="button"
            className={`${styles.starter} ${styles[tone]}`}
            onClick={() => (prefill ? onPrefill(prompt) : onSend(prompt))}
          >
            <span className={styles.starterCategory}>
              <span className={styles.starterIcon}>
                <Icon size={15} />
              </span>
              {category}
            </span>
            <span className={styles.starterText}>{text}</span>
            <span className={styles.starterUse}>
              Use this <ArrowRight size={13} />
            </span>
          </button>
        ))}
      </div>
    </section>
  );
}
