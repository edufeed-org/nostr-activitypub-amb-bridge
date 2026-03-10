"""Shared pytest fixtures with real PeerTube ActivityPub JSON data."""

import pytest


@pytest.fixture
def sample_video_ap():
    """A full PeerTube AP Video object based on verified real data."""
    return {
        "type": "Video",
        "id": "https://peertube.example.com/videos/watch/00000000-0000-4000-a000-000000000001",
        "name": "Test Video About 3D Printing",
        "content": "<p>This is a test video description.</p>",
        "summary": "Short summary of the test video",
        "mediaType": "text/markdown",
        "sensitive": False,
        "duration": "PT156S",
        "views": 42,
        "published": "2026-02-28T10:25:54.431Z",
        "updated": "2026-03-01T10:02:46.940Z",
        "originallyPublishedAt": "2026-02-20T08:00:00.000Z",
        "isLiveBroadcast": False,
        "category": {
            "identifier": "13",
            "name": "Education",
        },
        "licence": {
            "identifier": "1",
            "name": "CC BY 4.0",
        },
        "language": {
            "identifier": "de",
            "name": "German",
        },
        "tag": [
            {"type": "Hashtag", "name": "3dprinting"},
            {"type": "Hashtag", "name": "orcaslicer"},
            {"type": "Mention", "name": "@admin@peertube.example.com"},
        ],
        "icon": [
            {
                "type": "Image",
                "url": "https://peertube.example.com/lazy-static/thumbnails/00000000-0000-4000-a000-000000000002.jpg",
                "mediaType": "image/jpeg",
                "width": 280,
                "height": 157,
            },
            {
                "type": "Image",
                "url": "https://peertube.example.com/lazy-static/previews/00000000-0000-4000-a000-000000000002.jpg",
                "mediaType": "image/jpeg",
                "width": 850,
                "height": 480,
            },
        ],
        "url": [
            {
                "type": "Link",
                "mediaType": "text/html",
                "href": "https://peertube.example.com/w/ovjzowkYv7vf5Mfa4SoRPb",
            },
            {
                "type": "Link",
                "mediaType": "application/x-mpegURL",
                "href": "https://peertube.example.com/static/streaming-playlists/hls/00000000/master.m3u8",
                "tag": [
                    {
                        "type": "Link",
                        "mediaType": "video/mp4",
                        "href": "https://peertube.example.com/static/streaming-playlists/hls/00000000/9aacda50-1080-fragmented.mp4",
                        "height": 1080,
                        "width": 1920,
                        "size": 38971443,
                        "fps": 30,
                    },
                    {
                        "type": "Link",
                        "mediaType": "video/mp4",
                        "href": "https://peertube.example.com/static/streaming-playlists/hls/00000000/e03f254c-720-fragmented.mp4",
                        "height": 720,
                        "width": 1280,
                        "size": 8552237,
                        "fps": 30,
                    },
                    {
                        "type": "Link",
                        "mediaType": "application/x-bittorrent",
                        "href": "https://peertube.example.com/static/torrents/00000000-1080.torrent",
                        "height": 1080,
                    },
                    {
                        "type": "Infohash",
                        "name": "abc123def456",
                    },
                    {
                        "type": "Link",
                        "mediaType": "application/x-bittorrent;x-scheme-handler/magnet",
                        "href": "magnet:?xt=urn:btih:abc123",
                        "height": 1080,
                    },
                    {
                        "type": "Link",
                        "rel": ["metadata"],
                        "mediaType": "application/json",
                        "href": "https://peertube.example.com/api/v1/videos/00000000/metadata/1234",
                        "height": 1080,
                    },
                ],
            },
        ],
        "attributedTo": [
            "https://peertube.example.com/accounts/testuser",
            "https://peertube.example.com/video-channels/test_channel",
        ],
        "subtitleLanguage": [
            {
                "identifier": "en",
                "name": "English",
                "url": [
                    {
                        "type": "Link",
                        "mediaType": "text/vtt",
                        "href": "https://peertube.example.com/lazy-static/video-captions/00000000-en.vtt",
                    },
                    {
                        "type": "Link",
                        "mediaType": "application/x-mpegURL",
                        "href": "https://peertube.example.com/lazy-static/video-captions/00000000-en.vtt",
                    },
                ],
            },
            {
                "identifier": "fr",
                "name": "French",
                "url": [
                    {
                        "type": "Link",
                        "mediaType": "text/vtt",
                        "href": "https://peertube.example.com/lazy-static/video-captions/00000000-fr.vtt",
                    },
                    {
                        "type": "Link",
                        "mediaType": "application/x-mpegURL",
                        "href": "https://peertube.example.com/lazy-static/video-captions/00000000-fr.vtt",
                    },
                ],
            },
        ],
        "support": "Test support text",
    }


