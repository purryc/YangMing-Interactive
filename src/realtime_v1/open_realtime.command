#!/bin/zsh
set -eu
export PATH="/usr/local/bin:/opt/homebrew/bin:$PATH"
cd "$(dirname "$0")"
if ! curl -fsS http://127.0.0.1:8766/api/status >/dev/null 2>&1; then
  if [[ ! -d node_modules ]]; then npm ci --no-audit --no-fund; fi
  mkdir -p ../../qa/realtime_v1
  nohup node server.mjs >../../qa/realtime_v1/server.log 2>&1 &
  for attempt in {1..25}; do
    if curl -fsS http://127.0.0.1:8766/api/status >/dev/null 2>&1; then break; fi
    sleep 0.2
  done
fi
if curl -fsS http://127.0.0.1:8766/api/status >/dev/null 2>&1; then
  open http://127.0.0.1:8766
else
  printf '启动未成功，请查看 projects/scholar_voice_character/qa/realtime_v1/server.log\n'
  exit 1
fi
