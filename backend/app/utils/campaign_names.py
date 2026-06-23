from __future__ import annotations

from collections.abc import Iterable
from typing import Any


CAMPAIGN_NAME_LABELS = [
    "Campaign One",
    "Campaign Two",
    "Campaign Three",
    "Campaign Four",
    "Campaign Five",
    "Campaign Six",
    "Campaign Seven",
    "Campaign Eight",
    "Campaign Nine",
    "Campaign Ten",
    "Campaign Eleven",
    "Campaign Twelve",
]

DEFAULT_CAMPAIGN_ORDER = ["916", "936", "1178"]


def campaign_display_name(campaign_id: Any, campaign_ids: Iterable[Any] | None = None) -> str:
    """Return a readable campaign label while preserving the source ID."""
    normalized_id = _normalize_campaign_id(campaign_id)
    ordered_ids = _ordered_campaign_ids(campaign_ids) if campaign_ids is not None else DEFAULT_CAMPAIGN_ORDER

    if normalized_id in ordered_ids:
        index = ordered_ids.index(normalized_id)
    else:
        index = _fallback_index(normalized_id)

    return f"{CAMPAIGN_NAME_LABELS[index % len(CAMPAIGN_NAME_LABELS)]} ({normalized_id})"


def _ordered_campaign_ids(campaign_ids: Iterable[Any]) -> list[str]:
    unique_ids = {_normalize_campaign_id(campaign_id) for campaign_id in campaign_ids}
    return sorted(unique_ids, key=_campaign_sort_key)


def _campaign_sort_key(campaign_id: str) -> tuple[int, int | str]:
    try:
        return (0, int(campaign_id))
    except ValueError:
        return (1, campaign_id)


def _normalize_campaign_id(campaign_id: Any) -> str:
    try:
        value = float(campaign_id)
        if value.is_integer():
            return str(int(value))
    except (TypeError, ValueError):
        pass

    return str(campaign_id).strip()


def _fallback_index(campaign_id: str) -> int:
    try:
        return abs(int(campaign_id))
    except ValueError:
        return sum(ord(character) for character in campaign_id)
