from app.kb.review import collect, render


def test_collects_multiline_callouts_by_kind(tmp_path):
    (tmp_path / "web").mkdir()
    (tmp_path / "web" / "direct.md").write_text(
        "# Web\n"
        "> ⚠️ Gap: no browser list.\n"
        "> Ask a Capillary engineer.\n"
        "text\n"
        "> ⚠️ Source doc correction: WebSDK vs HydraSDK. *Pending SME confirmation.*\n"
    )
    (tmp_path / "_template").mkdir()
    (tmp_path / "_template" / "platform.md").write_text("> ⚠️ Gap: ignored template\n")

    callouts = collect(tmp_path)
    assert [(c.file, c.line, c.kind) for c in callouts] == [
        ("web/direct.md", 2, "Gap"),
        ("web/direct.md", 5, "Correction"),
    ]
    assert callouts[0].text == "⚠️ Gap: no browser list. Ask a Capillary engineer."
    assert "- [ ] L2: ⚠️ Gap: no browser list." in render(callouts)
