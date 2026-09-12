#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
patch_fix_onboarding.py  (2026-09-12, Hermes)

F13 — "lepas daftar masuk, mereka boleh guna sudah"

Dua penambahbaikan supaya aliran guru betul-betul "terus guna":

  F13a  Selepas log masuk Google/ID DELIMa, sandaran Drive diaktifkan AUTOMATIK
        (dulu mesti hidupkan suis sendiri di panel Drive). Ini menjadikan apa yang
        dijangka pengguna benar: arkib terus masuk folder SEPORATOOLKIT dalam Drive dia.

  F13b  Log masuk MOD SETEMPAT dengan emel lalai (akaun pemilik app) -> app meminta guru
        tetapkan emel & PIN mereka sendiri (modal Profil dibuka sekali + toast).
        Tanpa ini, semua guru yang pakai PIN lalai 1234 akan berkongsi satu akaun
        (dan satu arkib) atas nama emel lalai itu.

Nota penting (bukan kod): emel+PIN 1234 hanyalah kunci LOKAL untuk mod setempat.
Log masuk ID DELIMa menggunakan pengesahan Google sendiri (tiada kata laluan DELIMa
ditaip ke dalam app ini).

Guna: python3 patch_fix_onboarding.py index.html sepora_rbt_toolkit.html
"""
import datetime, os, shutil, sys

ANCHOR = """      sess.loginAt = new Date().toISOString();
      setSession(sess);
      setLocked(false);   // [F11] kunci dibuka selepas pengesahan
"""
NEW = """      sess.loginAt = new Date().toISOString();
      setSession(sess);
      setLocked(false);   // [F11] kunci dibuka selepas pengesahan
      // [F13a] log masuk ID DELIMa (Google) -> aktifkan sandaran Drive automatik
      try {
        if (sess.mode === 'delima' && !localStorage.getItem(SEPORA_GDRIVE.autoKey)) {
          localStorage.setItem(SEPORA_GDRIVE.autoKey, '1');
          showToast('Sandaran automatik ke folder "' + SEPORA_GDRIVE.folderName + '" dalam Drive anda: AKTIF.');
        }
      } catch (e) { }
"""

TAIL_OLD = """      showToast('Selamat datang ' + (sess.name || sess.email) + (sess.mode === 'delima' ? ' (ID DELIMa)' : ' (mod setempat)') + '!');
    }"""
TAIL_NEW = """      showToast('Selamat datang ' + (sess.name || sess.email) + (sess.mode === 'delima' ? ' (ID DELIMa)' : ' (mod setempat)') + '!');
      // [F13b] mod setempat dengan emel lalai -> minta guru tetapkan emel & PIN sendiri (sekali sahaja)
      try {
        const gunakanEmelLalai = sess.mode === 'setempat' &&
          String(sess.email || '').toLowerCase() === String(DEFAULT_AUTH.email || '').toLowerCase();
        if (gunakanEmelLalai && !localStorage.getItem('erph_profil_disemak')) {
          localStorage.setItem('erph_profil_disemak', '1');
          setTimeout(function () {
            try {
              openProfileModal();
              showToast('Sila tukar emel & PIN kepada milik anda supaya arkib anda berasingan.');
            } catch (e) { }
          }, 700);
        }
      } catch (e) { }
    }"""


def patch(src):
    if 'F13a' in src:
        return src, False
    assert src.count(ANCHOR) == 1, 'jangkar finishLogin bahagian atas tidak unik'
    src = src.replace(ANCHOR, NEW, 1)
    assert src.count(TAIL_OLD) == 1, 'jangkar hujung finishLogin tidak unik'
    src = src.replace(TAIL_OLD, TAIL_NEW, 1)
    return src, True


def main():
    files = sys.argv[1:] or ['index.html']
    for f in files:
        s = open(f, encoding='utf-8').read()
        os.makedirs('/tmp/sepora_bak', exist_ok=True)
        shutil.copy2(f, '/tmp/sepora_bak/' + os.path.basename(f) + '.bak-f13-' + datetime.datetime.now().strftime('%Y%m%d-%H%M%S'))
        out, ch = patch(s)
        open(f, 'w', encoding='utf-8').write(out)
        print('[OK] %s -> %s' % (f, 'ditampal' if ch else 'sudah ditampal'))
    for f in files:
        s = open(f, encoding='utf-8').read()
        for m in ('[F13a]', '[F13b]', "erph_profil_disemak", "SEPORA_GDRIVE.autoKey, '1'"):
            assert m in s, 'semakan gagal %s: %s' % (f, m)
    print('[SEMAK] F13a (auto-sandaran selepas DELIMa) + F13b (minta emel&PIN sendiri) OK')
    return 0


if __name__ == '__main__':
    sys.exit(main())
