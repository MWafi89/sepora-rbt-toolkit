#!/bin/bash
# ujian_klik_daftar.sh — klik SEBENAR (Input.dispatchMouseEvent) butang "Guru baharu?"
# pada 3 saiz skrin telefon. Menangkap regresi "butang nampak tapi tak jalan".
#!/bin/bash
set -u
URL="${TEST_URL:-https://sepora-rbt-toolkit.vercel.app/index.html}"
PROF=/tmp/ujian_klik_prof
PORT=9350
HERE="$(cd "$(dirname "$0")" && pwd)"
pkill -f "user-data-dir=$PROF" 2>/dev/null
sleep 1; rm -rf "$PROF"
chromium --headless=new --no-sandbox --disable-gpu --disable-dev-shm-usage \
  --remote-debugging-port=$PORT --user-data-dir="$PROF" about:blank >/tmp/klik.log 2>&1 &
CHR=$!
sleep 7
TEST_URL="$URL" CDP_PORT=$PORT timeout 180 node "$HERE/ujian_klik_daftar.js"
RC=$?
kill $CHR 2>/dev/null
pkill -f "user-data-dir=$PROF" 2>/dev/null
exit $RC
