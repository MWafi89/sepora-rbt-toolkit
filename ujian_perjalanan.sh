#!/bin/bash
# ujian_perjalanan.sh — PERJALANAN PENGGUNA BAHARU (guru) hujung-ke-hujung melalui chromium headless + CDP
#   Menjawab: "sebagai guru baharu, boleh ke guna app ini sampai habis?" (daftar -> jana RPH -> simpan ->
#             arkib -> eksport -> RPT/BBM -> Drive -> profil -> keluar/masuk semula)
# Guna:
#   bash ujian_perjalanan.sh
#   TEST_URL=http://127.0.0.1:8899/index.html bash ujian_perjalanan.sh
set -u
HERE="$(cd "$(dirname "$0")" && pwd)"
PROF=/tmp/ujian_perjalanan_prof
LOG=/tmp/ujian_perjalanan.log
PORT=9337
rm -rf "$PROF"
chromium --headless=new --no-sandbox --disable-gpu --disable-dev-shm-usage \
         --remote-debugging-port=$PORT --user-data-dir="$PROF" about:blank >"$LOG" 2>&1 &
CHR=$!
trap 'pkill -f "user-data-dir=$PROF" 2>/dev/null; sleep 1; rm -rf "$PROF" 2>/dev/null; rm -f "$LOG" 2>/dev/null' EXIT
sleep 6
TEST_URL="${TEST_URL:-https://sepora-rbt-toolkit.vercel.app/index.html}" CDP_PORT=$PORT \
  node "$HERE/ujian_perjalanan_guru.js"
exit $?
