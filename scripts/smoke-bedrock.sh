#!/usr/bin/env bash
# Smoke test for the Bedrock CTF stack.
# Run AFTER bringing the stack up:  docker compose up -d
#
# Verifies that:
#   1. the Bedrock gateway is healthy,
#   2. the gateway is actually serving Bedrock model IDs,
#   3. Open WebUI is up.
# It does NOT attempt to solve challenges.
set -euo pipefail

# Load .env if present so ports/keys match the running stack.
if [ -f "$(dirname "$0")/../.env" ]; then
  set -a; . "$(dirname "$0")/../.env"; set +a
fi

GW_PORT="${BEDROCK_PORT:-8081}"
OWUI_PORT="${OPENWEBUI_PORT:-4242}"
GW_KEY="${BEDROCK_API_KEY:-bedrock}"

echo "[*] Bedrock gateway health (http://localhost:${GW_PORT}/health)..."
curl -fsS "http://localhost:${GW_PORT}/health" >/dev/null && echo "    OK"

echo "[*] Bedrock gateway model list..."
models="$(curl -fsS "http://localhost:${GW_PORT}/api/v1/models" -H "Authorization: Bearer ${GW_KEY}")"
echo "${models}" | head -c 600; echo
echo "${models}" | grep -q "llama3-3-70b" \
  && echo "    OK (llama3-3-70b present)" \
  || { echo "    WARN: expected Bedrock model not found — check AWS creds/region"; }

echo "[*] Open WebUI health (http://localhost:${OWUI_PORT}/health)..."
curl -fsS "http://localhost:${OWUI_PORT}/health" >/dev/null && echo "    OK"

echo "[*] Smoke test passed."
