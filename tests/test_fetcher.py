"""Tests for peertube_to_amb.fetcher."""

import json
import tempfile

import pytest
import requests_mock as rm

from peertube_to_amb.fetcher import fetch_videos

BASE_URL = "https://peertube.example.com"


@pytest.fixture
def second_video_ap():
    """A second distinct video object for pagination tests."""
    return {
        "type": "Video",
        "id": f"{BASE_URL}/videos/watch/second-video-id",
        "name": "Second Test Video",
        "content": "Second video description",
        "duration": "PT120S",
        "published": "2026-02-20T08:00:00.000Z",
        "updated": "2026-02-21T08:00:00.000Z",
        "isLiveBroadcast": False,
    }


@pytest.fixture
def third_video_ap():
    """A third distinct video object for pagination tests."""
    return {
        "type": "Video",
        "id": f"{BASE_URL}/videos/watch/third-video-id",
        "name": "Third Test Video",
        "content": "Third video description",
        "duration": "PT90S",
        "published": "2026-02-15T08:00:00.000Z",
        "updated": "2026-02-16T08:00:00.000Z",
        "isLiveBroadcast": False,
    }


@pytest.fixture
def non_video_object():
    """An object that is not a Video (e.g. a Note)."""
    return {
        "type": "Note",
        "id": f"{BASE_URL}/objects/some-note-id",
        "content": "This is a note, not a video",
    }


class TestAccountBasedDiscovery:
    """Fetcher discovers videos via account actor -> outbox -> pages -> dereference."""

    def test_fetches_actor_then_outbox_then_page_then_video(
        self,
        sample_video_ap,
        sample_actor_person,
        sample_outbox_collection,
    ):
        single_page = {
            "@context": "https://www.w3.org/ns/activitystreams",
            "type": "OrderedCollectionPage",
            "orderedItems": [
                {
                    "type": "Create",
                    "object": f"{BASE_URL}/videos/watch/00000000-0000-4000-a000-000000000001",
                },
            ],
        }

        with rm.Mocker() as m:
            m.get(f"{BASE_URL}/accounts/testuser", json=sample_actor_person)
            m.get(sample_actor_person["outbox"], json=sample_outbox_collection)
            m.get(sample_outbox_collection["first"], json=single_page)
            m.get(f"{BASE_URL}/videos/watch/00000000-0000-4000-a000-000000000001", json=sample_video_ap)

            videos = fetch_videos(
                base_url=BASE_URL,
                account="testuser",
                channel=None,
                limit=None,
                request_delay=0,

                state_file=None,
            )

        assert len(videos) == 1

    def test_returned_video_has_correct_id(
        self,
        sample_video_ap,
        sample_actor_person,
        sample_outbox_collection,
    ):
        single_page = {
            "@context": "https://www.w3.org/ns/activitystreams",
            "type": "OrderedCollectionPage",
            "orderedItems": [
                {
                    "type": "Create",
                    "object": f"{BASE_URL}/videos/watch/00000000-0000-4000-a000-000000000001",
                },
            ],
        }

        with rm.Mocker() as m:
            m.get(f"{BASE_URL}/accounts/testuser", json=sample_actor_person)
            m.get(sample_actor_person["outbox"], json=sample_outbox_collection)
            m.get(sample_outbox_collection["first"], json=single_page)
            m.get(f"{BASE_URL}/videos/watch/00000000-0000-4000-a000-000000000001", json=sample_video_ap)

            videos = fetch_videos(
                base_url=BASE_URL,
                account="testuser",
                channel=None,
                limit=None,
                request_delay=0,

                state_file=None,
            )

        assert videos[0]["id"] == sample_video_ap["id"]


