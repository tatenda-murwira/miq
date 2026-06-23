from app.utils.campaign_names import campaign_display_name


def test_default_campaign_names_keep_source_id() -> None:
    assert campaign_display_name(916) == "Campaign One (916)"
    assert campaign_display_name(936) == "Campaign Two (936)"
    assert campaign_display_name(1178) == "Campaign Three (1178)"


def test_campaign_names_follow_sorted_ids_for_uploaded_data() -> None:
    campaign_ids = [300, 100, 200]

    assert campaign_display_name(100, campaign_ids) == "Campaign One (100)"
    assert campaign_display_name(200, campaign_ids) == "Campaign Two (200)"
    assert campaign_display_name(300, campaign_ids) == "Campaign Three (300)"
