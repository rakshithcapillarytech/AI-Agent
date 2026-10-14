// Per-browser conveniences: the list of this browser's onboardings and the user's first name.
// Sessions themselves live on the server; losing this list never loses a session.

export interface RecentSession {
  id: string;
  title: string;
  meta: string;
  environment: string | null;
  createdAt: number;
}

const SESSIONS_KEY = "copilot.sessions";
const NAME_KEY = "copilot.name";

function read<T>(key: string, fallback: T): T {
  try {
    const raw = localStorage.getItem(key);
    return raw ? (JSON.parse(raw) as T) : fallback;
  } catch {
    return fallback;
  }
}

function write(key: string, value: unknown): void {
  try {
    localStorage.setItem(key, JSON.stringify(value));
  } catch {
    // Storage unavailable (private window, blocked site data): the app still works.
  }
}

export const recentSessions = {
  list: (): RecentSession[] => read<RecentSession[]>(SESSIONS_KEY, []),
  add(session: RecentSession): RecentSession[] {
    const next = [session, ...this.list().filter((s) => s.id !== session.id)].slice(0, 30);
    write(SESSIONS_KEY, next);
    return next;
  },
};

export const userName = {
  get: (): string => read<string>(NAME_KEY, ""),
  set: (name: string) => write(NAME_KEY, name),
};

export function relativeTime(timestamp: number, now = Date.now()): string {
  const minutes = Math.round((now - timestamp) / 60_000);
  if (minutes < 1) return "now";
  if (minutes < 60) return `${minutes}m`;
  const hours = Math.round(minutes / 60);
  if (hours < 24) return `${hours}h`;
  return `${Math.round(hours / 24)}d`;
}

export function dayGroup(timestamp: number, now = new Date()): "Today" | "Yesterday" | "Earlier" {
  const day = (d: Date) => new Date(d.getFullYear(), d.getMonth(), d.getDate()).getTime();
  const diffDays = (day(now) - day(new Date(timestamp))) / 86_400_000;
  if (diffDays < 1) return "Today";
  if (diffDays < 2) return "Yesterday";
  return "Earlier";
}

export function greeting(now = new Date()): string {
  const hour = now.getHours();
  if (hour < 12) return "Good morning";
  if (hour < 17) return "Good afternoon";
  return "Good evening";
}