class TestPagination:
    """Fetcher follows next links across multiple pages."""

    def test_follows_next_link_to_second_page(
        self,
        sample_video_ap,
        second_video_ap,
        third_video_ap,
        sample_actor_person,
        sample_outbox_collection,
        sample_outbox_page,
        sample_outbox_page_last,
    ):
        with rm.Mocker() as m:
            m.get(f"{BASE_URL}/accounts/testuser", json=sample_actor_person)
            m.get(sample_actor_person["outbox"], json=sample_outbox_collection)
            m.get(sample_outbox_collection["first"], json=sample_outbox_page)
            m.get(sample_outbox_page["next"], json=sample_outbox_page_last)
            m.get(f"{BASE_URL}/videos/watch/00000000-0000-4000-a000-000000000001", json=sample_video_ap)
            m.get(f"{BASE_URL}/videos/watch/second-video-id", json=second_video_ap)
            m.get(f"{BASE_URL}/videos/watch/third-video-id", json=third_video_ap)

            videos = fetch_videos(
                base_url=BASE_URL,
                account="testuser",
                channel=None,
                limit=None,
                request_delay=0,

                state_file=None,
            )

        assert len(videos) == 3

    def test_stops_when_no_next_link(
        self,
        sample_video_ap,
        sample_actor_person,
        sample_outbox_collection,
    ):
        page_no_next = {
            "@context": "https://www.w3.org/ns/activitystreams",
            "type": "OrderedCollectionPage",
            "orderedItems": [
                {
                    "type": "Create",
                    "object": f"{BASE_URL}/videos/watch/00000000-0000-4000-a000-000000000001",
                },
            ],
        }

        with rm.Mocker() as m:
            m.get(f"{BASE_URL}/accounts/testuser", json=sample_actor_person)
            m.get(sample_actor_person["outbox"], json=sample_outbox_collection)
            m.get(sample_outbox_collection["first"], json=page_no_next)
            m.get(f"{BASE_URL}/videos/watch/00000000-0000-4000-a000-000000000001", json=sample_video_ap)

            videos = fetch_videos(
                base_url=BASE_URL,
                account="testuser",
                channel=None,
                limit=None,
                request_delay=0,

                state_file=None,
            )

        assert len(videos) == 1


class TestLimitParameter:
    """The limit parameter caps the number of videos returned."""

    def test_limit_caps_results(
        self,
        sample_video_ap,
        second_video_ap,
        sample_actor_person,
        sample_outbox_collection,
    ):
        page = {
            "@context": "https://www.w3.org/ns/activitystreams",
            "type": "OrderedCollectionPage",
            "orderedItems": [
                {
                    "type": "Create",
                    "object": f"{BASE_URL}/videos/watch/00000000-0000-4000-a000-000000000001",
                },
                {
                    "type": "Create",
                    "object": f"{BASE_URL}/videos/watch/second-video-id",
                },
            ],
        }

        with rm.Mocker() as m:
            m.get(f"{BASE_URL}/accounts/testuser", json=sample_actor_person)
            m.get(sample_actor_person["outbox"], json=sample_outbox_collection)
            m.get(sample_outbox_collection["first"], json=page)
            m.get(f"{BASE_URL}/videos/watch/00000000-0000-4000-a000-000000000001", json=sample_video_ap)
            m.get(f"{BASE_URL}/videos/watch/second-video-id", json=second_video_ap)

            videos = fetch_videos(
                base_url=BASE_URL,
                account="testuser",
                channel=None,
                limit=1,
                request_delay=0,

                state_file=None,
            )

        assert len(videos) == 1


class TestStateFile:
    """State file tracks already-processed videos to skip on next run."""

    def test_skips_videos_already_in_state_file(
        self,
        sample_video_ap,
        second_video_ap,
        sample_actor_person,
        sample_outbox_collection,
    ):
        page = {
            "@context": "https://www.w3.org/ns/activitystreams",
            "type": "OrderedCollectionPage",
            "orderedItems": [
                {
                    "type": "Create",
                    "object": f"{BASE_URL}/videos/watch/00000000-0000-4000-a000-000000000001",
                },
                {
                    "type": "Create",
                    "object": f"{BASE_URL}/videos/watch/second-video-id",
                },
            ],
        }

        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".json", delete=False
        ) as sf:
            json.dump(
                [f"{BASE_URL}/videos/watch/00000000-0000-4000-a000-000000000001"],
                sf,
            )
            state_path = sf.name

        with rm.Mocker() as m:
            m.get(f"{BASE_URL}/accounts/testuser", json=sample_actor_person)
            m.get(sample_actor_person["outbox"], json=sample_outbox_collection)
            m.get(sample_outbox_collection["first"], json=page)
            m.get(f"{BASE_URL}/videos/watch/second-video-id", json=second_video_ap)

            videos = fetch_videos(
                base_url=BASE_URL,
                account="testuser",
                channel=None,
                limit=None,
                request_delay=0,

                state_file=state_path,
            )

        assert len(videos) == 1
        assert videos[0]["id"] == second_video_ap["id"]


