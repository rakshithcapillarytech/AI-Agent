import { useCallback, useEffect, useState } from "react";
import { api } from "./api";
import { AdminView } from "./components/AdminView";
import { FaqView } from "./components/FaqView";
import { Home } from "./components/Home";
import { PrerequisitesView } from "./components/PrerequisitesView";
import styles from "./components/layout.module.css";
import { Rail } from "./components/Rail";
import { SessionView } from "./components/SessionView";
import { Sidebar } from "./components/Sidebar";
import { platformShort } from "./lib/catalog";
import { recentSessions, userName as storedName } from "./lib/recent";
import type { Profile } from "./types";

type View = { kind: "home" } | { kind: "admin" } | { kind: "prerequisites" } | { kind: "faq" } | { kind: "session"; id: string; startProfile?: Profile };

/** The session id lives in the URL (?session=…), so a link reopens that onboarding. */
function viewFromUrl(): View {
  const params = new URLSearchParams(window.location.search);
  if (params.has("admin")) return { kind: "admin" };
  if (params.has("prerequisites")) return { kind: "prerequisites" };
  if (params.has("faq")) return { kind: "faq" };
  const id = params.get("session");
  return id ? { kind: "session", id } : { kind: "home" };
}

export default function App() {
  const [view, setView] = useState<View>(viewFromUrl);
  const [recent, setRecent] = useState(recentSessions.list);
  const [name, setName] = useState(storedName.get);

  useEffect(() => {
    const onPopState = () => setView(viewFromUrl());
    window.addEventListener("popstate", onPopState);
    return () => window.removeEventListener("popstate", onPopState);
  }, []);

  const navigate = useCallback((next: View) => {
    const url =
      next.kind === "session"
        ? `?session=${encodeURIComponent(next.id)}`
        : next.kind === "admin"
          ? "?admin=1"
          : next.kind === "prerequisites"
            ? "?prerequisites=1"
            : next.kind === "faq"
              ? "?faq=1"
              : window.location.pathname;
    window.history.pushState(null, "", url);
    setView(next);
  }, []);

  const goHome = useCallback(() => navigate({ kind: "home" }), [navigate]);
  const openPrerequisites = useCallback(() => navigate({ kind: "prerequisites" }), [navigate]);
  const openFaq = useCallback(() => navigate({ kind: "faq" }), [navigate]);
  const openSession = useCallback((id: string) => navigate({ kind: "session", id }), [navigate]);

  const startOnboarding = useCallback(
    async (profile: Profile, contactName: string) => {
      const { session_id } = await api.createSession();
      if (contactName) {
        storedName.set(contactName);
        setName(contactName);
      }
      setRecent(
        recentSessions.add({
          id: session_id,
          title: profile.company || "Untitled onboarding",
          meta: profile.platforms.map((p) => platformShort(p.platform)).join(" · "),
          environment: profile.environment,
          createdAt: Date.now(),
        }),
      );
      navigate({ kind: "session", id: session_id, startProfile: profile });
    },
    [navigate],
  );

  return (
    <div className={styles.app}>
      <Rail
        homeActive={view.kind === "home"}
        onHome={goHome}
        prereqActive={view.kind === "prerequisites"}
        onPrereq={openPrerequisites}
        faqActive={view.kind === "faq"}
        onFaq={openFaq}
        userName={name}
      />
      <Sidebar
        recent={recent}
        activeId={view.kind === "session" ? view.id : null}
        onNew={goHome}
        onOpen={openSession}
      />
      <main className={styles.main}>
        {view.kind === "admin" ? (
          <AdminView />
        ) : view.kind === "prerequisites" ? (
          <PrerequisitesView />
        ) : view.kind === "faq" ? (
          <FaqView />
        ) : view.kind === "home" ? (
          <Home userName={name} recent={recent} onStart={startOnboarding} onOpen={openSession} />
        ) : (
          <SessionView key={view.id} id={view.id} startProfile={view.startProfile} onHome={goHome} />
        )}
      </main>
    </div>
  );
}
