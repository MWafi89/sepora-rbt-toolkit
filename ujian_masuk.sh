#!/bin/bash
# ujian_masuk.sh — bukti "jalan masuk SENANG" (F24) pada laman SEPORA RBT TOOLKIT
#   bash ujian_masuk.sh
#   TEST_URL=http://127.0.0.1:8899/index.html bash ujian_masuk.sh
set -u
HERE="$(cd "$(dirname "$0")" && pwd)"
PROF=/tmp/ujian_masuk_prof
LOG=/tmp/ujian_masuk.log
PORT=9338
rm -rf "$PROF"
chromium --headless=new --no-sandbox --disable-gpu --disable-dev-shm-usage \
         --remote-debugging-port=$PORT --user-data-dir="$PROF" about:blank >"$LOG" 2>&1 &
CHR=$!
trap 'kill $CHR 2>/dev/null; sleep 1; rm -rf "$PROF" 2>/dev/null; rm -f "$LOG" 2>/dev/null' EXIT
sleep 6
TEST_URL="${TEST_URL:-https://sepora-rbt-toolkit.vercel.app/index.html}" CDP_PORT=$PORT \
  node "$HERE/ujian_masuk.js"
exit $?