class TestHttp429Retry:
    """HTTP 429 responses trigger retry with backoff."""

    def test_retries_on_429_then_succeeds(
        self,
        sample_video_ap,
        sample_actor_person,
        sample_outbox_collection,
    ):
        page = {
            "@context": "https://www.w3.org/ns/activitystreams",
            "type": "OrderedCollectionPage",
            "orderedItems": [
                {
                    "type": "Create",
                    "object": f"{BASE_URL}/videos/watch/00000000-0000-4000-a000-000000000001",
                },
            ],
        }

        with rm.Mocker() as m:
            m.get(f"{BASE_URL}/accounts/testuser", json=sample_actor_person)
            m.get(sample_actor_person["outbox"], json=sample_outbox_collection)
            m.get(sample_outbox_collection["first"], json=page)
            m.get(
                f"{BASE_URL}/videos/watch/00000000-0000-4000-a000-000000000001",
                [
                    {"status_code": 429, "headers": {"Retry-After": "0"}, "text": "Too Many Requests"},
                    {"json": sample_video_ap},
                ],
            )

            videos = fetch_videos(
                base_url=BASE_URL,
                account="testuser",
                channel=None,
                limit=None,
                request_delay=0,

                state_file=None,
            )

        assert len(videos) == 1


class TestNonVideoObjectsSkipped:
    """Non-Video objects are skipped after dereference."""

    def test_non_video_object_is_skipped(
        self,
        non_video_object,
        sample_actor_person,
        sample_outbox_collection,
    ):
        page = {
            "@context": "https://www.w3.org/ns/activitystreams",
            "type": "OrderedCollectionPage",
            "orderedItems": [
                {
                    "type": "Create",
                    "object": f"{BASE_URL}/objects/some-note-id",
                },
            ],
        }

        with rm.Mocker() as m:
            m.get(f"{BASE_URL}/accounts/testuser", json=sample_actor_person)
            m.get(sample_actor_person["outbox"], json=sample_outbox_collection)
            m.get(sample_outbox_collection["first"], json=page)
            m.get(f"{BASE_URL}/objects/some-note-id", json=non_video_object)

            videos = fetch_videos(
                base_url=BASE_URL,
                account="testuser",
                channel=None,
                limit=None,
                request_delay=0,

                state_file=None,
            )

        assert len(videos) == 0


class TestUnreachableVideoSkipped:
    """Unreachable video URLs are logged and skipped gracefully."""

    def test_unreachable_video_url_is_skipped(
        self,
        sample_video_ap,
        sample_actor_person,
        sample_outbox_collection,
    ):
        page = {
            "@context": "https://www.w3.org/ns/activitystreams",
            "type": "OrderedCollectionPage",
            "orderedItems": [
                {
                    "type": "Create",
                    "object": f"{BASE_URL}/videos/watch/broken-video-id",
                },
                {
                    "type": "Create",
                    "object": f"{BASE_URL}/videos/watch/00000000-0000-4000-a000-000000000001",
                },
            ],
        }

        with rm.Mocker() as m:
            m.get(f"{BASE_URL}/accounts/testuser", json=sample_actor_person)
            m.get(sample_actor_person["outbox"], json=sample_outbox_collection)
            m.get(sample_outbox_collection["first"], json=page)
            m.get(f"{BASE_URL}/videos/watch/broken-video-id", status_code=500, text="Internal Server Error")
            m.get(f"{BASE_URL}/videos/watch/00000000-0000-4000-a000-000000000001", json=sample_video_ap)

            videos = fetch_videos(
                base_url=BASE_URL,
                account="testuser",
                channel=None,
                limit=None,
                request_delay=0,

                state_file=None,
            )

        assert len(videos) == 1
        assert videos[0]["id"] == sample_video_ap["id"]