@pytest.fixture
def sample_video_ap_minimal():
    """A Video with null content, empty tags, null originallyPublishedAt."""
    return {
        "type": "Video",
        "id": "https://peertube.example.com/videos/watch/minimal-video-id",
        "name": "Minimal Test Video",
        "content": None,
        "summary": None,
        "mediaType": "text/markdown",
        "sensitive": False,
        "duration": "PT60S",
        "views": 0,
        "published": "2026-01-15T12:00:00.000Z",
        "updated": "2026-01-16T14:30:00.000Z",
        "originallyPublishedAt": None,
        "isLiveBroadcast": False,
        "category": {
            "identifier": "13",
            "name": "Education",
        },
        "licence": {
            "identifier": "7",
            "name": "Public Domain Dedication",
        },
        "language": {
            "identifier": "en",
            "name": "English",
        },
        "tag": [],
        "icon": [
            {
                "type": "Image",
                "url": "https://peertube.example.com/lazy-static/thumbnails/minimal-thumb.jpg",
                "mediaType": "image/jpeg",
                "width": 280,
                "height": 157,
            },
        ],
        "url": [
            {
                "type": "Link",
                "mediaType": "text/html",
                "href": "https://peertube.example.com/w/minimalvideo",
            },
        ],
        "attributedTo": [
            "https://peertube.example.com/accounts/testuser",
        ],
        "subtitleLanguage": [],
    }


@pytest.fixture
def sample_video_ap_with_summary_fallback():
    """A Video with null content but a non-null summary for fallback."""
    return {
        "type": "Video",
        "id": "https://peertube.example.com/videos/watch/summary-fallback-id",
        "name": "Video With Summary Only",
        "content": None,
        "summary": "This is the summary text used as fallback",
        "mediaType": "text/markdown",
        "sensitive": False,
        "duration": "PT300S",
        "views": 10,
        "published": "2026-03-01T09:00:00.000Z",
        "updated": "2026-03-02T09:00:00.000Z",
        "originallyPublishedAt": None,
        "isLiveBroadcast": False,
        "category": {
            "identifier": "13",
            "name": "Education",
        },
        "licence": {
            "identifier": "2",
            "name": "CC BY-SA 4.0",
        },
        "language": {
            "identifier": "en",
            "name": "English",
        },
        "tag": [],
        "icon": [
            {
                "type": "Image",
                "url": "https://peertube.example.com/lazy-static/thumbnails/summary-thumb.jpg",
                "mediaType": "image/jpeg",
                "width": 280,
                "height": 157,
            },
        ],
        "url": [
            {
                "type": "Link",
                "mediaType": "text/html",
                "href": "https://peertube.example.com/w/summaryvideo",
            },
        ],
        "attributedTo": [
            "https://peertube.example.com/accounts/testuser",
        ],
        "subtitleLanguage": [],
    }


