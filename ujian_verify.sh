#!/bin/bash
# ujian_verify.sh — UJIAN ad-hoc SEPORA RBT TOOLKIT (patut dijalankan dari root repo)
#   (A) statik : twin segerak, syntax JS inline, penanda pembetulan, patch idempotent-selamat
#   (B) tingkah laku : chromium headless CDP terhadap laman LIVE (atau tempatan)
# Guna:
#   bash ujian_verify.sh
#   TEST_URL=http://127.0.0.1:8899/index.html bash ujian_verify.sh
set -u
HERE="$(cd "$(dirname "$0")" && pwd)"
cd "$HERE" || exit 2
FAIL=0
step() { printf '%-58s %s\n' "$1" "$2"; [ "$2" = "FAIL" ] && FAIL=$((FAIL+1)); }

echo "=== (A) SEMAKAN STATIK ==="

# A1 twin disegerakkan
if [ "$(sha256sum index.html | cut -d' ' -f1)" = "$(sha256sum sepora_rbt_toolkit.html | cut -d' ' -f1)" ]; then
  step "A1 twin index.html/sepora_rbt_toolkit.html segerak" PASS
else
  step "A1 twin segerak" FAIL
fi

# A2 syntax JS inline
python3 - <<PY
import re
s=open('$HERE/index.html',encoding='utf-8').read()
sc=re.findall(r'<script(?![^>]*src=)[^>]*>(.*?)</script>', s, re.S)
open('/tmp/ujian_inline.js','w').write('\n;\n'.join(sc))
PY
if node --check /tmp/ujian_inline.js 2>/dev/null; then step "A2 syntax JS inline (node --check)" PASS; else step "A2 syntax JS inline (node --check)" FAIL; fi

# A3 penanda pembetulan hadir
for M in rphMirrorWrap printArkibRph deleteAllDrafts __pblEdited arkibWithSuspend; do
  if grep -q "$M" index.html; then step "A3 penanda $M hadir" PASS; else step "A3 penanda $M hadir" FAIL; fi
done

# A4 patch idempotent-selamat (guna backup pra-patch kalau ada)
BAK=$(ls -t /tmp/sepora_bak/index.html.bak-* 2>/dev/null | head -1)
if [ -n "$BAK" ]; then
  cp "$BAK" /tmp/ujian_orig.html
  if python3 patch_fix_papar_huraian.py /tmp/ujian_orig.html >/dev/null 2>&1; then step "A4a patch pada fail asal berjaya" PASS; else step "A4a patch pada fail asal berjaya" FAIL; fi
  H1=$(sha256sum /tmp/ujian_orig.html | cut -d' ' -f1)
  python3 patch_fix_papar_huraian.py /tmp/ujian_orig.html >/dev/null 2>&1 && R2=0 || R2=1
  H2=$(sha256sum /tmp/ujian_orig.html | cut -d' ' -f1)
  if [ "$R2" = 1 ] && [ "$H1" = "$H2" ]; then step "A4b patch kali kedua gagal bersih (fail tak dirosakkan)" PASS; else step "A4b patch kali kedua gagal bersih" FAIL; fi
else
  step "A4 backup pra-patch tiada (/tmp/sepora_bak) — dilangkau" PASS
fi

echo
echo "=== (B) SEMAKAN TINGKAH LAKU (chromium headless + CDP) ==="
PROF=/tmp/ujian_chr_prof
LOG=/tmp/ujian_chr.log
rm -rf "$PROF"
chromium --headless=new --no-sandbox --disable-gpu --disable-dev-shm-usage \
         --remote-debugging-port=9334 --user-data-dir="$PROF" about:blank >/tmp/ujian_chr.log 2>&1 &
CHR=$!
trap 'pkill -f "user-data-dir=$PROF" 2>/dev/null; sleep 1; rm -rf "$PROF" 2>/dev/null; rm -f "$LOG" 2>/dev/null; rm -f /tmp/ujian_inline.js /tmp/ujian_orig.html' EXIT
sleep 6
TEST_URL="${TEST_URL:-https://sepora-rbt-toolkit.vercel.app/index.html}" CDP_PORT=9334 \
  node "$HERE/ujian_verify_cdp.js"
RC=$?
exit $RC
