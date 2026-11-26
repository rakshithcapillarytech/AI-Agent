import re
from datetime import date
from itertools import product

import pytest
from fastapi.testclient import TestClient

from app.api import main as api
from app.config import get_settings
from app.graph.state import IntegrationProfile
from app.kb.guide import GuideNotReady
from app.kb.humanguide import (
    build_steps_html,
    build_steps_markdown,
    guide_steps_filename,
    steps_for_summary,
)

KB = get_settings().knowledge_base_dir
PLATFORMS = ["android", "ios", "react-native", "flutter", "web"]
ALL_MODULES = ["core", "push", "inapp", "inbox_api", "inbox_ui", "visitor", "gamification", "multi_account"]


def profile(platform="react-native", mode="firebase", modules=("core", "push", "gamification"), **extra):
    return IntegrationProfile.model_validate(
        {
            "company": "Demo Retail",
            "platforms": [{"platform": platform, "config_mode": mode}],
            "modules": list(modules),
            "environment": "uat",
            "region": "IN",
            "customer_id_type": "mobile",
            **extra,
        }
    )


def android_version() -> str:
    import frontmatter

    return str(frontmatter.load(KB / "android" / "firebase.md").metadata["sdk_version"])


def headings(markdown: str) -> list[str]:
    out, in_fence = [], False
    for line in markdown.splitlines():
        if line.lstrip().startswith(("```", "~~~")):
            in_fence = not in_fence
        elif not in_fence and line.startswith("#"):
            out.append(line)
    return out


def test_every_platform_and_mode_builds_a_clean_document():
    for platform, mode in product(PLATFORMS, ["firebase", "direct"]):
        md = build_steps_markdown(profile(platform, mode, ALL_MODULES), KB, date(2026, 11, 23), full=True)
        page = build_steps_html(profile(platform, mode, ALL_MODULES), KB, date(2026, 11, 23), full=True)
        assert "{{sdk_version}}" not in md and "review_status:" not in md, (platform, mode)
        assert "For the AI assistant" not in md, (platform, mode)  # no instructions meant for an AI
        assert not any(h.lstrip("# ").startswith("API Reference") for h in headings(md)), (platform, mode)
        assert any(h.lstrip("# ").startswith("Steps") for h in headings(md)), (platform, mode)
        assert page.startswith("<!doctype html>") and "</html>" in page


def test_the_overview_for_the_ai_is_left_out_but_the_useful_shared_files_stay():
    md = build_steps_markdown(profile(), KB, full=True)
    heads = " ".join(headings(md))
    assert "Hydra SDK (Experience+): overview" not in heads
    assert "Prerequisites (all platforms)" in heads
    assert "Firebase setup" in heads
    assert "Troubleshooting (all platforms)" in heads
    assert "Push notifications on mobile" in heads  # push chosen


def test_only_the_chosen_features_are_included():
    core_only = build_steps_markdown(profile("react-native", "direct", ["core"]), KB, full=True)
    assert "#### Gamification" not in core_only and "#### Push" not in core_only
    chosen = build_steps_markdown(profile("react-native", "direct", ["core", "gamification"]), KB, full=True)
    assert "#### Gamification" in chosen and "#### Push" not in chosen
    inbox = build_steps_markdown(profile("android", "firebase", ["core", "inbox_ui"]), KB, full=True)
    assert "#### Inbox" in inbox and "#### In-App" not in inbox


def test_corrections_and_gaps_are_kept():
    md = build_steps_markdown(profile("android", "firebase", ["core", "gamification"]), KB, full=True)
    assert "⚠️ Correction" in md and f"`{android_version()}`" in md  # the current version, whatever it is
    assert "⚠️ Gap" in md
    page = build_steps_html(profile("android", "firebase", ["core", "gamification"]), KB, full=True)
    assert 'class="callout gap"' in page and 'class="callout correction"' in page


def test_the_checklist_is_personalised():
    md = build_steps_markdown(profile("android", "direct", ["core"], customer_id_type="email"), KB, full=True)
    assert "Get access to the Android SDK repository" in md
    assert "iOS repository" not in md
    assert "Set the CRM Account Linking Identifier to Email address" in md
    assert "gamification" not in md.split("## Placeholders")[0].lower().replace("gamification write key", "")