class TestOffsetParameter:
    """The offset parameter skips the first N videos before collecting."""

    def test_offset_skips_first_video(
        self,
        sample_video_ap,
        second_video_ap,
        sample_actor_person,
        sample_outbox_collection,
    ):
        page = {
            "@context": "https://www.w3.org/ns/activitystreams",
            "type": "OrderedCollectionPage",
            "orderedItems": [
                {
                    "type": "Create",
                    "object": f"{BASE_URL}/videos/watch/00000000-0000-4000-a000-000000000001",
                },
                {
                    "type": "Create",
                    "object": f"{BASE_URL}/videos/watch/second-video-id",
                },
            ],
        }

        with rm.Mocker() as m:
            m.get(f"{BASE_URL}/accounts/testuser", json=sample_actor_person)
            m.get(sample_actor_person["outbox"], json=sample_outbox_collection)
            m.get(sample_outbox_collection["first"], json=page)
            m.get(f"{BASE_URL}/videos/watch/00000000-0000-4000-a000-000000000001", json=sample_video_ap)
            m.get(f"{BASE_URL}/videos/watch/second-video-id", json=second_video_ap)

            videos = fetch_videos(
                base_url=BASE_URL,
                account="testuser",
                channel=None,
                limit=None,
                request_delay=0,
                state_file=None,
                offset=1,
            )

        assert len(videos) == 1
        assert videos[0]["id"] == second_video_ap["id"]

    def test_offset_with_limit(
        self,
        sample_video_ap,
        second_video_ap,
        third_video_ap,
        sample_actor_person,
        sample_outbox_collection,
    ):
        page = {
            "@context": "https://www.w3.org/ns/activitystreams",
            "type": "OrderedCollectionPage",
            "orderedItems": [
                {
                    "type": "Create",
                    "object": f"{BASE_URL}/videos/watch/00000000-0000-4000-a000-000000000001",
                },
                {
                    "type": "Create",
                    "object": f"{BASE_URL}/videos/watch/second-video-id",
                },
                {
                    "type": "Create",
                    "object": f"{BASE_URL}/videos/watch/third-video-id",
                },
            ],
        }

        with rm.Mocker() as m:
            m.get(f"{BASE_URL}/accounts/testuser", json=sample_actor_person)
            m.get(sample_actor_person["outbox"], json=sample_outbox_collection)
            m.get(sample_outbox_collection["first"], json=page)
            m.get(f"{BASE_URL}/videos/watch/00000000-0000-4000-a000-000000000001", json=sample_video_ap)
            m.get(f"{BASE_URL}/videos/watch/second-video-id", json=second_video_ap)
            m.get(f"{BASE_URL}/videos/watch/third-video-id", json=third_video_ap)

            videos = fetch_videos(
                base_url=BASE_URL,
                account="testuser",
                channel=None,
                limit=1,
                request_delay=0,
                state_file=None,
                offset=1,
            )

        assert len(videos) == 1
        assert videos[0]["id"] == second_video_ap["id"]

    def test_offset_beyond_available_returns_empty(
        self,
        sample_video_ap,
        sample_actor_person,
        sample_outbox_collection,
    ):
        page = {
            "@context": "https://www.w3.org/ns/activitystreams",
            "type": "OrderedCollectionPage",
            "orderedItems": [
                {
                    "type": "Create",
                    "object": f"{BASE_URL}/videos/watch/00000000-0000-4000-a000-000000000001",
                },
            ],
        }

        with rm.Mocker() as m:
            m.get(f"{BASE_URL}/accounts/testuser", json=sample_actor_person)
            m.get(sample_actor_person["outbox"], json=sample_outbox_collection)
            m.get(sample_outbox_collection["first"], json=page)
            m.get(f"{BASE_URL}/videos/watch/00000000-0000-4000-a000-000000000001", json=sample_video_ap)

            videos = fetch_videos(
                base_url=BASE_URL,
                account="testuser",
                channel=None,
                limit=None,
                request_delay=0,
                state_file=None,
                offset=10,
            )

        assert len(videos) == 0


class TestChannelBasedDiscovery:
    """Fetcher can discover videos via channel actor instead of account."""

    def test_channel_path_fetches_group_actor(
        self,
        sample_video_ap,
        sample_actor_group,
        sample_outbox_collection,
    ):
        channel_outbox_collection = {
            **sample_outbox_collection,
            "first": f"{BASE_URL}/video-channels/test_channel/outbox?page=true",
        }
        page = {
            "@context": "https://www.w3.org/ns/activitystreams",
            "type": "OrderedCollectionPage",
            "orderedItems": [
                {
                    "type": "Create",
                    "object": f"{BASE_URL}/videos/watch/00000000-0000-4000-a000-000000000001",
                },
            ],
        }
        channel_actor = {
            **sample_actor_group,
            "outbox": f"{BASE_URL}/video-channels/test_channel/outbox",
        }

        with rm.Mocker() as m:
            m.get(f"{BASE_URL}/video-channels/test_channel", json=channel_actor)
            m.get(channel_actor["outbox"], json=channel_outbox_collection)
            m.get(channel_outbox_collection["first"], json=page)
            m.get(f"{BASE_URL}/videos/watch/00000000-0000-4000-a000-000000000001", json=sample_video_ap)

            videos = fetch_videos(
                base_url=BASE_URL,
                account=None,
                channel="test_channel",
                limit=None,
                request_delay=0,

                state_file=None,
            )

        assert len(videos) == 1
        assert videos[0]["name"] == sample_video_ap["name"]
