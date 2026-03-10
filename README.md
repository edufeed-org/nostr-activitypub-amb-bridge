# peertube-to-amb

Bridge PeerTube videos to AMB (Nostr) events. Crawls a PeerTube instance via its ActivityPub outbox, maps video metadata to Nostr event tags (kind `30142`), and publishes them to a Nostr relay.

## Installation

```bash
pip install -e .
```

For development:

```bash
pip install -e ".[dev]"
```

## Quick start

Generate a Nostr keypair:

```bash
peertube-to-amb generate-key
```

This prints a new private/public key pair in both hex and bech32 (nsec/npub) formats:

```
Private key (hex):  <private_key_hex>
Private key (nsec): nsec1...
Public key  (hex):  <public_key_hex>
Public key  (npub): npub1...

To use this key, set the environment variable:
  export NOSTR_PRIVATE_KEY="nsec1..."
```

Then bridge videos from a PeerTube instance:

```bash
export NOSTR_PRIVATE_KEY="<your_private_key>"
peertube-to-amb bridge https://peertube.example.com --account my-account
```

## Commands

### `generate-key`

Generate a new Nostr keypair (private + public key).

```bash
peertube-to-amb generate-key
```

No arguments required. Outputs keys in both hex and bech32 (nsec/npub) formats.

### `bridge`

Fetch PeerTube videos and publish them as AMB (Nostr) events.

```
peertube-to-amb bridge <peertube_url> [options]
```

#### Required argument

| Argument | Description |
|---|---|
| `peertube_url` | Base URL of the PeerTube instance |

#### Options

| Option | Default | Description |
|---|---|---|
| `--account <name>` | — | PeerTube account to fetch videos from |
| `--channel <name>` | — | PeerTube channel to fetch videos from |
| `--limit <n>` | all | Maximum number of videos to fetch |
| `--relay-url <url>` | `ws://localhost:3334` | Nostr relay WebSocket URL |
| `--request-delay <secs>` | `0.5` | Delay in seconds between HTTP requests |
| `--max-concurrency <n>` | `1` | Maximum number of concurrent requests |
| `--state-file <path>` | — | Path to a JSON file for tracking already-processed videos (skips duplicates across runs) |
| `--dry-run` | off | Process and log videos without publishing to the relay |

### Global options

| Option | Default | Description |
|---|---|---|
| `--verbose` | off | Enable debug-level logging output |

### Environment variables

| Variable | Required | Description |
|---|---|---|
| `NOSTR_PRIVATE_KEY` | Yes (unless `--dry-run`) | Nostr private key — accepts both hex and bech32 (`nsec1...`) formats |

## Examples

Dry run — fetch 10 videos from an account and print the mapped events:

```bash
peertube-to-amb bridge https://peertube.example.com --account my-account --limit 10 --dry-run --verbose
```

Publish all videos from a channel to a relay:

```bash
export NOSTR_PRIVATE_KEY="nsec1..."
peertube-to-amb bridge https://peertube.example.com --channel <channel-name> --relay-url ws://relay.example.com:3334
```

Resume from a previous run using a state file:

```bash
peertube-to-amb bridge https://peertube.example.com --account <account-name> --state-file state.json
```

The state file tracks which videos have already been processed, so subsequent runs skip them.

## Docker

### Using docker compose

```bash
docker compose up -d
docker compose exec app peertube-to-amb generate-key
export NOSTR_PRIVATE_KEY="nsec1..."
docker compose exec app peertube-to-amb bridge https://peertube.example.com --account <account-name> --relay-url ws://relay.example.com:3334
```

### Using docker directly

```bash
docker build -t peertube-to-amb .
docker run --rm peertube-to-amb generate-key
docker run --rm -e NOSTR_PRIVATE_KEY="nsec1..." peertube-to-amb bridge https://peertube.example.com --account <account-name> --relay-url ws://relay.example.com:3334
```

## Development

Run tests:

```bash
pytest
```

## License

[MIT](LICENSE)

## Funding
This project is being funded by the BMBSFJ.

Förderkennzeichen: 01PZ25003

<img src="https://github.com/edufeed-org/comcal/raw/main/static/BMBFSFJ.png" width=250 alt="BMBSFJ"/>