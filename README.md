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
Auto-updated every 6 hours · last run: 2026-10-26 20:02 UTC

```bash
PEERS="6d34d1f26e35f6b3cd9886789ff4fc6b9dbfcf77@64.130.41.69:26656,d9bfa29e0cf9c4ce0cc9c26d98e5d97228f93b0b@65.109.88.38:12056,19b3ef846732c465cc32da3eaddb9c0fb41f57d2@62.210.93.159:26656,f63f84d496b4f5e5408c7ce60bbfcf5d4ec3c4d4@109.228.35.84:26656,1a3697e07371c1a69da0beb8b89df9d1336c1a1e@148.251.236.116:26656,1f216d7c3530b1d7dd62e337f4282a61c2d48a98@64.31.28.74:26656,acca7837e4eb5f9dc7f5a94ed1d82edda6931ff8@162.55.101.168:26656,ce1ef517855260d07fd78c42eb30adabaa0da53c@137.74.92.112:26656,9a8b0ecc4f1287f458fa9459d51695bfc1a96785@208.69.78.26:12056,8599a7e1017098e010a8418d9457562d143f9a53@185.44.207.108:26656,a3ffe056b2f6e5b943f879c5ec51fd8a6a61a71c@178.249.213.227:27656,7f067f54987cccfe489fbe302ff1bf6c56aaf02f@79.127.178.236:23656"

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
