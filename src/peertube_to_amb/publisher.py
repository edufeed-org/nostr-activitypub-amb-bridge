"""Nostr event signing and relay publishing."""

import asyncio
import logging

from nostr_sdk import Client, EventBuilder, Keys, Kind, NostrSigner, RelayUrl, SecretKey, Tag

logger = logging.getLogger(__name__)


async def publish_events(
    events: list,
    relay_url: str,
    private_key: str,
) -> list[bool]:
    """Sign and publish Nostr events to a relay.

    Each event dict is signed with the provided private key and sent to
    the specified relay. Returns a list of success/failure booleans
    corresponding to each event.

    Args:
        events: List of event dicts with 'tags' and 'content' keys.
        relay_url: WebSocket URL of the Nostr relay.
        private_key: Hex-encoded Nostr private key for signing events.

    Returns:
        A list of booleans, True if the event was accepted by the relay.
    """
    secret_key = SecretKey.parse(private_key)
    keys = Keys(secret_key)
    signer = NostrSigner.keys(keys)

    client = Client(signer)
    await client.add_relay(RelayUrl.parse(relay_url))
    await client.connect()

    results = []
    for event_dict in events:
        try:
            tags = [Tag.parse(t) for t in event_dict["tags"]]
            content = event_dict.get("content", "")
            builder = EventBuilder(Kind(30142), content).tags(tags)
            output = await client.send_event_builder(builder)
            logger.info("Published event %s", output.id.to_hex())
            results.append(True)
        except Exception as exc:
            d_tag = next((t[1] for t in event_dict["tags"] if t[0] == "d"), "?")
            logger.warning("Failed to publish event %s: %s", d_tag, exc)
            results.append(False)

    await client.disconnect()
    return results
