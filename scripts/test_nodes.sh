#!/usr/bin/env bash
# Run on the VPS. Tries to register a Redbelly node through Overledger, then runs a control on a test network. Keys are read from the shell and never saved.
# Usage: read -rs OL_KEY; export OL_KEY; read -rs ANKR_URL; export ANKR_URL; bash scripts/test_nodes.sh
# Optional control: export SEPOLIA_URL (Ankr eth_sepolia URL with your key). A control node is deleted straight after it is created.
set -u
B=https://fusion-rollup.quant.dev; O=evidence/tests/overledger-node-register.txt
: "${OL_KEY:?set OL_KEY}"; : "${ANKR_URL:?set ANKR_URL}"
red() { sed -e "s|$OL_KEY|<OL_KEY>|g" -e "s|$ANKR_URL|<ANKR_URL>|g" -e "s|${SEPOLIA_URL:-__none__}|<SEPOLIA_URL>|g"; }
call() { curl -s -m 60 -w "\nHTTP %{http_code}\n" -H "X-API-Key: $OL_KEY" -H 'accept: application/json' -H 'content-type: application/json' "$@"; }
{
echo "Test date: $(date -u '+%F %T') UTC; base: $B; auth: X-API-Key (Bearer was rejected in an earlier run); keys removed"
echo "== GET /users/me/nodes (before)"; call $B/users/me/nodes
echo "== POST /nodes, guessed network name"; call -X POST $B/nodes -d "{\"address\":\"$ANKR_URL\",\"dlt\":\"EVM\",\"network\":\"redbelly-mainnet\",\"name\":\"redbelly-test\"}"
echo "== POST /nodes, no network field"; call -X POST $B/nodes -d "{\"address\":\"$ANKR_URL\",\"dlt\":\"EVM\",\"name\":\"redbelly-test\"}"
if [ -n "${SEPOLIA_URL:-}" ]; then
  echo "== CONTROL POST /nodes, Ethereum Sepolia"; call -X POST $B/nodes -d "{\"address\":\"$SEPOLIA_URL\",\"dlt\":\"EVM\",\"network\":\"Ethereum Sepolia\",\"name\":\"control-test\"}" | tee /tmp/ol_ctl.txt
  ID=$(grep -o '"_id":"[^"]*"' /tmp/ol_ctl.txt | head -1 | cut -d'"' -f4)
  if [ -n "$ID" ]; then echo "== DELETE /nodes/<_id>"; call -X DELETE "$B/nodes/$ID"; else echo "== no _id found, delete by hand in Quant Connect"; fi
  rm -f /tmp/ol_ctl.txt
fi
echo "== GET /users/me/nodes (after)"; call $B/users/me/nodes
} 2>&1 | red > "$O.new"; echo "Wrote $O.new (review, then replace $O by hand if wanted)"
