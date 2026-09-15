#!/bin/bash
# ujian_gerbang_butang.sh — semua butang gerbang kelihatan & boleh ditekan pada 4 saiz skrin
#   bash ujian_gerbang_butang.sh
#   TEST_URL=http://127.0.0.1:8899/index.html bash ujian_gerbang_butang.sh
set -u
HERE="$(cd "$(dirname "$0")" && pwd)"
URL="${TEST_URL:-https://sepora-rbt-toolkit.vercel.app/index.html}"
PROF=/tmp/ujian_gerbang_prof
PORT=9354
pkill -f "user-data-dir=$PROF" 2>/dev/null
sleep 1
rm -rf "$PROF"
chromium --headless=new --no-sandbox --disable-gpu --disable-dev-shm-usage \
  --remote-debugging-port=$PORT --user-data-dir="$PROF" about:blank >/tmp/ujian_gerbang.log 2>&1 &
CHR=$!
sleep 7
TEST_URL="$URL" CDP_PORT=$PORT timeout 220 node "$HERE/ujian_gerbang_butang.js"
RC=$?
kill $CHR 2>/dev/null
pkill -f "user-data-dir=$PROF" 2>/dev/null
exit $RC
