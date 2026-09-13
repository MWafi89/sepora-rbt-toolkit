#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
patch_fix_id_normalize.py  (2026-09-13, Hermes)

F19 — Audit perjalanan GURU BAHARU: guru terkunci daripada akaun sendiri.

Penemuan (ujian perjalanan penuh CDP pada app live):
  D1 KRITIKAL: borang Profil menyimpan emel/ID TANPA normalisasi. Guru taip ID DELIMa
     'g-99001122' -> kredensial tersimpan 'g-99001122' (tiada domain). Selepas itu log masuk
     dengan 'g-99001122@moe-dl.edu.my' (yang mereka ingat) GAGAL -> nampak seperti data hilang
     (arkib dikunci pada kunci akaun yang salah). Bukti: J10/J11/J12 dalam ujian perjalanan.
  D2 TINGGI: log masuk tidak normalisasi input -> menaip ID DELIMa tanpa domain gagal walaupun
     itu ID rasmi guru.
  D3 SEDERHANA: mesej ralat log masuk tidak memberi jalan keluar (hanya "salah").
  D4 RENDAH: toster bertimbun (beberapa mesej serentak) -> mesej tersembunyi.

Pembetulan:
  1. normalizeIdDelima(v): buang awalan "ID DELIMa", tambah '@moe-dl.edu.my' jika tiada domain.
     Digunakan pada borang daftar, borang Profil, dan borang log masuk.
  2. submitTeacherProfile: normalisasi + pengesahan format emel + PIN minimum 4 aksara,
     dan toster menunjukkan emel sebenar yang disimpan.
  3. handleLoginSubmit: normalisasi input; mesej ralat memberi pilihan (butang Guru baharu).
  4. showToast: had 3 toser serentak (yang lama dibuang).

Guna: python3 patch_fix_id_normalize.py index.html sepora_rbt_toolkit.html
"""
import datetime, os, shutil, sys

HELPER_ANCHOR = "    async function handleLoginSubmit(event) {"
HELPER_NEW = """    /* [F19] Normalisasi ID DELIMa / emel: 'g-99001122' -> 'g-99001122@moe-dl.edu.my' */
    function normalizeIdDelima(v) {
      let s = String(v == null ? '' : v).trim().toLowerCase();
      if (!s) return '';
      s = s.replace(/^id\\s*delima\\s*[:\\-]?\\s*/i, '').trim();
      if (s.indexOf('@') === -1) s = s + '@moe-dl.edu.my';
      return s;
    }
    function idDelimaSah(emel) { return /^[^@\\s]+@[^@\\s]+\\.[^@\\s]+$/.test(String(emel || '')); }

    async function handleLoginSubmit(event) {"""

LOGIN_OLD = """      const inputEmail = document.getElementById('loginInputEmail').value.trim().toLowerCase();"""
LOGIN_NEW = """      const inputEmail = normalizeIdDelima(document.getElementById('loginInputEmail').value);   // [F19] terima ID DELIMa tanpa domain"""

LOGIN_ERR_OLD = """        showToast('Emel atau Kata Laluan/PIN salah. Sila cuba lagi!');"""
LOGIN_ERR_NEW = """        showToast('Emel/ID DELIMa atau PIN salah. Cuba lagi - atau tekan "Guru baharu?" untuk daftar akaun anda sendiri.');"""

PROF_OLD = """      const newEmail = document.getElementById('modalAuthEmail').value.trim().toLowerCase();
      const newPassword = document.getElementById('modalAuthPassword').value.trim();

      if (newEmail && newPassword) {
        await simpanKredensial(newEmail, newPassword);   // [W2] simpan hash, bukan teks biasa
      }

      localStorage.setItem('erph_teacher', JSON.stringify(teacherProfile));
      syncTeacherUI();
      closeModalDirectly();
      showToast('Profil dan Emel log masuk privasi berjaya dikemaskini!');"""
PROF_NEW = """      const newEmail = normalizeIdDelima(document.getElementById('modalAuthEmail').value);   // [F19]
      const newPassword = document.getElementById('modalAuthPassword').value.trim();

      if (newEmail && !idDelimaSah(newEmail)) {
        showToast('Emel/ID DELIMa tidak sah. Contoh: g-12345678 atau nama@moe-dl.edu.my');
        return;
      }
      if ((newEmail && !newPassword) || (!newEmail && newPassword)) {
        showToast('Isi KEDUA-DUA emel/ID DELIMa dan PIN (atau biarkan kedua-duanya kosong).');
        return;
      }
      if (newEmail && newPassword && newPassword.length < 4) {
        showToast('PIN terlalu pendek - minimum 4 aksara.');
        return;
      }
      if (newEmail && newPassword) {
        await simpanKredensial(newEmail, newPassword);   // [W2] hash, bukan teks biasa
        try { const f = document.getElementById('loginInputEmail'); if (f) f.value = newEmail; } catch (e) { }
      }

      localStorage.setItem('erph_teacher', JSON.stringify(teacherProfile));
      syncTeacherUI();
      closeModalDirectly();
      showToast(newEmail ? ('Profil dikemas kini. Log masuk anda: ' + newEmail) : 'Profil berjaya dikemaskini!');"""

TOAST_OLD = """      const toast = document.createElement('div');
      toast.className = 'toast';"""
TOAST_NEW = """      while (container.children.length >= 3) { try { container.removeChild(container.firstChild); } catch (e) { break; } }   // [F19] had 3 toser
      const toast = document.createElement('div');
      toast.className = 'toast';"""


def patch(src):
    if '[F19]' in src:
        return src, False
    for old, new, nama in (
        (HELPER_ANCHOR, HELPER_NEW, 'helper normalizeIdDelima'),
        (LOGIN_OLD, LOGIN_NEW, 'login normalisasi'),
        (LOGIN_ERR_OLD, LOGIN_ERR_NEW, 'mesej ralat login'),
        (PROF_OLD, PROF_NEW, 'profil normalisasi + pengesahan'),
        (TOAST_OLD, TOAST_NEW, 'had toser'),
    ):
        assert src.count(old) == 1, 'jangkar %s tidak unik (%d)' % (nama, src.count(old))
        src = src.replace(old, new, 1)
    return src, True


def main():
    files = sys.argv[1:] or ['index.html']
    for f in files:
        s = open(f, encoding='utf-8').read()
        os.makedirs('/tmp/sepora_bak', exist_ok=True)
        shutil.copy2(f, '/tmp/sepora_bak/' + os.path.basename(f) + '.bak-f19-' + datetime.datetime.now().strftime('%Y%m%d-%H%M%S'))
        out, ch = patch(s)
        open(f, 'w', encoding='utf-8').write(out)
        print('[OK] %s -> %s' % (f, 'ditampal' if ch else 'sudah ditampal'))
    for f in files:
        s = open(f, encoding='utf-8').read()
        for m in ('[F19]', 'function normalizeIdDelima', 'function idDelimaSah', 'had 3 toser'):
            assert m in s, 'semakan gagal %s: %s' % (f, m)
    print('[SEMAK] F19 normalisasi ID DELIMa OK')
    return 0


if __name__ == '__main__':
    sys.exit(main())
