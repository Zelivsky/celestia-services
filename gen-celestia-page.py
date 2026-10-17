#!/usr/bin/env python3
"""Generate the Celestia snapshot service page.

Unified Apollo Validator design (same as AtomOne/Gnoland Onyx):
inline dark CSS, .links navigation bar (Snapshots | Peers), cards,
numbered restore steps. Called by snapshot.sh after each snapshot;
values are baked from latest.json (page regenerates every run).
"""
import json

d = json.load(open("/var/www/snapshots/celestia/latest.json"))
h = f"{d['height']:,}"
s, c, f, k = d["size"], d["created"], d["file"], d["checksum"]

TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Celestia Snapshots - Apollo Validator</title>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet">
<style>
*{margin:0;padding:0;box-sizing:border-box}
body{font-family:"Inter",sans-serif;background:#0a0a0a;color:#e0e0e0;line-height:1.6}
.container{max-width:860px;margin:0 auto;padding:40px 20px}
h1{font-size:28px;margin-bottom:8px;color:#fff}
h2{font-size:20px;margin:32px 0 16px;color:#fff}
h3{font-size:16px;margin:24px 0 12px;color:#ccc}
.subtitle{color:#888;margin-bottom:32px;font-size:14px}
.back{color:#666;text-decoration:none;font-size:14px;display:inline-block;margin-bottom:24px}
.back:hover{color:#fff}
.card{background:#1a1a1a;border:1px solid #333;border-radius:12px;padding:24px;margin-bottom:24px}
.row{display:flex;justify-content:space-between;padding:10px 0;border-bottom:1px solid #222}
.row:last-child{border-bottom:none}
.label{color:#888}
.value{color:#fff;font-family:monospace;word-break:break-all;text-align:right}
.btn{display:inline-block;background:#2563eb;color:#fff;padding:12px 24px;border-radius:8px;text-decoration:none;margin-top:12px;margin-right:8px;font-size:14px;cursor:pointer;border:none}
.btn:hover{background:#1d4ed8}
.btn-outline{background:transparent;border:1px solid #333;color:#fff}
.btn-outline:hover{background:#333}
pre{background:#111;border:1px solid #333;border-radius:8px;padding:16px;overflow-x:auto;margin:12px 0;font-size:13px;color:#a0a0a0;white-space:pre-wrap;word-break:break-all}
code{background:#222;padding:2px 6px;border-radius:4px;font-size:13px}
.note{color:#666;font-size:13px;margin-top:12px}
.warning{background:#1a1208;border:1px solid #92400e;border-radius:8px;padding:16px;margin:16px 0;color:#fbbf24;font-size:14px}
.warning strong{color:#f59e0b}
.step{margin-bottom:24px}
.step-num{display:inline-block;background:#2563eb;color:#fff;width:28px;height:28px;border-radius:50%;text-align:center;line-height:28px;font-size:14px;font-weight:600;margin-right:8px}
.step-title{font-weight:600;color:#fff;font-size:16px}
p{margin-bottom:12px;color:#ccc;font-size:14px}
a{color:#60a5fa}
.links{display:flex;gap:12px;margin-bottom:24px;flex-wrap:wrap}
.link{padding:10px 20px;border-radius:8px;background:#1a1a1a;border:1px solid #333;color:#888;text-decoration:none;font-size:14px}
.link.active{background:#2563eb;border-color:#2563eb;color:#fff}
.link:hover{border-color:#60a5fa;color:#fff}
</style>
</head>
<body>
<div class="container">
<a href="https://apollo-validator.eu" class="back">&larr; Back to Apollo Validator</a>
<h1>Celestia Snapshot Service</h1>
<p class="subtitle">Pruned snapshots for Celestia mainnet (celestia). Updated every 6 hours. Node does not stop during snapshot creation.</p>

<div class="links">
<a href="index.html" class="link active">Snapshots</a>
<a href="peers.html" class="link">Peers</a>
</div>

<div class="card">
<h2>Latest Snapshot</h2>
<div class="row"><span class="label">Network</span><span class="value">Celestia Mainnet</span></div>
<div class="row"><span class="label">Chain ID</span><span class="value">celestia</span></div>
<div class="row"><span class="label">Height</span><span class="value">@@HEIGHT@@</span></div>
<div class="row"><span class="label">Size</span><span class="value">@@SIZE@@ (lz4 compressed)</span></div>
<div class="row"><span class="label">Type</span><span class="value">Pruned (keep-recent=100)</span></div>
<div class="row"><span class="label">Created</span><span class="value">@@CREATED@@</span></div>
<div class="row"><span class="label">SHA256</span><span class="value" style="font-size:12px">@@CHECKSUM@@</span></div>
<a class="btn" href="snapshots/@@FILE@@">Download Snapshot (@@SIZE@@)</a>
<a class="btn btn-outline" href="snapshots/@@FILE@@.sha256">SHA256</a>
</div>

<div class="card">
<h2>Snapshot Configuration</h2>
<p>This snapshot uses the following pruning settings:</p>
<h3>app.toml</h3>
<pre>pruning = "custom"
pruning-keep-recent = "100"
pruning-keep-every = "0"
pruning-interval = "19"</pre>
<h3>config.toml</h3>
<pre>indexer = "null"</pre>
<p class="note">Pruned snapshots exclude historical data to minimize size. Ideal for validators and consensus nodes.</p>
</div>

<div class="card">
<h2>Restore from Snapshot</h2>
<div class="warning"><strong>WARNING:</strong> Stop the node before restoring. If you are running a validator, back up <code>data/priv_validator_state.json</code> FIRST to avoid double-signing after restore.</div>
<div class="step"><span class="step-num">1</span><span class="step-title">Install lz4</span><p>Decompression utility for .tar.lz4 files.</p><pre>sudo apt install lz4 -y</pre></div>
<div class="step"><span class="step-num">2</span><span class="step-title">Stop the node</span><pre>sudo systemctl stop celestia-appd</pre></div>
<div class="step"><span class="step-num">3</span><span class="step-title">Back up validator state (validators only)</span><pre>cp ~/.celestia-app/data/priv_validator_state.json ~/.celestia-app/priv_validator_state.json.bak</pre></div>
<div class="step"><span class="step-num">4</span><span class="step-title">Download the snapshot and checksum</span><pre>cd ~/.celestia-app
wget -O @@FILE@@ https://snapshots.apollo-validator.eu/snapshots/@@FILE@@
wget -O @@FILE@@.sha256 https://snapshots.apollo-validator.eu/snapshots/@@FILE@@.sha256</pre></div>
<div class="step"><span class="step-num">5</span><span class="step-title">Verify checksum</span><pre>sha256sum -c @@FILE@@.sha256</pre></div>
<div class="step"><span class="step-num">6</span><span class="step-title">Reset node state and extract</span><pre>cd ~/.celestia-app
celestia-appd tendermint unsafe-reset-all --home ~/.celestia-app --keep-addr-book
lz4 -c -d @@FILE@@ | tar -x -C ~/.celestia-app
rm @@FILE@@ @@FILE@@.sha256</pre></div>
<div class="step"><span class="step-num">7</span><span class="step-title">Restore validator state (validators only)</span><pre>cp ~/.celestia-app/priv_validator_state.json.bak ~/.celestia-app/data/priv_validator_state.json</pre></div>
<div class="step"><span class="step-num">8</span><span class="step-title">Start the node</span><pre>sudo systemctl start celestia-appd
curl -s http://127.0.0.1:36657/status | jq -r .result.sync_info.catching_up</pre></div>
</div>

<div class="card">
<h2>Retention</h2>
<p>Only the latest snapshot is kept — each new run deletes all previous snapshot files (disk-conscious policy for this server).</p>
</div>

<div class="card">
<h2>API</h2>
<p>Get latest snapshot metadata programmatically:</p>
<pre>curl -s https://snapshots.apollo-validator.eu/api/celestia/snapshots/latest | jq</pre>
<p>Returns JSON with height, size, created, file, and checksum.</p>
</div>

<p class="note">Snapshots are created every 6 hours without stopping the node. Powered by <a href="https://apollo-validator.eu">Apollo Validator</a>.</p>
</div>
</body>
</html>
"""

html = (
    TEMPLATE
    .replace("@@HEIGHT@@", h)
    .replace("@@SIZE@@", s)
    .replace("@@CREATED@@", c)
    .replace("@@CHECKSUM@@", k)
    .replace("@@FILE@@", f)
)

with open("/var/www/snapshots/celestia/index.html", "w") as out:
    out.write(html)

print(f"Page generated for height {d['height']}")
