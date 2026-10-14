import { Check, type LucideIcon } from "lucide-react";
import type { ReactNode } from "react";
import styles from "./ui.module.css";

interface ChoiceCardProps {
  label: string;
  hint?: string;
  icon?: LucideIcon;
  selected: boolean;
  onToggle?: () => void;
  /** Shown instead of being toggleable, e.g. "Always included". */
  lockedBadge?: string;
  role?: "checkbox" | "radio";
}

/** A large, clickable option: easier for non-technical users than checkboxes or dropdowns. */
export function ChoiceCard({
  label,
  hint,
  icon: Icon,
  selected,
  onToggle,
  lockedBadge,
  role = "checkbox",
}: ChoiceCardProps) {
  return (
    <button
      type="button"
      role={role}
      aria-checked={selected}
      className={`${styles.choice} ${selected ? styles.choiceSelected : ""}`}
      onClick={onToggle}
      disabled={!!lockedBadge}
    >
      {Icon && (
        <span className={styles.choiceIcon}>
          <Icon size={18} strokeWidth={1.9} />
        </span>
      )}
      <span className={styles.choiceText}>
        <span className={styles.choiceLabel}>{label}</span>
        {hint && <span className={styles.choiceHint}>{hint}</span>}
        {lockedBadge && <span className={styles.badge}>{lockedBadge}</span>}
      </span>
      <span className={styles.choiceCheck} aria-hidden="true">
        <Check size={12} strokeWidth={3} />
      </span>
    </button>
  );
}

export function ChoiceGrid({ children, label }: { children: ReactNode; label: string }) {
  return (
    <div className={styles.choiceGrid} role="group" aria-label={label}>
      {children}
    </div>
  );
}

interface SegmentedProps<T extends string> {
  label: string;
  value: T | null;
  options: { id: T; label: string }[];
  onChange: (value: T) => void;
}

export function Segmented<T extends string>({ label, value, options, onChange }: SegmentedProps<T>) {
  return (
    <div className={styles.segmented} role="radiogroup" aria-label={label}>
      {options.map((option) => (
        <button
          key={option.id}
          type="button"
          role="radio"
          aria-checked={value === option.id}
          className={`${styles.segment} ${value === option.id ? styles.segmentActive : ""}`}
          onClick={() => onChange(option.id)}
        >
          {option.label}
        </button>
      ))}
    </div>
  );
}

interface TextFieldProps {
  label: string;
  value: string;
  onChange: (value: string) => void;
  placeholder?: string;
  optional?: boolean;
  type?: "text" | "email" | "date";
  autoFocus?: boolean;
}

export function TextField({ label, value, onChange, placeholder, optional, type = "text", autoFocus }: TextFieldProps) {
  return (
    <label className={styles.field}>
      <span className={styles.fieldLabel}>
        {label} {optional && <span className={styles.optional}>(optional)</span>}
      </span>
      <input
        className={styles.input}
        type={type}
        value={value}
        placeholder={placeholder}
        onChange={(event) => onChange(event.target.value)}
        autoFocus={autoFocus}
      />
    </label>
  );
}

export function EnvPill({ environment }: { environment: string | null | undefined }) {
  if (!environment) return null;
  const isProd = environment === "production";
  return (
    <span className={`${styles.pill} ${isProd ? styles.pillProd : styles.pillUat}`}>
      <span className={styles.dot} />
      {isProd ? "Production" : "UAT"}
    </span>
  );
}

export { styles as ui };
