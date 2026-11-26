import { CircleCheck, TriangleAlert } from "lucide-react";
import { useEffect, useState } from "react";
import { api } from "../api";
import type { SourcesStatus } from "../types";
import styles from "./freshness.module.css";

/** One line saying when the guides were last checked against Capillary's online docs. Hidden if that isn't known. */
export function SourceFreshness() {
  const [status, setStatus] = useState<SourcesStatus | null>(null);

  useEffect(() => {
    const controller = new AbortController();
    api
      .sourcesStatus(controller.signal)
      .then(setStatus)
      .catch(() => undefined);
    return () => controller.abort();
  }, []);

  if (!status?.synced || !status.synced_at) return null;
  const date = new Date(status.synced_at).toLocaleDateString(undefined, { day: "numeric", month: "short", year: "numeric" });
  const behind = status.pages_to_review > 0;
  return (
    <p className={`${styles.line} ${behind ? styles.behind : ""}`}>
      {behind ? <TriangleAlert size={14} /> : <CircleCheck size={14} />}
      {behind
        ? `Capillary's online docs changed since this was reviewed (${status.pages_to_review} page${status.pages_to_review === 1 ? "" : "s"}). Confirm important details with your Capillary contact.`
        : `Checked against Capillary's online docs on ${date}.`}
    </p>
  );
}
