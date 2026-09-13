#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
patch_fix_pratonton_logout.py  (2026-09-13, Hermes)

F21 — BUG: selepas Log Keluar -> Log Masuk semula, kawasan pratonton RPH mati
      ("Jana RPH" tidak menghasilkan apa-apa).

Bukti (ujian perjalanan guru baharu, P17):
  selepas P12 (keluar -> masuk semula) + loadSlotToRph + autoGenerateSmartRph,
  #rphPreviewContainer kekal KOSONG (textContent = 0) walaupun tunggu 10 saat.

Punca: logoutSession() melakukan `pv.innerHTML = ''` — ini memusnahkan SEMUA elemen
kanak-kanak pratonton (previewTajuk, previewSK, previewObjektif, ...). Selepas itu
autoGenerateSmartRph() tidak dapat mencari elemen tersebut (getElementById pulang null),
jadi penjanaan berhenti secara senyap. Log masuk semula tidak membina semula struktur itu.

Pembetulan:
  1. Semasa boot: simpan struktur pratonton asal -> window.__rphPvTpl.
  2. logoutSession(): JANGAN musnahkan struktur - pulihkan templat jika perlu, kemudian
     kosongkan TEKS/ nilai sahaja (dokumen guru sebelumnya tetap tidak kelihatan, F11 kekal).
  3. pastikanPratonton(): dipanggil di checkAuthStatus() dan hujung finishLogin() supaya
     struktur pratonton pulih sendiri kalau hilang.

Guna: python3 patch_fix_pratonton_logout.py index.html sepora_rbt_toolkit.html
"""
import datetime, os, shutil, sys

BOOT_ANCHOR = """    const SEPORA_LINKTREE_URL = "https://linktr.ee/RBTSEPORA"""
BOOT_NEW = """    // [F21] simpan struktur pratonton ASAL (pristine, sebelum apa-apa penjanaan) supaya boleh
    // dipulihkan selepas log keluar - struktur hidup, kandungan guru sebelumnya hilang.
    try { const _pv0 = document.getElementById('rphPreviewContainer'); if (_pv0) window.__rphPvTpl = _pv0.innerHTML; } catch (e) { }
    const SEPORA_LINKTREE_URL = "https://linktr.ee/RBTSEPORA"""

HELPER_ANCHOR = """    function checkAuthStatus() {"""
HELPER_NEW = """    /* [F21] pastikan struktur pratonton RPH wujud (kalau pernah dipadam, pulihkan templat) */
    function pastikanPratonton() {
      try {
        const pv = document.getElementById('rphPreviewContainer');
        if (!pv) return false;
        if (!pv.querySelector('[id^="preview"]') && window.__rphPvTpl) { pv.innerHTML = window.__rphPvTpl; return true; }
        return true;
      } catch (e) { return false; }
    }

    function checkAuthStatus() {"""

LOGOUT_OLD = """      const pv = document.getElementById('rphPreviewContainer');
      if (pv) pv.innerHTML = '';"""
LOGOUT_NEW = """      // [F21] JANGAN musnahkan struktur pratonton (kalau tidak "Jana RPH" mati selepas log masuk
      // semula): pulihkan templat, kemudian kosongkan teks/nilai supaya dokumen guru sebelumnya
      // tidak kelihatan (keperluan F11 kekal).
      try {
        pastikanPratonton();
        const pv = document.getElementById('rphPreviewContainer');
        if (pv && window.__rphPvTpl) pv.innerHTML = window.__rphPvTpl;   // [F21] templat BERSIH: struktur hidup, kandungan guru lepas hilang
      } catch (e) { }"""

FINISH_ANCHOR = """      if (typeof syncTeacherUI === 'function') syncTeacherUI();
      refreshDriveChip();"""
FINISH_NEW = """      if (typeof syncTeacherUI === 'function') syncTeacherUI();
      pastikanPratonton();   // [F21] pratonton pulih selepas log masuk
      refreshDriveChip();"""


def patch(src):
    if '[F21]' in src:
        return src, False
    for old, new, nama in (
        (HELPER_ANCHOR, HELPER_NEW, 'helper pastikanPratonton'),
        (BOOT_ANCHOR, BOOT_NEW, 'boot simpan templat'),
        (LOGOUT_OLD, LOGOUT_NEW, 'logout tidak musnahkan struktur'),
        (FINISH_ANCHOR, FINISH_NEW, 'pulih selepas log masuk'),
    ):
        assert src.count(old) == 1, 'jangkar %s tidak unik (%d)' % (nama, src.count(old))
        src = src.replace(old, new, 1)
    return src, True


def main():
    files = sys.argv[1:] or ['index.html']
    for f in files:
        s = open(f, encoding='utf-8').read()
        os.makedirs('/tmp/sepora_bak', exist_ok=True)
        shutil.copy2(f, '/tmp/sepora_bak/' + os.path.basename(f) + '.bak-f21-' + datetime.datetime.now().strftime('%Y%m%d-%H%M%S'))
        out, ch = patch(s)
        open(f, 'w', encoding='utf-8').write(out)
        print('[OK] %s -> %s' % (f, 'ditampal' if ch else 'sudah ditampal'))
    for f in files:
        s = open(f, encoding='utf-8').read()
        for m in ('[F21]', 'function pastikanPratonton', '__rphPvTpl'):
            assert m in s, 'semakan gagal %s: %s' % (f, m)
    print('[SEMAK] F21 pratonton selepas logout OK')
    return 0


if __name__ == '__main__':
    sys.exit(main())
