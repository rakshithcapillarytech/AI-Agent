import { Check } from "lucide-react";
import { guideLabel } from "../lib/catalog";
import styles from "./session.module.css";

/** "android/direct.md › 3. Add the SDK" → the guide and the step's title. */
function parse(step: string) {
  const [file, title = step] = step.split(" › ");
  return { file, title: title.replace(/^\d+\.\s*/, "") };
}

/** The integration plan: every step from the client's guides, with the current one marked. */
export function Steps({ steps, current }: { steps: string[]; current: number }) {
  const parsed = steps.map(parse);
  const showGuide = new Set(parsed.map((p) => p.file)).size > 1; // only when several guides are mixed
  const done = Math.min(current, steps.length);

  return (
    <div className={styles.checklist}>
      <p className={styles.checklistCount}>
        {done} of {steps.length} done
      </p>
      <ol className={styles.stepList}>
        {parsed.map(({ file, title }, index) => {
          const state = index < current ? "done" : index === current ? "current" : "todo";
          return (
            <li key={`${file}-${index}`} className={styles[`step_${state}`]} aria-current={state === "current" ? "step" : undefined}>
              <span className={styles.stepDot}>{state === "done" && <Check size={10} strokeWidth={3.5} />}</span>
              <span>
                {title}
                {showGuide && <span className={styles.stepGuide}>{guideLabel(file)}</span>}
              </span>
            </li>
          );
        })}
      </ol>
    </div>
  );
}
