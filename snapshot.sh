#!/bin/bash
set -euo pipefail

DATA_DIR=/root/.celestia-app
SNAP_DIR=/var/www/snapshots/celestia/snapshots
META_DIR=/var/www/snapshots/celestia
CELESTIA_RPC=localhost:36657
KEEP_LAST=1

# Get current height
HEIGHT=$(curl -s --max-time 5 http://$CELESTIA_RPC/status | jq -r '.result.sync_info.latest_block_height')
if [ -z "$HEIGHT" ] || [ "$HEIGHT" = "null" ]; then echo "ERROR: Cannot get block height"; exit 1; fi

SNAP_FILE="celestia-mainnet-${HEIGHT}.tar.lz4"
SNAP_PATH="$SNAP_DIR/$SNAP_FILE"
CHECKSUM_FILE="$SNAP_PATH.sha256"

# Skip if snapshot already exists
if [ -f "$SNAP_PATH" ]; then
    echo "Snapshot for height $HEIGHT already exists, skipping"
    exit 0
fi

# STEP 1: Delete OLD snapshots BEFORE creating new one (save disk space)
echo "Cleaning old snapshots..."
cd "$SNAP_DIR"
# `|| true` is required: with `set -euo pipefail` an empty SNAP_DIR makes
# ls/grep exit non-zero and kills the script right after this line.
ls -t celestia-mainnet-*.tar.lz4 2>/dev/null | grep -v "$SNAP_FILE" | tail -n +$((KEEP_LAST + 1)) | xargs -r sudo rm -f || true
ls -t celestia-mainnet-*.sha256 2>/dev/null | grep -v "$SNAP_FILE.sha256" | tail -n +$((KEEP_LAST + 1)) | xargs -r sudo rm -f || true
# Also remove the previous snapshot (keep only the new one)
ls -t celestia-mainnet-*.tar.lz4 2>/dev/null | grep -v "$SNAP_FILE" | xargs -r sudo rm -f || true
ls -t celestia-mainnet-*.sha256 2>/dev/null | grep -v "$SNAP_FILE.sha256" | xargs -r sudo rm -f || true

echo "Free space before snapshot: $(df -h / | tail -1 | awk '{print $4}')"

# STEP 2: Create new snapshot
echo "Creating snapshot at height $HEIGHT..."
# Live node keeps writing/compacting during tar → "file changed / removed"
# warnings make tar exit 1, which under `set -euo pipefail` killed the
# script before checksum/latest.json (rc=1, 2026-10-17). Tolerate tar's rc;
# lz4 still gets a full stream and the archive restores fine (same practice
# as the gnoland snapshot scripts).
(sudo tar -C "$DATA_DIR" -cf - data/ || true) | lz4 -9 > "$SNAP_PATH"
sha256sum "$SNAP_PATH" > "$CHECKSUM_FILE"

SIZE=$(du -h "$SNAP_PATH" | cut -f1)
CHECKSUM=$(awk '{print $1}' "$CHECKSUM_FILE")
TIMESTAMP=$(date -u +%Y-%m-%dT%H:%M:%SZ)

# STEP 3: Update metadata
cat > "$META_DIR/latest.json" << EOF
{"height":$HEIGHT,"size":"$SIZE","created":"$TIMESTAMP","file":"$SNAP_FILE","checksum":"sha256:$CHECKSUM","network":"celestia-mainnet"}
EOF

echo "Snapshot created: $SNAP_FILE ($SIZE)"
echo "Free space after snapshot: $(df -h / | tail -1 | awk '{print $4}')"

# Regenerate snapshot page
sudo python3 /home/celestia/gen-celestia-page.py
