import { Check, ClipboardCheck, Copy, RotateCcw } from "lucide-react";
import { type ComponentPropsWithoutRef, useRef, useState } from "react";
import Markdown from "react-markdown";
import { copyText } from "../lib/clipboard";
import remarkGfm from "remark-gfm";
import { CUSTOMER_IDS, ENVIRONMENTS, MODULES, REGIONS, labelOf, platformShort } from "../lib/catalog";
import type { ChatMessage, Profile } from "../types";
import { MarkTile } from "./MarkTile";
import styles from "./session.module.css";

function CodeBlock(props: ComponentPropsWithoutRef<"pre">) {
  const ref = useRef<HTMLPreElement>(null);
  const [copied, setCopied] = useState(false);
  const copy = async () => {
    if (!(await copyText(ref.current?.innerText ?? ""))) return;
    setCopied(true);
    setTimeout(() => setCopied(false), 1600);
  };
  return (
    <div className={styles.codeBlock}>
      <button type="button" className={styles.copyButton} onClick={copy} aria-label="Copy code">
        {copied ? <Check size={14} /> : <Copy size={14} />}
        {copied ? "Copied" : "Copy"}
      </button>
      <pre ref={ref} {...props} />
    </div>
  );
}

const markdownComponents = {
  pre: CodeBlock,
  a: (props: ComponentPropsWithoutRef<"a">) => <a {...props} target="_blank" rel="noreferrer" />,
};

function SetupCard({ profile }: { profile: Partial<Profile> }) {
  const rows = [
    ["Apps", (profile.platforms ?? []).map((p) => {
      const firebase = p.config_mode === "firebase" ? "with Firebase" : p.config_mode === "direct" ? "no Firebase" : "Firebase: not sure";
      return `${platformShort(p.platform)} (${firebase})`;
    }).join(", ")],
    ["Features", (profile.modules ?? []).map((m) => labelOf(MODULES, m)).join(", ")],
    ["Where", labelOf(ENVIRONMENTS, profile.environment)],
    ["Region", labelOf(REGIONS, profile.region)],
    ["Customers sign in with", labelOf(CUSTOMER_IDS, profile.customer_id_type)],
  ];
  return (
    <div className={styles.setupCard}>
      <div className={styles.setupHead}>
        <ClipboardCheck size={16} />
        Setup details for {profile.company || "your company"}
      </div>
      <dl>
        {rows.map(([label, value]) => (
          <div key={label}>
            <dt>{label}</dt>
            <dd>{value || "—"}</dd>
          </div>
        ))}
      </dl>
    </div>
  );
}

interface MessageProps {
  message: ChatMessage;
  profile: Partial<Profile>;
  onRetry: () => void;
}

export function Message({ message, profile, onRetry }: MessageProps) {
  if (message.kind === "setup") {
    return (
      <div className={styles.userRow}>
        <SetupCard profile={profile} />
      </div>
    );
  }

  if (message.role === "user") {
    return (
      <div className={styles.userRow}>
        <div className={styles.userBubble}>{message.text}</div>
      </div>
    );
  }

  const waiting = message.status === "streaming" && !message.text;
  return (
    <div className={styles.assistantRow}>
      <MarkTile size={28} />
      <div className={`${styles.assistantBody} ${message.status === "error" ? styles.errorBody : ""}`}>
        {waiting ? (
          <span className={styles.typing} aria-label="The assistant is thinking">
            <i />
            <i />
            <i />
          </span>
        ) : (
          <div className={styles.markdown}>
            <Markdown remarkPlugins={[remarkGfm]} components={markdownComponents}>
              {message.text}
            </Markdown>
          </div>
        )}
        {message.status === "error" && (
          <button type="button" className={styles.retry} onClick={onRetry}>
            <RotateCcw size={14} /> Try again
          </button>
        )}
      </div>
    </div>
  );
}
