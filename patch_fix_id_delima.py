#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
patch_fix_id_delima.py  (2026-09-12, Hermes)

F16 — Guru daftar dengan ID DELIMa MEREKA SENDIRI (bukan akaun pemilik)

Arahan: "mereka guna id mereka masing2 ... bukan id saya"

Perubahan:
  1. Borang daftar (Pilihan B) menerima ID DELIMa tanpa domain juga:
       'g-57258425'  ->  identiti jadi 'g-57258425@moe-dl.edu.my'
     (jadi guru boleh taip ID DELIMa sekolah mereka, bukan perlu ingat format emel)
  2. Sesi menyimpan medan 'delimaId' supaya ID DELIMa mereka dipaparkan semula
     dalam panel Drive ("ID DELIMa: g-57258425").
  3. Label borang dijelaskan: "ID DELIMa atau emel anda sendiri".

Nota keselamatan (kekal): app TIDAK menyimpan kata laluan DELIMa. Guru menaip kata
laluan mereka pada halaman Google DELIMa sendiri semasa log masuk Google; app hanya
menerima token Drive (skop drive.file).

Guna: python3 patch_fix_id_delima.py index.html sepora_rbt_toolkit.html
"""
import datetime, os, shutil, sys

FORM_LABEL_OLD = """              <label class="form-label">Emel anda</label>
              <input type="email" id="daftarEmel" class="form-control" placeholder="cth: nama@moe-dl.edu.my" required>"""
FORM_LABEL_NEW = """              <label class="form-label">ID DELIMa atau emel anda sendiri</label>
              <input type="text" id="daftarEmel" class="form-control" placeholder="cth: g-57258425 atau nama@moe-dl.edu.my" required>"""

VALID_OLD = """      const emel = String((document.getElementById('daftarEmel') || {}).value || '').trim().toLowerCase();"""
VALID_NEW = """      let emel = String((document.getElementById('daftarEmel') || {}).value || '').trim().toLowerCase();
      // [F16] terima ID DELIMa tanpa domain (cth: g-57258425) -> jadikan emel MOE
      let idDelima = '';
      if (emel && emel.indexOf('@') === -1) { idDelima = emel; emel = emel + '@moe-dl.edu.my'; }"""

FINISH_OLD = """      finishLogin({ email: emel, name: nama, mode: 'setempat' });"""
FINISH_NEW = """      finishLogin({ email: emel, name: nama, mode: 'setempat', delimaId: idDelima || '' });"""

PANEL_OLD = """        ['Akaun DELIMa', sess ? esc(sess.email) + (sess.mode === 'delima' ? ' <span style="color:#059669;">(disahkan)</span>' : ' <span style="color:#b45309;">(mod setempat)</span>') : '<em>Belum log masuk</em>'],"""
PANEL_NEW = """        ['Akaun DELIMa', sess ? (sess.delimaId ? 'ID DELIMa: <strong>' + esc(sess.delimaId) + '</strong> &bull; ' : '') + esc(sess.email) + (sess.mode === 'delima' ? ' <span style="color:#059669;">(disahkan Google)</span>' : ' <span style="color:#b45309;">(mod setempat)</span>') : '<em>Belum log masuk</em>'],"""


def patch(src):
    if 'F16] terima ID DELIMa' in src:
        return src, False
    for old, new, nama in ((FORM_LABEL_OLD, FORM_LABEL_NEW, 'label borang daftar'),
                           (VALID_OLD, VALID_NEW, 'validasi emel/ID'),
                           (FINISH_OLD, FINISH_NEW, 'finishLogin dgn delimaId'),
                           (PANEL_OLD, PANEL_NEW, 'paparan ID DELIMa dlm panel')):
        assert src.count(old) == 1, 'jangkar %s tidak unik' % nama
        src = src.replace(old, new, 1)
    return src, True


def main():
    files = sys.argv[1:] or ['index.html']
    for f in files:
        s = open(f, encoding='utf-8').read()
        os.makedirs('/tmp/sepora_bak', exist_ok=True)
        shutil.copy2(f, '/tmp/sepora_bak/' + os.path.basename(f) + '.bak-f16-' + datetime.datetime.now().strftime('%Y%m%d-%H%M%S'))
        out, ch = patch(s)
        open(f, 'w', encoding='utf-8').write(out)
        print('[OK] %s -> %s' % (f, 'ditampal' if ch else 'sudah ditampal'))
    for f in files:
        s = open(f, encoding='utf-8').read()
        for m in ('[F16] terima ID DELIMa', "let idDelima = ''", 'delimaId: idDelima', 'ID DELIMa: <strong>'):
            assert m in s, 'semakan gagal %s: %s' % (f, m)
    print('[SEMAK] F16 ID DELIMa guru sendiri OK')
    return 0


if __name__ == '__main__':
    sys.exit(main())
