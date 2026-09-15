#!/bin/bash
# ujian_daftar_realiti.sh — daftar guru baharu seperti manusia: klik + taip SEBENAR
set -u
HERE="$(cd "$(dirname "$0")" && pwd)"
URL="${TEST_URL:-https://sepora-rbt-toolkit.vercel.app/index.html}"
PROF=/tmp/ujian_realiti_prof
PORT=9400
pkill -f "user-data-dir=$PROF" 2>/dev/null
sleep 1
rm -rf "$PROF"
chromium --headless=new --no-sandbox --disable-gpu --disable-dev-shm-usage \
  --disable-features=Translate --no-first-run \
  --remote-debugging-port=$PORT --user-data-dir="$PROF" about:blank >/tmp/ujian_realiti.log 2>&1 &
CHR=$!
for i in $(seq 1 25); do
  if curl -sS -m 2 "http://127.0.0.1:$PORT/json/version" >/dev/null 2>&1; then break; fi
  sleep 1
done
TEST_URL="$URL" CDP_PORT=$PORT timeout 200 node "$HERE/ujian_daftar_realiti.js"
RC=$?
kill $CHR 2>/dev/null
pkill -f "user-data-dir=$PROF" 2>/dev/null
exit $RC
