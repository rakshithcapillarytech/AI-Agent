import { Download, FileText } from "lucide-react";
import { api } from "../api";
import { ui } from "./controls";
import styles from "./session.module.css";

interface GuideDownloadProps {
  sessionId: string;
  ready: boolean;
  /** "header" is compact; "panel" is the full-width call to action in the details panel. */
  variant: "header" | "panel";
}

const NOT_READY = "Available once we know whether each app uses Firebase.";

/** Downloads the client's tailored Markdown guide, to attach to their own AI assistant. */
export function GuideDownload({ sessionId, ready, variant }: GuideDownloadProps) {
  const className =
    variant === "header" ? `${ui.button} ${ui.small}` : `${ui.button} ${ui.primary} ${ui.block}`;
  const label = variant === "header" ? "AI guide" : "Download AI guide (.md)";

  if (!ready) {
    return (
      <button type="button" className={className} disabled title={NOT_READY}>
        <Download size={15} /> {label}
      </button>
    );
  }
  return (
    <a
      className={className}
      href={api.guideUrl(sessionId)}
      download
      title="Download your setup's documentation as one Markdown file for Claude, Cursor or ChatGPT"
    >
      <Download size={15} /> {label}
    </a>
  );
}

/** A short readable summary of the steps: save it as a PDF from the browser, keep the .html, or open the long version. */
export function StepsDownload({ sessionId, ready }: { sessionId: string; ready: boolean }) {
  if (!ready) {
    return (
      <div className={styles.stepsButtons}>
        <button type="button" className={`${ui.button} ${ui.primary} ${ui.block}`} disabled title={NOT_READY}>
          <FileText size={15} /> Save steps as PDF
        </button>
      </div>
    );
  }
  return (
    <div className={styles.stepsButtons}>
      <a
        className={`${ui.button} ${ui.primary} ${ui.block}`}
        href={`${api.stepsUrl(sessionId)}#print`}
        target="_blank"
        rel="noreferrer"
        title="Opens your short summary and the print window; choose Save as PDF"
      >
        <FileText size={15} /> Save steps as PDF
      </a>
      <span className={styles.stepsLinks}>
        <a href={api.stepsUrl(sessionId, { download: true })} download>
          Download .html
        </a>
        <span aria-hidden="true">·</span>
        <a href={`${api.stepsUrl(sessionId, { full: true })}#print`} target="_blank" rel="noreferrer" title="Every section with all the code (long)">
          Full version with code
        </a>
      </span>
    </div>
  );
}
