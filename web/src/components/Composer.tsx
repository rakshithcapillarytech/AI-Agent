import { ArrowUp } from "lucide-react";
import { type KeyboardEvent, forwardRef, useEffect, useImperativeHandle, useRef } from "react";
import { platformShort } from "../lib/catalog";
import type { Profile } from "../types";
import { EnvPill, ui } from "./controls";
import styles from "./session.module.css";

export interface ComposerHandle {
  focus: () => void;
}

interface ComposerProps {
  value: string;
  onChange: (value: string) => void;
  onSend: () => void;
  disabled: boolean;
  profile: Partial<Profile>;
}

export const Composer = forwardRef<ComposerHandle, ComposerProps>(function Composer(
  { value, onChange, onSend, disabled, profile },
  ref,
) {
  const textarea = useRef<HTMLTextAreaElement>(null);

  useImperativeHandle(ref, () => ({
    focus: () => {
      const el = textarea.current;
      if (!el) return;
      el.focus();
      el.setSelectionRange(el.value.length, el.value.length);
    },
  }));

  // Grow with the content, up to a limit.
  useEffect(() => {
    const el = textarea.current;
    if (!el) return;
    el.style.height = "auto";
    el.style.height = `${Math.min(el.scrollHeight, 220)}px`;
  }, [value]);

  const canSend = !disabled && value.trim().length > 0;

  const onKeyDown = (event: KeyboardEvent<HTMLTextAreaElement>) => {
    if (event.key === "Enter" && !event.shiftKey && !event.nativeEvent.isComposing) {
      event.preventDefault();
      if (canSend) onSend();
    }
  };

  return (
    <div className={styles.composer}>
      <label className="visually-hidden" htmlFor="composer">
        Message the assistant
      </label>
      <textarea
        id="composer"
        ref={textarea}
        className={styles.composerInput}
        rows={2}
        value={value}
        placeholder="Ask anything about your setup, or paste an error message…"
        onChange={(event) => onChange(event.target.value)}
        onKeyDown={onKeyDown}
      />
      <div className={styles.composerBar}>
        <div className={styles.composerContext}>
          <EnvPill environment={profile.environment} />
          {(profile.platforms ?? []).map((p) => (
            <span key={p.platform} className={ui.pill}>
              {platformShort(p.platform)}
            </span>
          ))}
          <span className={styles.composerHint}>Enter to send · Shift + Enter for a new line</span>
        </div>
        <button type="button" className={styles.sendButton} onClick={onSend} disabled={!canSend}>
          <ArrowUp size={16} strokeWidth={2.4} />
          Send
        </button>
      </div>
    </div>
  );
});
