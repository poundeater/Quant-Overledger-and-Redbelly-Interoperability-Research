#!/usr/bin/env bash
# T5: tries a fixed list of network names for Ankr's Redbelly mainnet endpoint. Testnet names are probes: the endpoint is mainnet, so only the error text matters.
# Any node that does get created is deleted by its _id. Usage: read -rs OL_KEY; export OL_KEY; read -rs ANKR_URL; export ANKR_URL; bash scripts/test_names.sh
set -u
B=https://fusion-rollup.quant.dev; O=evidence/tests/overledger-node-names.txt
: "${OL_KEY:?set OL_KEY}"; : "${ANKR_URL:?set ANKR_URL}"
red() { sed -e "s|$OL_KEY|<OL_KEY>|g" -e "s|$ANKR_URL|<ANKR_URL>|g"; }
call() { curl -s -m 60 -w "\nHTTP %{http_code}\n" -H "X-API-Key: $OL_KEY" -H 'accept: application/json' -H 'content-type: application/json' "$@"; }
NAMES=("Redbelly Mainnet" "Redbelly Network" "Redbelly Network Mainnet" "Redbelly" "Redbelly Testnet" "Redbelly Network Testnet")
{
echo "Test date: $(date -u '+%F %T') UTC; base: $B; auth: X-API-Key; keys removed; names tried: ${#NAMES[@]}"
echo "== GET /users/me/nodes (before)"; call $B/users/me/nodes
for n in "${NAMES[@]}"; do
  echo "== POST /nodes, network=\"$n\""
  out=$(call -X POST $B/nodes -d "{\"address\":\"$ANKR_URL\",\"dlt\":\"EVM\",\"network\":\"$n\",\"name\":\"name-test\"}")
  echo "$out"
  id=$(echo "$out" | grep -o '"_id":"[^"]*"' | head -1 | cut -d'"' -f4)
  if [ -n "$id" ]; then echo "== DELETE /nodes/$id"; call -X DELETE "$B/nodes/$id"; fi
  sleep 2
done
echo "== GET /users/me/nodes (after)"; call $B/users/me/nodes
} 2>&1 | red > "$O"; echo "Wrote $O. Read it before committing."
