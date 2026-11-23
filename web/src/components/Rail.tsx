import { CircleHelp, ClipboardList, House, UserRound } from "lucide-react";
import styles from "./layout.module.css";
import { MarkTile } from "./MarkTile";

interface RailProps {
  homeActive: boolean;
  onHome: () => void;
  prereqActive: boolean;
  onPrereq: () => void;
  faqActive: boolean;
  onFaq: () => void;
  userName: string;
}

export function Rail({ homeActive, onHome, prereqActive, onPrereq, faqActive, onFaq, userName }: RailProps) {
  const initials = userName
    .split(/\s+/)
    .filter(Boolean)
    .slice(0, 2)
    .map((part) => part[0]?.toUpperCase())
    .join("");

  return (
    <nav className={styles.rail} aria-label="Main">
      <div className={styles.railLogo}>
        <MarkTile size={34} />
      </div>
      <button
        type="button"
        className={`${styles.railItem} ${homeActive ? styles.railItemActive : ""}`}
        onClick={onHome}
        aria-current={homeActive ? "page" : undefined}
      >
        <span className={styles.railIcon}>
          <House size={19} strokeWidth={1.9} />
        </span>
        Home
      </button>
      <button
        type="button"
        className={`${styles.railItem} ${prereqActive ? styles.railItemActive : ""}`}
        onClick={onPrereq}
        aria-current={prereqActive ? "page" : undefined}
      >
        <span className={styles.railIcon}>
          <ClipboardList size={19} strokeWidth={1.9} />
        </span>
        Prerequisites
      </button>
      <button
        type="button"
        className={`${styles.railItem} ${faqActive ? styles.railItemActive : ""}`}
        onClick={onFaq}
        aria-current={faqActive ? "page" : undefined}
      >
        <span className={styles.railIcon}>
          <CircleHelp size={19} strokeWidth={1.9} />
        </span>
        FAQ
      </button>
      <div className={styles.railSpacer} />
      <span className={styles.avatar} title={userName || "You"}>
        {initials || <UserRound size={18} />}
      </span>
    </nav>
  );
}
