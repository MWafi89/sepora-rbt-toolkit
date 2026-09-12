#!/bin/bash
# ujian_lengkap.sh — UJIAN LENGKAP SEPORA RBT TOOLKIT (kitaran hayat RPH + arkib) melalui chromium headless + CDP
#   Menjawab: (1) aplikasi lengkap?  (2) setiap RPH dijana tersimpan ke arkib?  (3) boleh edit & guna semula?
# Guna:
#   bash ujian_lengkap.sh
#   TEST_URL=http://127.0.0.1:8899/index.html bash ujian_lengkap.sh
set -u
HERE="$(cd "$(dirname "$0")" && pwd)"
PROF=/tmp/ujian_lengkap_prof
LOG=/tmp/ujian_lengkap.log
PORT=9336
rm -rf "$PROF"
chromium --headless=new --no-sandbox --disable-gpu --disable-dev-shm-usage \
         --remote-debugging-port=$PORT --user-data-dir="$PROF" about:blank >"$LOG" 2>&1 &
CHR=$!
trap 'pkill -f "user-data-dir=$PROF" 2>/dev/null; sleep 1; rm -rf "$PROF" 2>/dev/null; rm -f "$LOG" 2>/dev/null' EXIT
sleep 6
TEST_URL="${TEST_URL:-https://sepora-rbt-toolkit.vercel.app/index.html}" CDP_PORT=$PORT \
  node "$HERE/ujian_lengkap_cdp.js"
exit $?
