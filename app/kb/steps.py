"""The integration plan: the numbered steps in each loaded platform file's `## Steps` section."""

from pathlib import Path

from app.kb.sections import split_sections


def steps_for_files(files: list[str], kb_dir: Path) -> list[str]:
    """Plan entries like 'android/direct.md › 3. Add the SDK dependencies', in file order.

    Shared files have no Steps section, and a file that isn't written yet contributes nothing.
    """
    plan = []
    for rel in files:
        path = kb_dir / rel
        if not path.is_file():
            continue
        for section in split_sections(path.read_text(encoding="utf-8")):
            if len(section.path) == 2 and section.path[0] == "Steps":
                plan.append(f"{rel} › {section.path[1]}")
    return plan
