import { Check, Link2, PanelRight } from "lucide-react";
import { useEffect, useRef, useState } from "react";
import { PHASES, phaseIndex } from "../lib/catalog";
import { copyText } from "../lib/clipboard";
import { useConversation } from "../lib/useConversation";
import type { Profile } from "../types";
import { Composer, type ComposerHandle } from "./Composer";
import { ContextPanel } from "./ContextPanel";
import { EnvPill, ui } from "./controls";
import { GuideDownload } from "./GuideDownload";
import { Message } from "./Message";
import { PageHeader } from "./PageHeader";
import styles from "./session.module.css";
import { StarterCards } from "./StarterCards";

interface SessionViewProps {
  id: string;
  startProfile?: Profile;
  onHome: () => void;
}

function CopyLinkButton() {
  const [copied, setCopied] = useState(false);
  const copy = async () => {
    if (!(await copyText(window.location.href))) return;
    setCopied(true);
    setTimeout(() => setCopied(false), 1600);
  };
  return (
    <button type="button" className={`${ui.button} ${ui.small}`} onClick={copy} title="Anyone with this link can continue this onboarding">
      {copied ? <Check size={15} /> : <Link2 size={15} />}
      {copied ? "Link copied" : "Copy link"}
    </button>
  );
}

export function SessionView({ id, startProfile, onHome }: SessionViewProps) {
  const { session, messages, busy, loadError, send, retry } = useConversation(id, startProfile);
  const [draft, setDraft] = useState("");
  const [showDetails, setShowDetails] = useState(false);
  const composer = useRef<ComposerHandle>(null);
  const scroller = useRef<HTMLDivElement>(null);
  const stickToBottom = useRef(true);

  useEffect(() => {
    const el = scroller.current;
    if (el && stickToBottom.current) el.scrollTop = el.scrollHeight;
  }, [messages]);

  const sendText = (text: string) => {
    stickToBottom.current = true;
    void send(text);
  };

  if (loadError || (session && !startProfile && session.messages.length === 0 && messages.length === 0)) {
    return (
      <>
        <PageHeader title="Onboarding not found" subtitle="This link doesn't match an onboarding that has started" />
        <div className={styles.centered}>
          <p>Start a new onboarding from the home page.</p>
          <button type="button" className={`${ui.button} ${ui.primary}`} onClick={onHome}>
            Go to home
          </button>
        </div>
      </>
    );
  }

  if (!session) {
    return (
      <>
        <PageHeader title="Loading your onboarding…" subtitle="One moment" />
        <div className={styles.centered}>
          <span className={styles.typing} aria-label="Loading">
            <i />
            <i />
            <i />
          </span>
        </div>
      </>
    );
  }

  const current = phaseIndex(session.phase);
  const hasAskedSomething = messages.some((m) => m.role === "user" && m.kind === "chat");

  const submit = () => {
    const text = draft.trim();
    if (!text || busy) return;
    setDraft("");
    sendText(text);
  };

  const prefill = (text: string) => {
    setDraft(text);
    requestAnimationFrame(() => composer.current?.focus());
  };

  return (
    <>
      <PageHeader
        title={session.profile.company ? `${session.profile.company} onboarding` : "Your onboarding"}
        subtitle={`Step ${current + 1} of ${PHASES.length} · ${PHASES[current]?.label ?? ""}`}
        actions={
          <>
            <EnvPill environment={session.profile.environment} />
            <GuideDownload sessionId={id} ready={session.guide_ready} variant="header" />
            <CopyLinkButton />
            <button
              type="button"
              className={`${ui.button} ${ui.small} ${styles.detailsToggle}`}
              onClick={() => setShowDetails((v) => !v)}
              aria-expanded={showDetails}
            >
              <PanelRight size={15} /> Details
            </button>
          </>
        }
      />
      <div className={styles.layout}>
        <div className={styles.threadColumn}>
          <div
            ref={scroller}
            className={styles.scroll}
            onScroll={(event) => {
              const el = event.currentTarget;
              stickToBottom.current = el.scrollHeight - el.scrollTop - el.clientHeight < 120;
            }}
          >
            <div className={styles.thread} aria-live="polite">
              {messages.map((message, index) => (
                <Message key={index} message={message} profile={session.profile} onRetry={retry} />
              ))}
              {!hasAskedSomething && !busy && <StarterCards onSend={sendText} onPrefill={prefill} />}
            </div>
          </div>
          <div className={styles.composerDock}>
            <Composer
              ref={composer}
              value={draft}
              onChange={setDraft}
              onSend={submit}
              disabled={busy}
              profile={session.profile}
            />
          </div>
        </div>
        <div className={`${styles.contextWrap} ${showDetails ? styles.contextOpen : ""}`}>
          <ContextPanel sessionId={id} session={session} />
        </div>
      </div>
    </>
  );
}
