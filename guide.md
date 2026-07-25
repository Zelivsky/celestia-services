# Celestia Mainnet Validator Guide

Step-by-step guide for setting up a Celestia consensus node.

## Hardware Requirements

| Component | Minimum | Recommended |
|-----------|---------|-------------|
| CPU | 32 cores (GFNI + SHA-NI) | 32+ cores |
| RAM | 32 GB | 64 GB |
| Storage | 12 TiB NVMe | 12+ TiB NVMe |
| Network | 1 Gbps | 1 Gbps |

**OS:** Ubuntu 24.04 LTS

## Installation

```bash
# Install Go
wget https://go.dev/dl/go1.22.5.linux-amd64.tar.gz
sudo tar -C /usr/local -xzf go1.22.5.linux-amd64.tar.gz

# Build
git clone https://github.com/celestiaorg/celestia-app.git
cd celestia-app && make install
```

## Configuration

```bash
celestia-appd init <moniker> --chain-id celestia
wget -O ~/.celestia-app/config/genesis.json https://raw.githubusercontent.com/celestiaorg/networks/main/mainnet/genesis.json
```

## Running

```bash
celestia-appd start
```

## Sync

### From Snapshot (fast)
```bash
sudo systemctl stop celestia-appd
wget -O snapshot.tar.lz4 https://snapshots.apollo-validator.eu/celestia/snapshots/latest.tar.lz4
rm -rf ~/.celestia-app/db ~/.celestia-app/wal
lz4 -c -d snapshot.tar.lz4 | tar -x -C ~/.celestia-app/
sudo systemctl start celestia-appd
```

## Validator Registration

```bash
celestia-appd tx staking create-validator \
  --amount=1000000utia \
  --commission-rate=0.10 \
  --chain-id=celestia \
  --gas=auto
```

## Links

- [Public RPC](https://rpc.apollo-validator.eu/celestia/)
- [Snapshots](https://snapshots.apollo-validator.eu/celestia/)
- [Official Docs](https://docs.celestia.org)
