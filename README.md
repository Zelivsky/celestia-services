# Celestia Mainnet Services

Public infrastructure and tools for Celestia mainnet operators by [Apollo Validator](https://apollo-validator.eu).

[![Celestia](https://img.shields.io/badge/Chain-celestia--mainnet-blue)](https://celestia.org)
[![RPC](https://img.shields.io/badge/RPC-rpc.apollo--validator.eu-green)](https://rpc.apollo-validator.eu/celestia/)

## Services

| Service | Endpoint | Status |
|---|---|---|
| Public RPC | `https://rpc.apollo-validator.eu/celestia/` | 🟢 Active |
| Snapshots | `https://snapshots.apollo-validator.eu/celestia/` | 🟢 Active |
| State Sync Guide | [statesync.md](statesync.md) | 🟢 Active |
| Peers List | [peers.md](peers.md) (auto-updated) | 🟢 Active |
| Validator Guide | [guide.md](guide.md) | 🟢 Active |
| Validator Monitor | @celesta_monitor_apollo_bot | 🟢 Active |

## Snapshots

Page: `https://snapshots.apollo-validator.eu/celestia/`

### Download Latest

```bash
curl -s https://snapshots.apollo-validator.eu/api/celestia/snapshots/latest | jq
wget -O celestia-snapshot.tar.lz4 https://snapshots.apollo-validator.eu/celestia/snapshots/latest.tar.lz4
```

### Restore from Snapshot

```bash
sudo apt install lz4 -y
sudo systemctl stop celestia-appd
cp ~/.celestia-app/data/priv_validator_state.json ~/priv_validator_state.json.bak
wget -O celestia-snapshot.tar.lz4 https://snapshots.apollo-validator.eu/celestia/snapshots/latest.tar.lz4
rm -rf ~/.celestia-app/db ~/.celestia-app/wal
lz4 -c -d celestia-snapshot.tar.lz4 | tar -x -C ~/.celestia-app/
cp ~/priv_validator_state.json.bak ~/.celestia-app/data/priv_validator_state.json
sudo systemctl start celestia-appd
rm -v celestia-snapshot.tar.lz4
```

## Public RPC

Base URL: `https://rpc.apollo-validator.eu/celestia/`

### Usage Examples

```bash
curl -s https://rpc.apollo-validator.eu/celestia/status | jq
curl -s https://rpc.apollo-validator.eu/celestia/status | jq -r '.result.sync_info.latest_block_height'
curl -s https://rpc.apollo-validator.eu/celestia/net_info | jq -r '.result.n_peers'
```

### Configuration

```
RPC URL: https://rpc.apollo-validator.eu/celestia/
Chain ID: celestia
```

## Validator Monitor Bot

**Bot:** [@celesta_monitor_apollo_bot](https://t.me/celesta_monitor_apollo_bot)

### Commands

| Command | Description |
|---------|-------------|
| `/add <address>` | Add validator to monitoring |
| `/remove <address>` | Remove validator |
| `/list` | List your validators |
| `/status` | Show network info |
| `/help` | Show help |

### Auto Alerts

- 🚨 RPC unreachable
- ⚠️ Validator left active set
- ⚠️ Zero voting power
- ⚠️ Low peers

## Validator Guide

Full guide: [guide.md](guide.md)

## Validator

| Field | Value |
|---|---|
| Operator | Apollo Validator |
| Consensus | `celestiavaloper1mcjmn4s8ee5ce0wsuat98kqxggfrhk04te0d38` |
| Chain | celestia |
| Website | [apollo-validator.eu](https://apollo-validator.eu) |

## Links

- [Celestia Website](https://celestia.org)
- [Mintscan Explorer](https://www.mintscan.io/celestia)
- [Official Docs](https://docs.celestia.org)
- [Discord](https://discord.gg/celestia)

## License

MIT
