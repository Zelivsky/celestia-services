# Celestia Node Setup Guide

Complete guide for setting up or updating a **Celestia mainnet** consensus node or validator.

> **Chain:** `celestia` · **Binary:** `celestia-appd` **v10.5.0** · **OS:** Ubuntu 24.04 LTS (glibc ≥ 2.38) · **Default ports:** P2P `26656`, RPC `26657`, gRPC `9090`

Source of truth: [docs.celestia.org](https://docs.celestia.org/operate/networks/overview) and [celestiaorg/celestia-app releases](https://github.com/celestiaorg/celestia-app/releases). Never run a binary newer than the version the chain currently requires.

## Quick Start (Variables)

Set these before running any command:

```bash
# Required
export MONIKER="your-node-name"
export WALLET="my-wallet"

# Optional (defaults)
export CELESTIA_CHAIN_ID="celestia"
export CELESTIA_HOME="$HOME/.celestia-app"
export CELESTIA_PORT="26"   # Node uses 26656, 26657, 26317, 26090, 26660, …
```

Our public services run on port prefix `36` (`36656`, `36657`, `36090`). For a fresh node the default `26` prefix is fine — pick a free prefix only if you host several chains on one machine.

---

## Prerequisites

| | |
|---|---|
| OS | **Ubuntu 24.04 LTS** (v9+ binaries need glibc ≥ 2.38; 22.04 will not start) |
| Validator / consensus node | 32 cores · 32 GB RAM · 2 TB NVMe · 1 Gbps |
| Archival consensus node | 32 cores · 64 GB RAM · 16 TB NVMe · 1 Gbps |
| CPU (validators) | Must pass the [CPU benchmark](https://github.com/celestiaorg/celestia-app/blob/main/tools/cpu_requirements/README.md) — needs **GFNI + SHA-NI** instructions |
| Access | root or sudo |

Check glibc before anything else:

```bash
ldd --version   # must be >= 2.38
```

Official hardware reference: [docs.celestia.org hardware requirements](https://docs.celestia.org/operate/getting-started/hardware-requirements/).

**Open ports** (adjust if you use a custom prefix):

| Port | Purpose |
|------|---------|
| 26656 | P2P |
| 9090 | gRPC |
| 26657 | RPC (keep on localhost; publish via reverse proxy if needed) |

---

## 1. Install Dependencies

```bash
sudo apt update && sudo apt upgrade -y
sudo apt install -y curl git wget htop tmux build-essential jq make lz4 gcc unzip \
  clang pkg-config libssl-dev aria2 ncdu
```

---

## 2. Install Go

```bash
cd $HOME
VER="1.26.8"
wget "https://go.dev/dl/go$VER.linux-amd64.tar.gz"
sudo rm -rf /usr/local/go
sudo tar -C /usr/local -xzf "go$VER.linux-amd64.tar.gz"
rm "go$VER.linux-amd64.tar.gz"

# PATH
[ ! -f ~/.bash_profile ] && touch ~/.bash_profile
echo "export PATH=$PATH:/usr/local/go/bin:$HOME/go/bin" >> ~/.bash_profile
source $HOME/.bash_profile
[ ! -d ~/go/bin ] && mkdir -p ~/go/bin

go version   # expect: go1.26.8
```

When building a different celestia-app release, check the `go` / `toolchain` directives in that release's `go.mod` first.

---

## 3. Install celestia-app

**Version pin (2026-10-28):** the compatible mainnet binary is **`v10.5.0`**
([networks overview](https://docs.celestia.org/operate/networks/overview)).
Always re-check the pin before installing — the chain upgrades via on-chain
governance and a newer GitHub release does **not** mean the chain runs it yet.

### Option A — build from source (recommended)

```bash
cd $HOME
rm -rf celestia-app
git clone https://github.com/celestiaorg/celestia-app.git
cd celestia-app
git checkout tags/v10.5.0

# Enable BBR TCP congestion control (Linux only, needs sudo)
make enable-bbr
make check-bbr   # should print: BBR is enabled.

make install
# installs the multiplexer binary to ~/go/bin/celestia-appd
```

### Option B — pre-built binary

```bash
# latest compatible version from the docs
bash -c "$(curl -sL https://docs.celestia.org/celestia-app.sh)" -- -v v10.5.0
```

### Verify

```bash
celestia-appd version
# expect: 10.5.0
```

> **Multiplexer note:** v9+ binaries are multiplexers that can serve several
> historical app versions. They may download older binaries into
> `~/.celestia-app/bin/<version>/` on first start. Do not delete that directory
> while the node needs it; if you hit
> `App cannot be started without CometBFT when using the multiplexer`,
> remove `~/.celestia-app/bin` and re-download via the make targets from the
> [official FAQ](https://docs.celestia.org/operate/consensus-validators/validator-node#app-cannot-be-started-without-cometbft-when-using-the-multiplexer).

---

## 4. Initialize Node

```bash
source ~/.bash_profile   # picks up MONIKER, CELESTIA_CHAIN_ID, CELESTIA_HOME, CELESTIA_PORT

# Point the client at your local RPC (use your port prefix)
celestia-appd config node "tcp://localhost:${CELESTIA_PORT}657"
celestia-appd config chain-id "$CELESTIA_CHAIN_ID"
celestia-appd config keyring-backend file   # NEVER "test" on mainnet

# Initialize home directory
celestia-appd init "$MONIKER" --chain-id "$CELESTIA_CHAIN_ID" --home "$CELESTIA_HOME"
```

Set PebbleDB (default for new nodes since v9 — faster and smaller than goleveldb):

```bash
sed -i -e 's/^db_backend *=.*/db_backend = "pebbledb"/' "$CELESTIA_HOME/config/config.toml"
sed -i -e 's/^app-db-backend *=.*/app-db-backend = "pebbledb"/' "$CELESTIA_HOME/config/app.toml"
```

> If you are upgrading an **existing** goleveldb node to pebbledb, stop the node
> and use the official
> [migrate-db tool](https://github.com/celestiaorg/celestia-app/tree/main/tools/migrate-db)
> — do not just flip `db_backend` on a live database.

---

## 5. Download Genesis & Addrbook

```bash
# Official way (downloads the network's genesis)
celestia-appd download-genesis celestia --home "$CELESTIA_HOME"

# Or directly from the networks repo
wget -O "$CELESTIA_HOME/config/genesis.json" \
  https://raw.githubusercontent.com/celestiaorg/networks/main/celestia/genesis.json

# Optional addrbook — helps find peers faster on a cold start
wget -O "$CELESTIA_HOME/config/addrbook.json" \
  https://server-1.itrocket.net/mainnet/celestia/addrbook.json
```

Verify genesis integrity:

```bash
sha256sum "$CELESTIA_HOME/config/genesis.json"
```

Expected SHA256:

```
9727aac9bbfb021ce7fc695a92f901986421283a891b89e0af97bc9fad187793
```

(`chain_id = celestia`, `genesis_time = 2023-10-31T14:00:00Z`, 87,995,175 bytes)

---

## 6. Configure Seeds and Peers

```bash
# Official seeds
SEEDS=$(curl -sL https://raw.githubusercontent.com/celestiaorg/networks/master/celestia/seeds.txt | tr '\n' ',' | sed 's/,$//')
echo "$SEEDS"

# Verified peer list from our service (regenerated every 6 hours)
PEERS=$(curl -s https://snapshots.apollo-validator.eu/celestia/peers.md \
  | grep -oE '[a-f0-9]{40}@[0-9.]+:[0-9]+' | tr '\n' ',' | sed 's/,$//')
echo "$PEERS"

sed -i.bak \
  -e "s/^seeds *=.*/seeds = \"$SEEDS\"/" \
  -e "s/^persistent_peers *=.*/persistent_peers = \"$PEERS\"/" \
  "$CELESTIA_HOME/config/config.toml"
```

Manual alternative: copy the PEERS block from
[snapshots.apollo-validator.eu/celestia/peers.html](https://snapshots.apollo-validator.eu/celestia/peers.html).

Also set `external_address` so peers can dial you back:

```bash
sed -i.bak -e "s%^external_address = \"\"%external_address = \"$(wget -qO- eth0.me):${CELESTIA_PORT}656\"%" \
  "$CELESTIA_HOME/config/config.toml"
```

---

## 7. Configure Custom Ports

```bash
# app.toml
sed -i.bak \
  -e "s%:1317%:${CELESTIA_PORT}317%g;
s%:8080%:${CELESTIA_PORT}080%g;
s%:9090%:${CELESTIA_PORT}090%g;
s%:9091%:${CELESTIA_PORT}091%g;
s%:8545%:${CELESTIA_PORT}545%g;
s%:8546%:${CELESTIA_PORT}546%g;
s%:6065%:${CELESTIA_PORT}065%g" "$CELESTIA_HOME/config/app.toml"

# config.toml
sed -i.bak \
  -e "s%:26658%:${CELESTIA_PORT}658%g;
s%:26657%:${CELESTIA_PORT}657%g;
s%:6060%:${CELESTIA_PORT}060%g;
s%:26656%:${CELESTIA_PORT}656%g;
s%:26660%:${CELESTIA_PORT}660%g" "$CELESTIA_HOME/config/config.toml"
```

For celestia-app ≥ v4 the CometBFT gRPC listener is **required** — add it under
`[rpc]` in `config.toml` (or pass `--rpc.grpc_laddr`):

```bash
# append if missing — pick a free port in your prefix range
grep -q '^grpc_laddr' "$CELESTIA_HOME/config/config.toml" \
  || echo "grpc_laddr = \"tcp://127.0.0.1:${CELESTIA_PORT}098\"" >> "$CELESTIA_HOME/config/config.toml"
```

Better: edit the existing `grpc_laddr` line inside `[rpc]`:

```toml
[rpc]
grpc_laddr = "tcp://127.0.0.1:26098"
```

If you run a **validator with Fibre**, set the priv-validator signing listener to
a loopback IP (the hostname `localhost` is no longer accepted):

```toml
priv_validator_grpc_laddr = "127.0.0.1:26659"
```

See the [Fibre signing guide](https://docs.celestia.org/operate/consensus-validators/fibre).

---

## 8. Configure Pruning & Storage

```bash
# Application-state pruning (recommended for validators)
sed -i \
  -e "s/^pruning *=.*/pruning = \"custom\"/" \
  -e "s/^pruning-keep-recent *=.*/pruning-keep-recent = \"100\"/" \
  -e "s/^pruning-interval *=.*/pruning-interval = \"19\"/" \
  "$CELESTIA_HOME/config/app.toml"

# Block retention: keep a large recent window without retaining all blocks
sed -i -e "s/^min-retain-blocks *=.*/min-retain-blocks = 600000/" \
  "$CELESTIA_HOME/config/app.toml"
```

**Pruning options** (`app.toml`):

| Option | Keep recent | Interval | Disk usage (rough) |
|--------|-------------|----------|--------------------|
| `default` | 100 | 0 | ~200 GB+ |
| `nothing` (archive) | 0 | 0 | ~10 TB+ |
| `everything` | 86400 | 10 | smallest app state |
| `custom` | 100 | 19 | ~50 GB app state (block store still grows with `min-retain-blocks`) |

Optional — publish CometBFT state-sync snapshots for your own / public use
(our node uses these values):

```bash
sed -i \
  -e "s/^snapshot-interval *=.*/snapshot-interval = 1500/" \
  -e "s/^snapshot-keep-recent *=.*/snapshot-keep-recent = 2/" \
  "$CELESTIA_HOME/config/app.toml"
```

Storage hardening (saves disk; `discard_abci_responses = true` means
`/block_results` queries will fail — set `false` on a public RPC node):

```bash
sed -i \
  -e "s/^discard_abci_responses *=.*/discard_abci_responses = true/" \
  -e "s/^compact *=.*/compact = true/" \
  "$CELESTIA_HOME/config/config.toml"
```

---

## 9. Configure Gas, Prometheus, Indexing

```bash
# Minimum gas prices
sed -i 's|minimum-gas-prices =.*|minimum-gas-prices = "0.002utia"|g' \
  "$CELESTIA_HOME/config/app.toml"

# Prometheus metrics
sed -i -e "s/prometheus = false/prometheus = true/" \
  "$CELESTIA_HOME/config/config.toml"

# Transaction indexer — "null" saves the most disk
sed -i -e 's/^indexer *=.*/indexer = "null"/' \
  "$CELESTIA_HOME/config/config.toml"
```

`indexer = "kv"` is needed only if you want `tx_search` / query by hash.

---

## 10. Create Systemd Service

```bash
sudo tee /etc/systemd/system/celestia-appd.service > /dev/null <<EOF
[Unit]
Description=Celestia node
After=network-online.target

[Service]
User=$USER
WorkingDirectory=$CELESTIA_HOME
ExecStart=$(which celestia-appd) start --home $CELESTIA_HOME
Restart=on-failure
RestartSec=5
LimitNOFILE=65535

[Install]
WantedBy=multi-user.target
EOF

sudo systemctl daemon-reload
sudo systemctl enable celestia-appd
```

On our node the unit runs as root:

```
ExecStart=/root/go/bin/celestia-appd start --home /root/.celestia-app
```

---

## 11. Sync the Node

Pick **one** of the three options. For a brand-new node, snapshot restore or
state sync is strongly preferred over block sync (~3 weeks).

| Method | Time | Notes |
|--------|------|-------|
| **Snapshot** (quick sync) | ~1–5 h | Full `data/` from a pruned node; no deep history |
| **State sync** | ~1 h | Light-client-verified state; truncated history |
| **Block sync** | ~3 weeks | From genesis; slowest, most trustless |

### Option A — snapshot (ours)

```bash
# Latest metadata
curl -s https://snapshots.apollo-validator.eu/api/celestia/snapshots/latest | jq
# { height, size, created, file, checksum, network }
```

Then follow the **8-step restore** on the
[snapshot page](https://snapshots.apollo-validator.eu/celestia/):

1. `sudo apt install lz4 -y`
2. `sudo systemctl stop celestia-appd`
3. Back up validator state:
   `cp ~/.celestia-app/data/priv_validator_state.json ~/.celestia-app/priv_validator_state.json.bak`
4. Download the archive + `.sha256` from the page (path:
   `https://snapshots.apollo-validator.eu/celestia/snapshots/<file>`)
5. `sha256sum -c <file>.sha256`
6. Reset and extract:
   ```bash
   celestia-appd tendermint unsafe-reset-all --home ~/.celestia-app --keep-addr-book
   lz4 -c -d <file> | tar -x -C ~/.celestia-app
   ```
7. Restore validator state:
   `cp ~/.celestia-app/priv_validator_state.json.bak ~/.celestia-app/data/priv_validator_state.json`
8. `sudo systemctl start celestia-appd` and check `catching_up`

> **Validators:** never skip the `priv_validator_state.json` backup. Restoring a
> stale signing state on a live validator can cause double-signing and slashing.
> Prefer `celestia-appd tendermint reset-state` when you only need to clear
> blockstore/state without touching signing state.

Snapshot size is currently **~48 GB** compressed (pruned node with
`min-retain-blocks = 600000`) — plan disk and download time accordingly.
Only the latest archive is kept.

### Option B — state sync

```toml
# ~/.celestia-app/config/config.toml
[statesync]
enable = true
rpc_servers = "https://rpc.apollo-validator.eu/celestia/,https://celestia-mainnet-rpc.itrocket.net"
trust_height = <TRUST_HEIGHT>
trust_hash = "<TRUST_HASH>"
```

Fill trust values from a trusted RPC:

```bash
HEIGHT=$(curl -s https://rpc.apollo-validator.eu/celestia/status | jq -r .result.sync_info.latest_block_height)
HASH=$(curl -s "https://rpc.apollo-validator.eu/celestia/block?height=$HEIGHT" | jq -r .result.block_id.hash)
echo "trust_height = $HEIGHT"
echo "trust_hash = \"$HASH\""
```

At least two RPC servers are recommended. On start the logs should show
`Discovering snapshots`. State sync does **not** work if the node already has
local state (`LastBlockHeight > 0`).

### Option C — block sync

Default behaviour when `[statesync] enable = false` and there is no local state.
Slowest path — only for nodes that need full verifiable history from genesis.

```bash
# Optional: skip re-executing historical proposal data during block sync (v9+)
# [blocksync]
# verify_data = false   # default; set true to restore pre-v9 behaviour
```

### Verify sync

```bash
curl -s "http://localhost:${CELESTIA_PORT}657/status" | jq .result.sync_info
# catching_up: false  →  synced
```

---

## 12. Start the Node

```bash
sudo systemctl restart celestia-appd
sudo journalctl -u celestia-appd -fo cat
```

If the node is already configured, a plain start is enough:

```bash
sudo systemctl start celestia-appd
```

---

## Sync Status Checker

Save as `sync-checker.sh` and run `bash sync-checker.sh`:

```bash
#!/bin/bash
rpc_port=$(grep -m 1 -oP '^laddr = "\K[^"]+' "$CELESTIA_HOME/config/config.toml" | cut -d ':' -f 3)
while true; do
  local_height=$(curl -s localhost:$rpc_port/status | jq -r '.result.sync_info.latest_block_height')
  network_height=$(curl -s https://rpc.apollo-validator.eu/celestia/status | jq -r '.result.sync_info.latest_block_height')

  if ! [[ "$local_height" =~ ^[0-9]+$ ]] || ! [[ "$network_height" =~ ^[0-9]+$ ]]; then
    echo -e "\033[1;31mError: Invalid block height data. Retrying...\033[0m"
    sleep 5
    continue
  fi

  blocks_left=$((network_height - local_height))
  echo -e "\033[1;33mNode Height:\033[1;34m $local_height\033[0m \033[1;33m| Network Height:\033[1;36m $network_height\033[0m \033[1;33m| Blocks Left:\033[1;31m $blocks_left\033[0m"
  sleep 5
done
```

---

## Wallet

```bash
# Create a new wallet — SAVE THE MNEMONIC
celestia-appd keys add $WALLET --keyring-backend file

# Restore an existing wallet
celestia-appd keys add $WALLET --recover --keyring-backend file

# Addresses
WALLET_ADDRESS=$(celestia-appd keys show $WALLET -a --keyring-backend file)
VALOPER_ADDRESS=$(celestia-appd keys show $WALLET --bech val -a --keyring-backend file)
echo "export WALLET_ADDRESS=$WALLET_ADDRESS" >> ~/.bash_profile
echo "export VALOPER_ADDRESS=$VALOPER_ADDRESS" >> ~/.bash_profile
source ~/.bash_profile

# Balance (node must be running)
celestia-appd query bank balances $WALLET_ADDRESS

# Sync check before staking
celestia-appd status 2>&1 | jq
```

> **Never use `--keyring-backend test` on mainnet.** The `test` backend stores
> keys unencrypted on disk. Use `file` (encrypted on disk) or `os` (system keyring).

Fund the wallet with TIA, wait until the node reports `catching_up: false`, then
create the validator.

---

## Create Validator

Minimum commission on Celestia mainnet is **10%** (CIP-41). Maximums are governed —
check current on-chain parameters before choosing rates.

```bash
celestia-appd tx staking create-validator \
  --amount 1000000utia \
  --pubkey "$(celestia-appd tendermint show-validator)" \
  --moniker "$MONIKER" \
  --identity "" \
  --website "" \
  --security-contact "" \
  --details "Apollo Validator" \
  --chain-id $CELESTIA_CHAIN_ID \
  --commission-rate 0.10 \
  --commission-max-rate 0.20 \
  --commission-max-change-rate 0.01 \
  --min-self-delegation 1000000 \
  --from $WALLET \
  --keyring-backend file \
  --gas 220000 \
  --fees 21000utia \
  --yes
```

Edit an existing validator:

```bash
celestia-appd tx staking edit-validator \
  --new-moniker "$MONIKER" \
  --commission-rate 0.10 \
  --from $WALLET \
  --keyring-backend file \
  --chain-id $CELESTIA_CHAIN_ID \
  --gas auto --gas-adjustment 1.5 --fees 21000utia -y
```

Downtime: validators miss a jail if they skip more than **2,500 of the last
10,000** signed blocks. Unjail with:

```bash
celestia-appd tx slashing unjail --from $WALLET --keyring-backend file \
  --chain-id $CELESTIA_CHAIN_ID --gas auto --gas-adjustment 1.5 --fees 21000utia -y
```

Optional bridge node (supports the DA network; not required for consensus-only):

```bash
celestia-appd bridge init --core.ip 127.0.0.1 --core.port ${CELESTIA_PORT}090
celestia-appd bridge start
```

Ensure `[grpc] enable = true` in `app.toml` before connecting a bridge.

---

## Cheat Sheet

### Service Management

```bash
sudo systemctl status celestia-appd
sudo systemctl start celestia-appd
sudo systemctl stop celestia-appd
sudo systemctl restart celestia-appd
sudo systemctl enable celestia-appd
sudo systemctl disable celestia-appd
sudo systemctl daemon-reload

sudo journalctl -u celestia-appd -fo cat     # follow logs
sudo journalctl -u celestia-appd -n 100 --no-pager
```

### Node Info

```bash
celestia-appd status 2>&1 | jq
celestia-appd status 2>&1 | jq .NodeInfo
celestia-appd status 2>&1 | jq .SyncInfo
celestia-appd status 2>&1 | jq .ValidatorInfo

# Your peer ID (useful for the networks repo / peers list)
echo "$(celestia-appd tendermint show-node-id)@$(wget -qO- eth0.me):${CELESTIA_PORT}656"
```

### Key Management

```bash
celestia-appd keys add $WALLET --keyring-backend file
celestia-appd keys add $WALLET --recover --keyring-backend file
celestia-appd keys list --keyring-backend file
celestia-appd keys delete $WALLET --keyring-backend file
celestia-appd keys show $WALLET --keyring-backend file
celestia-appd keys export $WALLET --keyring-backend file
celestia-appd keys import $WALLET wallet.backup --keyring-backend file
```

### Validator Operations

```bash
VALOPER_ADDRESS=$(celestia-appd keys show $WALLET --bech val -a --keyring-backend file)

celestia-appd q staking validator $VALOPER_ADDRESS
celestia-appd q slashing signing-info "$(celestia-appd tendermint show-validator)"

# Active validator set
celestia-appd q staking validators -oj --limit=3000 \
  | jq '.validators[] | select(.status=="BOND_STATUS_BONDED")' \
  | jq -r '(.tokens|tonumber/pow(10;6)|floor|tostring) + " \t " + .description.moniker' \
  | sort -gr | nl
```

### Staking Operations

```bash
# Delegate
celestia-appd tx staking delegate $VALOPER_ADDRESS 1000000utia \
  --from $WALLET --keyring-backend file --chain-id $CELESTIA_CHAIN_ID \
  --gas auto --gas-adjustment 1.5 --fees 21000utia -y

# Redelegate
celestia-appd tx staking redelegate $VALOPER_ADDRESS <NEW_VALOPER> 1000000utia \
  --from $WALLET --keyring-backend file --chain-id $CELESTIA_CHAIN_ID \
  --gas auto --gas-adjustment 1.5 --fees 21000utia -y

# Unbond
celestia-appd tx staking unbond $VALOPER_ADDRESS 1000000utia \
  --from $WALLET --keyring-backend file --chain-id $CELESTIA_CHAIN_ID \
  --gas auto --gas-adjustment 1.5 --fees 21000utia -y
```

### Withdraw Rewards

```bash
celestia-appd tx distribution withdraw-all-rewards \
  --from $WALLET --keyring-backend file --chain-id $CELESTIA_CHAIN_ID \
  --gas auto --gas-adjustment 1.5 --fees 21000utia -y

celestia-appd tx distribution withdraw-rewards $VALOPER_ADDRESS --commission \
  --from $WALLET --keyring-backend file --chain-id $CELESTIA_CHAIN_ID \
  --gas auto --gas-adjustment 1.5 --fees 21000utia -y
```

### Governance

```bash
celestia-appd query gov proposals
celestia-appd query gov proposal <PROPOSAL_ID>
celestia-appd tx gov vote <PROPOSAL_ID> yes \
  --from $WALLET --keyring-backend file --chain-id $CELESTIA_CHAIN_ID \
  --gas auto --gas-adjustment 1.5 --fees 21000utia -y
```

Watch active proposals carefully — **network upgrade proposals carry the halt
height and target binary version**.

### Token Transfer

```bash
celestia-appd tx bank send $WALLET <TO_ADDRESS> 1000000utia \
  --keyring-backend file --chain-id $CELESTIA_CHAIN_ID \
  --gas auto --gas-adjustment 1.5 --fees 21000utia -y
```

### Storage Resets (validators)

```bash
# Preferred for validators: clear blockstore/state, keep signing state + addrbook
celestia-appd tendermint reset-state --home $CELESTIA_HOME

# DANGEROUS for live validators: resets priv_validator_state.json
# (use only when the node is NOT in the active set)
celestia-appd tendermint unsafe-reset-all --home $CELESTIA_HOME --keep-addr-book
```

---

## Upgrade Guide (update an existing node)

Celestia upgrades through **on-chain governance**. Plan for a ~24 h response window.

### 1. Stay informed

- [celestiaorg/celestia-app releases](https://github.com/celestiaorg/celestia-app/releases)
- [Networks overview — compatible versions](https://docs.celestia.org/operate/networks/overview)
- Telegram announcements: `t.me/+smSFIA7XXLU4MjJh`
- Discord `#mainnet-beta-announcements`
- Active gov proposals (`celestia-appd query gov proposals`)

### 2. Confirm the pin

The upgrade proposal / release notes name the **target version**. The docs
networks table is updated when the chain is on that version. As of this writing:
**mainnet = `v10.5.0`**.

```bash
celestia-appd version   # what you run
```

### 3. Build the new binary (before the halt height)

```bash
sudo systemctl stop celestia-appd

cd $HOME/celestia-app
git fetch --tags
git checkout tags/vX.Y.Z        # the version from the proposal — not "latest"
make install

celestia-appd version           # must print vX.Y.Z
```

### 4. Restart after the upgrade height

```bash
sudo systemctl start celestia-appd
sudo journalctl -u celestia-appd -fo cat
```

Watch for a successful `upgraded from app version N to N+1` line and that
`catching_up` returns to `false`.

### 5. After every network upgrade (our ops note)

Once the chain resumes producing blocks, manually regenerate public
snapshots/peers **~50 blocks after resume** (≈3 min) so published metadata does
not describe the pre-upgrade chain for up to 6 hours.

### Rules

- **Never** start a binary newer than the chain requires — you will hit an
  AppHash mismatch and need a resync from snapshot.
- Do **not** change pruning / `min-retain-blocks` during an upgrade window.
- After a major upgrade, if the node cannot sync, compare your binary with the
  networks table and only then consider `reset-state` + snapshot restore.

---

## Security

### SSH key authentication

```bash
# On your LOCAL machine
ssh-keygen -t ed25519

# Copy to server
ssh-copy-id $USER@YOUR_SERVER_IP

# On the server — disable password auth
sudo sed -i 's/PasswordAuthentication yes/PasswordAuthentication no/' /etc/ssh/sshd_config
sudo systemctl restart sshd
```

### Firewall

```bash
sudo ufw default allow outgoing
sudo ufw default deny incoming
sudo ufw allow ssh/tcp
sudo ufw allow ${CELESTIA_PORT}656/tcp   # P2P
# Only expose gRPC/RPC if a bridge or public endpoint needs them
# sudo ufw allow ${CELESTIA_PORT}090/tcp  # gRPC
sudo ufw enable
```

### Key safety

- Never share `priv_validator_key.json`, mnemonics, or keyring passwords.
- Back up `priv_validator_key.json` offline; restore path is documented in
  [Migrating a validator](https://docs.celestia.org/operate/consensus-validators/validator-node#migrating-a-validator-to-another-machine).
- Prefer local signing (Fibre); remote/Horcrux-style signing setups are
  deprecated for validators.

---

## Delete Node

```bash
sudo systemctl stop celestia-appd
sudo systemctl disable celestia-appd
sudo rm -rf /etc/systemd/system/celestia-appd.service
sudo systemctl daemon-reload

rm -f $(which celestia-appd)
rm -rf $CELESTIA_HOME
rm -rf $HOME/celestia-app

sed -i "/CELESTIA_/d" $HOME/.bash_profile
sed -i "/WALLET=/d" $HOME/.bash_profile
sed -i "/MONIKER=/d" $HOME/.bash_profile
```

> Delete `priv_validator_key.json` only after you are sure you will never run
> this validator identity again. Keep offline backups until then.

---

## Troubleshooting

### Node won't start

```bash
sudo journalctl -u celestia-appd -n 100 --no-pager
```

Common causes:

1. **glibc too old** → Ubuntu 24.04 required (`ldd --version`)
2. **Port already in use** → change `CELESTIA_PORT` or free the port
3. **Genesis mismatch** → re-download and re-verify sha256
4. **Wrong binary version** → install the version from the networks table
5. **Database locked** → another `celestia-appd` process is running
6. **`App cannot be started without CometBFT when using the multiplexer`** →
   remove `~/.celestia-app/bin` and re-download historical binaries
7. **Fibre signer error about `localhost`** → use `127.0.0.1` in
   `priv_validator_grpc_laddr`

### `+2/3 committed an invalid block: wrong Block.Header.Version`

The chain upgraded and your binary is behind. Install the target version from
the upgrade proposal / networks table and restart. See the
[official FAQ](https://docs.celestia.org/operate/consensus-validators/validator-node#23-committed-an-invalid-block-wrong-blockheaderversion).

### Sync is slow or stuck

```bash
# Use a snapshot instead of block sync
curl -s https://snapshots.apollo-validator.eu/api/celestia/snapshots/latest | jq

# Or enable state sync (Option B above)
```

### High memory usage

```bash
sed -i 's/cache_size = 8192/cache_size = 2048/' $CELESTIA_HOME/config/config.toml
sudo systemctl restart celestia-appd
```

### `node is not persisting finalize block responses`

```bash
sed -i 's/^discard_abci_responses *=.*/discard_abci_responses = false/' \
  $CELESTIA_HOME/config/config.toml
sudo systemctl restart celestia-appd
```

### Too many concurrent heavy RPC requests

Lower load on the public RPC, or raise the budget carefully:

```toml
[rpc]
max_concurrent_heavy_requests = 20   # 0 = default 20; negative disables the cap (not recommended)
```

---

## Apollo Validator Services

| Service | Endpoint |
|---------|----------|
| Snapshots | https://snapshots.apollo-validator.eu/celestia/ |
| Snapshot API | https://snapshots.apollo-validator.eu/api/celestia/snapshots/latest |
| Peers page | https://snapshots.apollo-validator.eu/celestia/peers.html |
| Peers raw | https://snapshots.apollo-validator.eu/celestia/peers.md |
| Public RPC | https://rpc.apollo-validator.eu/celestia/status |
| Website | https://apollo-validator.eu/networks/celestia/ |
| Repo | https://github.com/Zelivsky/celestia-services |

### Our node (reference layout)

| | |
|---|---|
| Home | `/root/.celestia-app` |
| Service | `celestia-appd.service` (User=root) |
| Binary | `/root/go/bin/celestia-appd` (multiplexer, v10.5.0) |
| Ports | P2P `36656`, RPC `36657` (localhost + nginx), gRPC `36090` |
| Pruning | `custom` 100/19 · `min-retain-blocks = 600000` · indexer `null` · pebbledb |
| State-sync snapshots | interval 1500 / keep 2 |
| Snapshot cron | every 6 h → `/var/www/snapshots/celestia/snapshots/` |
| Peers cron | every 6 h → `peers-gen-celestia.py` |
| Our validator | `celestiavaloper1mcjmn4s8ee5ce0wsuat98kqxggfrhk04te0d38` |

---

## Links

- Official docs: https://docs.celestia.org/
- Compatible versions: https://docs.celestia.org/operate/networks/overview
- Consensus node guide: https://docs.celestia.org/operate/consensus-validators/consensus-node
- Validator guide: https://docs.celestia.org/operate/consensus-validators/validator-node
- Hardware: https://docs.celestia.org/operate/getting-started/hardware-requirements/
- Networks repo (genesis/seeds): https://github.com/celestiaorg/networks
- celestia-app releases: https://github.com/celestiaorg/celestia-app/releases
- CPU benchmark tool: https://github.com/celestiaorg/celestia-app/blob/main/tools/cpu_requirements/README.md
- Snapshots: https://snapshots.apollo-validator.eu/celestia/
- Peers: https://snapshots.apollo-validator.eu/celestia/peers.html
- Public RPC: https://rpc.apollo-validator.eu/celestia/status

---
Provided by [Apollo Validator](https://apollo-validator.eu)