def test_the_page_is_self_contained_and_printable():
    page = build_steps_html(profile(), KB, full=True)
    assert '<nav class="toc"' in page and 'href="#' in page
    assert 'id="print"' in page and "window.print()" in page and "#print" in page
    assert "@media print" in page and "break-before:page" in page
    assert "<script src" not in page and "<link" not in page and "http-equiv" not in page
    assert 'class="snippet"' in page  # code blocks are highlighted
    assert 'class="filename"' in page  # and show the file they belong in


def test_a_hostile_company_name_cannot_inject_markup():
    page = build_steps_html(profile(company='<img src=x onerror=alert(1)> <script>alert(2)</script> | "Co"'), KB)
    body = page.split("<main", 1)[1].split("</main>")[0]
    assert "<script>alert" not in body and "<img src=x" not in body
    assert "&lt;script&gt;" in body
    assert "<title>Hydra SDK integration steps: &lt;img" in page


def test_not_ready_without_a_config_mode():
    for full in (False, True):
        with pytest.raises(GuideNotReady):
            build_steps_html(profile(mode=None), KB, full=full)
        with pytest.raises(GuideNotReady):
            build_steps_html(IntegrationProfile(), KB, full=full)


def test_filename():
    assert guide_steps_filename(profile(company="Demo Retail!")) == "hydra-integration-steps-demo-retail-react-native.html"
    assert guide_steps_filename(profile(), full=True).endswith("react-native-full.html")


@pytest.fixture
def session(monkeypatch):
    state: dict = {"messages": ["hi"], "profile": profile().model_dump()}

    async def fake_values(_session_id: str) -> dict:
        return state

    monkeypatch.setattr(api, "_values", fake_values)
    return state


def test_endpoint_opens_the_page_or_downloads_it(session):
    client = TestClient(api.app)  # no `with`: the database lifespan isn't started
    shown = client.get("/sessions/abc/steps")
    assert shown.status_code == 200 and shown.headers["content-type"].startswith("text/html")
    assert "content-disposition" not in shown.headers
    saved = client.get("/sessions/abc/steps", params={"download": "1"})
    assert saved.headers["content-disposition"] == 'attachment; filename="hydra-integration-steps-demo-retail-react-native.html"'
    assert re.search(r"Hydra SDK integration steps: Demo Retail", saved.text)
    full = client.get("/sessions/abc/steps", params={"download": "1", "full": "1"})
    assert full.headers["content-disposition"].endswith('react-native-full.html"')
    assert len(full.text) > 5 * len(saved.text)  # the default is the short one


def test_endpoint_errors(session):
    client = TestClient(api.app)
    session["messages"] = []
    assert client.get("/sessions/abc/steps").status_code == 404
    session["messages"] = ["hi"]
    session["profile"] = profile(mode=None).model_dump()
    assert client.get("/sessions/abc/steps").status_code == 409
    assert client.get("/sessions/abc/guide").status_code == 409  # the AI guide keeps its behaviour


# ── The short summary (the default) ───────────────────────────────────────────────────────────────────────


def numbered_steps(md: str) -> list[str]:
    return [line for line in md.splitlines() if re.match(r"^\d+\. \*\*", line)]


def test_the_summary_is_short_for_every_setup():
    """A person should be able to read it: a few thousand characters, not dozens of pages."""
    for platform, mode in product(PLATFORMS, ["firebase", "direct"]):
        md = build_steps_markdown(profile(platform, mode, ALL_MODULES), KB)
        assert len(md) <= 12_000, (platform, mode, len(md))
        assert "```" not in md, (platform, mode)  # no code: it is in the guide
        assert 5 <= len(numbered_steps(md)) <= 25, (platform, mode)
        full = build_steps_markdown(profile(platform, mode, ALL_MODULES), KB, full=True)
        assert len(md) * 3 < len(full), (platform, mode)


