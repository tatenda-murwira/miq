from app.utils.campaign_names import campaign_display_name


def test_default_campaign_names_keep_source_id() -> None:
    assert campaign_display_name(916) == "Campaign Alpha 916"
    assert campaign_display_name(936) == "Campaign Bravo 936"
    assert campaign_display_name(1178) == "Campaign Charlie 1178"


def test_campaign_names_follow_sorted_ids_for_uploaded_data() -> None:
    campaign_ids = [300, 100, 200]

    assert campaign_display_name(100, campaign_ids) == "Campaign Alpha 100"
    assert campaign_display_name(200, campaign_ids) == "Campaign Bravo 200"
    assert campaign_display_name(300, campaign_ids) == "Campaign Charlie 300"
