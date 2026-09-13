#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
patch_fix_masuk.py  (2026-09-13, Hermes)

F18 — "Pengguna baharu bagaimana mau masuk?"

Masalah sebenar (ditemui semasa audit aliran kemasukan):
  Gerbang log masuk = akaun LALAI app (emel pemilik + PIN lalai). Guru baharu pada
  peranti baharu TIDAK tahu PIN itu, dan laluan Google bergantung pada Client ID.
  Jadi guru baharu tiada jalan masuk yang jelas.

Pembetulan:
  1. Butang jelas pada gerbang: "Guru baharu? Daftar guna ID DELIMa anda sendiri"
     -> buka skrin DAFTAR (Pilihan A: Google ID DELIMa / Pilihan B: guna tanpa Google).
  2. openDaftarModal(paksa, dariGerbang): boleh dipaksa buka walaupun peranti ini sudah
     mendaftar, dan menyediakan pautan "Kembali ke log masuk" (supaya tidak terperangkap).
  3. Medan emel gerbang diisi daripada kredensial tersimpan (jadi selepas guru daftar,
     gerbang memaparkan emel GURU, bukan emel pemilik).

Guna: python3 patch_fix_masuk.py index.html sepora_rbt_toolkit.html
"""
import datetime, os, shutil, sys

GATE_BTN_OLD = """      <div class="delima-foot">"""
GATE_BTN_NEW = """      <button class="delima-toggle" style="margin-top:0.45rem; border-color:rgba(26,115,232,0.45); color:var(--primary);" onclick="openDaftarModal(true, true)">
        <i class="fa-solid fa-user-plus"></i> Guru baharu? Daftar guna ID DELIMa anda sendiri
      </button>
      <div class="delima-foot">"""

MODAL_SIG_OLD = """    function openDaftarModal() {
      if (sudahDaftar()) return;
      window.__modalWajib = true;"""
MODAL_SIG_NEW = """    function tutupDaftarDariGerbang() { window.__modalWajib = false; closeModalDirectly(); }
    function openDaftarModal(paksa, dariGerbang) {
      if (!paksa && sudahDaftar()) return;
      window.__modalWajib = true;"""

MODAL_TAIL_OLD = """            Mod ini tidak menyandar ke Drive. Anda boleh daftar guna ID DELIMa bila-bila masa melalui menu Drive.
          </p>
        </div>`;
      openModal(html);
    }"""
MODAL_TAIL_NEW = """            Mod ini tidak menyandar ke Drive. Anda boleh daftar guna ID DELIMa bila-bila masa melalui menu Drive.
          </p>
        </div>
        ${dariGerbang ? '<p style="font-size:0.75rem; text-align:center; margin-top:0.6rem;"><span onclick="tutupDaftarDariGerbang()" style="cursor:pointer; text-decoration:underline; color:var(--text-muted);">Kembali ke log masuk</span></p>' : ''}`;
      openModal(html);
    }"""

HELP_OLD = """          <span onclick="showDefaultLoginHelp(event)" style="cursor:pointer; text-decoration:underline;">Lupa PIN? Tunjuk log masuk asal</span>"""
HELP_NEW = """          <span onclick="showDefaultLoginHelp(event)" style="cursor:pointer; text-decoration:underline;">Lupa PIN?</span> &bull; Guru baharu: tekan butang <strong>Guru baharu?</strong> di bawah."""

PREFILL_ANCHOR = """      if (sess && sess.email && !isLocked()) isLoggedIn = true;   // [F11] kunci skrin dihormati"""
PREFILL_NEW = """      if (sess && sess.email && !isLocked()) isLoggedIn = true;   // [F11] kunci skrin dihormati
      // [F18] gerbang memaparkan emel akaun tersimpan (guru sendiri, bukan pemilik app)
      try {
        const _f = document.getElementById('loginInputEmail');
        if (_f && !_f.value) _f.value = (authCredentials && authCredentials.email) || DEFAULT_AUTH.email;
      } catch (e) { }"""


def patch(src):
    if '[F18]' in src:
        return src, False
    for old, new, nama in (
        (GATE_BTN_OLD, GATE_BTN_NEW, 'butang guru baharu'),
        (MODAL_SIG_OLD, MODAL_SIG_NEW, 'tandatangan openDaftarModal'),
        (MODAL_TAIL_OLD, MODAL_TAIL_NEW, 'pautan kembali'),
        (HELP_OLD, HELP_NEW, 'teks bantuan gerbang'),
        (PREFILL_ANCHOR, PREFILL_NEW, 'prefill emel gerbang'),
    ):
        assert src.count(old) == 1, 'jangkar %s tidak unik (%d)' % (nama, src.count(old))
        src = src.replace(old, new, 1)
    return src, True


def main():
    files = sys.argv[1:] or ['index.html']
    for f in files:
        s = open(f, encoding='utf-8').read()
        os.makedirs('/tmp/sepora_bak', exist_ok=True)
        shutil.copy2(f, '/tmp/sepora_bak/' + os.path.basename(f) + '.bak-masuk-' + datetime.datetime.now().strftime('%Y%m%d-%H%M%S'))
        out, ch = patch(s)
        open(f, 'w', encoding='utf-8').write(out)
        print('[OK] %s -> %s' % (f, 'ditampal' if ch else 'sudah ditampal'))
    for f in files:
        s = open(f, encoding='utf-8').read()
        for m in ('[F18]', 'openDaftarModal(true, true)', 'tutupDaftarDariGerbang', 'function openDaftarModal(paksa, dariGerbang)'):
            assert m in s, 'semakan gagal %s: %s' % (f, m)
    print('[SEMAK] F18 jalan masuk guru baharu OK')
    return 0


if __name__ == '__main__':
    sys.exit(main())
