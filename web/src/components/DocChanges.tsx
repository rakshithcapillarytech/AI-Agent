import { ExternalLink, RefreshCw } from "lucide-react";
import { useState } from "react";
import { api } from "../api";
import type { SourcesAdmin } from "../types";
import styles from "./admin.module.css";
import { ui } from "./controls";

const when = (iso: string | null | undefined) => (iso ? new Date(iso).toLocaleString() : "never");

/** "20261203-101500" (how the update names its branch) as a readable date. */
const stamp = (value: string) => {
  const m = /^(\d{4})(\d{2})(\d{2})/.exec(value);
  return m ? new Date(Number(m[1]), Number(m[2]) - 1, Number(m[3])).toLocaleDateString(undefined, { day: "numeric", month: "short", year: "numeric" }) : value;
};

/**
 * Capillary's online docs against our guides: pages that changed after a person last reviewed them (with the diff),
 * key facts that no longer match, and a button to fetch the docs now. Mark pages reviewed once the guides are updated.
 */
export function DocChanges({ data, onChange }: { data: SourcesAdmin | null; onChange: () => void }) {
  const [busy, setBusy] = useState<string | null>(null);
  const [message, setMessage] = useState<string | null>(null);

  const run = async (key: string, action: () => Promise<void>) => {
    setBusy(key);
    setMessage(null);
    try {
      await action();
      onChange();
    } catch {
      setMessage("That didn't work. If a sync is already running, wait for it to finish.");
    } finally {
      setBusy(null);
    }
  };

  const syncNow = () =>
    run("sync", async () => {
      const result = await api.syncSources();
      const failed = Object.keys(result.failed).length;
      setMessage(
        `Fetched the docs: ${result.changed.length} changed, ${result.added.length} new${failed ? `, ${failed} couldn't be fetched (the old copy was kept)` : ""}.`,
      );
    });

  if (data === null) return <p className={styles.empty}>Loading…</p>;

  const header = (
    <div className={styles.actions}>
      <span className={styles.meta}>
        {data.synced
          ? `Last fetched ${when(data.synced_at)} · ${data.pages} pages · ${data.anchors.total - data.anchors.failing.length} of ${data.anchors.total} key facts match`
          : (data.reason ?? "Not fetched yet.")}
      </span>
      <button type="button" className={`${ui.button} ${ui.small}`} disabled={busy !== null} onClick={syncNow}>
        <RefreshCw size={14} /> {busy === "sync" ? "Fetching… about a minute" : "Check the online docs now"}
      </button>
    </div>
  );

  if (!data.synced) return <div className={styles.list}>{header}</div>;
  const quiet = data.changed.length === 0 && data.anchors.failing.length === 0;

  return (
    <div className={styles.list}>
      {header}
      {message && <p className={styles.note}>{message}</p>}
      {data.last_proposal && (
        <p className={styles.meta}>
          Last automatic update ({stamp(data.last_proposal.created_at)}): {data.last_proposal.status}.
          {data.last_proposal.applied.length > 0 &&
            ` Updated by itself: ${[...new Set(data.last_proposal.applied.flatMap((a) => a.values))].join(", ")}.`}
          {Object.keys(data.last_proposal.needs_person).length > 0 &&
            ` Left for a person: ${Object.keys(data.last_proposal.needs_person).length} page(s).`}
        </p>
      )}
      {Object.keys(data.last_run?.failed ?? {}).length > 0 && (
        <p role="alert" className={styles.error}>
          Couldn't fetch: {Object.keys(data.last_run?.failed ?? {}).join(", ")}. Their old copies were kept.
        </p>
      )}
      {quiet && (
        <p className={styles.empty}>Nothing to review. Every page matches what was last reviewed, and the key facts still match.</p>
      )}

      {data.anchors.failing.length > 0 && (
        <section className={styles.card}>
          <b>Key facts that no longer match</b>
          <ul className={styles.tried}>
            {data.anchors.failing.map((fact) => (
              <li key={fact.id}>
                {fact.fact} <span className={styles.meta}>({fact.problem}; page {fact.page})</span>
              </li>
            ))}
          </ul>
        </section>
      )}

      {data.changed.map((page) => (
        <article key={page.slug} className={styles.card}>
          <div className={styles.cardHead}>
            <b>{page.title || page.slug}</b>
            <span className={styles.meta}>
              updated {page.reviewed_updated_at?.slice(0, 10) ?? "?"} → {page.updated_at?.slice(0, 10) ?? "?"}
            </span>
          </div>
          <p className={styles.meta}>Guides built from it: {page.guides.length ? page.guides.join(", ") : "none"}</p>
          {page.diff ? (
            <details>
              <summary>What changed</summary>
              <pre className={styles.thread}>{page.diff.join("\n")}</pre>
            </details>
          ) : (
            <p className={styles.meta}>No earlier copy was kept to compare with.</p>
          )}
          <div className={styles.actions}>
            <a className={styles.link} href={page.url} target="_blank" rel="noreferrer">
              Open the page <ExternalLink size={12} />
            </a>
            <button
              type="button"
              className={`${ui.button} ${ui.small}`}
              disabled={busy !== null}
              onClick={() => run(page.slug, async () => void (await api.acceptSources({ slugs: [page.slug] })))}
            >
              Mark reviewed
            </button>
          </div>
        </article>
      ))}

      {data.changed.length > 1 && (
        <div className={styles.actions}>
          <span className={styles.meta}>Update the guides first, then mark everything reviewed.</span>
          <button
            type="button"
            className={`${ui.button} ${ui.small}`}
            disabled={busy !== null}
            onClick={() => run("all", async () => void (await api.acceptSources({ all: true })))}
          >
            Mark all reviewed
          </button>
        </div>
      )}
      {data.unmapped.length > 0 && (
        <p className={styles.meta}>Pages no guide is built from: {data.unmapped.join(", ")}.</p>
      )}
    </div>
  );
}
