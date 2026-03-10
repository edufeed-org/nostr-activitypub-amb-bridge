"""ActivityPub outbox crawler for PeerTube instances."""

import json
import logging
import time
from pathlib import Path

import requests

logger = logging.getLogger(__name__)

AP_HEADERS = {"Accept": "application/activity+json"}


def _ap_get(
    session: requests.Session,
    url: str,
    request_delay: float,
    _backoff: float = 5.0,
) -> requests.Response:
    """HTTP GET with ActivityPub headers, rate limiting, and 429 retry."""
    max_retries = 5
    for _attempt in range(max_retries):
        if request_delay > 0:
            time.sleep(request_delay)

        resp = session.get(url, headers=AP_HEADERS, timeout=30)

        if resp.status_code == 429:
            retry_after = resp.headers.get("Retry-After")
            if retry_after is not None:
                wait = float(retry_after)
            else:
                wait = _backoff
            logger.warning("429 for %s -- retrying after %.1fs", url, wait)
            time.sleep(wait)
            _backoff = min(_backoff * 2, 60.0)
            continue

        return resp

    raise RuntimeError(f"Max retries ({max_retries}) exceeded for {url}")


def _load_state(state_file: str | None) -> set[str]:
    """Load processed URIs from a JSON state file."""
    if state_file is None:
        return set()
    path = Path(state_file)
    if not path.exists():
        return set()
    with open(path) as f:
        data = json.load(f)
    return set(data)


def _save_state(state_file: str | None, processed_uris: set[str]) -> None:
    """Save processed URIs as a JSON array to *state_file*."""
    if state_file is None:
        return
    with open(state_file, "w") as f:
        json.dump(sorted(processed_uris), f)


def _discover_outbox_urls(
    session: requests.Session,
    base_url: str,
    account: str | None,
    channel: str | None,
    request_delay: float,
) -> list[str]:
    """Discover outbox URLs from account and/or channel actors."""
    outbox_urls: list[str] = []

    if account:
        actor_url = f"{base_url}/accounts/{account}"
        resp = _ap_get(session, actor_url, request_delay)
        resp.raise_for_status()
        actor = resp.json()
        outbox_urls.append(actor["outbox"])

    if channel:
        actor_url = f"{base_url}/video-channels/{channel}"
        resp = _ap_get(session, actor_url, request_delay)
        resp.raise_for_status()
        actor = resp.json()
        outbox_urls.append(actor["outbox"])

    return outbox_urls


def _crawl_outbox(
    session: requests.Session,
    outbox_url: str,
    request_delay: float,
    limit: int | None,
    offset: int,
    processed_uris: set[str],
    creator_cache: dict,
) -> tuple[list[dict], int]:
    """Crawl an outbox, paginating through OrderedCollectionPages.

    Returns:
        A tuple of (videos, num_skipped) where num_skipped is how many
        eligible videos were skipped due to the offset.
    """
    videos: list[dict] = []
    skipped = 0

    resp = _ap_get(session, outbox_url, request_delay)
    resp.raise_for_status()
    collection = resp.json()

    page_url = collection.get("first")
    if not page_url:
        return videos, skipped

    visited_pages: set[str] = set()

    while page_url and page_url not in visited_pages:
        visited_pages.add(page_url)

        resp = _ap_get(session, page_url, request_delay)
        resp.raise_for_status()
        page = resp.json()

        if page.get("type") == "OrderedCollection":
            page_url = page.get("first")
            continue

        for item in page.get("orderedItems", []):
            if limit is not None and len(videos) >= limit:
                return videos, skipped

            object_url = item.get("object")
            if not object_url or not isinstance(object_url, str):
                continue

            if object_url in processed_uris:
                continue

            try:
                obj_resp = _ap_get(session, object_url, request_delay)
                obj_resp.raise_for_status()
            except (requests.HTTPError, requests.RequestException) as exc:
                logger.warning("Failed to fetch %s: %s", object_url, exc)
                continue

            obj = obj_resp.json()

            if obj.get("type") != "Video":
                logger.debug(
                    "Skipping non-Video type %s: %s", obj.get("type"), object_url
                )
                continue

            if obj.get("isLiveBroadcast"):
                logger.debug("Skipping live broadcast: %s", object_url)
                continue

            if skipped < offset:
                skipped += 1
                continue

            videos.append(obj)
            processed_uris.add(object_url)

        page_url = page.get("next")

    return videos, skipped


def fetch_videos(
    base_url: str,
    account: str | None,
    channel: str | None,
    limit: int | None,
    request_delay: float,
    state_file: str | None,
    offset: int = 0,
) -> list[dict]:
    """Fetch video metadata from a PeerTube instance via its ActivityPub outbox."""
    processed_uris = _load_state(state_file)
    creator_cache: dict = {}
    all_videos: list[dict] = []

    session = requests.Session()

    outbox_urls = _discover_outbox_urls(
        session, base_url, account, channel, request_delay
    )

    remaining_offset = offset
    for outbox_url in outbox_urls:
        remaining = None if limit is None else limit - len(all_videos)
        if limit is not None and remaining <= 0:
            break

        videos, num_skipped = _crawl_outbox(
            session, outbox_url, request_delay, remaining,
            remaining_offset, processed_uris, creator_cache,
        )
        all_videos.extend(videos)
        remaining_offset = max(0, remaining_offset - num_skipped)

    _save_state(state_file, processed_uris)

    return all_videos
