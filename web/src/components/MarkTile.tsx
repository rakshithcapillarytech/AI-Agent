import styles from "./ui.module.css";

/** The product mark: Capillary's gradient tile with an arrow-into-SDK glyph. */
export function MarkTile({ size = 32 }: { size?: number }) {
  return (
    <span className={styles.markTile} style={{ width: size, height: size }} aria-hidden="true">
      <svg viewBox="0 0 24 24" width={size * 0.6} height={size * 0.6} fill="none">
        <path
          d="M5 12h8m0 0-3-3m3 3-3 3M17 7v10"
          stroke="currentColor"
          strokeWidth="2.2"
          strokeLinecap="round"
          strokeLinejoin="round"
        />
      </svg>
    </span>
  );
}
