#!/usr/bin/env bash
# Run on the VPS. Calls Redbelly mainnet through the public Ankr endpoint, saves timing and answers. No keys involved.
U=https://rpc.ankr.com/redbelly_mainnet; O=evidence/tests/ankr-rpc.txt
echo "Test date: $(date -u +%F) UTC; endpoint: $U (public, no key)" > $O
for m in eth_chainId net_version web3_clientVersion eth_blockNumber eth_gasPrice; do
  echo "== $m" >> $O
  curl -s -m 20 -w "\nHTTP %{http_code} in %{time_total}s\n" -H 'content-type: application/json' \
    -d "{\"jsonrpc\":\"2.0\",\"id\":1,\"method\":\"$m\",\"params\":[]}" $U >> $O
done
cat $O
