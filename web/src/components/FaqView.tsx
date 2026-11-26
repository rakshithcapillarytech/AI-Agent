import { BookOpen, Search } from "lucide-react";
import { useEffect, useMemo, useState } from "react";
import { api } from "../api";
import { PLATFORMS, guideLabel } from "../lib/catalog";
import type { Faq, FaqItem, Platform } from "../types";
import { Inline } from "./Inline";
import { PageHeader } from "./PageHeader";
import { SourceFreshness } from "./SourceFreshness";
import styles from "./faq.module.css";

type PlatformFilter = Platform | "all";

const shows = (item: FaqItem, platform: PlatformFilter) =>
  platform === "all" || item.platforms === null || item.platforms.includes(platform);

const MOBILE: Platform[] = ["android", "ios", "react-native", "flutter"];
const appsLabel = (platforms: Platform[]) =>
  platforms.length === MOBILE.length && MOBILE.every((p) => platforms.includes(p))
    ? "Mobile apps"
    : platforms.map((p) => PLATFORMS.find((x) => x.id === p)?.label ?? p).join(", ");

const matches = (item: FaqItem, query: string) => {
  const words = query.toLowerCase().split(/\s+/).filter(Boolean);
  const text = `${item.question} ${item.answer}`.toLowerCase();
  return words.every((w) => text.includes(w));
};

/** Common questions, answered from the platform guides. Needs no session. */
export function FaqView() {
  const [faq, setFaq] = useState<Faq | null>(null);
  const [error, setError] = useState(false);
  const [query, setQuery] = useState("");
  const [category, setCategory] = useState("all");
  const [platform, setPlatform] = useState<PlatformFilter>("all");

  useEffect(() => {
    const controller = new AbortController();
    api
      .faq(controller.signal)
      .then(setFaq)
      .catch((e: unknown) => {
        if (!(e instanceof DOMException && e.name === "AbortError")) setError(true);
      });
    return () => controller.abort();
  }, []);

  const visible = useMemo(
    () =>
      (faq?.items ?? []).filter(
        (item) => (category === "all" || item.category === category) && shows(item, platform) && matches(item, query),
      ),
    [faq, category, platform, query],
  );

  return (
    <>
      <PageHeader title="FAQ" subtitle="Quick answers to the questions teams ask most, taken from the integration guides" />
      <div className={styles.page}>
        <div className={styles.inner}>
          <SourceFreshness />
          <div className={styles.controls}>
            <label className={styles.search}>
              <Search size={16} aria-hidden="true" />
              <input
                type="search"
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                placeholder="Search, for example “push”, “token” or “SHA256”"
                aria-label="Search the FAQ"
              />
            </label>
            <div className={styles.group} role="radiogroup" aria-label="Your app">
              {[{ id: "all" as const, label: "All apps" }, ...PLATFORMS].map((p) => (
                <button
                  key={p.id}
                  type="button"
                  role="radio"
                  aria-checked={platform === p.id}
                  className={`${styles.chip} ${platform === p.id ? styles.chipOn : ""}`}
                  onClick={() => setPlatform(p.id)}
                >
                  {p.label}
                </button>
              ))}
            </div>
            <div className={styles.group} role="radiogroup" aria-label="Topic">
              {[{ id: "all", label: "All topics" }, ...(faq?.categories ?? [])].map((c) => (
                <button
                  key={c.id}
                  type="button"
                  role="radio"
                  aria-checked={category === c.id}
                  className={`${styles.chip} ${category === c.id ? styles.chipOn : ""}`}
                  onClick={() => setCategory(c.id)}
                >
                  {c.label}
                </button>
              ))}
            </div>
          </div>

          {error && (
            <p role="alert" className={styles.error}>
              Couldn't load the FAQ. Is the server running?
            </p>
          )}
          {!faq && !error && <p className={styles.empty}>Loading…</p>}

          {faq && (
            <div aria-live="polite">
              <p className={styles.count}>
                {visible.length} {visible.length === 1 ? "question" : "questions"}
              </p>
              {visible.length === 0 && (
                <p className={styles.empty}>
                  Nothing matches. Try fewer words, or ask your Capillary contact; they can answer what isn't covered here.
                </p>
              )}
              {faq.categories.map((c) => {
                const items = visible.filter((i) => i.category === c.id);
                if (items.length === 0) return null;
                return (
                  <section key={c.id} className={styles.section}>
                    <h2 className={styles.sectionTitle}>{c.label}</h2>
                    <ul className={styles.list}>
                      {items.map((item) => (
                        <li key={item.id}>
                          <details className={styles.item}>
                            <summary className={styles.question}>
                              <Inline text={item.question} />
                            </summary>
                            <div className={styles.answer}>
                              <p>
                                <Inline text={item.answer} />
                              </p>
                              <p className={styles.source}>
                                <BookOpen size={13} aria-hidden="true" />
                                From: {item.sources.map(guideLabel).join(", ")}
                                {item.platforms && ` · ${appsLabel(item.platforms)}`}
                              </p>
                            </div>
                          </details>
                        </li>
                      ))}
                    </ul>
                  </section>
                );
              })}
            </div>
          )}
        </div>
      </div>
    </>
  );
}
