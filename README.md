# Celestia Mainnet Services

[![Chain](https://img.shields.io/badge/Chain-celestia%20mainnet-blue)](https://snapshots.apollo-validator.eu/celestia/)
[![Snapshots](https://img.shields.io/badge/Snapshots-active-brightgreen)](https://snapshots.apollo-validator.eu/celestia/)
[![RPC](https://img.shields.io/badge/Public%20RPC-active-brightgreen)](https://rpc.apollo-validator.eu/celestia/status)

Public infrastructure for the **Celestia mainnet** (chain-id `celestia`) by Apollo Validator.

## Services

| # | Service | Endpoint | Status |
|---|---------|----------|--------|
| 1 | [Snapshots](#snapshots) | [snapshots.apollo-validator.eu/celestia/](https://snapshots.apollo-validator.eu/celestia/) | 🟢 Active |
| 2 | [Peers List](#peers-list) | [snapshots.apollo-validator.eu/celestia/peers.html](https://snapshots.apollo-validator.eu/celestia/peers.html) | 🟢 Active |
| 3 | [Public RPC](#public-rpc) | [rpc.apollo-validator.eu/celestia/](https://rpc.apollo-validator.eu/celestia/status) | 🟢 Active |
| 4 | [State Sync](#state-sync) | [this section](#state-sync) | 🟢 Active |
| 5 | [Validator Guide](guide.md) | [guide.md](guide.md) | 🟢 Active |
| 6 | Validator Monitor Bot | — | 🟡 Planned |

## Public RPC

Tendermint RPC, proxied from our node:

```bash
# Node status
curl -s https://rpc.apollo-validator.eu/celestia/status | jq .result.sync_info

# Latest block
curl -s https://rpc.apollo-validator.eu/celestia/block | jq .result.block.header

# Validator set
curl -s https://rpc.apollo-validator.eu/celestia/validators | jq '.result.validators | length'
```

- Chain ID: `celestia`
- Endpoint base: `https://rpc.apollo-validator.eu/celestia/`
- Upstream: `127.0.0.1:36657` (local node, pruning: custom, keep-recent 100 — historical blocks are pruned)

## Snapshots

- **Page:** [snapshots.apollo-validator.eu/celestia/](https://snapshots.apollo-validator.eu/celestia/)
- **Every 6 hours**, only the latest archive is kept (`data/` of a pruned node, lz4)
- Typical size: **~4 GB** compressed (pruning `custom` keep-recent 100 / interval 19, `min-retain-blocks` 600000, indexer off)

```bash
# Latest metadata (height / size / sha256)
curl -s https://snapshots.apollo-validator.eu/api/celestia/snapshots/latest | jq

# Download (current file — see latest.json for the exact name)
wget https://snapshots.apollo-validator.eu/celestia/snapshots/celestia-mainnet-HEIGHT.tar.lz4
```

### Restore from Snapshot

Full 8-step procedure (incl. `celestia-appd tendermint unsafe-reset-all --keep-addr-book`
and `priv_validator_state.json` backup) is on the [snapshot page](https://snapshots.apollo-validator.eu/celestia/).

## State Sync

Join the network in minutes without downloading a tarball. Our node publishes
CometBFT state-sync snapshots every **1500 blocks** (keeps last 2).

```toml
# ~/.celestia-app/config/config.toml
[state_sync]
enable = true
rpc_servers = "https://rpc.apollo-validator.eu/celestia/,https://celestia-mainnet-rpc.itrocket.net"
trust_height = <TRUST_HEIGHT>
trust_hash = "<TRUST_HASH>"
```

```bash
HEIGHT=$(curl -s https://rpc.apollo-validator.eu/celestia/status | jq -r .result.sync_info.latest_block_height)
HASH=$(curl -s "https://rpc.apollo-validator.eu/celestia/block?height=$HEIGHT" | jq -r .result.block_id.hash)
echo "trust_height = $HEIGHT"
echo "trust_hash = \"$HASH\""
```

Then start `celestia-appd` — it downloads a recent state snapshot and syncs the tail.

## Peers List

- **Page:** [snapshots.apollo-validator.eu/celestia/peers.html](https://snapshots.apollo-validator.eu/celestia/peers.html)
- **Raw:** [peers.md](https://snapshots.apollo-validator.eu/peers.md)
- Verified every 6 hours (TCP probe)

### Quick Setup

<!-- PEERS:BEGIN -->
Auto-updated every 6 hours · last run: 2026-10-19 14:02 UTC

```bash
PEERS="1f216d7c3530b1d7dd62e337f4282a61c2d48a98@64.31.28.74:26656,129f31ae84d154b3064fa7928ec9a04cad0a40cc@95.216.246.249:26656,0c380953bd93a8a2d999c89d26152386429cfdb0@185.26.11.135:26656,6abaa1068992644ac40ce25a42aa9968014fa1c5@95.31.6.54:23533,d9d45cb5041c7622df1bd6c8bf2d229c20f34ce2@31.7.196.90:26656,da2e194590fa122b68a487d3d417fe6cd0b8e457@85.195.79.254:26656,5c2e00ee29251542d8dd961851bea6d69279ebab@88.198.50.175:63656,fc25a389790d9f1e8dc39496313e1e0fe2b138f7@135.181.138.95:2890,acca7837e4eb5f9dc7f5a94ed1d82edda6931ff8@162.55.101.168:26656,b5436af232fcb06fb1dd788388524e2434a90272@195.154.103.146:26656,4c488ed2e06731599122cfc7d7c0a8068c5cc550@116.202.237.217:26656,1a3697e07371c1a69da0beb8b89df9d1336c1a1e@148.251.236.116:26656,519547dea7f3b476c137b2cbe94a1b6a998f5d12@95.217.38.34:26656,bf40271a7abdc7fcf5e2f6929c54dcb6e88c7541@57.129.87.205:26656,46bfd5c13a7e30916ce4b7acad0f6e011099a00c@40.160.22.87:26656,44613a0b112bda77405e2791782dcc595ea49683@43.167.158.221:26656,f63f84d496b4f5e5408c7ce60bbfcf5d4ec3c4d4@109.228.35.84:26656,d644d846ab6db18474a5edc25bef56d86eb610d5@84.32.186.153:26656,0e0787c2aafb0e03f0e5b99e866eaf11adfe0c0d@64.130.47.114:26656"

sed -i "s/^persistent_peers = .*/persistent_peers = \"$PEERS\"/" ~/.celestia-app/config/config.toml

sudo systemctl restart celestia-appd
```
<!-- PEERS:END -->

## Official Seeds

```
acca7837e4eb5f9dc7f5a94ed1d82edda6931ff8@seed.celestia.pops.one:26656
12ad7c73c7e1f2460941326937a039139aa78884@celestia-mainnet-seed.itrocket.net:40656
```

Source: [celestiaorg/networks/celestia/seeds.txt](https://github.com/celestiaorg/networks/blob/main/celestia/seeds.txt)

## Installation Guide

Short version in [guide.md](guide.md) (requirements, binary version pin, genesis + sha256,
config, start, validator registration).

## Chain Information

| | |
|---|---|
| Chain ID | `celestia` |
| Binary | `celestia-appd` **v9.0.8** (chain app version `9`; latest release [v10.4.0](https://github.com/celestiaorg/celestia-app/releases) awaits a chain upgrade — take the version the chain runs, from official release notes/gov proposals) |
| Genesis | [celestiaorg/networks/celestia/genesis.json](https://raw.githubusercontent.com/celestiaorg/networks/main/celestia/genesis.json) |
| Genesis SHA256 | `9727aac9bbfb021ce7fc695a92f901986421283a891b89e0af97bc9fad187793` (87,995,175 bytes) |
| Ports | P2P `36656`, RPC `36657` (proxied publicly), gRPC `36090` |
| Node home / service | `~/.celestia-app` (`/root/.celestia-app` on our node), `celestia-appd.service` |
| Pruning | `custom`, keep-recent `100`, interval `19`; `min-retain-blocks = 600000`; indexer `null` |
| Our validator | `celestiavaloper1mcjmn4s8ee5ce0wsuat98kqxggfrhk04te0d38` (Apollo Validator) |

## Validator Monitor Bot

Telegram watchlist bot for Celestia — **planned**, not yet active.

## Links

- Website: [apollo-validator.eu/networks/celestia/](https://apollo-validator.eu/networks/celestia/)
- Snapshots: [snapshots.apollo-validator.eu/celestia/](https://snapshots.apollo-validator.eu/celestia/)
- RPC: [rpc.apollo-validator.eu/celestia/](https://rpc.apollo-validator.eu/celestia/status)
- Docs: [celestia.org/docs](https://docs.celestia.org/)
- Repo: [celestiaorg/celestia-app](https://github.com/celestiaorg/celestia-app)

---
Provided by [Apollo Validator](https://apollo-validator.eu)
