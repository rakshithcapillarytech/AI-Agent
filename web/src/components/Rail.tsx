import { House, UserRound } from "lucide-react";
import styles from "./layout.module.css";
import { MarkTile } from "./MarkTile";

interface RailProps {
  homeActive: boolean;
  onHome: () => void;
  userName: string;
}

export function Rail({ homeActive, onHome, userName }: RailProps) {
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
      <div className={styles.railSpacer} />
      <span className={styles.avatar} title={userName || "You"}>
        {initials || <UserRound size={18} />}
      </span>
    </nav>
  );
}
