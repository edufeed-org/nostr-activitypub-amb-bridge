"""Tests for peertube_to_amb.publisher."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from nostr_sdk import RelayUrl

from peertube_to_amb.publisher import publish_events


@pytest.fixture
def sample_event_data():
    """A single event dict with tags and content ready for publishing."""
    return {
        "tags": [
            [
                "d",
                "https://peertube.example.com/videos/watch/00000000-0000-4000-a000-000000000001",
            ],
            ["type", "LearningResource"],
            ["type", "VideoObject"],
            ["name", "Test Video About 3D Printing"],
            ["duration", "PT156S"],
            ["datePublished", "2026-02-28T10:25:54.431Z"],
            ["inLanguage", "de"],
            [
                "license:id",
                "https://creativecommons.org/licenses/by/4.0/",
            ],
            ["isAccessibleForFree", "true"],
            ["learningResourceType:id", "http://w3id.org/kim/hcrt/video"],
            ["learningResourceType:prefLabel:en", "Video"],
        ],
        "content": "",
    }


@pytest.fixture
def two_event_data(sample_event_data):
    """Two events for batch publishing tests."""
    second_event = {
        "tags": [
            [
                "d",
                "https://peertube.example.com/videos/watch/second-video",
            ],
            ["type", "LearningResource"],
            ["type", "VideoObject"],
            ["name", "Second Video"],
        ],
        "content": "Second video description",
    }
    return [sample_event_data, second_event]


def _mock_client():
    """Create a mock nostr_sdk Client with async methods."""
    client = MagicMock()
    client.add_relay = AsyncMock()
    client.connect = AsyncMock()
    client.disconnect = AsyncMock()

    mock_output = MagicMock()
    mock_output.id.to_hex.return_value = "abc123"
    client.send_event_builder = AsyncMock(return_value=mock_output)

    return client


@pytest.mark.asyncio
class TestEventPublishing:
    """Published events are sent via the nostr-sdk Client."""

    async def test_sends_one_event(
        self, sample_event_data, relay_url, sample_private_key
    ):
        mock_client = _mock_client()

        with patch("peertube_to_amb.publisher.Client", return_value=mock_client):
            results = await publish_events(
                [sample_event_data], relay_url, sample_private_key
            )

        assert results == [True]
        assert mock_client.send_event_builder.call_count == 1

    async def test_connects_to_relay(
        self, sample_event_data, relay_url, sample_private_key
    ):
        mock_client = _mock_client()

        with patch("peertube_to_amb.publisher.Client", return_value=mock_client):
            await publish_events(
                [sample_event_data], relay_url, sample_private_key
            )

        args = mock_client.add_relay.call_args[0]
        assert len(args) == 1
        assert isinstance(args[0], RelayUrl)
        mock_client.connect.assert_awaited_once()
        mock_client.disconnect.assert_awaited_once()


@pytest.mark.asyncio
class TestBatchPublishing:
    """Batch publishing returns success/failure booleans per event."""

    async def test_returns_list_of_booleans(
        self, two_event_data, relay_url, sample_private_key
    ):
        mock_client = _mock_client()

        with patch("peertube_to_amb.publisher.Client", return_value=mock_client):
            results = await publish_events(
                two_event_data, relay_url, sample_private_key
            )

        assert len(results) == 2
        assert all(isinstance(r, bool) for r in results)

    async def test_all_accepted_returns_all_true(
        self, two_event_data, relay_url, sample_private_key
    ):
        mock_client = _mock_client()

        with patch("peertube_to_amb.publisher.Client", return_value=mock_client):
            results = await publish_events(
                two_event_data, relay_url, sample_private_key
            )

        assert results == [True, True]


@pytest.mark.asyncio
class TestPublishFailure:
    """Handle publish failures gracefully."""

    async def test_send_failure_returns_false(
        self, sample_event_data, relay_url, sample_private_key
    ):
        mock_client = _mock_client()
        mock_client.send_event_builder = AsyncMock(
            side_effect=Exception("relay rejected")
        )

        with patch("peertube_to_amb.publisher.Client", return_value=mock_client):
            results = await publish_events(
                [sample_event_data], relay_url, sample_private_key
            )

        assert results == [False]

    async def test_partial_failure(
        self, two_event_data, relay_url, sample_private_key
    ):
        mock_client = _mock_client()
        mock_output = MagicMock()
        mock_output.id.to_hex.return_value = "abc123"
        mock_client.send_event_builder = AsyncMock(
            side_effect=[mock_output, Exception("second failed")]
        )

        with patch("peertube_to_amb.publisher.Client", return_value=mock_client):
            results = await publish_events(
                two_event_data, relay_url, sample_private_key
            )

        assert results == [True, False]
