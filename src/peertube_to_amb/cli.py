"""CLI entry point for peertube-to-amb."""

import argparse
import asyncio
import logging
import os
import sys

from nostr_sdk import Keys, SecretKey

from peertube_to_amb.fetcher import fetch_videos
from peertube_to_amb.mapper import map_video_to_nostr_tags
from peertube_to_amb.publisher import publish_events

logger = logging.getLogger(__name__)


def _build_bridge_parser(subparsers: argparse._SubParsersAction) -> None:
    """Add the 'bridge' subcommand parser."""
    parser = subparsers.add_parser(
        "bridge",
        help="Fetch PeerTube videos and publish as AMB (Nostr) events",
    )

    parser.add_argument(
        "peertube_url",
        help="Base URL of the PeerTube instance (e.g. https://videos.example.com)",
    )
    parser.add_argument(
        "--relay-url",
        default="ws://localhost:3334",
        help="Nostr relay WebSocket URL (default: ws://localhost:3334)",
    )
    parser.add_argument(
        "--account",
        default=None,
        help="PeerTube account to fetch videos from",
    )
    parser.add_argument(
        "--channel",
        default=None,
        help="PeerTube channel to fetch videos from",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=None,
        help="Maximum number of videos to fetch",
    )
    parser.add_argument(
        "--offset",
        type=int,
        default=0,
        help="Number of videos to skip before fetching (default: 0)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Process videos without publishing to relay",
    )
    parser.add_argument(
        "--request-delay",
        type=float,
        default=0.5,
        help="Delay in seconds between HTTP requests (default: 0.5)",
    )
    parser.add_argument(
        "--max-concurrency",
        type=int,
        default=1,
        help="Maximum number of concurrent requests (default: 1)",
    )
    parser.add_argument(
        "--state-file",
        default=None,
        help="Path to state file for tracking processed videos",
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Enable verbose logging output",
    )


def _build_generate_key_parser(subparsers: argparse._SubParsersAction) -> None:
    """Add the 'generate-key' subcommand parser."""
    subparsers.add_parser(
        "generate-key",
        help="Generate a new Nostr keypair (private + public key)",
    )


def build_parser() -> argparse.ArgumentParser:
    """Build and return the argument parser."""
    parser = argparse.ArgumentParser(
        prog="peertube-to-amb",
        description="Bridge PeerTube videos to AMB (Nostr) events.",
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Enable verbose logging output",
    )

    subparsers = parser.add_subparsers(dest="command")
    _build_bridge_parser(subparsers)
    _build_generate_key_parser(subparsers)

    return parser


def run_generate_key() -> None:
    """Generate a new Nostr keypair and print it."""
    keys = Keys.generate()

    print(f"Private key (hex):  {keys.secret_key().to_hex()}")
    print(f"Private key (nsec): {keys.secret_key().to_bech32()}")
    print(f"Public key  (hex):  {keys.public_key().to_hex()}")
    print(f"Public key  (npub): {keys.public_key().to_bech32()}")
    print()
    print("To use this key, set the environment variable:")
    print(f"  export NOSTR_PRIVATE_KEY=\"{keys.secret_key().to_bech32()}\"")


def _resolve_private_key(raw: str) -> str:
    """Accept a hex or nsec1 private key and return hex."""
    secret_key = SecretKey.parse(raw)
    return secret_key.to_hex()


def run_bridge(args: argparse.Namespace) -> None:
    """Run the fetch-map-publish pipeline."""
    raw_key = os.environ.get("NOSTR_PRIVATE_KEY")

    if not args.dry_run and not raw_key:
        logger.error("NOSTR_PRIVATE_KEY environment variable is required unless --dry-run is set")
        sys.exit(1)

    private_key = _resolve_private_key(raw_key) if raw_key else None

    logger.info("Fetching videos from %s", args.peertube_url)
    videos = fetch_videos(
        base_url=args.peertube_url,
        account=args.account,
        channel=args.channel,
        limit=args.limit,
        offset=args.offset,
        request_delay=args.request_delay,
        state_file=args.state_file,
    )
    logger.info("Fetched %d videos", len(videos))

    events = []
    for video in videos:
        tags, content = map_video_to_nostr_tags(video)
        events.append({"tags": tags, "content": content})
    logger.info("Mapped %d videos to Nostr events", len(events))

    if args.dry_run:
        logger.info("Dry run: skipping publish step")
        for event in events:
            logger.info("Event: %s", event)
        return

    results = asyncio.run(publish_events(
        events=events,
        relay_url=args.relay_url,
        private_key=private_key,
    ))
    succeeded = sum(1 for r in results if r)
    logger.info("Published %d/%d events", succeeded, len(results))


def main() -> None:
    """CLI entry point."""
    parser = build_parser()
    args = parser.parse_args()

    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )

    if args.command == "generate-key":
        run_generate_key()
    elif args.command == "bridge":
        run_bridge(args)
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
