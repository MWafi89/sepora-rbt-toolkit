#!/bin/bash
# ujian_gerbang_baharu.sh — guru baharu boleh masuk? (F28)
set -u
HERE="$(cd "$(dirname "$0")" && pwd)"
URL="${TEST_URL:-http://127.0.0.1:8899/index.html}"
PROF=/tmp/ujian_gbh_prof
PORT=9390
pkill -f "user-data-dir=$PROF" 2>/dev/null
sleep 1
rm -rf "$PROF"
chromium --headless=new --no-sandbox --disable-gpu --disable-dev-shm-usage \
  --disable-features=Translate --no-first-run \
  --remote-debugging-port=$PORT --user-data-dir="$PROF" about:blank >/tmp/ujian_gbh.log 2>&1 &
CHR=$!
for i in $(seq 1 25); do
  if curl -sS -m 2 "http://127.0.0.1:$PORT/json/version" >/dev/null 2>&1; then break; fi
  sleep 1
done
TEST_URL="$URL" CDP_PORT=$PORT timeout 200 node "$HERE/ujian_gerbang_baharu.js"
RC=$?
kill $CHR 2>/dev/null
pkill -f "user-data-dir=$PROF" 2>/dev/null
exit $RC
