import { Download } from "lucide-react";
import { api } from "../api";
import { ui } from "./controls";

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
