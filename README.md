# Celestia Mainnet Services

Public infrastructure and tools for Celestia mainnet operators by [Apollo Validator](https://apollo-validator.eu).

[![Celestia](https://img.shields.io/badge/Chain-celestia--mainnet-blue)](https://celestia.org)

## Services

| Service | Endpoint | Status |
|---|---|---|
| Snapshots | `https://snapshots.apollo-validator.eu/celestia/` | 🟢 Active |
| Public RPC | Coming soon | 🟡 Planned |
| State Sync Guide | Coming soon | 🟡 Planned |
| Peers List | Coming soon | 🟡 Planned |
| Validator Guide | [guide.md](guide.md) | 🟡 Planned |
| Validator Monitor | Coming soon | 🟡 Planned |

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

Coming soon.

## Validator Monitor Bot

Coming soon.

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
