import { Bug, Check, ChevronDown, Copy, Wrench } from "lucide-react";
import { useState } from "react";
import { copyText } from "../lib/clipboard";
import { type PromptKind, buildPrompt } from "../lib/prompts";
import type { Profile } from "../types";
import { ui } from "./controls";
import styles from "./session.module.css";

const PROMPTS: { kind: PromptKind; label: string; icon: typeof Wrench }[] = [
  { kind: "setup", label: "Copy “Help me set up” prompt", icon: Wrench },
  { kind: "debug", label: "Copy “Help me debug” prompt", icon: Bug },
];

interface PromptCopyProps {
  profile: Partial<Profile>;
  ready: boolean;
}

/** Copy buttons for the two ready-made prompts, personalised with the client's setup. */
export function PromptCopy({ profile, ready }: PromptCopyProps) {
  const [copied, setCopied] = useState<PromptKind | null>(null);
  const [preview, setPreview] = useState<PromptKind | null>(null);

  const [failed, setFailed] = useState<PromptKind | null>(null);

  const copy = async (kind: PromptKind) => {
    if (await copyText(buildPrompt(kind, profile))) {
      setFailed(null);
      setCopied(kind);
      setTimeout(() => setCopied((current) => (current === kind ? null : current)), 1800);
    } else {
      // Clipboard blocked: show the prompt so it can be selected and copied by hand.
      setFailed(kind);
      setPreview(kind);
    }
  };

  return (
    <div className={styles.prompts}>
      <p className={styles.promptsHint}>
        <b>Then</b> paste one of these prompts with the file attached, and fill in the last line.
      </p>
      {PROMPTS.map(({ kind, label, icon: Icon }) => (
        <div key={kind} className={styles.promptRow}>
          <button
            type="button"
            className={`${ui.button} ${ui.small} ${ui.block}`}
            onClick={() => copy(kind)}
            disabled={!ready}
            title={ready ? undefined : "Available once we know whether each app uses Firebase."}
          >
            {copied === kind ? <Check size={15} /> : <Icon size={15} />}
            {copied === kind ? "Copied: paste it in your AI" : label}
          </button>
          {ready && (
            <button
              type="button"
              className={styles.previewToggle}
              onClick={() => setPreview(preview === kind ? null : kind)}
              aria-expanded={preview === kind}
            >
              {preview === kind ? "Hide" : "Preview"}
              <ChevronDown size={13} className={preview === kind ? styles.flipped : undefined} />
            </button>
          )}
          {failed === kind && (
            <span className={styles.copyFailed}>Your browser blocked copying. Select the text below and copy it.</span>
          )}
          {preview === kind && (
            <pre className={styles.promptPreview}>
              {buildPrompt(kind, profile)}
              <button type="button" className={styles.previewCopy} onClick={() => copy(kind)} aria-label="Copy prompt">
                <Copy size={13} />
              </button>
            </pre>
          )}
        </div>
      ))}
    </div>
  );
}
