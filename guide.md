# Celestia Mainnet Validator Guide

Structured digest of the official Celestia docs for running a **celestia mainnet**
validator on our infrastructure. Source of truth: [docs.celestia.org](https://docs.celestia.org/)
and [celestiaorg/celestia-app releases](https://github.com/celestiaorg/celestia-app/releases).

## Hardware Requirements

- 32+ cores with GFNI/SHA-NI instructions
- 32–64 GB RAM
- 12 TiB NVMe (mainnet archive class; a pruned consensus node needs far less)
- Ubuntu 24.04 LTS

## Installation

```bash
# Toolchain (per official docs; verify the current required Go version)
# git clone https://github.com/celestiaorg/celestia-app.git
# cd celestia-app && git checkout <PINNED_TAG> && make install
```

**Version pin (2026-10-17):** the chain runs app version `9` — our node runs
**`celestia-appd` v9.0.8** (`~/.celestia-app/bin/v9.0.8/` layout).
The latest upstream release is [v10.4.0](https://github.com/celestiaorg/celestia-app/releases/tag/v10.4.0) (2026-10-07),
which the chain has **not** upgraded to yet.

> Never run a binary newer than the chain requires — install the version named
> in the active on-chain upgrade proposal / official release notes, then switch
> only at the upgrade height.

```bash
celestia-appd version   # expect: the chain-required version
```

## Genesis

```bash
wget -O ~/.celestia-app/config/genesis.json \
  https://raw.githubusercontent.com/celestiaorg/networks/main/celestia/genesis.json
sha256sum ~/.celestia-app/config/genesis.json
```

Expected SHA256:

```
9727aac9bbfb021ce7fc695a92f901986421283a891b89e0af97bc9fad187793
```

(`chain_id = celestia`, `genesis_time = 2023-10-31T14:00:00Z`, 87,995,175 bytes)

## Configuration

- `--chain-id celestia`
- P2P `36656`, RPC `36657` (bind RPC to localhost; publish via nginx proxy), gRPC `36090`
- `~/.celestia-app/config/config.toml` — `[p2p] persistent_peers` (see [peers list](https://snapshots.apollo-validator.eu/celestia/peers.html)),
  seeds from [celestiaorg/networks/celestia/seeds.txt](https://github.com/celestiaorg/networks/blob/main/celestia/seeds.txt)
- `~/.celestia-app/config/app.toml` (note: **inside `config/`**):
  - `pruning = "custom"`, `pruning-keep-recent = "100"`, `pruning-interval = "19"`
  - `min-retain-blocks = 600000` (CometBFT block pruning)
  - `snapshot-interval = 1500`, `snapshot-keep-recent = 2` (state-sync snapshots we publish)
  - indexer = `null`

## Running

```bash
celestia-appd start --home ~/.celestia-app
# our unit: /etc/systemd/system/celestia-appd.service
#   ExecStart=…/celestia-appd start --home /root/.celestia-app
sudo systemctl enable --now celestia-appd
```

## Sync

Pick one:

1. **State sync (fastest, minutes)** — config block + commands in the
   [README §State Sync](README.md#state-sync).
2. **From snapshot** — 8-step restore on the
   [snapshot page](https://snapshots.apollo-validator.eu/celestia/) (download
   `data/` archive, `celestia-appd tendermint unsafe-reset-all --keep-addr-book`,
   extract, keep `priv_validator_state.json` for validators).
3. **P2P sync from peers** — slowest, needs the full historical block range
   (our node serves pruned history only).

Verify: `curl -s localhost:36657/status | jq .result.sync_info` → `catching_up: false`.

## Validator Registration

```bash
celestia-appd tx staking create-validator \
  --chain-id=celestia --amount=1000000utia ...
```

(See the official docs for the full set of flags: pubkey, amount, commission-rate
— min commission is governed (CIP-41, 10%).)

## Upgrading

Celestia upgrades via on-chain governance proposals: watch
[celestiaorg/celestia-app releases](https://github.com/celestiaorg/celestia-app/releases)
and the proposal `title`/`description` for the halt height + target version,
install the new binary **before** the halt, and restart after it (same shape as
the coordinated-halt pattern documented in our gnoland guide).

## Service Paths (our node)

| | |
|---|---|
| Home | `/root/.celestia-app` |
| Service | `celestia-appd.service` (User=root) |
| Binary runner | `/root/.celestia-app/bin/<version>/celestia-appd` |
| State-sync snapshots | interval 1500 / keep 2 |
| Snapshot archive | `/var/www/snapshots/celestia/snapshots/` (cron `0 */6`) |
| Peers generator | `/home/celestia/peers-gen-celestia.py` (cron `2 2,8,14,20`) |

## Links

- Snapshots: https://snapshots.apollo-validator.eu/celestia/
- Peers: https://snapshots.apollo-validator.eu/celestia/peers.html
- Public RPC: https://rpc.apollo-validator.eu/celestia/status
- Website: https://apollo-validator.eu/networks/celestia/
- Official docs: https://docs.celestia.org/
- Networks repo (genesis/seeds): https://github.com/celestiaorg/networks