def test_the_summary_has_the_parts_a_person_needs_and_no_ai_or_file_jargon():
    md = build_steps_markdown(profile(), KB)
    heads = [h.lstrip("# ") for h in headings(md)]
    for wanted in ["Your setup", "Before you start", "Minimum versions", "Steps", "If it doesn't work", "Confirm with your Capillary contact"]:
        assert wanted in heads, wanted
    assert "For the AI assistant" not in md and "_shared/" not in md and ".md`" not in md
    assert "{{" not in md


def test_summary_steps_follow_the_chosen_features():
    def steps(modules, platform="react-native", mode="firebase"):
        return " ".join(numbered_steps(build_steps_markdown(profile(platform, mode, modules), KB)))

    core = steps(["core"])
    assert "Notification Service Extension" not in core and "Gamification:" not in core and "push permission" not in core
    assert "Install the package" in core and "Identify the user" in core
    pushed = steps(["core", "push"])
    assert "Notification Service Extension" in pushed and "push permission" in pushed and "Gamification:" not in pushed
    games = steps(["core", "gamification"])
    assert "Gamification: package version" in games and "Loyalty View" in games and "push permission" not in games
    android = steps(["core", "push"], "android", "firebase")
    assert "notification permission" in android and "GamificationUIManager" not in android


def test_summary_steps_are_numbered_in_order_and_point_to_the_guide_step():
    md = build_steps_markdown(profile("android", "firebase", ["core", "push"]), KB)
    lines = numbered_steps(md)
    assert [int(line.split(".")[0]) for line in lines] == list(range(1, len(lines) + 1))
    assert "*Push notifications · Guide step 9*" in md  # tagged, and the guide's own number is kept
    assert "Optional · Guide step 8" in md  # "(optional)" moves from the title to a tag
    assert "(optional)" not in " ".join(lines).lower()


def test_step_feature_map_still_matches_the_guides():
    """step_modules.yaml hides steps by number: fail loudly if a guide renumbers or renames them."""
    import yaml

    mapping = yaml.safe_load((KB / "step_modules.yaml").read_text(encoding="utf-8"))
    problems = []
    for rel, steps in mapping.items():
        shown = {s["id"]: s["title"] for s in steps_for_summary(f"{rel}.md", KB, ["push", "gamification"])}
        for step_id, info in steps.items():
            title = shown.get(step_id)
            if title is None:
                problems.append(f"{rel}: no step {step_id}")
            elif info["title"].lower() not in title.lower() and info["title"].lower() not in _raw_title(rel, step_id):
                problems.append(f"{rel} step {step_id}: title {title!r} no longer mentions {info['title']!r}")
    assert not problems, "\n".join(problems)


def _raw_title(rel: str, step_id: str) -> str:
    text = (KB / f"{rel}.md").read_text(encoding="utf-8")
    match = re.search(rf"^### {re.escape(step_id)}\. (.+)$", text, re.MULTILINE)
    return match.group(1).lower() if match else ""


def test_the_summary_is_personalised_and_escapes_the_company():
    md = build_steps_markdown(profile("android", "direct", ["core"], customer_id_type="email"), KB)
    assert "Get access to the Android SDK repository" in md and "iOS repository" not in md
    assert "Set the CRM Account Linking Identifier to Email address" in md
    page = build_steps_html(profile(company="<script>alert(1)</script>"), KB)
    assert "<script>alert(1)" not in page.split("<main", 1)[1].split("</main>")[0]


def test_two_apps_get_their_own_steps_and_versions():
    both = IntegrationProfile.model_validate(
        {
            "company": "Duo",
            "platforms": [{"platform": "android", "config_mode": "direct"}, {"platform": "ios", "config_mode": "direct"}],
            "modules": ["core"],
            "environment": "uat",
            "region": "IN",
            "customer_id_type": "mobile",
        }
    )
    md = build_steps_markdown(both, KB)
    assert "### Android (native) without Firebase Remote Config" in md and "### iOS (native) without Firebase Remote Config" in md
    assert md.count("## Minimum versions") == 1 and md.count("### iOS (native)") == 2  # versions and steps
    assert len(numbered_steps(md)) >= 14