@pytest.fixture
def sample_video_ap_live():
    """A live broadcast Video that should be skipped/flagged."""
    return {
        "type": "Video",
        "id": "https://peertube.example.com/videos/watch/live-video-id",
        "name": "Live Stream Test",
        "content": "Live content",
        "summary": None,
        "mediaType": "text/markdown",
        "sensitive": False,
        "duration": "PT0S",
        "views": 100,
        "published": "2026-03-05T18:00:00.000Z",
        "updated": "2026-03-05T20:00:00.000Z",
        "originallyPublishedAt": None,
        "isLiveBroadcast": True,
        "category": {
            "identifier": "13",
            "name": "Education",
        },
        "licence": {
            "identifier": "1",
            "name": "CC BY 4.0",
        },
        "language": {
            "identifier": "en",
            "name": "English",
        },
        "tag": [],
        "icon": [],
        "url": [],
        "attributedTo": [],
        "subtitleLanguage": [],
    }


@pytest.fixture
def sample_outbox_collection():
    """An OrderedCollection response from a PeerTube outbox."""
    return {
        "@context": "https://www.w3.org/ns/activitystreams",
        "type": "OrderedCollection",
        "totalItems": 2586,
        "first": "https://peertube.example.com/accounts/testuser/outbox?page=true",
    }


@pytest.fixture
def sample_outbox_page():
    """An OrderedCollectionPage with orderedItems and next link."""
    return {
        "@context": "https://www.w3.org/ns/activitystreams",
        "type": "OrderedCollectionPage",
        "id": "https://peertube.example.com/accounts/testuser/outbox?page=true",
        "next": "https://peertube.example.com/accounts/testuser/outbox?page=true&cursor=2",
        "partOf": "https://peertube.example.com/accounts/testuser/outbox",
        "orderedItems": [
            {
                "type": "Create",
                "object": "https://peertube.example.com/videos/watch/00000000-0000-4000-a000-000000000001",
            },
            {
                "type": "Create",
                "object": "https://peertube.example.com/videos/watch/second-video-id",
            },
        ],
    }


@pytest.fixture
def sample_outbox_page_last():
    """A final OrderedCollectionPage with no next link."""
    return {
        "@context": "https://www.w3.org/ns/activitystreams",
        "type": "OrderedCollectionPage",
        "id": "https://peertube.example.com/accounts/testuser/outbox?page=true&cursor=2",
        "partOf": "https://peertube.example.com/accounts/testuser/outbox",
        "orderedItems": [
            {
                "type": "Create",
                "object": "https://peertube.example.com/videos/watch/third-video-id",
            },
        ],
    }


@pytest.fixture
def sample_actor_person():
    """A Person actor for attributedTo dereference."""
    return {
        "@context": "https://www.w3.org/ns/activitystreams",
        "type": "Person",
        "id": "https://peertube.example.com/accounts/testuser",
        "name": "testchannel",
        "preferredUsername": "testuser",
        "outbox": "https://peertube.example.com/accounts/testuser/outbox",
        "inbox": "https://peertube.example.com/accounts/testuser/inbox",
        "url": "https://peertube.example.com/accounts/testuser",
    }


@pytest.fixture
def sample_actor_group():
    """A Group actor for channel attributedTo dereference."""
    return {
        "@context": "https://www.w3.org/ns/activitystreams",
        "type": "Group",
        "id": "https://peertube.example.com/video-channels/test_channel",
        "name": "Test Channel",
        "preferredUsername": "test_channel",
        "outbox": "https://peertube.example.com/video-channels/test_channel/outbox",
        "inbox": "https://peertube.example.com/video-channels/test_channel/inbox",
        "url": "https://peertube.example.com/video-channels/test_channel",
    }


@pytest.fixture
def creator_cache(sample_actor_person, sample_actor_group):
    """Pre-populated creator cache for mapper tests."""
    return {
        "https://peertube.example.com/accounts/testuser": sample_actor_person,
        "https://peertube.example.com/video-channels/test_channel": sample_actor_group,
    }


@pytest.fixture
def relay_url():
    """Return a test relay URL."""
    return "ws://localhost:3334"


@pytest.fixture
def sample_private_key():
    """A hex-encoded test private key (NOT a real key, for testing only)."""
    return "a" * 64
