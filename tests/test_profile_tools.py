from app.graph.state import IntegrationProfile
from app.tools.profile import ProfileUpdate, merge_profile


def test_platform_details_accumulate_across_updates():
    profile = merge_profile(
        IntegrationProfile(), ProfileUpdate(platforms=[{"platform": "android", "language": "kotlin"}])
    )
    profile = merge_profile(
        profile, ProfileUpdate(platforms=[{"platform": "android", "config_mode": "direct"}])
    )
    assert len(profile.platforms) == 1
    assert profile.platforms[0].language == "kotlin"
    assert profile.platforms[0].config_mode == "direct"


def test_any_update_clears_confirmation():
    confirmed = IntegrationProfile(region="IN", confirmed=True)
    assert merge_profile(confirmed, ProfileUpdate(region="US")).confirmed is False


def test_missing_required_lists_gaps():
    profile = IntegrationProfile(platforms=[{"platform": "web"}], modules=["core"])
    assert profile.missing_required() == [
        "config_mode for web",
        "environment",
        "region",
        "customer_id_type",
    ]
