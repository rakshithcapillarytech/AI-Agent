import pytest

from app.config import get_settings
from app.kb.lint import lint_file, platform_files

GOOD = """---
platform: android
config_mode: direct
sdk_package: com.capillary:hydra-core
sdk_version: 1.0.0
modules_covered: [core]
modules_missing: [push]
sources: ["doc pp.1-2"]
owner: TBD
last_verified: null
review_status: draft
---
## Coverage
## Requirements
## Prerequisites
## Steps
implementation("com.capillary:hydra-core:{{sdk_version}}") // {{account_id}}
## Modules
## Verification
## Known Issues
## API Reference
"""


def _write(tmp_path, rel: str, text: str):
    path = tmp_path / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text)
    return path


def test_template_conforming_file_passes(tmp_path):
    assert lint_file(_write(tmp_path, "android/direct.md", GOOD), tmp_path) == []


def test_broken_file_reports_each_problem(tmp_path):
    broken = (
        GOOD.replace("owner: TBD\n", "")
        .replace("## Verification\n", "")
        .replace("{{account_id}}", "{{acount_id}} <VERSION>")
        .replace("modules_missing: [push]", "modules_missing: [notifications]")
    )
    problems = lint_file(_write(tmp_path, "android/firebase.md", broken), tmp_path)
    assert "missing front-matter field: owner" in problems
    assert "missing heading: ## Verification" in problems
    assert "unknown placeholders: ['acount_id']" in problems
    assert any("<VERSION>" in p for p in problems)
    assert any("doesn't match file name 'firebase'" in p for p in problems)
    assert any("unknown modules" in p for p in problems)


KB_DIR = get_settings().knowledge_base_dir


@pytest.mark.parametrize("path", platform_files(KB_DIR), ids=lambda p: str(p.relative_to(KB_DIR)))
def test_every_real_platform_file_passes(path):
    assert lint_file(path, KB_DIR) == []


def test_all_ten_platform_files_exist():
    assert len(platform_files(KB_DIR)) == 10
