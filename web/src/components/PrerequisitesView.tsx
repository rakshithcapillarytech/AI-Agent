import { Info, KeyRound, Laptop, Send, ShieldAlert, TriangleAlert, Wrench } from "lucide-react";
import { type ReactNode, useEffect, useState } from "react";
import { api } from "../api";
import { MODULES, PLATFORMS } from "../lib/catalog";
import type { ConfigMode, Module, Platform, PrereqRow, Prerequisites, VersionRow } from "../types";
import { Segmented } from "./controls";
import { Inline } from "./Inline";
import { PageHeader } from "./PageHeader";
import styles from "./prerequisites.module.css";

const MODES: { id: ConfigMode; label: string }[] = [
  { id: "firebase", label: "With Firebase Remote Config" },
  { id: "direct", label: "Without Firebase (values in code)" },
];

const FEATURES = MODULES.filter((m) => m.id !== "core");
const moduleLabel = (id: Module) => MODULES.find((m) => m.id === id)?.label ?? id;

function Section({ icon, title, hint, children }: { icon: ReactNode; title: string; hint: string; children: ReactNode }) {
  return (
    <section className={styles.section}>
      <header className={styles.sectionHead}>
        <span className={styles.sectionIcon}>{icon}</span>
        <div>
          <h2 className={styles.sectionTitle}>{title}</h2>
          <p className={styles.sectionHint}>{hint}</p>
        </div>
      </header>
      {children}
    </section>
  );
}

function KeyList({ rows, empty }: { rows: PrereqRow[]; empty: string }) {
  if (rows.length === 0) return <p className={styles.empty}>{empty}</p>;
  return (
    <ul className={styles.rows}>
      {rows.map((row) => (
        <li key={row.id} className={styles.row}>
          <div className={styles.rowTop}>
            <b className={styles.rowTitle}>
              <Inline text={row.title} />
            </b>
            <span className={row.required ? styles.required : styles.optional}>{row.required ? "Required" : "Can wait"}</span>
            {row.needed_for.map((m) => (
              <span key={m} className={styles.tag}>
                {moduleLabel(m)}
              </span>
            ))}
          </div>
          <p className={styles.rowHow}>
            <Inline text={row.how} />
          </p>
        </li>
      ))}
    </ul>
  );
}

function VersionTable({ rows }: { rows: VersionRow[] }) {
  return (
    <dl className={styles.versions}>
      {rows.map((row) => (
        <div key={row.label} className={styles.versionRow}>
          <dt>{row.label}</dt>
          <dd>
            <Inline text={row.value} />
            {row.note && <span className={styles.note}>{row.note}</span>}
            {row.general && <span className={styles.tag}>general knowledge</span>}
          </dd>
        </div>
      ))}
    </dl>
  );
}

/** Reference page: what to have ready (keys, access, versions, tools) for one platform. Needs no session. */
export function PrerequisitesView() {
  const [platform, setPlatform] = useState<Platform>("react-native");
  const [mode, setMode] = useState<ConfigMode>("firebase");
  const [modules, setModules] = useState<Module[]>(FEATURES.map((m) => m.id));
  const [data, setData] = useState<Prerequisites | null>(null);
  const [error, setError] = useState(false);

  useEffect(() => {
    const controller = new AbortController();
    setError(false);
    api
      .prerequisites(platform, mode, modules, controller.signal)
      .then(setData)
      .catch((e: unknown) => {
        if (!(e instanceof DOMException && e.name === "AbortError")) setError(true);
      });
    return () => controller.abort();
  }, [platform, mode, modules]);

  const toggle = (id: Module) => setModules((cur) => (cur.includes(id) ? cur.filter((m) => m !== id) : [...cur, id]));
  const platformLabel = PLATFORMS.find((p) => p.id === platform)?.label ?? platform;

  return (
    <>
      <PageHeader
        title="Prerequisites"
        subtitle="Everything to have ready before you write code: keys, access, minimum versions and tools"
      />
      <div className={styles.page}>
        <div className={styles.inner}>
          <div className={styles.controls}>
            <div className={styles.control}>
              <span className={styles.controlLabel}>Your app</span>
              <div className={styles.chips} role="radiogroup" aria-label="App type">
                {PLATFORMS.map((p) => (
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
            </div>
            <div className={styles.control}>
              <span className={styles.controlLabel}>How the SDK gets its settings</span>
              <Segmented label="Configuration" value={mode} onChange={setMode} options={MODES} />
            </div>
            <div className={styles.control}>
              <span className={styles.controlLabel}>Features you need</span>
              <div className={styles.chips} role="group" aria-label="Features">
                {FEATURES.map((f) => (
                  <button
                    key={f.id}
                    type="button"
                    aria-pressed={modules.includes(f.id)}
                    className={`${styles.chip} ${modules.includes(f.id) ? styles.chipOn : ""}`}
                    onClick={() => toggle(f.id)}
                  >
                    {f.label}
                  </button>
                ))}
              </div>
            </div>
          </div>

          <p className={styles.banner}>
            <ShieldAlert size={16} />
            Never paste keys, tokens or service-account files into chat, email or git.
          </p>

          {error && (
            <p role="alert" className={styles.error}>
              Couldn't load the prerequisites. Is the server running?
            </p>
          )}

          {data && (
            <div className={styles.body} aria-live="polite" aria-label={`Prerequisites for ${platformLabel}`}>
              <Section
                icon={<KeyRound size={18} />}
                title="Keys and values Capillary gives you"
                hint="Sent once your app is registered. Your platform guide says where each goes."
              >
                <KeyList rows={data.from_capillary} empty="Nothing for this setup." />
              </Section>

              <Section
                icon={<Send size={18} />}
                title="What you send to Capillary"
                hint="Used to register your app. A mismatch stops the SDK."
              >
                <KeyList rows={data.give_capillary} empty="Nothing for this setup." />
              </Section>

              <Section icon={<Wrench size={18} />} title="Accounts and access you set up" hint="Repository access, Firebase and CRM settings.">
                <KeyList rows={data.setup} empty="Nothing for this setup." />
              </Section>

              <Section icon={<Info size={18} />} title="Minimum versions" hint={`For ${platformLabel}.`}>
                <VersionTable rows={data.versions} />
              </Section>

              <Section icon={<Laptop size={18} />} title="Your computer" hint="What to install to build the app.">
                <VersionTable rows={data.computer} />
                <p className={styles.gap}>
                  <TriangleAlert size={15} /> {data.computer_gap}
                </p>
              </Section>

              {data.gaps.length > 0 && (
                <Section
                  icon={<TriangleAlert size={18} />}
                  title="Not documented yet"
                  hint="Not published by Capillary. Confirm with your contact."
                >
                  <ul className={styles.gaps}>
                    {data.gaps.map((g) => (
                      <li key={g}>{g}</li>
                    ))}
                  </ul>
                </Section>
              )}
            </div>
          )}
          {!data && !error && <p className={styles.empty}>Loading…</p>}
        </div>
      </div>
    </>
  );
}
